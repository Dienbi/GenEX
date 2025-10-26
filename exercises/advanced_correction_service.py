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
        """Génère automatiquement une URL de vidéo d'explication"""
        # Simulation d'une génération automatique de vidéo
        # En production, cela pourrait :
        # 1. Utiliser Text-to-Speech pour créer l'audio
        # 2. Générer des slides avec le contenu de l'exercice
        # 3. Combiner audio + slides en vidéo
        # 4. Uploader sur un service de stockage
        # 5. Retourner l'URL de la vidéo générée
        
        # Pour l'instant, retournons une URL YouTube éducative comme exemple
        # Vous pouvez remplacer cela par votre logique de génération
        return f"https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Exemple
    
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
