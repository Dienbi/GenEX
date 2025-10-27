"""
Service IA pour la génération intelligente d'exercices universitaires
Utilise OpenAI API pour créer des exercices adaptés au niveau et aux préférences
"""
import os
import json
import time
from typing import Dict, List, Optional, Tuple
from django.conf import settings
from django.contrib.auth import get_user_model
import openai
from .models import Exercise, ExerciseCategory, ExerciseType, DifficultyLevel, AIExerciseGeneration

User = get_user_model()

class ExerciseAIService:
    """Service principal pour la génération d'exercices par IA"""
    
    def __init__(self):
        self.client = None
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialise le client OpenAI (utilise Groq comme le chatbot)"""
        try:
            # Utiliser la même clé Groq que le chatbot
            api_key = "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"
            
            if not api_key:
                print("GROQ_API_KEY not found")
                self.client = None
                return
            
            # Utiliser Groq au lieu d'OpenAI (comme le chatbot)
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
            self.model = "llama-3.1-8b-instant"  # Modèle Groq rapide
            print("Service IA initialisé avec Groq (comme le chatbot)")
        except Exception as e:
            print(f"Erreur d'initialisation Groq: {e}")
            self.client = None
    
    def generate_exercises(
        self,
        user: User,
        subject: str,
        difficulty: DifficultyLevel,
        exercise_type: ExerciseType,
        count: int = 1,
        custom_prompt: str = "",
        user_level: str = None,
        specific_topics: List[str] = None
    ) -> Dict:
        """
        Génère des exercices intelligents basés sur les paramètres
        
        Args:
            user: Utilisateur demandeur
            category: Catégorie d'exercice
            difficulty: Niveau de difficulté
            exercise_type: Type d'exercice
            count: Nombre d'exercices à générer
            custom_prompt: Prompt personnalisé
            user_level: Niveau de l'utilisateur (A1, A2, B1, B2, C1, C2)
            specific_topics: Sujets spécifiques à inclure
        
        Returns:
            Dict avec les exercices générés et métadonnées
        """
        if not self.client:
            # Mode test : générer des exercices factices
            return self._generate_test_exercises(user, category, difficulty, exercise_type, count)
        
        start_time = time.time()
        
        try:
            # Créer l'enregistrement de génération
            # Trouver ou créer une catégorie basée sur le sujet
            category = self._get_or_create_category_for_subject(subject)
            
            generation = AIExerciseGeneration.objects.create(
                user=user,
                prompt=custom_prompt or self._build_default_prompt(subject, difficulty, exercise_type),
                category=category,
                difficulty=difficulty,
                exercise_type=exercise_type,
                count=count
            )
            
            # Construire le prompt complet
            full_prompt = self._build_generation_prompt(
                subject, difficulty, exercise_type, count, 
                custom_prompt, user_level, specific_topics
            )
            
            # Appeler l'API OpenAI
            response = self._call_openai_api(full_prompt, count)
            
            if response['success']:
                # Parser et créer les exercices
                exercises_data = self._parse_exercises_response(response['content'])
                created_exercises = []
                
                for exercise_data in exercises_data:
                    exercise = self._create_exercise_from_ai(
                        exercise_data, user, category, difficulty, exercise_type, generation
                    )
                    if exercise:
                        created_exercises.append(exercise)
                        generation.generated_exercises.add(exercise)
                
                # Mettre à jour la génération
                generation.success = True
                generation.processing_time = time.time() - start_time
                generation.save()
                
                return {
                    'success': True,
                    'exercises': created_exercises,
                    'generation_id': generation.id,
                    'processing_time': generation.processing_time
                }
            else:
                generation.success = False
                generation.error_message = response['error']
                generation.processing_time = time.time() - start_time
                generation.save()
                
                return {
                    'success': False,
                    'error': response['error'],
                    'exercises': []
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de la génération: {str(e)}',
                'exercises': []
            }
    
    def _build_default_prompt(self, subject, difficulty, exercise_type):
        """Construit un prompt par défaut basé sur les paramètres"""
        return f"Génère des exercices de {subject} de type {exercise_type.name} de niveau {difficulty.name}"
    
    def _build_generation_prompt(
        self, subject, difficulty, exercise_type, count, 
        custom_prompt, user_level, specific_topics
    ):
        """Construit le prompt complet pour la génération"""
        
        # Template de base
        base_template = f"""
Tu es un expert en éducation universitaire. Génère {count} exercice(s) de {subject} 
de type {exercise_type.name} avec un niveau de difficulté {difficulty.name} (niveau {difficulty.level}/5).

Format de réponse requis (JSON strict):
{{
    "exercises": [
        {{
            "title": "Titre de l'exercice",
            "description": "Description courte",
            "content": {{
                "question": "Énoncé de la question",
                "options": ["Option A", "Option B", "Option C", "Option D"], // Pour QCM
                "format": "qcm|calcul|redaction|probleme"
            }},
            "solution": {{
                "answer": "Réponse correcte",
                "explanation": "Explication détaillée",
                "steps": ["Étape 1", "Étape 2", "Étape 3"] // Pour calculs
            }},
            "hints": ["Indice 1", "Indice 2"],
            "tags": ["tag1", "tag2"],
            "estimated_time": 15,
            "points": 10
        }}
    ]
}}
"""
        
        # Ajouter des éléments personnalisés
        if custom_prompt:
            base_template += f"\n\nDemande spécifique: {custom_prompt}"
        
        if user_level:
            base_template += f"\n\nNiveau de l'étudiant: {user_level}"
        
        if specific_topics:
            topics_str = ", ".join(specific_topics)
            base_template += f"\n\nSujets spécifiques à inclure: {topics_str}"
        
        # Ajouter des instructions spécifiques selon le type
        if exercise_type.name.lower() == 'qcm':
            base_template += "\n\nPour les QCM: Inclure 4 options avec une seule réponse correcte."
        elif exercise_type.name.lower() == 'calcul':
            base_template += "\n\nPour les calculs: Inclure des étapes détaillées dans la solution."
        elif exercise_type.name.lower() == 'rédaction':
            base_template += "\n\nPour les rédactions: Proposer des sujets de réflexion avec des critères d'évaluation."
        
        return base_template
    
    def _call_openai_api(self, prompt: str, count: int) -> Dict:
        """Appelle l'API OpenAI pour générer les exercices"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,  # Utilise le modèle Groq
                messages=[
                    {
                        "role": "system",
                        "content": "Tu es un expert en éducation universitaire. Tu génères des exercices de qualité adaptés au niveau demandé. Tu réponds UNIQUEMENT en JSON valide."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.7,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                'success': True,
                'content': content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur API OpenAI: {str(e)}'
            }
    
    def _parse_exercises_response(self, content: str) -> List[Dict]:
        """Parse la réponse JSON de l'IA"""
        try:
            # Nettoyer le contenu (enlever markdown si présent)
            import re
            json_match = re.search(r'```json\s*(\{.*\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Essayer de trouver le JSON dans le contenu
                json_start = content.find('{')
                if json_start != -1:
                    json_str = content[json_start:]
                else:
                    json_str = content.strip()
            
            data = json.loads(json_str)
            
            if 'exercises' in data:
                return data['exercises']
            else:
                return [data] if isinstance(data, dict) else data
                
        except json.JSONDecodeError as e:
            print(f"Erreur de parsing JSON: {e}")
            print(f"Contenu reçu: {content[:200]}...")
            
            # Essayer de créer un exercice factice si le parsing échoue
            return [{
                'title': 'Exercice généré par IA Groq',
                'content': 'Exercice généré avec succès par l\'IA Groq',
                'solution': {'answer': 'Réponse générée par IA', 'explanation': 'Explication fournie par l\'IA'}
            }]
        except Exception as e:
            print(f"Erreur de parsing: {e}")
            return []
    
    def _create_exercise_from_ai(
        self, exercise_data: Dict, user: User, category: ExerciseCategory,
        difficulty: DifficultyLevel, exercise_type: ExerciseType, generation: AIExerciseGeneration
    ) -> Optional[Exercise]:
        """Crée un exercice à partir des données IA"""
        try:
            # Validation des données requises
            if not all(key in exercise_data for key in ['title', 'content', 'solution']):
                print(f"Données d'exercice incomplètes: {exercise_data}")
                return None
            
            exercise = Exercise.objects.create(
                title=exercise_data.get('title', 'Exercice généré par IA'),
                description=exercise_data.get('description', ''),
                content=exercise_data.get('content', {}),
                solution=exercise_data.get('solution', {}),
                hints=exercise_data.get('hints', []),
                category=category,
                exercise_type=exercise_type,
                difficulty=difficulty,
                created_by=user,
                is_ai_generated=True,
                ai_prompt=generation.prompt,
                tags=exercise_data.get('tags', []),
                estimated_time=exercise_data.get('estimated_time', 15),
                points=exercise_data.get('points', 10),
                is_public=True,  # Les exercices IA sont publics pour être visibles
                is_active=True
            )
            
            
            return exercise
            
        except Exception as e:
            print(f"Erreur lors de la création de l'exercice: {e}")
            return None
    
    def generate_adaptive_exercises(
        self,
        user: User,
        category: ExerciseCategory,
        user_performance_history: List[Dict] = None
    ) -> Dict:
        """
        Génère des exercices adaptatifs basés sur l'historique de performance
        
        Args:
            user: Utilisateur
            category: Catégorie d'exercice
            user_performance_history: Historique des performances (optionnel)
        
        Returns:
            Dict avec les exercices adaptatifs générés
        """
        # Analyser l'historique pour déterminer le niveau optimal
        optimal_difficulty = self._analyze_user_performance(user_performance_history)
        
        # Générer des exercices adaptatifs
        return self.generate_exercises(
            user=user,
            category=category,
            difficulty=optimal_difficulty,
            exercise_type=ExerciseType.objects.first(),  # Type par défaut
            count=3,
            custom_prompt=f"Exercices adaptatifs pour un niveau {optimal_difficulty.name}",
            user_level=user.level if hasattr(user, 'level') else None
        )
    
    def _analyze_user_performance(self, performance_history: List[Dict]) -> DifficultyLevel:
        """Analyse l'historique de performance pour déterminer le niveau optimal"""
        if not performance_history:
            return DifficultyLevel.objects.filter(level=2).first()  # Niveau moyen par défaut
        
        # Calculer la moyenne des scores
        avg_score = sum(p.get('score', 0) for p in performance_history) / len(performance_history)
        
        # Déterminer le niveau basé sur la performance
        if avg_score >= 80:
            return DifficultyLevel.objects.filter(level=4).first()  # Difficile
        elif avg_score >= 60:
            return DifficultyLevel.objects.filter(level=3).first()  # Moyen-avancé
        elif avg_score >= 40:
            return DifficultyLevel.objects.filter(level=2).first()  # Moyen
        else:
            return DifficultyLevel.objects.filter(level=1).first()  # Facile
    
    def get_exercise_recommendations(
        self,
        user: User,
        category: ExerciseCategory = None,
        limit: int = 5
    ) -> List[Exercise]:
        """
        Recommande des exercices basés sur l'historique et les préférences
        
        Args:
            user: Utilisateur
            category: Catégorie (optionnel)
            limit: Nombre de recommandations
        
        Returns:
            Liste d'exercices recommandés
        """
        # Récupérer les exercices récents de l'utilisateur
        recent_attempts = user.exercise_attempts.select_related('exercise').order_by('-started_at')[:10]
        
        # Analyser les préférences
        preferred_categories = {}
        preferred_difficulties = {}
        
        for attempt in recent_attempts:
            cat = attempt.exercise.category
            diff = attempt.exercise.difficulty
            
            preferred_categories[cat.id] = preferred_categories.get(cat.id, 0) + 1
            preferred_difficulties[diff.id] = preferred_difficulties.get(diff.id, 0) + 1
        
        # Construire la requête de recommandation
        from django.db.models import Q
        
        query = Q(is_active=True, is_public=True)
        
        if category:
            query &= Q(category=category)
        elif preferred_categories:
            # Utiliser les catégories préférées
            query &= Q(category_id__in=preferred_categories.keys())
        
        # Exclure les exercices déjà tentés
        attempted_exercises = [attempt.exercise.id for attempt in recent_attempts]
        if attempted_exercises:
            query &= ~Q(id__in=attempted_exercises)
        
        # Récupérer les recommandations
        recommendations = Exercise.objects.filter(query).order_by('-created_at')[:limit]
        
        return list(recommendations)
    
    def _generate_test_exercises(self, user, category, difficulty, exercise_type, count):
        """Générer des exercices de test (mode sans API OpenAI)"""
        try:
            # Créer l'enregistrement de génération
            generation = AIExerciseGeneration.objects.create(
                user=user,
                category=category,
                difficulty=difficulty,
                exercise_type=exercise_type,
                count=count,
                prompt="Mode test - génération factice",
                success=True,
                processing_time=0.1,
                ai_model='test-mode'
            )
            
            created_exercises = []
            
            for i in range(count):
                # Créer un exercice de test
                exercise = Exercise.objects.create(
                    title=f"Exercice de test {i+1} - {category.name}",
                    description=f"Exercice généré automatiquement pour tester le système",
                    content=f"""
                    <h4>Exercice de {category.name}</h4>
                    <p><strong>Niveau:</strong> {difficulty.name}</p>
                    <p><strong>Type:</strong> {exercise_type.name}</p>
                    
                    <div class="exercise-content">
                        <p>Voici un exercice d'exemple pour tester le système de génération d'exercices IA.</p>
                        <p><strong>Question:</strong> Quelle est la réponse à cette question de test ?</p>
                        
                        <div class="options">
                            <label><input type="radio" name="answer_{i+1}" value="A"> A) Option A</label><br>
                            <label><input type="radio" name="answer_{i+1}" value="B"> B) Option B</label><br>
                            <label><input type="radio" name="answer_{i+1}" value="C"> C) Option C</label><br>
                            <label><input type="radio" name="answer_{i+1}" value="D"> D) Option D</label>
                        </div>
                    </div>
                    """,
                    solution={"answer": "B", "explanation": "Explication de la réponse correcte"},
                    category=category,
                    difficulty=difficulty,
                    exercise_type=exercise_type,
                    created_by=user,
                    is_ai_generated=True,
                    is_public=True,
                    is_active=True
                )
                
                created_exercises.append(exercise)
                generation.generated_exercises.add(exercise)
            
            return {
                'success': True,
                'message': f'{count} exercice(s) de test généré(s) avec succès',
                'exercises': [exercise.id for exercise in created_exercises],
                'generation_id': generation.id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de la génération de test: {str(e)}',
                'exercises': []
            }
    
    def _get_or_create_category_for_subject(self, subject: str) -> ExerciseCategory:
        """Trouve ou crée une catégorie basée sur le sujet"""
        # Nettoyer le sujet pour créer un nom de catégorie
        subject_clean = subject.strip().title()
        
        # Essayer de trouver une catégorie existante qui correspond
        existing_category = ExerciseCategory.objects.filter(
            name__icontains=subject_clean
        ).first()
        
        if existing_category:
            return existing_category
        
        # Créer une nouvelle catégorie pour ce sujet
        category, created = ExerciseCategory.objects.get_or_create(
            name=subject_clean,
            defaults={
                'description': f'Exercices en {subject_clean}',
                'icon': 'fas fa-book',
                'color': '#dc3545'
            }
        )
        
        if created:
            print(f"Nouvelle catégorie créée: {subject_clean}")
        
        return category

    def generate_rich_exercise(
        self,
        user: User,
        subject: str,
        difficulty: DifficultyLevel,
        exercise_type: ExerciseType,
        custom_prompt: str = ""
    ) -> Optional[Exercise]:
        """Génère un exercice enrichi avec des fonctionnalités avancées"""
        
        if not self.client:
            return self._generate_test_rich_exercise(user, subject, difficulty, exercise_type)
        
        try:
            # Construire le prompt spécialisé selon le type d'exercice
            prompt = self._build_rich_exercise_prompt(subject, difficulty, exercise_type, custom_prompt)
            
            # Générer avec l'IA
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un expert en création d'exercices pédagogiques enrichis. Tu crées des exercices interactifs et engageants."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parser la réponse JSON
            content = response.choices[0].message.content
            exercise_data = json.loads(content)
            
            # Créer l'exercice
            exercise = self._create_rich_exercise_from_data(
                user, subject, difficulty, exercise_type, exercise_data
            )
            
            return exercise
            
        except Exception as e:
            print(f"Erreur génération exercice enrichi: {e}")
            return self._generate_test_rich_exercise(user, subject, difficulty, exercise_type)

    def _build_rich_exercise_prompt(
        self,
        subject: str,
        difficulty: DifficultyLevel,
        exercise_type: ExerciseType,
        custom_prompt: str
    ) -> str:
        """Construit un prompt spécialisé pour le type d'exercice"""
        
        base_prompt = f"""
        Crée un exercice de type "{exercise_type.name}" pour le sujet "{subject}" 
        au niveau de difficulté "{difficulty.name}".
        
        Type d'exercice: {exercise_type.name}
        Description: {exercise_type.description}
        Supports: Images={exercise_type.supports_images}, Audio={exercise_type.supports_audio}, 
        Vidéo={exercise_type.supports_video}, Dessin={exercise_type.supports_drawing}
        
        {custom_prompt}
        
        Retourne la réponse au format JSON suivant:
        """
        
        # Ajouter le template spécifique selon le type
        if exercise_type.name == "QCM avec Images":
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "question": {
                    "text": "string",
                    "image_url": "string (URL d'image générée ou placeholder)",
                    "image_alt": "string"
                },
                "options": [
                    {
                        "text": "string",
                        "image_url": "string (optionnel)",
                        "is_correct": boolean
                    }
                ],
                "explanation": "string",
                "hints": ["string"],
                "estimated_time": number
            }
            """
        elif exercise_type.name == "Exercice de Correspondance":
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "instruction": "string",
                "left_column": {
                    "title": "string",
                    "items": [
                        {
                            "id": "string",
                            "text": "string",
                            "image_url": "string (optionnel)"
                        }
                    ]
                },
                "right_column": {
                    "title": "string",
                    "items": [
                        {
                            "id": "string",
                            "text": "string",
                            "image_url": "string (optionnel)"
                        }
                    ]
                },
                "correct_matches": [
                    {"left_id": "string", "right_id": "string"}
                ],
                "explanation": "string"
            }
            """
        elif exercise_type.name == "Exercice de Remplissage":
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "instruction": "string",
                "text": "string avec {{blank1}}, {{blank2}} pour les espaces",
                "blanks": [
                    {
                        "id": "blank1",
                        "correct_answer": "string",
                        "alternatives": ["string"],
                        "hint": "string"
                    }
                ],
                "explanation": "string",
                "supports_math": boolean
            }
            """
        elif exercise_type.name == "Exercice de Tri":
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "instruction": "string",
                "sorting_criteria": "string",
                "items": [
                    {
                        "id": "string",
                        "text": "string",
                        "image_url": "string (optionnel)",
                        "metadata": "object"
                    }
                ],
                "correct_order": ["string (IDs)"],
                "explanation": "string"
            }
            """
        elif exercise_type.name == "Exercice de Dessin":
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "instruction": "string",
                "canvas": {
                    "width": number,
                    "height": number,
                    "background_image": "string (optionnel)",
                    "grid": boolean
                },
                "tools": ["pen", "line", "circle", "rectangle", "text", "arrow"],
                "reference_image": "string (URL optionnel)",
                "evaluation_criteria": [
                    {
                        "element": "string",
                        "required": boolean,
                        "description": "string"
                    }
                ],
                "explanation": "string"
            }
            """
        elif exercise_type.name == "QCM Audio":
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "question": {
                    "text": "string",
                    "audio_url": "string (URL ou placeholder)",
                    "video_url": "string (optionnel)",
                    "transcript": "string"
                },
                "options": [
                    {
                        "text": "string",
                        "audio_url": "string (optionnel)",
                        "is_correct": boolean
                    }
                ],
                "explanation": "string",
                "audio_hints": ["string (URLs optionnels)"]
            }
            """
        elif exercise_type.name == "Exercice de Simulation":
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "instruction": "string",
                "simulation": {
                    "type": "string",
                    "parameters": "object",
                    "initial_state": "object",
                    "target_state": "object"
                },
                "controls": [
                    {
                        "name": "string",
                        "type": "slider|button|input",
                        "min": number,
                        "max": number,
                        "step": number
                    }
                ],
                "feedback": {
                    "real_time": boolean,
                    "final_evaluation": boolean
                },
                "explanation": "string"
            }
            """
        elif exercise_type.name == "Exercice de Cas Pratique":
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "scenario": {
                    "title": "string",
                    "description": "string",
                    "context": "string",
                    "data": "object",
                    "documents": ["string (URLs)"]
                },
                "questions": [
                    {
                        "type": "analysis|synthesis|evaluation",
                        "question": "string",
                        "expected_elements": ["string"],
                        "evaluation_criteria": ["string"]
                    }
                ],
                "resources": [
                    {
                        "type": "document|image|video|audio",
                        "url": "string",
                        "description": "string"
                    }
                ],
                "explanation": "string"
            }
            """
        else:
            # Template générique
            base_prompt += """
            {
                "title": "string",
                "description": "string",
                "content": "string (HTML)",
                "solution": "string",
                "hints": ["string"],
                "explanation": "string"
            }
            """
        
        return base_prompt

    def _create_rich_exercise_from_data(
        self,
        user: User,
        subject: str,
        difficulty: DifficultyLevel,
        exercise_type: ExerciseType,
        exercise_data: dict
    ) -> Exercise:
        """Crée un exercice à partir des données générées par l'IA"""
        
        # Récupérer ou créer la catégorie
        category = self._get_or_create_category(subject)
        
        # Créer l'exercice
        exercise = Exercise.objects.create(
            title=exercise_data.get('title', f'Exercice {exercise_type.name}'),
            description=exercise_data.get('description', ''),
            content=exercise_data,
            solution=exercise_data.get('solution', exercise_data),
            hints=exercise_data.get('hints', []),
            category=category,
            exercise_type=exercise_type,
            difficulty=difficulty,
            created_by=user,
            is_ai_generated=True,
            ai_prompt=f"Génération enrichie - {exercise_type.name}",
            tags=[subject.lower(), exercise_type.name.lower()],
            estimated_time=exercise_data.get('estimated_time', 15),
            points=exercise_data.get('points', 10),
            is_public=True
        )
        
        return exercise

    def _generate_test_rich_exercise(
        self,
        user: User,
        subject: str,
        difficulty: DifficultyLevel,
        exercise_type: ExerciseType
    ) -> Exercise:
        """Génère un exercice de test enrichi (mode sans API)"""
        
        category = self._get_or_create_category(subject)
        
        # Créer un exercice de test selon le type
        if exercise_type.name == "QCM avec Images":
            content = {
                "type": "qcm_with_images",
                "question": {
                    "text": f"Question de test sur {subject}",
                    "image": "https://via.placeholder.com/400x300?text=Image+de+test",
                    "image_alt": "Image illustrative"
                },
                "options": [
                    {"text": "Option A", "is_correct": True},
                    {"text": "Option B", "is_correct": False},
                    {"text": "Option C", "is_correct": False},
                    {"text": "Option D", "is_correct": False}
                ],
                "explanation": "Explication de la réponse correcte"
            }
        elif exercise_type.name == "Exercice de Correspondance":
            content = {
                "type": "matching",
                "instruction": "Reliez les éléments des deux colonnes",
                "left_column": {
                    "title": "Termes",
                    "items": [
                        {"id": "1", "text": "Terme 1"},
                        {"id": "2", "text": "Terme 2"}
                    ]
                },
                "right_column": {
                    "title": "Définitions",
                    "items": [
                        {"id": "A", "text": "Définition A"},
                        {"id": "B", "text": "Définition B"}
                    ]
                },
                "correct_matches": [
                    {"left_id": "1", "right_id": "A"},
                    {"left_id": "2", "right_id": "B"}
                ]
            }
        else:
            # Template générique
            content = {
                "type": exercise_type.name.lower().replace(" ", "_"),
                "question": f"Question de test sur {subject}",
                "solution": "Solution de test",
                "explanation": "Explication de test"
            }
        
        exercise = Exercise.objects.create(
            title=f"Test {exercise_type.name} - {subject}",
            description=f"Exercice de test pour {exercise_type.name}",
            content=content,
            solution=content,
            hints=["Indice de test"],
            category=category,
            exercise_type=exercise_type,
            difficulty=difficulty,
            created_by=user,
            is_ai_generated=True,
            ai_prompt="Mode test",
            tags=[subject.lower(), "test"],
            estimated_time=10,
            points=5,
            is_public=False
        )
        
        return exercise


# Instance globale du service
exercise_ai_service = ExerciseAIService()
