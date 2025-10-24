import os
from openai import OpenAI
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GroqChatService:
    """Service pour l'intégration avec Groq API"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key="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",
            base_url="https://api.groq.com/openai/v1"
        )
        self.model = "llama-3.1-8b-instant"  # Modèle Groq actuel et rapide
    
    def get_response(self, user_message, conversation_history=None, subject=None):
        """Obtenir une réponse du chatbot Groq"""
        try:
            # Construire le système prompt
            system_prompt = self._build_system_prompt(subject)
            
            # Préparer les messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Ajouter l'historique de conversation
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Limiter à 10 derniers messages
            
            # Ajouter le message actuel
            messages.append({"role": "user", "content": user_message})
            
            # Appeler l'API Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                timeout=30
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Erreur Groq API: {str(e)}")
            return self._get_fallback_response(subject)
    
    def _build_system_prompt(self, subject=None):
        """Construire le prompt système basé sur le sujet détecté"""
        base_prompt = """Tu es un assistant éducatif intelligent spécialisé dans l'aide aux étudiants. 
        Tu es patient, encourageant et adaptes tes explications au niveau de l'étudiant.
        
        Règles importantes:
        - Réponds toujours en français
        - Sois précis et pédagogique
        - Utilise des exemples concrets quand c'est possible
        - Encourage l'étudiant à poser des questions
        - Si tu ne connais pas quelque chose, dis-le honnêtement
        - Reste dans le domaine éducatif et académique"""
        
        if subject:
            subject_prompts = {
                "mathématiques": """
                Tu es spécialisé en mathématiques. Tu peux aider avec:
                - Algèbre, géométrie, calcul
                - Résolution de problèmes
                - Explications de concepts mathématiques
                - Exercices et méthodes de résolution
                """,
                "physique": """
                Tu es spécialisé en physique. Tu peux aider avec:
                - Mécanique, thermodynamique, électricité
                - Résolution de problèmes physiques
                - Explications de lois et principes
                - Applications pratiques
                """,
                "informatique": """
                Tu es spécialisé en informatique. Tu peux aider avec:
                - Programmation (Python, Java, C++, etc.)
                - Algorithmes et structures de données
                - Bases de données
                - Développement web et logiciel
                """,
                "chimie": """
                Tu es spécialisé en chimie. Tu peux aider avec:
                - Chimie organique et inorganique
                - Équilibres chimiques
                - Réactions et mécanismes
                - Calculs stœchiométriques
                """,
                "biologie": """
                Tu es spécialisé en biologie. Tu peux aider avec:
                - Biologie cellulaire et moléculaire
                - Génétique et évolution
                - Anatomie et physiologie
                - Écologie et environnement
                """,
                "histoire": """
                Tu es spécialisé en histoire. Tu peux aider avec:
                - Histoire de France et du monde
                - Analyse de documents historiques
                - Contextualisation d'événements
                - Méthodologie historique
                """,
                "français": """
                Tu es spécialisé en français et littérature. Tu peux aider avec:
                - Grammaire et orthographe
                - Analyse littéraire
                - Rédaction et expression écrite
                - Histoire de la littérature
                """
            }
            
            if subject.lower() in subject_prompts:
                base_prompt += f"\n\n{subject_prompts[subject.lower()]}"
        
        return base_prompt
    
    def _get_fallback_response(self, subject=None):
        """Réponse de secours en cas d'erreur API"""
        if subject:
            return f"Je suis désolé, j'ai rencontré un problème technique. Je suis là pour t'aider avec {subject}. Peux-tu reformuler ta question ?"
        else:
            return "Je suis désolé, j'ai rencontré un problème technique. Peux-tu reformuler ta question ? Je suis là pour t'aider dans tes études !"
    
    def test_connection(self):
        """Tester la connexion à l'API Groq"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test de connexion"}],
                max_tokens=10
            )
            return True, "Connexion réussie"
        except Exception as e:
            return False, str(e)
