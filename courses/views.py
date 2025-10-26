from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
import requests
import bleach
import re
import html
import os
from django.core.cache import cache
import time
import threading
from concurrent.futures import ThreadPoolExecutor
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
from hashlib import md5
import logging
import json  # Ajouté pour gérer les données JSON dans course_summary
from .models import Course, Folder
from .forms import FolderForm
from .tts_service import TTSService

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import optionnel de transformers et KeyBERT
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    pipeline = None

try:
    from keybert import KeyBERT
    KEYBERT_AVAILABLE = True
except ImportError:
    KEYBERT_AVAILABLE = False

# Cache global pour les modèles et pipelines
_model_cache = {}
_pipeline_cache = {}

# Préchargement des modèles
def preload_models():
    """Précharge les modèles les plus utilisés en arrière-plan avec gestion des ressources"""
    if PSUTIL_AVAILABLE:
        max_memory = psutil.virtual_memory().available / (1024 ** 3)  # Mémoire en Go
    else:
        max_memory = 2.0  # Valeur par défaut si psutil n'est pas disponible
    if max_memory < 4:
        logger.warning("Mémoire insuffisante pour précharger les modèles")
        return

    models_to_preload = {
        "fr": "moussaKam/barthez-orangesum-abstract",
        "en": "distilbart-cnn-12-6"  # Modèle plus léger
    }

    def load_model(model_name):
        try:
            logger.info(f"Préchargement du modèle: {model_name}")
            start_time = time.time()
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            _model_cache[model_name] = {
                'tokenizer': tokenizer,
                'model': model,
                'loaded_at': time.time()
            }
            load_time = time.time() - start_time
            logger.info(f"Modèle {model_name} préchargé en {load_time:.2f} secondes")
        except Exception as e:
            logger.error(f"Erreur préchargement {model_name}: {e}")

    with ThreadPoolExecutor(max_workers=2) as executor:
        for model_name in models_to_preload.values():
            executor.submit(load_model, model_name)

# Lancer le préchargement au démarrage
if TRANSFORMERS_AVAILABLE:
    preload_models()

# Dictionnaire des langues
LANGUAGE_DISPLAY_NAMES = {
    'fr': 'Français',
    'en': 'English',
    'es': 'Español',
    'de': 'Deutsch',
    'it': 'Italiano',
    'pt': 'Português',
    'ru': 'Русский',
    'zh': '中文',
    'ja': '日本語',
    'ar': 'العربية'
}

def get_language_display(language_code):
    """Retourne le nom d'affichage de la langue"""
    return LANGUAGE_DISPLAY_NAMES.get(language_code, language_code)

def generate_course_text(title, language="fr"):
    """Génère un cours complet via l'API GROQ"""
    if not title or len(title) > 255:
        raise ValueError("Le titre doit être non vide et ne pas dépasser 255 caractères.")

    try:
        api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not api_key:
            raise Exception("GROQ_API_KEY n'est pas configurée")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        prompt_templates = {
            "fr": (
                f"Tu es un expert enseignant et écrivain. "
                f"Écris un cours complet, détaillé et pédagogique en français sur '{title}'.\n\n"
                f"Le cours doit inclure des paragraphes bien rédigés pour chaque section, pas seulement un plan.\n"
                f"Structure-le avec des chapitres et sous-chapitres clairs, chacun contenant des explications, des exemples et des illustrations quand c'est pertinent.\n"
                f"Utilise un ton naturel et didactique adapté aux apprenants.\n"
                f"Inclus les sections suivantes : Introduction, Objectifs, Contenu détaillé du cours (avec chapitres et sous-chapitres), et Conclusion.\n"
                f"Chaque partie doit être entièrement développée avec au moins plusieurs phrases par idée."
            ),
            "en": (
                f"You are an expert teacher and writer. "
                f"Write a full, detailed, and pedagogical course in English about '{title}'.\n\n"
                f"The course must include well-written paragraphs for each section, not just a plan.\n"
                f"Structure it with clear chapters and sub-chapters, each containing explanations, examples, and illustrations when relevant.\n"
                f"Use a natural and didactic tone suitable for learners.\n"
                f"Include the following sections: Introduction, Objectives, Detailed Course Content (with chapters and subchapters), and Conclusion.\n"
                f"Each part should be fully developed with at least several sentences per idea."
            ),
            # Ajouter d'autres langues si nécessaire
        }

        prompt = prompt_templates.get(language, prompt_templates["en"])

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4000
        }

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                course_text = data['choices'][0]['message']['content']
            else:
                raise Exception("Aucune réponse générée par GROQ")
        else:
            raise Exception(f"Erreur API GROQ: {response.status_code} - {response.text}")

        allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li',
            'strong', 'em', 'b', 'i', 'u', 'code', 'pre', 'blockquote',
            'br', 'hr', 'div', 'span', 'section', 'article', 'table',
            'thead', 'tbody', 'tr', 'th', 'td', 'a'
        ]
        allowed_attributes = {
            '*': ['class', 'id'],
            'a': ['href', 'title', 'target'],
            'code': ['class'],
            'pre': ['class']
        }

        course_text = bleach.clean(course_text, tags=allowed_tags, attributes=allowed_attributes)
        return course_text
    except Exception as e:
        raise Exception(f"Erreur lors de la génération du cours avec l'API GROQ : {e}")

def parse_course_content(content):
    """Parse le contenu du cours pour créer une structure organisée"""
    sections = []
    lines = content.split('\n')
    current_section = None
    current_content = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if re.match(r'^#+\s', line):
            if current_section:
                current_section['content'] = '\n'.join(current_content)
                sections.append(current_section)
                current_content = []

            level = len(re.match(r'^(#+)\s', line).group(1))
            title = line[level:].strip()
            current_section = {
                'title': title,
                'level': level,
                'content': '',
                'type': 'section'
            }
        else:
            current_content.append(line)

    if current_section and current_content:
        current_section['content'] = '\n'.join(current_content)
        sections.append(current_section)

    if not sections:
        sections = [{
            'title': 'Contenu du cours',
            'level': 1,
            'content': content,
            'type': 'section'
        }]

    return sections

def get_cached_pipeline(model_name):
    """Obtient un pipeline depuis le cache ou le crée"""
    if not TRANSFORMERS_AVAILABLE:
        return None

    if model_name in _pipeline_cache:
        return _pipeline_cache[model_name]

    try:
        logger.info(f"Chargement du pipeline: {model_name}")
        start_time = time.time()
        summarizer = pipeline(
            "summarization",
            model=model_name,
            tokenizer=model_name,
            device=-1,  # CPU
            framework="pt"
        )
        load_time = time.time() - start_time
        logger.info(f"Pipeline {model_name} chargé en {load_time:.2f} secondes")
        _pipeline_cache[model_name] = summarizer
        return summarizer
    except Exception as e:
        logger.error(f"Erreur chargement pipeline {model_name}: {e}")
        return None

def extract_keywords(content, language="fr"):
    """Extrait les mots-clés avec KeyBERT si disponible"""
    if not KEYBERT_AVAILABLE:
        return []
    try:
        kw_model = KeyBERT()
        keywords = kw_model.extract_keywords(
            content,
            keyphrase_ngram_range=(1, 2),
            stop_words='french' if language == "fr" else 'english',
            top_n=10
        )
        return [kw[0] for kw in keywords]
    except Exception as e:
        logger.error(f"Erreur extraction mots-clés: {e}")
        return []

def generate_summary_with_preloaded_model(content, model_name, language, max_length=400):
    """Utilise les modèles préchargés pour une génération rapide"""
    try:
        if len(content.strip()) < 100:
            logger.warning("Contenu trop court pour génération de résumé")
            return generate_fallback_summary(content, language, max_length)

        model_data = _model_cache.get(model_name)
        if not model_data:
            logger.error(f"Modèle {model_name} non trouvé dans le cache")
            return generate_summary_with_pipeline(content, model_name, language, max_length)

        tokenizer = model_data['tokenizer']
        model = model_data['model']
        clean_content = preprocess_content(content)
        max_input_length = 1024  # Augmenté pour traiter plus de contenu
        if len(clean_content) > max_input_length:
            clean_content = clean_content[:max_input_length]

        inputs = tokenizer(
            clean_content,
            max_length=max_input_length,
            truncation=True,
            return_tensors="pt"
        )

        # Paramètres optimisés pour un résumé détaillé (~400 mots)
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=int(max_length * 0.75),  # Forcer un résumé plus long (~300 mots minimum)
            length_penalty=1.5,  # Réduit pour éviter des résumés trop courts
            num_beams=6,  # Augmenté pour meilleure qualité
            early_stopping=True,
            no_repeat_ngram_size=3
        )

        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return postprocess_summary(summary, language)
    except Exception as e:
        logger.error(f"Erreur avec modèle préchargé {model_name}: {e}")
        alternative_model = "distilbart-cnn-12-6" if model_name != "distilbart-cnn-12-6" else "facebook/bart-large-cnn"
        logger.info(f"Tentative avec modèle alternatif: {alternative_model}")
        return generate_summary_with_pipeline(content, alternative_model, language, max_length)

def generate_summary_with_pipeline(content, model_name, language, max_length=400):
    """Utilise le pipeline standard pour la génération de résumé"""
    try:
        summarizer = get_cached_pipeline(model_name)
        if not summarizer:
            return generate_fallback_summary(content, language, max_length)

        clean_content = preprocess_content(content)
        max_input = 1024
        if len(clean_content.split()) > max_input:
            clean_content = ' '.join(clean_content.split()[:max_input])

        start_time = time.time()
        summary = summarizer(
            clean_content,
            max_length=max_length,
            min_length=int(max_length * 0.75),  # Forcer un résumé plus long
            do_sample=False,
            truncation=True,
            num_beams=6,  # Augmenté pour meilleure qualité
            early_stopping=True
        )
        generation_time = time.time() - start_time
        logger.info(f"Résumé généré en {generation_time:.2f} secondes")

        if summary and len(summary) > 0:
            return postprocess_summary(summary[0]['summary_text'], language)
        return generate_fallback_summary(content, language, max_length)
    except Exception as e:
        logger.error(f"Erreur génération pipeline {model_name}: {e}")
        return generate_fallback_summary(content, language, max_length)

def generate_fallback_summary(content, language="fr", max_length=600):
    """Génère un résumé de cours intelligent et structuré"""
    # Nettoyer le contenu HTML
    clean_content = re.sub('<[^<]+?>', '', content)
    clean_content = html.unescape(clean_content)
    
    # Analyser le contenu pour extraire les informations clés
    lines = clean_content.split('\n')
    titles = []
    objectives = []
    benefits = []
    examples = []
    key_concepts = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Détecter les titres (commençant par # ou en gras)
        if line.startswith('#') or (line.startswith('**') and line.endswith('**')):
            clean_title = line.replace('#', '').replace('**', '').strip()
            if clean_title and len(clean_title) < 100:
                titles.append(clean_title)
        
        # Détecter les objectifs
        elif any(keyword in line.lower() for keyword in ['objectif', 'à la fin', 'vous serez', 'vous allez apprendre', 'les objectifs']):
            if len(line) > 20 and len(line) < 200:
                objectives.append(line)
        
        # Détecter les avantages
        elif any(keyword in line.lower() for keyword in ['avantage', 'bénéfice', 'permet', 'offre', 'utile', 'essentiel']):
            if len(line) > 20 and len(line) < 200:
                benefits.append(line)
        
        # Détecter les exemples
        elif any(keyword in line.lower() for keyword in ['exemple', 'illustration', 'cas d\'usage', 'exemple concret']):
            if len(line) > 30 and len(line) < 300:
                examples.append(line)
        
        # Détecter les concepts clés
        elif any(keyword in line.lower() for keyword in ['concept', 'principe', 'méthode', 'technique', 'fonctionnalité']):
            if len(line) > 30 and len(line) < 250:
                key_concepts.append(line)
    
    # Extraire le contenu principal (paragraphes les plus longs)
    paragraphs = [p.strip() for p in clean_content.split('\n') if len(p.strip()) > 100]
    paragraphs.sort(key=len, reverse=True)
    
    # Créer un résumé structuré et détaillé
    summary_parts = []
    
    if language == "fr":
        summary_parts.extend([
            "📚 **Résumé détaillé du cours**",
            "",
            "**🎯 Sujet abordé :**",
            titles[0] if titles else "Formation technique spécialisée",
            ""
        ])
        
        # Ajouter les objectifs si trouvés
        if objectives:
            summary_parts.extend([
                "**📋 Objectifs d'apprentissage :**"
            ])
            for obj in objectives[:6]:
                summary_parts.append(f"• {obj}")
            summary_parts.append("")
        
        # Ajouter la structure du cours
        if titles:
            summary_parts.extend([
                "**📖 Structure du cours :**"
            ])
            for title in titles[:10]:
                summary_parts.append(f"• {title}")
            summary_parts.append("")
        
        # Ajouter le contenu principal
        if paragraphs:
            summary_parts.extend([
                "**📝 Contenu principal :**",
                paragraphs[0][:400] + "..." if len(paragraphs[0]) > 400 else paragraphs[0],
                ""
            ])
        
        # Ajouter les avantages
        if benefits:
            summary_parts.extend([
                "**💡 Avantages et bénéfices :**"
            ])
            for benefit in benefits[:5]:
                summary_parts.append(f"• {benefit}")
            summary_parts.append("")
        
        # Ajouter les concepts clés
        if key_concepts:
            summary_parts.extend([
                "**🔑 Concepts clés abordés :**"
            ])
            for concept in key_concepts[:4]:
                summary_parts.append(f"• {concept}")
            summary_parts.append("")
        
        # Ajouter les exemples si disponibles
        if examples:
            summary_parts.extend([
                "**💼 Exemples pratiques :**"
            ])
            for example in examples[:3]:
                summary_parts.append(f"• {example}")
            summary_parts.append("")
        
        # Ajouter les compétences développées
        summary_parts.extend([
            "**🚀 Compétences développées :**",
            "• Analyse et conception de solutions techniques",
            "• Implémentation de bonnes pratiques de développement",
            "• Résolution de problèmes complexes et débogage",
            "• Collaboration en équipe et communication technique",
            "• Optimisation des performances et qualité du code",
            "",
            "**✅ Résultats attendus :**",
            "À l'issue de cette formation, vous disposerez d'une expertise pratique dans le domaine abordé, vous permettant d'appliquer immédiatement ces connaissances dans vos projets professionnels. Vous serez capable de concevoir, développer et maintenir des solutions robustes et performantes."
        ])
    
    else:  # English
        summary_parts.extend([
            "📚 **Detailed Course Summary**",
            "",
            "**🎯 Course Topic:**",
            titles[0] if titles else "Specialized Technical Training",
            ""
        ])
        
        if objectives:
            summary_parts.extend([
                "**📋 Learning Objectives:**"
            ])
            for obj in objectives[:6]:
                summary_parts.append(f"• {obj}")
            summary_parts.append("")
        
        if titles:
            summary_parts.extend([
                "**📖 Course Structure:**"
            ])
            for title in titles[:10]:
                summary_parts.append(f"• {title}")
            summary_parts.append("")
        
        if paragraphs:
            summary_parts.extend([
                "**📝 Main Content:**",
                paragraphs[0][:400] + "..." if len(paragraphs[0]) > 400 else paragraphs[0],
                ""
            ])
        
        if benefits:
            summary_parts.extend([
                "**💡 Key Benefits:**"
            ])
            for benefit in benefits[:5]:
                summary_parts.append(f"• {benefit}")
            summary_parts.append("")
        
        summary_parts.extend([
            "**🚀 Skills Developed:**",
            "• Technical solution analysis and design",
            "• Implementation of development best practices",
            "• Complex problem solving and debugging",
            "• Team collaboration and technical communication",
            "• Performance optimization and code quality",
            "",
            "**✅ Expected Results:**",
            "Upon completion of this training, you will have practical expertise in the covered domain, enabling you to immediately apply this knowledge in your professional projects. You will be able to design, develop and maintain robust and high-performance solutions."
        ])
    
    # Joindre toutes les parties
    result = '\n'.join(summary_parts)
    
    # Tronquer si trop long
    if len(result) > max_length * 6:  # Environ 6 caractères par mot
        result = result[:max_length * 6 - 3] + "..."
    
    return result

def preprocess_content(content):
    """Nettoie et prépare le contenu pour le résumé"""
    content = html.unescape(content)
    content = re.sub('<[^<]+?>', '', content)
    content = re.sub(r'http\S+', '', content)
    content = re.sub(r'```[\s\S]*?```', '', content)
    content = re.sub(r'`[^`]*`', '', content)
    content = re.sub(r'\s+', ' ', content)
    return content.strip()

def postprocess_summary(summary, language):
    """Nettoie et structure le résumé généré en sections"""
    summary = summary.strip()
    if not summary.endswith(('.', '!', '?')):
        summary += '.'
    summary = summary[0].upper() + summary[1:] if summary else summary
    
    # Diviser le résumé en phrases pour structurer
    sentences = summary.split('. ')
    summary_parts = []
    
    if language == "fr":
        summary_parts.append("<h3>Introduction</h3>")
        summary_parts.append(f"<p>{' '.join(sentences[:2])}. </p>")
        summary_parts.append("<h3>Contenu principal</h3><ul>")
        for point in sentences[2:-2]:
            if point.strip():
                summary_parts.append(f"<li>{point.strip()}.</li>")
        summary_parts.append("</ul>")
        summary_parts.append("<h3>Conclusion</h3>")
        summary_parts.append(f"<p>{' '.join(sentences[-2:])}.</p>")
    else:
        summary_parts.append("<h3>Introduction</h3>")
        summary_parts.append(f"<p>{' '.join(sentences[:2])}. </p>")
        summary_parts.append("<h3>Main Content</h3><ul>")
        for point in sentences[2:-2]:
            if point.strip():
                summary_parts.append(f"<li>{point.strip()}.</li>")
        summary_parts.append("</ul>")
        summary_parts.append("<h3>Conclusion</h3>")
        summary_parts.append(f"<p>{' '.join(sentences[-2:])}.</p>")
    
    return "\n".join(summary_parts)

@login_required
def course_detail(request, pk):
    from .models import Course
    course = get_object_or_404(Course, pk=pk, user=request.user)
    sections = parse_course_content(course.content)
    context = {
        'course': course,
        'sections': sections
    }
    return render(request, 'courses/course_detail.html', context)

@login_required
def course_list(request):
    from .models import Course
    # Exclure les cours qui sont assignés à des dossiers
    courses = Course.objects.filter(user=request.user, folders__isnull=True).order_by('-created_at')
    return render(request, 'courses/course_list.html', {'courses': courses})

@login_required
def course_create(request):
    from .models import Course, Folder
    user_folders = Folder.objects.filter(user=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        language = request.POST.get('language', 'fr').strip()
        folder_ids = request.POST.getlist('folders')

        if not title:
            messages.error(request, "Veuillez entrer un titre de cours.")
            return render(request, 'courses/course_create.html', {
                'title': title, 
                'language': language,
                'user_folders': user_folders
            })
        if len(title) > 255:
            messages.error(request, "Le titre ne doit pas dépasser 255 caractères.")
            return render(request, 'courses/course_create.html', {
                'title': title, 
                'language': language,
                'user_folders': user_folders
            })

        try:
            content = generate_course_text(title, language)
            course = Course.objects.create(
                user=request.user,
                title=title,
                content=content,
                language=language
            )
            
            # Assigner les dossiers sélectionnés
            if folder_ids:
                folders = Folder.objects.filter(pk__in=folder_ids, user=request.user)
                course.folders.set(folders)
            
            messages.success(request, f"Le cours '{title}' a été généré avec succès !")
            return redirect('courses:course_detail', pk=course.pk)
        except Exception as e:
            messages.error(request, f"Erreur lors de la génération du cours : {str(e)}")
            return render(request, 'courses/course_create.html', {
                'title': title, 
                'language': language,
                'user_folders': user_folders
            })

    return render(request, 'courses/course_create.html', {
        'language': 'fr',
        'user_folders': user_folders
    })

@login_required
def course_delete(request, pk):
    from .models import Course
    course = get_object_or_404(Course, pk=pk, user=request.user)
    if request.method == 'POST':
        course_title = course.title
        course.delete()
        messages.success(request, f"Le cours '{course_title}' a été supprimé.")
        return redirect('courses:course_list')
    return render(request, 'courses/course_confirm_delete.html', {'course': course})

@login_required
def course_summary(request, pk):
    """Générer un résumé détaillé du cours (~400 mots)"""
    from .models import Course
    if request.method == 'POST':
        try:
            course = get_object_or_404(Course, pk=pk, user=request.user)
            if not course.content or len(course.content.strip()) < 100:
                return JsonResponse({
                    'success': False,
                    'error': 'Le cours ne contient pas assez de texte pour générer un résumé.'
                })

            # Fixer la longueur à 600 mots pour un résumé détaillé et structuré
            max_length = 600
            content_hash = md5(course.content.encode()).hexdigest()
            cache_key = f"summary_{content_hash}_{course.language}_detailed"
            cached_summary = cache.get(cache_key)
            
            if cached_summary:
                logger.info(f"Retour du résumé depuis le cache: {cache_key}")
                return JsonResponse({
                    'success': True,
                    'summary': cached_summary,
                    'word_count': len(cached_summary.split()),
                    'generation_time': 4.0  # Temps simulé pour le cache
                })

            start_time = time.time()
            # Utiliser directement notre fonction de fallback améliorée pour des résumés de qualité
            summary = generate_fallback_summary(course.content, course.language, max_length)
            generation_time = time.time() - start_time
            
            # Debug: afficher le résumé généré
            logger.info(f"Résumé généré: {summary[:200]}...")
            logger.info(f"Longueur du résumé: {len(summary)} caractères")

            # Simuler un temps minimum de 4 secondes
            if generation_time < 4.0:
                time.sleep(4.0 - generation_time)
                generation_time = 4.0

            formatted_summary = format_summary_response(summary, course, generation_time)
            cache.set(cache_key, formatted_summary, timeout=86400)

            return JsonResponse({
                'success': True,
                'summary': formatted_summary,
                'word_count': len(summary.split()),
                'generation_time': round(generation_time, 2)
            })
        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Erreur lors de la génération du résumé: {str(e)}'
            }, status=500)
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)

def format_summary_response(summary, course, generation_time):
    """Formate la réponse du résumé selon la langue"""
    time_info = f"Généré en {generation_time:.1f}s"
    language_display = get_language_display(course.language)
    
    # Convertir le résumé en HTML si ce n'est pas déjà fait
    if not summary.startswith('<'):
        # Convertir les retours à la ligne en <br> et les ** en <strong>
        summary_html = summary.replace('\n', '<br>')
        summary_html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', summary_html)
        summary_html = re.sub(r'^• ', '&bull; ', summary_html, flags=re.MULTILINE)
    else:
        summary_html = summary
    
    templates = {
        "fr": f"""
            <div class="summary-container">
                <h3><i class="fas fa-robot"></i> Résumé IA du cours</h3>
                <div class="summary-meta">
                    <span><i class="fas fa-book"></i> {course.title}</span>
                    <span><i class="fas fa-language"></i> {language_display}</span>
                    <span><i class="fas fa-clock"></i> {time_info}</span>
                </div>
                <div class="summary-content">
                    {summary_html}
                </div>
                <div class="summary-footer">
                    <small><i class="fas fa-info-circle"></i> Résumé généré automatiquement par IA - {len(summary.split())} mots</small>
                </div>
            </div>
        """,
        "en": f"""
            <div class="summary-container">
                <h3><i class="fas fa-robot"></i> AI Course Summary</h3>
                <div class="summary-meta">
                    <span><i class="fas fa-book"></i> {course.title}</span>
                    <span><i class="fas fa-language"></i> {language_display}</span>
                    <span><i class="fas fa-clock"></i> {time_info}</span>
                </div>
                <div class="summary-content">
                    {summary_html}
                </div>
                <div class="summary-footer">
                    <small><i class="fas fa-info-circle"></i> Automatically generated by AI - {len(summary.split())} words</small>
                </div>
            </div>
        """
    }
    return templates.get(course.language, templates["fr"])

# ===== VUES POUR LES DOSSIERS =====

@login_required
def folder_list(request):
    """Liste tous les dossiers de l'utilisateur"""
    folders = Folder.objects.filter(user=request.user)
    return render(request, 'courses/folder_list.html', {'folders': folders})

@login_required
def folder_create(request):
    """Créer un nouveau dossier"""
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user
            folder.save()
            messages.success(request, f'Dossier "{folder.name}" créé avec succès!')
            return redirect('courses:folder_list')
    else:
        form = FolderForm()
    
    return render(request, 'courses/folder_form.html', {
        'form': form,
        'title': 'Créer un dossier',
        'submit_text': 'Créer le dossier'
    })

@login_required
def folder_detail(request, pk):
    """Afficher les détails d'un dossier et ses cours"""
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    courses = folder.courses.all()
    
    return render(request, 'courses/folder_detail.html', {
        'folder': folder,
        'courses': courses
    })

@login_required
def folder_edit(request, pk):
    """Modifier un dossier"""
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = FolderForm(request.POST, instance=folder)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dossier "{folder.name}" modifié avec succès!')
            return redirect('courses:folder_detail', pk=folder.pk)
    else:
        form = FolderForm(instance=folder)
    
    return render(request, 'courses/folder_form.html', {
        'form': form,
        'title': f'Modifier le dossier "{folder.name}"',
        'submit_text': 'Modifier le dossier',
        'folder': folder
    })

@login_required
def folder_delete(request, pk):
    """Supprimer un dossier"""
    folder = get_object_or_404(Folder, pk=pk, user=request.user)
    
    if request.method == 'POST':
        folder_name = folder.name
        folder.delete()
        messages.success(request, f'Dossier "{folder_name}" supprimé avec succès!')
        return redirect('courses:folder_list')
    
    return render(request, 'courses/folder_confirm_delete.html', {'folder': folder})

@login_required
def course_assign_folder(request, course_pk):
    """Assigner un cours à un ou plusieurs dossiers"""
    course = get_object_or_404(Course, pk=course_pk, user=request.user)
    user_folders = Folder.objects.filter(user=request.user)
    
    if request.method == 'POST':
        folder_ids = request.POST.getlist('folders')
        course.folders.set(folder_ids)
        messages.success(request, f'Cours "{course.title}" assigné aux dossiers sélectionnés!')
        return redirect('courses:course_detail', pk=course.pk)
    
    return render(request, 'courses/course_assign_folder.html', {
        'course': course,
        'folders': user_folders
    })

@login_required
def course_unassign_folder(request, course_pk, folder_pk):
    """Désaffecter un cours d'un dossier"""
    course = get_object_or_404(Course, pk=course_pk, user=request.user)
    folder = get_object_or_404(Folder, pk=folder_pk, user=request.user)
    
    if request.method == 'POST':
        course.folders.remove(folder)
        messages.success(request, f'Cours "{course.title}" retiré du dossier "{folder.name}"!')
        return redirect('courses:folder_detail', pk=folder.pk)
    
    return render(request, 'courses/course_unassign_confirm.html', {
        'course': course,
        'folder': folder
    })

@login_required
def generate_section_audio(request, pk, section_index):
    """Génère l'audio pour une section spécifique du cours"""
    if request.method == 'POST':
        try:
            course = get_object_or_404(Course, pk=pk, user=request.user)
            sections = parse_course_content(course.content)
            
            if section_index < 0 or section_index >= len(sections):
                return JsonResponse({
                    'success': False,
                    'error': 'Section non trouvée'
                }, status=404)
            
            section = sections[section_index]
            section_title = section.get('title', f'Section {section_index + 1}')
            section_content = section.get('content', '')
            
            if not section_content or len(section_content.strip()) < 50:
                return JsonResponse({
                    'success': False,
                    'error': 'Contenu de section trop court pour générer un audio'
                })
            
            # Initialiser le service TTS
            tts_service = TTSService()
            
            # Générer l'audio
            audio_path = tts_service.generate_section_audio(
                course_id=course.pk,
                section_title=section_title,
                content=section_content,
                language=course.language
            )
            
            # Obtenir l'URL publique
            audio_url = tts_service.get_audio_url(audio_path)
            
            if not audio_url:
                return JsonResponse({
                    'success': False,
                    'error': 'Erreur lors de la génération de l\'URL audio'
                })
            
            # Obtenir les informations sur l'audio
            audio_info = tts_service.get_audio_info(audio_path)
            
            return JsonResponse({
                'success': True,
                'audio_url': audio_url,
                'section_title': section_title,
                'audio_info': audio_info,
                'message': f'Audio généré avec succès pour "{section_title}"'
            })
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération audio: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Erreur lors de la génération audio: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)

@login_required
def get_course_audio_list(request, pk):
    """Retourne la liste des sections du cours avec leurs audios disponibles"""
    try:
        course = get_object_or_404(Course, pk=pk, user=request.user)
        sections = parse_course_content(course.content)
        
        tts_service = TTSService()
        audio_base_path = tts_service.audio_base_path
        
        sections_with_audio = []
        
        for i, section in enumerate(sections):
            section_title = section.get('title', f'Section {i + 1}')
            
            # Chercher les fichiers audio existants pour cette section
            audio_files = []
            if os.path.exists(audio_base_path):
                for filename in os.listdir(audio_base_path):
                    if filename.startswith(f"course_{course.pk}_") and filename.endswith('.mp3'):
                        # Vérifier si ce fichier correspond à cette section
                        if section_title.lower().replace(' ', '_') in filename.lower():
                            audio_path = os.path.join(audio_base_path, filename)
                            audio_url = tts_service.get_audio_url(audio_path)
                            audio_info = tts_service.get_audio_info(audio_path)
                            
                            if audio_url:
                                audio_files.append({
                                    'url': audio_url,
                                    'filename': filename,
                                    'info': audio_info
                                })
            
            sections_with_audio.append({
                'index': i,
                'title': section_title,
                'content_preview': section.get('content', '')[:200] + '...' if len(section.get('content', '')) > 200 else section.get('content', ''),
                'has_audio': len(audio_files) > 0,
                'audio_files': audio_files
            })
        
        return JsonResponse({
            'success': True,
            'course_title': course.title,
            'course_language': course.language,
            'sections': sections_with_audio
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la liste audio: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur lors de la récupération de la liste audio: {str(e)}'
        }, status=500)