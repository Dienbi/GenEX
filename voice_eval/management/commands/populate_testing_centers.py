"""Management command to populate testing centers database"""
from django.core.management.base import BaseCommand
from voice_eval.models import TestingCenter


class Command(BaseCommand):
    help = 'Populate testing centers database with British Council and Alliance Française locations'

    def handle(self, *args, **options):
        centers_data = [
            {
                'name': 'British Council Tunisia - Tunis',
                'address': '87 Avenue Mohamed V, BP 96 Le Belvédère',
                'city': 'Tunis',
                'country': 'Tunisia',
                'latitude': 36.8060,
                'longitude': 10.1720,
                'phone': '+216 71 145 700',
                'email': 'info@britishcouncil.tn',
                'website': 'https://www.britishcouncil.tn',
                'languages': ['en', 'fr'],
                'certifications': ['IELTS', 'BestMyTest', 'Cambridge English'],
                'is_active': True
            },
            {
                'name': 'British Council - Sousse',
                'address': 'Hotel Riadh Palm Sousse, Boulevard 14 Janvier',
                'city': 'Sousse',
                'country': 'Tunisia',
                'latitude': 35.8250,
                'longitude': 10.6400,
                'phone': '+216 73 225 888',
                'email': 'sousse@britishcouncil.tn',
                'website': 'https://www.britishcouncil.tn',
                'languages': ['en', 'fr'],
                'certifications': ['IELTS Writing', 'IELTS Speaking'],
                'is_active': True
            },
            {
                'name': 'British Council - Sfax',
                'address': 'Avenue Habib Bourguiba',
                'city': 'Sfax',
                'country': 'Tunisia',
                'latitude': 34.7400,
                'longitude': 10.7600,
                'phone': '+216 74 298 444',
                'email': 'sfax@britishcouncil.tn',
                'website': 'https://www.britishcouncil.tn',
                'languages': ['en', 'fr'],
                'certifications': ['IELTS Writing', 'IELTS Speaking'],
                'is_active': True
            },
            {
                'name': 'British Council - Bizerte',
                'address': 'British Council Testing Centre',
                'city': 'Bizerte',
                'country': 'Tunisia',
                'latitude': 37.2747,
                'longitude': 9.8739,
                'phone': '+216 72 431 777',
                'email': 'bizerte@britishcouncil.tn',
                'website': 'https://www.britishcouncil.tn',
                'languages': ['en', 'fr'],
                'certifications': ['IELTS', 'Cambridge English'],
                'is_active': True
            },
            {
                'name': 'British Council - Gabès',
                'address': 'British Council Testing Centre',
                'city': 'Gabès',
                'country': 'Tunisia',
                'latitude': 33.8815,
                'longitude': 10.0982,
                'phone': '+216 75 270 555',
                'email': 'gabes@britishcouncil.tn',
                'website': 'https://www.britishcouncil.tn',
                'languages': ['en', 'fr'],
                'certifications': ['IELTS', 'Cambridge English'],
                'is_active': True
            },
            {
                'name': 'Alliance Française de Tunis',
                'address': '29 Rue Ali Ibn Abi Taleb, El Menzah 6',
                'city': 'Ariana',
                'country': 'Tunisia',
                'latitude': 36.8470,
                'longitude': 10.1590,
                'phone': '+216 71 233 599',
                'email': 'contact@aftunisie.org',
                'website': 'https://www.aftunisie.org',
                'languages': ['fr', 'en'],
                'certifications': ['DELF', 'DALF', 'TCF', 'TEF'],
                'is_active': True
            },
        ]

        created_count = 0
        updated_count = 0

        for center_data in centers_data:
            center, created = TestingCenter.objects.update_or_create(
                name=center_data['name'],
                defaults=center_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {center.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Updated: {center.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Done! Created {created_count} new centers, updated {updated_count} existing centers.'
            )
        )
