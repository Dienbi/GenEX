#!/usr/bin/env python
"""
Service de correction automatique d'exercices avec l'IA
"""
import os
import time
import json
import re
from typing import Dict, List, Optional, Tuple
from django.contrib.auth import get_user_model
from django.conf import settings
import openai

from .models import Exercise, ExerciseSubmission, ExerciseCorrectionSession

User = get_user_model()


class ExerciseCorrectionService:
    """Service de correction automatique d'exercices avec l'IA Groq"""
    
    def __init__(self):
        self.client = None
        self.model = None
        self._initialize_groq()
    
    def _initialize_groq(self):
        """Initialise le client Groq pour la correction"""
        try:
            # Utiliser la même clé Groq que le chatbot
            api_key = "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"
            
            if not api_key:
                print("GROQ_API_KEY not found")
                self.client = None
                return
            
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.1-8b-instant"
            print("Service de correction IA initialisé avec Groq")
        except Exception as e:
            print(f"Erreur d'initialisation Groq pour correction: {e}")
            self.client = None
    
    def correct_exercise(
        self, 
        user: User, 
        exercise: Exercise, 
        user_answer: str
    ) -> Dict:
        """
        Corrige automatiquement un exercice avec l'IA
        
        Args:
            user: Utilisateur qui soumet l'exercice
            exercise: Exercice à corriger
            user_answer: Réponse de l'utilisateur
            
        Returns:
            Dict avec les résultats de la correction
        """
        if not self.client:
            return self._generate_test_correction(user, exercise, user_answer)
        
        start_time = time.time()
        
        try:
            # Créer ou récupérer la session de correction
            session, created = ExerciseCorrectionSession.objects.get_or_create(
                user=user,
                exercise=exercise,
                defaults={'is_active': True}
            )
            
            if not created:
                session.attempts += 1
            
            # Construire le prompt de correction
            correction_prompt = self._build_correction_prompt(exercise, user_answer)
            
            # Appeler l'IA pour la correction
            response = self._call_correction_api(correction_prompt)
            
            if response['success']:
                # Parser la réponse de correction
                correction_data = self._parse_correction_response(response['content'])
                
                # Créer la soumission
                submission = self._create_submission(
                    user, exercise, user_answer, correction_data, session
                )
                
                # Mettre à jour la session
                self._update_correction_session(session, submission)
                
                processing_time = time.time() - start_time
                
                return {
                    'success': True,
                    'submission_id': submission.id,
                    'is_correct': submission.is_correct,
                    'score': submission.score,
                    'feedback': submission.feedback,
                    'suggestions': submission.suggestions,
                    'confidence_score': submission.confidence_score,
                    'processing_time': processing_time
                }
            else:
                return {
                    'success': False,
                    'error': response['error']
                }
                
        except Exception as e:
            error_message = f"Erreur lors de la correction: {str(e)}"
            print(error_message)
            return {
                'success': False,
                'error': error_message
            }
    
    def _build_correction_prompt(self, exercise: Exercise, user_answer: str) -> str:
        """Construit le prompt pour la correction IA"""
        prompt = f"""
Tu es un expert en éducation qui corrige des exercices universitaires.

EXERCICE À CORRIGER:
Titre: {exercise.title}
Description: {exercise.description}
Contenu: {exercise.content}
Solution attendue: {exercise.solution}

RÉPONSE DE L'ÉTUDIANT:
{user_answer}

INSTRUCTIONS DE CORRECTION:
1. Analyse la réponse de l'étudiant
2. Compare avec la solution attendue
3. Évalue la justesse (0-100%)
4. Fournis un feedback constructif
5. Suggère des améliorations si nécessaire

Réponds UNIQUEMENT en JSON avec cette structure:
{{
    "is_correct": true/false,
    "score": 85.5,
    "feedback": "Explication détaillée de la correction",
    "suggestions": ["Suggestion 1", "Suggestion 2"],
    "confidence_score": 0.9,
    "correction_details": {{
        "correct_elements": ["Éléments corrects"],
        "incorrect_elements": ["Éléments incorrects"],
        "missing_elements": ["Éléments manquants"]
    }}
}}
"""
        return prompt
    
    def _call_correction_api(self, prompt: str) -> Dict:
        """Appelle l'API Groq pour la correction"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en correction d'exercices universitaires. Tu analyses les réponses des étudiants et fournis des corrections détaillées et constructives. Tu réponds UNIQUEMENT en JSON valide."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3,  # Plus conservateur pour la correction
                top_p=0.9
            )
            
            content = response.choices[0].message.content.strip()
            return {
                'success': True,
                'content': content
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur API correction: {str(e)}'
            }
    
    def _parse_correction_response(self, content: str) -> Dict:
        """Parse la réponse de correction de l'IA"""
        try:
            # Nettoyer le contenu
            import re
            json_match = re.search(r'```json\s*(\{.*\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                json_start = content.find('{')
                if json_start != -1:
                    json_str = content[json_start:]
                else:
                    json_str = content.strip()
            
            data = json.loads(json_str)
            
            # Validation des données requises
            required_fields = ['is_correct', 'score', 'feedback']
            if not all(field in data for field in required_fields):
                raise ValueError("Données de correction incomplètes")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"Erreur parsing correction JSON: {e}")
            print(f"Contenu reçu: {content[:200]}...")
            
            # Fallback: correction basique
            return {
                'is_correct': False,
                'score': 0.0,
                'feedback': 'Erreur lors de l\'analyse de la correction. Veuillez réessayer.',
                'suggestions': ['Vérifiez votre réponse et réessayez'],
                'confidence_score': 0.0,
                'correction_details': {
                    'correct_elements': [],
                    'incorrect_elements': ['Erreur de parsing'],
                    'missing_elements': []
                }
            }
        except Exception as e:
            print(f"Erreur parsing correction: {e}")
            return {
                'is_correct': False,
                'score': 0.0,
                'feedback': 'Erreur lors de la correction automatique.',
                'suggestions': ['Contactez un enseignant pour assistance'],
                'confidence_score': 0.0,
                'correction_details': {
                    'correct_elements': [],
                    'incorrect_elements': ['Erreur système'],
                    'missing_elements': []
                }
            }
    
    def _create_submission(
        self, 
        user: User, 
        exercise: Exercise, 
        user_answer: str, 
        correction_data: Dict,
        session: ExerciseCorrectionSession
    ) -> ExerciseSubmission:
        """Crée une soumission d'exercice avec les résultats de correction"""
        
        # Supprimer l'ancienne soumission si elle existe
        ExerciseSubmission.objects.filter(user=user, exercise=exercise).delete()
        
        submission = ExerciseSubmission.objects.create(
            user=user,
            exercise=exercise,
            user_answer=user_answer,
            is_correct=correction_data.get('is_correct', False),
            score=float(correction_data.get('score', 0.0)),
            feedback=correction_data.get('feedback', ''),
            suggestions=correction_data.get('suggestions', []),
            ai_correction=correction_data,
            confidence_score=float(correction_data.get('confidence_score', 0.0)),
            ai_model=self.model
        )
        
        return submission
    
    def _update_correction_session(
        self, 
        session: ExerciseCorrectionSession, 
        submission: ExerciseSubmission
    ):
        """Met à jour la session de correction"""
        session.attempts += 1
        
        if submission.score > session.best_score:
            session.best_score = submission.score
        
        # Calculer le temps total
        if session.started_at:
            time_diff = time.time() - session.started_at.timestamp()
            session.total_time = time_diff / 60  # en minutes
        
        # Mettre à jour le feedback cumulatif
        if session.cumulative_feedback:
            session.cumulative_feedback += f"\n\nTentative {session.attempts}:\n{submission.feedback}"
        else:
            session.cumulative_feedback = f"Tentative {session.attempts}:\n{submission.feedback}"
        
        # Ajouter les domaines d'amélioration
        if submission.suggestions:
            session.improvement_areas.extend(submission.suggestions)
            session.improvement_areas = list(set(session.improvement_areas))  # Supprimer les doublons
        
        session.save()
    
    def _generate_test_correction(
        self, 
        user: User, 
        exercise: Exercise, 
        user_answer: str
    ) -> Dict:
        """Génère une correction de test (mode sans API)"""
        try:
            # Créer une session de test
            session, created = ExerciseCorrectionSession.objects.get_or_create(
                user=user,
                exercise=exercise,
                defaults={'is_active': True}
            )
            
            # Simulation de correction basique
            is_correct = len(user_answer) > 10  # Logique simple
            score = min(100, len(user_answer) * 2)  # Score basé sur la longueur
            
            correction_data = {
                'is_correct': is_correct,
                'score': score,
                'feedback': f'Correction de test: Votre réponse fait {len(user_answer)} caractères.',
                'suggestions': ['Essayez de développer votre réponse', 'Ajoutez plus de détails'],
                'confidence_score': 0.8,
                'correction_details': {
                    'correct_elements': ['Réponse fournie'],
                    'incorrect_elements': [],
                    'missing_elements': []
                }
            }
            
            submission = self._create_submission(user, exercise, user_answer, correction_data, session)
            self._update_correction_session(session, submission)
            
            return {
                'success': True,
                'submission_id': submission.id,
                'is_correct': submission.is_correct,
                'score': submission.score,
                'feedback': submission.feedback,
                'suggestions': submission.suggestions,
                'confidence_score': submission.confidence_score,
                'processing_time': 0.1
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur correction test: {str(e)}'
            }
    
    def get_user_progress(self, user: User) -> Dict:
        """Récupère les progrès de l'utilisateur"""
        submissions = ExerciseSubmission.objects.filter(user=user)
        
        if not submissions.exists():
            return {
                'total_submissions': 0,
                'average_score': 0,
                'correct_submissions': 0,
                'improvement_areas': []
            }
        
        total_submissions = submissions.count()
        correct_submissions = submissions.filter(is_correct=True).count()
        from django.db import models
        average_score = submissions.aggregate(avg_score=models.Avg('score'))['avg_score'] or 0
        
        # Récupérer les domaines d'amélioration
        improvement_areas = []
        for submission in submissions:
            improvement_areas.extend(submission.suggestions)
        
        improvement_areas = list(set(improvement_areas))
        
        return {
            'total_submissions': total_submissions,
            'average_score': round(average_score, 2),
            'correct_submissions': correct_submissions,
            'success_rate': round((correct_submissions / total_submissions) * 100, 2),
            'improvement_areas': improvement_areas[:5]  # Top 5
        }


# Instance globale du service
exercise_correction_service = ExerciseCorrectionService()
