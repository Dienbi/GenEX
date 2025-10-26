"""
Commande Django pour initialiser les données de base du module exercices
"""
from django.core.management.base import BaseCommand
from exercises.models import ExerciseCategory, ExerciseType, DifficultyLevel

class Command(BaseCommand):
    help = 'Initialise les données de base pour le module exercices'

    def handle(self, *args, **options):
        self.stdout.write('Initialisation des données de base...')
        
        # Créer les catégories d'exercices
        categories_data = [
            {
                'name': 'Mathématiques',
                'description': 'Exercices de mathématiques (algèbre, géométrie, calcul)',
                'icon': 'calculator',
                'color': '#e74c3c'
            },
            {
                'name': 'Physique',
                'description': 'Exercices de physique (mécanique, électricité, optique)',
                'icon': 'atom',
                'color': '#3498db'
            },
            {
                'name': 'Chimie',
                'description': 'Exercices de chimie (réactions, équilibres, solutions)',
                'icon': 'flask',
                'color': '#9b59b6'
            },
            {
                'name': 'Informatique',
                'description': 'Exercices de programmation et algorithmique',
                'icon': 'code',
                'color': '#2ecc71'
            },
            {
                'name': 'Langues',
                'description': 'Exercices de langues (grammaire, vocabulaire, compréhension)',
                'icon': 'language',
                'color': '#f39c12'
            },
            {
                'name': 'Histoire',
                'description': 'Exercices d\'histoire et de géographie',
                'icon': 'globe',
                'color': '#34495e'
            }
        ]
        
        for cat_data in categories_data:
            category, created = ExerciseCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'✓ Catégorie créée: {category.name}')
            else:
                self.stdout.write(f'- Catégorie existante: {category.name}')
        
        # Créer les types d'exercices
        types_data = [
            {
                'name': 'QCM',
                'description': 'Questions à choix multiples',
                'template': '{"question": "", "options": ["A", "B", "C", "D"], "correct": 0}',
                'is_interactive': True
            },
            {
                'name': 'Calcul',
                'description': 'Exercices de calcul numérique',
                'template': '{"question": "", "expected_format": "number", "tolerance": 0.01}',
                'is_interactive': True
            },
            {
                'name': 'Rédaction',
                'description': 'Exercices de rédaction et d\'expression',
                'template': '{"question": "", "min_words": 100, "criteria": []}',
                'is_interactive': False
            },
            {
                'name': 'Problème',
                'description': 'Résolution de problèmes complexes',
                'template': '{"question": "", "steps": [], "solution": ""}',
                'is_interactive': False
            },
            {
                'name': 'Vrai/Faux',
                'description': 'Questions de type vrai/faux',
                'template': '{"question": "", "correct": true}',
                'is_interactive': True
            }
        ]
        
        for type_data in types_data:
            exercise_type, created = ExerciseType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                self.stdout.write(f'✓ Type créé: {exercise_type.name}')
            else:
                self.stdout.write(f'- Type existant: {exercise_type.name}')
        
        # Créer les niveaux de difficulté
        difficulties_data = [
            {
                'name': 'Très Facile',
                'level': 1,
                'description': 'Niveau débutant, exercices de base',
                'color': '#27ae60'
            },
            {
                'name': 'Facile',
                'level': 2,
                'description': 'Niveau élémentaire, exercices simples',
                'color': '#2ecc71'
            },
            {
                'name': 'Moyen',
                'level': 3,
                'description': 'Niveau intermédiaire, exercices modérés',
                'color': '#f39c12'
            },
            {
                'name': 'Difficile',
                'level': 4,
                'description': 'Niveau avancé, exercices complexes',
                'color': '#e67e22'
            },
            {
                'name': 'Très Difficile',
                'level': 5,
                'description': 'Niveau expert, exercices très complexes',
                'color': '#e74c3c'
            }
        ]
        
        for diff_data in difficulties_data:
            difficulty, created = DifficultyLevel.objects.get_or_create(
                level=diff_data['level'],
                defaults=diff_data
            )
            if created:
                self.stdout.write(f'✓ Niveau créé: {difficulty.name}')
            else:
                self.stdout.write(f'- Niveau existant: {difficulty.name}')
        
        self.stdout.write(
            self.style.SUCCESS('✓ Initialisation terminée avec succès!')
        )
