from django.core.management.base import BaseCommand
from exercises.models import ExerciseType
import json

class Command(BaseCommand):
    help = 'Initialise les types d\'exercices enrichis avec des fonctionnalités avancées'

    def handle(self, *args, **options):
        # Types d'exercices enrichis
        exercise_types = [
            {
                'name': 'QCM avec Images',
                'description': 'Questions à choix multiples avec support d\'images, diagrammes et graphiques',
                'template': json.dumps({
                    'type': 'qcm_with_images',
                    'question': {
                        'text': 'string',
                        'image': 'string (URL)',
                        'image_alt': 'string'
                    },
                    'options': [
                        {
                            'text': 'string',
                            'image': 'string (URL)',
                            'is_correct': 'boolean'
                        }
                    ],
                    'explanation': 'string',
                    'hints': ['string']
                }),
                'is_interactive': True,
                'icon': 'fas fa-images',
                'color': '#28a745',
                'supports_images': True,
                'supports_drawing': False,
                'supports_audio': False,
                'supports_video': True,
                'difficulty_level': 2
            },
            {
                'name': 'Exercice de Correspondance',
                'description': 'Relier des éléments de deux colonnes (mots, définitions, images, etc.)',
                'template': json.dumps({
                    'type': 'matching',
                    'instruction': 'string',
                    'left_column': {
                        'title': 'string',
                        'items': [
                            {
                                'id': 'string',
                                'text': 'string',
                                'image': 'string (URL)',
                                'audio': 'string (URL)'
                            }
                        ]
                    },
                    'right_column': {
                        'title': 'string',
                        'items': [
                            {
                                'id': 'string',
                                'text': 'string',
                                'image': 'string (URL)',
                                'audio': 'string (URL)'
                            }
                        ]
                    },
                    'correct_matches': [
                        {'left_id': 'string', 'right_id': 'string'}
                    ],
                    'explanation': 'string'
                }),
                'is_interactive': True,
                'icon': 'fas fa-link',
                'color': '#ffc107',
                'supports_images': True,
                'supports_drawing': False,
                'supports_audio': True,
                'supports_video': False,
                'difficulty_level': 3
            },
            {
                'name': 'Exercice de Remplissage',
                'description': 'Compléter des phrases, formules ou textes avec des espaces vides',
                'template': json.dumps({
                    'type': 'fill_in_blank',
                    'instruction': 'string',
                    'text': 'string avec {{blank}} pour les espaces à remplir',
                    'blanks': [
                        {
                            'id': 'string',
                            'position': 'number',
                            'correct_answer': 'string',
                            'alternatives': ['string'],
                            'hint': 'string'
                        }
                    ],
                    'explanation': 'string',
                    'supports_math': 'boolean'
                }),
                'is_interactive': True,
                'icon': 'fas fa-edit',
                'color': '#17a2b8',
                'supports_images': True,
                'supports_drawing': False,
                'supports_audio': False,
                'supports_video': True,
                'difficulty_level': 2
            },
            {
                'name': 'Exercice de Tri',
                'description': 'Ordonner des éléments selon un critère (chronologie, importance, etc.)',
                'template': json.dumps({
                    'type': 'sorting',
                    'instruction': 'string',
                    'items': [
                        {
                            'id': 'string',
                            'text': 'string',
                            'image': 'string (URL)',
                            'metadata': 'object'
                        }
                    ],
                    'correct_order': ['string (IDs)'],
                    'sorting_criteria': 'string',
                    'explanation': 'string'
                }),
                'is_interactive': True,
                'icon': 'fas fa-sort-amount-down',
                'color': '#6f42c1',
                'supports_images': True,
                'supports_drawing': False,
                'supports_audio': False,
                'supports_video': False,
                'difficulty_level': 3
            },
            {
                'name': 'Exercice de Dessin',
                'description': 'Créer des schémas, graphiques, diagrammes ou dessins',
                'template': json.dumps({
                    'type': 'drawing',
                    'instruction': 'string',
                    'canvas': {
                        'width': 'number',
                        'height': 'number',
                        'background_image': 'string (URL)',
                        'grid': 'boolean'
                    },
                    'tools': ['pen', 'line', 'circle', 'rectangle', 'text', 'arrow'],
                    'reference_image': 'string (URL)',
                    'evaluation_criteria': [
                        {
                            'element': 'string',
                            'required': 'boolean',
                            'position_tolerance': 'number',
                            'description': 'string'
                        }
                    ],
                    'explanation': 'string'
                }),
                'is_interactive': True,
                'icon': 'fas fa-paint-brush',
                'color': '#e83e8c',
                'supports_images': True,
                'supports_drawing': True,
                'supports_audio': False,
                'supports_video': True,
                'difficulty_level': 4
            },
            {
                'name': 'QCM Audio',
                'description': 'Questions à choix multiples avec support audio et vidéo',
                'template': json.dumps({
                    'type': 'qcm_audio',
                    'question': {
                        'text': 'string',
                        'audio': 'string (URL)',
                        'video': 'string (URL)',
                        'transcript': 'string'
                    },
                    'options': [
                        {
                            'text': 'string',
                            'audio': 'string (URL)',
                            'is_correct': 'boolean'
                        }
                    ],
                    'explanation': 'string',
                    'audio_hints': ['string (URL)']
                }),
                'is_interactive': True,
                'icon': 'fas fa-volume-up',
                'color': '#fd7e14',
                'supports_images': False,
                'supports_drawing': False,
                'supports_audio': True,
                'supports_video': True,
                'difficulty_level': 3
            },
            {
                'name': 'Exercice de Simulation',
                'description': 'Simulations interactives avec manipulation d\'objets virtuels',
                'template': json.dumps({
                    'type': 'simulation',
                    'instruction': 'string',
                    'simulation': {
                        'type': 'string',
                        'parameters': 'object',
                        'initial_state': 'object',
                        'target_state': 'object'
                    },
                    'controls': [
                        {
                            'name': 'string',
                            'type': 'slider|button|input',
                            'min': 'number',
                            'max': 'number',
                            'step': 'number'
                        }
                    ],
                    'feedback': {
                        'real_time': 'boolean',
                        'final_evaluation': 'boolean'
                    },
                    'explanation': 'string'
                }),
                'is_interactive': True,
                'icon': 'fas fa-cogs',
                'color': '#20c997',
                'supports_images': True,
                'supports_drawing': True,
                'supports_audio': True,
                'supports_video': True,
                'difficulty_level': 5
            },
            {
                'name': 'Exercice de Cas Pratique',
                'description': 'Résolution de problèmes complexes avec analyse et synthèse',
                'template': json.dumps({
                    'type': 'case_study',
                    'scenario': {
                        'title': 'string',
                        'description': 'string',
                        'context': 'string',
                        'data': 'object',
                        'documents': ['string (URL)']
                    },
                    'questions': [
                        {
                            'type': 'analysis|synthesis|evaluation',
                            'question': 'string',
                            'expected_elements': ['string'],
                            'evaluation_criteria': ['string']
                        }
                    ],
                    'resources': [
                        {
                            'type': 'document|image|video|audio',
                            'url': 'string',
                            'description': 'string'
                        }
                    ],
                    'explanation': 'string'
                }),
                'is_interactive': True,
                'icon': 'fas fa-briefcase',
                'color': '#6c757d',
                'supports_images': True,
                'supports_drawing': True,
                'supports_audio': True,
                'supports_video': True,
                'difficulty_level': 5
            }
        ]

        created_count = 0
        updated_count = 0

        for exercise_type_data in exercise_types:
            exercise_type, created = ExerciseType.objects.get_or_create(
                name=exercise_type_data['name'],
                defaults=exercise_type_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Cree: {exercise_type.name}')
                )
            else:
                # Mettre à jour les types existants
                for key, value in exercise_type_data.items():
                    setattr(exercise_type, key, value)
                exercise_type.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'[UPDATE] Mis a jour: {exercise_type.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n[SUCCESS] Initialisation terminee!\n'
                f'[OK] {created_count} types crees\n'
                f'[UPDATE] {updated_count} types mis a jour\n'
                f'[TOTAL] {ExerciseType.objects.count()} types d\'exercices'
            )
        )
