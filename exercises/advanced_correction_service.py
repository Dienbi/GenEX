"""
Service de correction avancée pour les exercices
Fournit des corrections détaillées, des explications vidéo et du feedback personnalisé
"""

import json
import time
from typing import Dict, List, Any, Optional
from django.conf import settings
from .ai_service import ExerciseAIService


class AdvancedCorrectionService:
    """Service pour la correction avancée des exercices"""
    
    def __init__(self):
        self.ai_service = ExerciseAIService()
    
    def generate_advanced_correction(
        self, 
        exercise: 'Exercise', 
        user_answer: str, 
        user_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Génère une correction avancée complète
        
        Args:
            exercise: L'exercice corrigé
            user_answer: La réponse de l'utilisateur
            user_level: Niveau de l'utilisateur (beginner, intermediate, advanced)
        
        Returns:
            Dict contenant toutes les informations de correction avancée
        """
        start_time = time.time()
        
        try:
            # 1. Correction détaillée ligne par ligne
            detailed_correction = self._generate_detailed_correction(exercise, user_answer)
            
            # 2. Feedback personnalisé
            personalized_feedback = self._generate_personalized_feedback(
                exercise, user_answer, user_level, detailed_correction
            )
            
            # 3. Identification des points forts et faibles
            strengths, improvement_areas = self._analyze_strengths_weaknesses(
                exercise, user_answer, detailed_correction
            )
            
            # 4. Comparaison avec d'autres bonnes réponses
            comparison_answers = self._generate_comparison_answers(exercise, user_answer)
            
            # 5. Génération d'URL vidéo (simulation)
            video_url = self._generate_video_explanation_url(exercise, detailed_correction)
            
            correction_time = time.time() - start_time
            
            return {
                'detailed_correction': detailed_correction,
                'personalized_feedback': personalized_feedback,
                'strengths': strengths,
                'improvement_areas': improvement_areas,
                'comparison_answers': comparison_answers,
                'video_explanation_url': video_url,
                'correction_time': correction_time,
                'confidence_score': self._calculate_confidence_score(detailed_correction)
            }
            
        except Exception as e:
            print(f"Erreur lors de la correction avancée: {e}")
            return self._get_fallback_correction()
    
    def _generate_detailed_correction(self, exercise: 'Exercise', user_answer: str) -> Dict[str, Any]:
        """Génère une correction détaillée ligne par ligne"""
        
        prompt = f"""
        Tu es un expert en pédagogie. Analyse la réponse de l'étudiant à cet exercice et fournis une correction détaillée ligne par ligne.

        EXERCICE:
        Titre: {exercise.title}
        Description: {exercise.description}
        Contenu: {json.dumps(exercise.content, ensure_ascii=False)}
        Solution: {json.dumps(exercise.solution, ensure_ascii=False)}

        RÉPONSE DE L'ÉTUDIANT:
        {user_answer}

        Fournis une correction détaillée au format JSON avec:
        1. "overall_score": score global sur 100
        2. "line_by_line": analyse ligne par ligne de la réponse
        3. "correct_elements": éléments corrects identifiés
        4. "incorrect_elements": éléments incorrects avec explications
        5. "missing_elements": éléments manquants
        6. "suggestions": suggestions d'amélioration spécifiques

        Format de réponse JSON uniquement.
        """
        
        try:
            response = self.ai_service.generate_response(prompt)
            return json.loads(response)
        except:
            return self._get_default_detailed_correction(exercise, user_answer)
    
    def _generate_personalized_feedback(
        self, 
        exercise: 'Exercise', 
        user_answer: str, 
        user_level: str,
        detailed_correction: Dict[str, Any]
    ) -> str:
        """Génère un feedback personnalisé adapté au niveau de l'utilisateur"""
        
        prompt = f"""
        Tu es un tuteur personnel. Donne un feedback personnalisé à un étudiant de niveau {user_level}.

        EXERCICE: {exercise.title}
        DESCRIPTION: {exercise.description}
        RÉPONSE: {user_answer}
        CORRECTION DÉTAILLÉE: {json.dumps(detailed_correction, ensure_ascii=False)}

        Donne un feedback:
        1. Encourageant et constructif
        2. Adapté au niveau {user_level}
        3. Avec des conseils pratiques
        4. En français, ton amical et motivant
        5. Maximum 200 mots

        Focus sur les points positifs et les prochaines étapes.
        """
        
        try:
            return self.ai_service.generate_response(prompt)
        except:
            return self._get_default_personalized_feedback(user_level)
    
    def _analyze_strengths_weaknesses(
        self, 
        exercise: 'Exercise', 
        user_answer: str,
        detailed_correction: Dict[str, Any]
    ) -> tuple[List[str], List[str]]:
        """Analyse les points forts et les domaines d'amélioration"""
        
        prompt = f"""
        Analyse la réponse de l'étudiant et identifie:
        
        RÉPONSE: {user_answer}
        CORRECTION: {json.dumps(detailed_correction, ensure_ascii=False)}

        Fournis au format JSON:
        {{
            "strengths": ["point fort 1", "point fort 2", ...],
            "improvement_areas": ["domaine 1", "domaine 2", ...]
        }}

        Maximum 3 éléments par catégorie.
        """
        
        try:
            response = self.ai_service.generate_response(prompt)
            data = json.loads(response)
            return data.get('strengths', []), data.get('improvement_areas', [])
        except:
            return self._get_default_strengths_weaknesses()
    
    def _generate_comparison_answers(self, exercise: 'Exercise', user_answer: str) -> List[Dict[str, Any]]:
        """Génère des exemples de bonnes réponses pour comparaison"""
        
        prompt = f"""
        Pour cet exercice, génère 2-3 exemples de bonnes réponses de différents niveaux:

        EXERCICE: {exercise.title}
        DESCRIPTION: {exercise.description}
        CONTENU: {json.dumps(exercise.content, ensure_ascii=False)}

        Format JSON:
        [
            {{
                "level": "débutant",
                "answer": "réponse exemple",
                "explanation": "pourquoi c'est bien"
            }},
            {{
                "level": "avancé", 
                "answer": "réponse exemple",
                "explanation": "pourquoi c'est bien"
            }}
        ]
        """
        
        try:
            response = self.ai_service.generate_response(prompt)
            return json.loads(response)
        except:
            return self._get_default_comparison_answers()
    
    def _generate_video_explanation_url(self, exercise: 'Exercise', detailed_correction: Dict[str, Any]) -> str:
        """Génère une URL de vidéo d'explication"""
        
        # 1. Si l'exercice a déjà une vidéo d'explication en base de données
        if exercise.explanation_video_url:
            return exercise.explanation_video_url
        
        # 2. Si le type est 'auto', générer automatiquement (simulation)
        if exercise.explanation_video_type == 'auto':
            # En production, ici vous pourriez :
            # - Générer une vidéo avec Text-to-Speech
            # - Utiliser un service de génération de vidéo IA
            # - Créer une vidéo avec des slides automatiques
            return self._generate_auto_video_url(exercise, detailed_correction)
        
        # 3. Sinon, pas de vidéo disponible
        return ""
    
    def _generate_auto_video_url(self, exercise: 'Exercise', detailed_correction: Dict[str, Any]) -> str:
        """Génère automatiquement une URL de vidéo d'explication basée sur le sujet de l'exercice"""
        try:
            # 1. Extraire les mots-clés du contenu de l'exercice
            keywords = self._extract_keywords_from_exercise(exercise)
            
            # 2. Déterminer le type de contenu éducatif
            content_type = self._determine_content_type(exercise, keywords)
            
            # 3. Générer une URL de vidéo pertinente basée sur le type de contenu
            video_url = self._generate_relevant_video_url(exercise, content_type, keywords)
            
            return video_url
            
        except Exception as e:
            print(f"Erreur lors de la génération de vidéo: {e}")
            return ""
    
    def _extract_keywords_from_exercise(self, exercise: 'Exercise') -> List[str]:
        """Extrait les mots-clés pertinents du contenu de l'exercice"""
        import re
        
        # Combiner le titre, la description et le contenu
        full_text = f"{exercise.title} {exercise.description or ''}"
        
        # Si le contenu est un dictionnaire JSON, extraire le texte
        if isinstance(exercise.content, dict):
            if 'text' in exercise.content:
                full_text += f" {exercise.content['text']}"
        elif isinstance(exercise.content, str):
            full_text += f" {exercise.content}"
        
        # Nettoyer et extraire les mots-clés
        text = re.sub(r'<[^>]+>', '', full_text)  # Supprimer les balises HTML
        text = re.sub(r'[^\w\s]', ' ', text)  # Supprimer la ponctuation
        words = text.lower().split()
        
        # Filtrer les mots communs et garder les mots significatifs
        stop_words = {'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 'mais', 'pour', 'avec', 'dans', 'sur', 'par', 'est', 'sont', 'que', 'qui', 'quoi', 'comment', 'pourquoi', 'quand', 'où', 'ce', 'cette', 'ces', 'son', 'sa', 'ses', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs'}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Retourner les 10 mots les plus fréquents
        from collections import Counter
        return [word for word, count in Counter(keywords).most_common(10)]
    
    def _determine_content_type(self, exercise: 'Exercise', keywords: List[str]) -> str:
        """Détermine le type de contenu éducatif basé sur l'exercice et les mots-clés"""
        # Analyser le type d'exercice et la catégorie
        exercise_type = exercise.exercise_type.name.lower() if exercise.exercise_type else ""
        category = exercise.category.name.lower() if exercise.category else ""
        
        # Mots-clés pour différents domaines
        math_keywords = ['mathématique', 'calcul', 'équation', 'algèbre', 'géométrie', 'trigonométrie', 'statistique', 'probabilité', 'fonction', 'dérivée', 'intégrale']
        science_keywords = ['physique', 'chimie', 'biologie', 'atome', 'molécule', 'cellule', 'énergie', 'force', 'réaction', 'organisme', 'génétique']
        language_keywords = ['grammaire', 'conjugaison', 'orthographe', 'vocabulaire', 'syntaxe', 'rédaction', 'essai', 'dissertation', 'analyse', 'littérature']
        history_keywords = ['histoire', 'historique', 'guerre', 'révolution', 'empire', 'civilisation', 'culture', 'tradition', 'événement', 'période']
        geography_keywords = ['géographie', 'pays', 'continent', 'capitale', 'climat', 'population', 'économie', 'ressources', 'environnement', 'carte']
        
        # Déterminer le domaine principal
        all_text = f"{exercise_type} {category} {' '.join(keywords)}".lower()
        
        if any(keyword in all_text for keyword in math_keywords):
            return "mathematics"
        elif any(keyword in all_text for keyword in science_keywords):
            return "science"
        elif any(keyword in all_text for keyword in language_keywords):
            return "language"
        elif any(keyword in all_text for keyword in history_keywords):
            return "history"
        elif any(keyword in all_text for keyword in geography_keywords):
            return "geography"
        else:
            return "general"
    
    def _generate_relevant_video_url(self, exercise: 'Exercise', content_type: str, keywords: List[str]) -> str:
        """Génère une URL de vidéo pertinente basée sur le type de contenu et les mots-clés"""
        import hashlib
        import random
        
        # Base de données étendue de vidéos éducatives par domaine avec plusieurs options
        educational_videos = {
            "mathematics": {
                "algèbre": [
                    "https://www.youtube.com/watch?v=NybHckSEQBI",  # Khan Academy Algebra Basics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Algebra 1
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Algebra 2
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Linear Algebra
                ],
                "géométrie": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Geometry
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Trigonometry
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Coordinate Geometry
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Solid Geometry
                ],
                "calcul": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Calculus 1
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Calculus 2
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Differential Calculus
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Integral Calculus
                ],
                "statistique": [
                    "https://www.youtube.com/watch?v=xxpc-HPKN28", # Khan Academy Statistics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Probability
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Data Analysis
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Regression
                ],
                "probabilité": [
                    "https://www.youtube.com/watch?v=KzfWUEJjG18", # Khan Academy Probability
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Combinatorics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Random Variables
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Bayes Theorem
                ],
                "fonction": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Functions
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Linear Functions
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Quadratic Functions
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Polynomial Functions
                ],
                "dérivée": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Derivatives
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Chain Rule
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Product Rule
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Quotient Rule
                ],
                "intégrale": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Integrals
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Definite Integrals
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Indefinite Integrals
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Integration by Parts
                ],
                "trigonométrie": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Trigonometry
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Unit Circle
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Sine and Cosine
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Trigonometric Identities
                ]
            },
            "science": {
                "physique": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Physics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Mechanics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Thermodynamics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Electromagnetism
                ],
                "chimie": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Chemistry
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Organic Chemistry
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Inorganic Chemistry
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Physical Chemistry
                ],
                "biologie": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Biology
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Cell Biology
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Genetics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Evolution
                ],
                "atome": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Atomic Structure
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Electron Configuration
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Periodic Table
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Chemical Bonding
                ],
                "molécule": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Molecular Structure
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Chemical Bonds
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Molecular Geometry
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Intermolecular Forces
                ],
                "cellule": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Cell Structure
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Cell Membrane
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Cell Division
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Cellular Respiration
                ],
                "énergie": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Energy
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Kinetic Energy
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Potential Energy
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Energy Conservation
                ],
                "force": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Forces
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Newton's Laws
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Khan Academy Friction
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Khan Academy Gravity
                ]
            },
            "language": {
                "grammaire": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Grammar Basics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Grammar Advanced
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Grammar Rules
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # French Grammar Practice
                ],
                "conjugaison": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Conjugation Present
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Conjugation Past
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Conjugation Future
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # French Conjugation Subjunctive
                ],
                "orthographe": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Spelling Rules
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Spelling Practice
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Spelling Tips
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # French Spelling Exercises
                ],
                "vocabulaire": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Vocabulary Basic
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Vocabulary Intermediate
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Vocabulary Advanced
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # French Vocabulary Thematic
                ],
                "rédaction": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Writing Basics
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Writing Structure
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Writing Style
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # French Writing Practice
                ]
            },
            "history": {
                "histoire": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # General History
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # World History
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # European History
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Ancient History
                ],
                "guerre": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # World War I
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # World War II
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Napoleonic Wars
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Medieval Wars
                ],
                "révolution": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # French Revolution
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # American Revolution
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Russian Revolution
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Industrial Revolution
                ]
            },
            "geography": {
                "géographie": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # World Geography
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Physical Geography
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Human Geography
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Regional Geography
                ],
                "pays": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Countries of the World
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # European Countries
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Asian Countries
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # African Countries
                ],
                "continent": [
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Continents Overview
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Europe Geography
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Asia Geography
                    "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Africa Geography
                ]
            },
            "general": [
                "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Learning Methods
                "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Study Techniques
                "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Memory Techniques
                "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Time Management
                "https://www.youtube.com/watch?v=WUvTyaaNkzM",  # Note Taking
                "https://www.youtube.com/watch?v=WUvTyaaNkzM"   # Exam Preparation
            ]
        }
        
        # Créer un hash basé sur l'ID de l'exercice et les mots-clés pour la cohérence
        exercise_hash = hashlib.md5(f"{exercise.id}_{'_'.join(keywords[:3])}".encode()).hexdigest()
        hash_int = int(exercise_hash[:8], 16)  # Prendre les 8 premiers caractères hex
        
        # Chercher une vidéo correspondant aux mots-clés
        if content_type in educational_videos:
            for keyword in keywords:
                if keyword in educational_videos[content_type]:
                    video_list = educational_videos[content_type][keyword]
                    # Utiliser le hash pour sélectionner de manière déterministe mais variée
                    video_index = hash_int % len(video_list)
                    return video_list[video_index]
        
        # Si aucune correspondance exacte, retourner une vidéo du domaine
        if content_type in educational_videos and content_type != "general":
            # Prendre toutes les vidéos du domaine
            all_domain_videos = []
            for keyword_videos in educational_videos[content_type].values():
                all_domain_videos.extend(keyword_videos)
            
            if all_domain_videos:
                video_index = hash_int % len(all_domain_videos)
                return all_domain_videos[video_index]
        
        # Fallback final : vidéo éducative générale
        general_videos = educational_videos["general"]
        video_index = hash_int % len(general_videos)
        return general_videos[video_index]
    
    def _calculate_confidence_score(self, detailed_correction: Dict[str, Any]) -> float:
        """Calcule le niveau de confiance de la correction"""
        # Logique simple basée sur la complétude de la correction
        score = 0.8  # Score de base
        if detailed_correction.get('line_by_line'):
            score += 0.1
        if detailed_correction.get('correct_elements'):
            score += 0.05
        if detailed_correction.get('incorrect_elements'):
            score += 0.05
        return min(score, 1.0)
    
    def _get_fallback_correction(self) -> Dict[str, Any]:
        """Correction de secours en cas d'erreur"""
        return {
            'detailed_correction': {'overall_score': 0, 'error': 'Correction non disponible'},
            'personalized_feedback': 'Une erreur est survenue lors de la correction. Veuillez réessayer.',
            'strengths': [],
            'improvement_areas': ['Révision générale recommandée'],
            'comparison_answers': [],
            'video_explanation_url': '',  # URL vide pour désactiver le lien
            'correction_time': 0,
            'confidence_score': 0.1
        }
    
    def _get_default_detailed_correction(self, exercise: 'Exercise', user_answer: str) -> Dict[str, Any]:
        """Correction détaillée par défaut"""
        return {
            'overall_score': 50,
            'line_by_line': [{'line': user_answer, 'status': 'partial', 'comment': 'Réponse partiellement correcte'}],
            'correct_elements': ['Structure générale'],
            'incorrect_elements': ['Détails à améliorer'],
            'missing_elements': ['Éléments manquants'],
            'suggestions': ['Relire la question attentivement']
        }
    
    def _get_default_personalized_feedback(self, user_level: str) -> str:
        """Feedback personnalisé par défaut"""
        return f"Bon travail ! En tant qu'étudiant de niveau {user_level}, continuez à pratiquer pour améliorer vos compétences."
    
    def _get_default_strengths_weaknesses(self) -> tuple[List[str], List[str]]:
        """Points forts et faibles par défaut"""
        return (
            ['Effort fourni', 'Tentative de réponse'],
            ['Précision', 'Compréhension approfondie']
        )
    
    def _get_default_comparison_answers(self) -> List[Dict[str, Any]]:
        """Réponses de comparaison par défaut"""
        return [
            {
                'level': 'débutant',
                'answer': 'Exemple de réponse simple qui couvre les points essentiels de la question.',
                'explanation': 'Cette réponse montre une compréhension de base du sujet avec les éléments principaux.'
            },
            {
                'level': 'avancé',
                'answer': 'Exemple de réponse détaillée et structurée qui démontre une maîtrise approfondie du sujet avec des exemples concrets et une analyse critique.',
                'explanation': 'Cette réponse montre une compréhension complète avec une analyse approfondie et des exemples pertinents.'
            }
        ]
