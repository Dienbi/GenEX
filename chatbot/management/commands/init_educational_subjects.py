from django.core.management.base import BaseCommand
from chatbot.models import EducationalSubject


class Command(BaseCommand):
    help = 'Initialise les sujets éducatifs par défaut'

    def handle(self, *args, **options):
        subjects_data = [
            {
                'name': 'mathématiques',
                'description': 'Algèbre, géométrie, calcul, statistiques',
                'keywords': 'math, maths, mathématiques, algèbre, géométrie, calcul, statistiques, équation, fonction, dérivée, intégrale, trigonométrie, probabilité'
            },
            {
                'name': 'physique',
                'description': 'Mécanique, thermodynamique, électricité, optique',
                'keywords': 'physique, mécanique, thermodynamique, électricité, optique, force, énergie, mouvement, onde, champ, particule, atome'
            },
            {
                'name': 'chimie',
                'description': 'Chimie organique, inorganique, équilibres',
                'keywords': 'chimie, molécule, atome, réaction, équilibre, acide, base, oxydation, réduction, liaison, composé'
            },
            {
                'name': 'informatique',
                'description': 'Programmation, algorithmes, bases de données',
                'keywords': 'informatique, programmation, code, algorithme, python, java, javascript, html, css, base de données, sql, développement'
            },
            {
                'name': 'biologie',
                'description': 'Biologie cellulaire, génétique, évolution',
                'keywords': 'biologie, cellule, génétique, évolution, ADN, protéine, organisme, écosystème, reproduction, développement'
            },
            {
                'name': 'histoire',
                'description': 'Histoire de France et du monde',
                'keywords': 'histoire, historique, guerre, révolution, empire, royaume, civilisation, chronologie, événement, période'
            },
            {
                'name': 'français',
                'description': 'Grammaire, littérature, expression écrite',
                'keywords': 'français, grammaire, orthographe, littérature, rédaction, expression, conjugaison, vocabulaire, syntaxe'
            },
            {
                'name': 'anglais',
                'description': 'Langue anglaise et littérature',
                'keywords': 'anglais, english, grammar, vocabulary, literature, writing, speaking, listening, comprehension'
            },
            {
                'name': 'géographie',
                'description': 'Géographie physique et humaine',
                'keywords': 'géographie, géographique, pays, continent, climat, population, économie, environnement, cartographie'
            },
            {
                'name': 'philosophie',
                'description': 'Pensée philosophique et éthique',
                'keywords': 'philosophie, philosophique, éthique, morale, logique, raisonnement, argumentation, pensée, réflexion'
            }
        ]

        created_count = 0
        for subject_data in subjects_data:
            subject, created = EducationalSubject.objects.get_or_create(
                name=subject_data['name'],
                defaults={
                    'description': subject_data['description'],
                    'keywords': subject_data['keywords']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Créé le sujet: {subject.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Le sujet {subject.name} existe déjà')
                )

        self.stdout.write(
            self.style.SUCCESS(f'{created_count} nouveaux sujets éducatifs créés')
        )
