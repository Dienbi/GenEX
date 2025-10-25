import json
import time
import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import ChatSession, ChatMessage, EducationalSubject, UploadedFile
from .services import GroqChatService
from .file_processor import FileProcessor
from .pdf_generator import PDFGenerator
import logging

logger = logging.getLogger(__name__)


class ChatbotView(LoginRequiredMixin, View):
    """Vue principale du chatbot"""
    
    def get(self, request):
        # Récupérer les sessions de chat de l'utilisateur
        sessions = ChatSession.objects.filter(user=request.user, is_active=True)
        
        # Récupérer les sujets éducatifs
        subjects = EducationalSubject.objects.filter(is_active=True)
        
        context = {
            'sessions': sessions,
            'subjects': subjects,
            'user_theme': request.user.theme_preference if request.user.is_authenticated else 'auto',
        }
        return render(request, 'chatbot/chat.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(LoginRequiredMixin, View):
    """API pour gérer les messages du chatbot"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'error': 'Message vide'}, status=400)
            
            # Récupérer ou créer une session
            if session_id:
                session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            else:
                session = ChatSession.objects.create(
                    user=request.user,
                    title=message[:50] + "..." if len(message) > 50 else message
                )
            
            # Enregistrer le message de l'utilisateur
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=message
            )
            
            # Détecter le sujet éducatif
            detected_subject = self._detect_educational_subject(message)
            if detected_subject:
                user_message.subject_detected = detected_subject
                user_message.save()
            
            # Obtenir la réponse du chatbot
            start_time = time.time()
            chat_service = GroqChatService()
            
            # Récupérer l'historique de la conversation
            conversation_history = self._get_conversation_history(session)
            
            response = chat_service.get_response(message, conversation_history, detected_subject)
            response_time = time.time() - start_time
            
            # Enregistrer la réponse du chatbot
            assistant_message = ChatMessage.objects.create(
                session=session,
                message_type='assistant',
                content=response,
                subject_detected=detected_subject,
                response_time=response_time
            )
            
            return JsonResponse({
                'success': True,
                'response': response,
                'session_id': session.id,
                'message_id': assistant_message.id,
                'response_time': round(response_time, 2)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données JSON invalides'}, status=400)
        except Exception as e:
            logger.error(f"Erreur dans ChatAPIView: {str(e)}")
            return JsonResponse({'error': 'Erreur interne du serveur'}, status=500)
    
    def _detect_educational_subject(self, message):
        """Détecte le sujet éducatif basé sur le contenu du message"""
        message_lower = message.lower()
        
        subjects = EducationalSubject.objects.filter(is_active=True)
        for subject in subjects:
            for keyword in subject.keyword_list:
                if keyword.lower() in message_lower:
                    return subject.name
        
        return None
    
    def _get_conversation_history(self, session):
        """Récupère l'historique de la conversation"""
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        history = []
        
        # Récupérer les fichiers uploadés dans cette session
        uploaded_files = UploadedFile.objects.filter(session=session).order_by('uploaded_at')
        logger.info(f"🔍 Session {session.id}: {uploaded_files.count()} fichiers trouvés")
        
        file_context = ""
        if uploaded_files.exists():
            file_context = "\n\n=== FICHIERS UPLOADÉS DANS CETTE SESSION ===\n"
            for file in uploaded_files:
                logger.info(f"📎 Fichier trouvé: {file.filename} - Contenu: {len(file.content_text)} caractères")
                file_context += f"\n📎 {file.filename} ({file.file_type.upper()}):\n{file.content_text[:2000]}{'...' if len(file.content_text) > 2000 else ''}\n"
            file_context += "\n=== FIN DES FICHIERS ===\n"
            
            # Ajouter le contexte des fichiers au début de l'historique
            history.append({
                "role": "system",
                "content": f"Tu as accès aux fichiers uploadés dans cette session. Voici leur contenu:{file_context}\n\nUtilise ce contenu pour répondre aux questions de l'utilisateur."
            })
            logger.info(f"📝 Contexte des fichiers ajouté: {len(file_context)} caractères")
        else:
            logger.warning(f"⚠️ Aucun fichier trouvé pour la session {session.id}")
        
        for msg in messages:
            role = "user" if msg.message_type == "user" else "assistant"
            history.append({
                "role": role,
                "content": msg.content
            })
        
        logger.info(f"📚 Historique complet: {len(history)} messages")
        return history


@method_decorator(csrf_exempt, name='dispatch')
class ChatSessionAPIView(LoginRequiredMixin, View):
    """API pour gérer les sessions de chat"""
    
    def get(self, request, session_id):
        """Récupérer les messages d'une session"""
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'subject': msg.subject_detected
            })
        
        return JsonResponse({
            'session': {
                'id': session.id,
                'title': session.title,
                'created_at': session.created_at.isoformat()
            },
            'messages': messages_data
        })
    
    def delete(self, request, session_id):
        """Supprimer une session"""
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.is_active = False
        session.save()
        
        return JsonResponse({'success': True})


@login_required
def chatbot_widget(request):
    """Widget du chatbot pour la navbar"""
    return render(request, 'chatbot/widget.html')


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def upload_file(request):
    """Upload et traitement d'un fichier"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'Aucun fichier fourni'}, status=400)
        
        file = request.FILES['file']
        session_id = request.POST.get('session_id')
        
        # Vérifier que la session existe
        session = None
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        
        # Traiter le fichier
        try:
            content, file_type, file_size = FileProcessor.process_file(file)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        
        # Sauvegarder le fichier
        uploaded_file = UploadedFile.objects.create(
            user=request.user,
            session=session,
            file=file,
            filename=file.name,
            file_type=file_type,
            file_size=file_size,
            content_text=content
        )
        
        logger.info(f"💾 Fichier sauvegardé: {file.name} - Session: {session.id if session else 'None'} - Contenu: {len(content)} caractères")
        
        # Upload silencieux - aucun message créé
        if session:
            # Pas de message automatique - upload silencieux
            return JsonResponse({
                'success': True,
                'file_id': uploaded_file.id,
                'filename': file.name,
                'file_type': file_type,
                'file_size': uploaded_file.get_file_size_display(),
                'file_content': content  # Inclure le contenu pour référence
            })
        
        return JsonResponse({
            'success': True,
            'file_id': uploaded_file.id,
            'filename': file.name,
            'file_type': file_type,
            'file_size': uploaded_file.get_file_size_display()
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de l'upload: {e}")
        return JsonResponse({'error': 'Erreur lors du traitement du fichier'}, status=500)


@login_required
@require_http_methods(["GET"])
def get_uploaded_files(request, session_id):
    """Récupérer les fichiers uploadés pour une session"""
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    files = UploadedFile.objects.filter(session=session).order_by('-uploaded_at')
    
    files_data = []
    for file in files:
        files_data.append({
            'id': file.id,
            'filename': file.filename,
            'file_type': file.file_type,
            'file_size': file.get_file_size_display(),
            'uploaded_at': file.uploaded_at.isoformat(),
            'url': file.file.url if file.file else None
        })
    
    return JsonResponse({'files': files_data})


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def generate_pdf(request):
    """Génère et télécharge un PDF basé sur le contenu fourni"""
    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        title = data.get('title', 'Document généré')
        filename = data.get('filename', 'document.pdf')
        pdf_type = data.get('type', 'normal')  # 'normal' ou 'educational'
        
        if not content:
            return JsonResponse({'error': 'Contenu requis pour générer le PDF'}, status=400)
        
        # Générer le PDF selon le type
        if pdf_type == 'educational':
            topic = data.get('topic', 'Sujet éducatif')
            level = data.get('level', 'intermédiaire')
            pdf_content = PDFGenerator.generate_educational_pdf(topic, content, level)
        else:
            pdf_content = PDFGenerator.generate_pdf(content, title, filename)
        
        # Créer la réponse avec le PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(pdf_content)
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du PDF: {e}")
        return JsonResponse({'error': 'Erreur lors de la génération du PDF'}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class ThemeToggleView(LoginRequiredMixin, View):
    """Vue pour basculer entre les thèmes"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            theme = data.get('theme', 'auto')
            
            # Valider le thème
            valid_themes = ['light', 'dark', 'auto']
            if theme not in valid_themes:
                return JsonResponse({'error': 'Thème invalide'}, status=400)
            
            # Mettre à jour la préférence de l'utilisateur
            user = request.user
            user.theme_preference = theme
            user.save()
            
            return JsonResponse({
                'success': True,
                'theme': theme,
                'message': f'Thème changé vers {theme}'
            })
            
        except Exception as e:
            logger.error(f"Erreur lors du changement de thème: {e}")
            return JsonResponse({'error': 'Erreur lors du changement de thème'}, status=500)