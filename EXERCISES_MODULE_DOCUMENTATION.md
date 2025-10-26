# Module Exercices Intelligents - GenEX

## Vue d'ensemble

Le module Exercices Intelligents de GenEX est un système avancé de génération et de gestion d'exercices universitaires utilisant l'intelligence artificielle. Il permet de créer, organiser et résoudre des exercices adaptatifs basés sur le niveau et les préférences des utilisateurs.

## Fonctionnalités principales

### 🤖 Génération IA d'exercices
- **Génération intelligente** : Utilise l'API OpenAI pour créer des exercices personnalisés
- **Adaptation au niveau** : Génère des exercices adaptés au niveau de l'utilisateur
- **Prompts personnalisés** : Possibilité de spécifier des sujets ou des types d'exercices particuliers
- **Multiples formats** : QCM, Calcul, Rédaction, Problèmes, Vrai/Faux

### 📚 Gestion des exercices
- **Catégorisation** : Mathématiques, Physique, Chimie, Informatique, Langues, Histoire
- **Niveaux de difficulté** : 5 niveaux (Très Facile à Très Difficile)
- **Types d'exercices** : QCM, Calcul, Rédaction, Problème, Vrai/Faux
- **Métadonnées** : Tags, temps estimé, points, indices

### 🎯 Sessions d'exercices
- **Sessions personnalisées** : Création de sessions avec paramètres spécifiques
- **Suivi de progression** : Suivi en temps réel de la progression
- **Limite de temps** : Sessions avec contraintes temporelles
- **Statistiques** : Scores, temps passé, tentatives

### 📊 Analytics et recommandations
- **Recommandations intelligentes** : Suggestions basées sur l'historique
- **Analytics de performance** : Statistiques détaillées des performances
- **Adaptation continue** : Ajustement automatique du niveau de difficulté

## Architecture technique

### Modèles de données

#### ExerciseCategory
- Catégories d'exercices (Mathématiques, Physique, etc.)
- Icônes et couleurs pour l'interface
- Description et métadonnées

#### ExerciseType
- Types d'exercices (QCM, Calcul, etc.)
- Templates JSON pour la structure
- Support interactif

#### DifficultyLevel
- 5 niveaux de difficulté (1-5)
- Couleurs et descriptions
- Système de progression

#### Exercise
- Modèle principal des exercices
- Contenu structuré en JSON
- Solutions et indices
- Métadonnées IA

#### ExerciseAttempt
- Tentatives de résolution
- Scores et temps passé
- Historique des tentatives

#### ExerciseSession
- Sessions d'exercices
- Configuration et paramètres
- Suivi de progression

### Service IA (ai_service.py)

```python
class ExerciseAIService:
    def generate_exercises(user, category, difficulty, exercise_type, count, custom_prompt)
    def generate_adaptive_exercises(user, category, user_performance_history)
    def get_exercise_recommendations(user, category, limit)
```

### API REST

#### Endpoints principaux
- `GET /exercises/api/exercises/` - Liste des exercices
- `POST /exercises/api/exercises/generate_ai/` - Génération IA
- `POST /exercises/api/exercises/{id}/attempt/` - Soumission de tentative
- `GET /exercises/api/exercises/recommendations/` - Recommandations
- `GET /exercises/api/sessions/` - Sessions d'exercices

#### Filtres et recherche
- Filtrage par catégorie, difficulté, type
- Recherche textuelle
- Tri par date, difficulté, points
- Pagination

## Configuration

### 1. Installation des dépendances

```bash
pip install django-filter openai reportlab qrcode[pil] sentence-transformers spacy
```

### 2. Configuration des settings

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'django_filters',
    'exercises',
    # ...
]

# OpenAI API
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
```

### 3. Migrations

```bash
python manage.py migrate exercises
```

### 4. Initialisation des données

```bash
python manage.py shell
>>> from exercises.init_data import init_exercise_data
>>> init_exercise_data()
```

## Utilisation

### Interface utilisateur

#### Page principale (`/exercises/`)
- Vue d'ensemble des exercices
- Filtres et recherche
- Statistiques personnelles
- Génération IA

#### Résolution d'exercices (`/exercises/{id}/solve/`)
- Interface de résolution
- Indices et aide
- Suivi du temps
- Soumission des réponses

#### Sessions (`/exercises/sessions/`)
- Création de sessions
- Suivi de progression
- Statistiques de session

### API REST

#### Génération d'exercices IA

```python
import requests

data = {
    "category": 1,  # Mathématiques
    "difficulty": 3,  # Moyen
    "exercise_type": 1,  # QCM
    "count": 3,
    "custom_prompt": "Exercices sur les équations du second degré",
    "specific_topics": ["équations", "polynômes"]
}

response = requests.post('/exercises/api/exercises/generate_ai/', json=data)
```

#### Soumission de tentative

```python
data = {
    "user_answer": "x = 2 ou x = -3",
    "hints_used": ["indice1"],
    "time_spent": 120
}

response = requests.post('/exercises/api/exercises/1/attempt/', json=data)
```

### Service IA

#### Génération basique

```python
from exercises.ai_service import exercise_ai_service

result = exercise_ai_service.generate_exercises(
    user=user,
    category=category,
    difficulty=difficulty,
    exercise_type=exercise_type,
    count=3,
    custom_prompt="Exercices de calcul intégral"
)
```

#### Recommandations adaptatives

```python
recommendations = exercise_ai_service.get_exercise_recommendations(
    user=user,
    category=category,
    limit=5
)
```

## Personnalisation

### Templates d'exercices

Chaque type d'exercice utilise un template JSON :

```json
{
  "question": "Énoncé de la question",
  "options": ["A", "B", "C", "D"],
  "correct": 0,
  "explanation": "Explication de la réponse"
}
```

### Prompts IA personnalisés

```python
custom_prompt = """
Génère des exercices de mathématiques de niveau universitaire
sur le thème des dérivées avec des applications pratiques.
Inclure des graphiques et des exemples concrets.
"""
```

### Niveaux de difficulté

```python
# Créer un nouveau niveau
DifficultyLevel.objects.create(
    name="Expert",
    level=6,
    description="Niveau expert avancé",
    color="#8e44ad"
)
```

## Intégration avec d'autres modules

### Module Voice Evaluation
- Exercices de prononciation
- Évaluation audio des réponses
- Intégration avec l'IA vocale

### Module Chat Tutor
- Aide contextuelle pendant les exercices
- Explications personnalisées
- Support en temps réel

### Module Courses
- Exercices liés aux cours
- Progression intégrée
- Évaluation continue

## Déploiement

### Variables d'environnement

```bash
export OPENAI_API_KEY="your-openai-api-key"
export DJANGO_SETTINGS_MODULE="GenEX.settings"
```

### Configuration de production

```python
# settings.py
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-3.5-turbo'  # ou 'gpt-4'
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.7
```

### Monitoring

- Logs des générations IA
- Métriques de performance
- Suivi des erreurs
- Analytics d'utilisation

## Sécurité

### Authentification
- Tous les endpoints nécessitent une authentification
- Vérification des permissions utilisateur
- Protection CSRF

### Validation des données
- Validation des réponses utilisateur
- Sanitisation des inputs
- Vérification des types d'exercices

### Limitation des ressources
- Limite de générations par utilisateur
- Timeout des requêtes IA
- Cache des résultats

## Maintenance

### Nettoyage des données
```python
# Supprimer les exercices inactifs anciens
Exercise.objects.filter(
    is_active=False,
    created_at__lt=timezone.now() - timedelta(days=30)
).delete()
```

### Sauvegarde
- Export des exercices
- Sauvegarde des sessions
- Historique des générations

### Mise à jour
- Migration des templates
- Mise à jour des modèles IA
- Synchronisation des données

## Support et développement

### Tests
```bash
python manage.py test exercises
```

### Documentation API
- Swagger/OpenAPI disponible
- Exemples d'utilisation
- Codes d'erreur

### Contribution
- Guidelines de développement
- Standards de code
- Processus de review

---

Ce module représente une solution complète pour la génération et la gestion d'exercices intelligents, intégrée parfaitement dans l'écosystème GenEX.
