from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from exercises.models import ExerciseCollection

User = get_user_model()

class Command(BaseCommand):
    help = 'Créer des collections de test pour les utilisateurs'

    def handle(self, *args, **options):
        # Récupérer le premier utilisateur (ou créer un utilisateur de test)
        user = User.objects.first()
        
        if not user:
            self.stdout.write(
                self.style.WARNING('Aucun utilisateur trouvé. Créez d\'abord un utilisateur.')
            )
            return

        # Collections de test
        test_collections = [
            {
                'name': 'Mes Exercices Favoris',
                'description': 'Collection de mes exercices préférés',
                'color': '#dc3545',
                'icon': 'fas fa-heart',
                'is_public': False
            },
            {
                'name': 'Mathématiques Avancées',
                'description': 'Exercices de mathématiques de niveau avancé',
                'color': '#007bff',
                'icon': 'fas fa-calculator',
                'is_public': True
            },
            {
                'name': 'À Réviser',
                'description': 'Exercices que je dois réviser',
                'color': '#ffc107',
                'icon': 'fas fa-book',
                'is_public': False
            },
            {
                'name': 'Physique Quantique',
                'description': 'Exercices sur la physique quantique',
                'color': '#6f42c1',
                'icon': 'fas fa-atom',
                'is_public': True
            }
        ]

        created_count = 0
        for collection_data in test_collections:
            collection, created = ExerciseCollection.objects.get_or_create(
                user=user,
                name=collection_data['name'],
                defaults=collection_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Collection créée: {collection.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Collection existe déjà: {collection.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'{created_count} nouvelles collections créées pour {user.username}')
        )

