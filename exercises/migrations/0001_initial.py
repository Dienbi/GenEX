# Generated manually for exercises module

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExerciseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text="Nom de l'icône (ex: 'math', 'physics')", max_length=50)),
                ('color', models.CharField(default='#007bff', help_text='Code couleur hexadécimal', max_length=7)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': "Catégorie d'exercice",
                'verbose_name_plural': "Catégories d'exercices",
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('template', models.TextField(help_text='Template JSON pour la structure de l\'exercice')),
                ('is_interactive', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': "Type d'exercice",
                'verbose_name_plural': "Types d'exercices",
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DifficultyLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('level', models.IntegerField(help_text='Niveau numérique (1-5)', unique=True)),
                ('description', models.TextField(blank=True)),
                ('color', models.CharField(default='#28a745', max_length=7)),
            ],
            options={
                'verbose_name': 'Niveau de difficulté',
                'verbose_name_plural': 'Niveaux de difficulté',
                'ordering': ['level'],
            },
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('content', models.JSONField(help_text='Contenu structuré de l\'exercice')),
                ('solution', models.JSONField(help_text='Solution de l\'exercice')),
                ('hints', models.JSONField(blank=True, default=list, help_text='Indices pour l\'exercice')),
                ('is_ai_generated', models.BooleanField(default=False)),
                ('ai_prompt', models.TextField(blank=True, help_text='Prompt utilisé pour générer l\'exercice')),
                ('tags', models.JSONField(blank=True, default=list, help_text='Tags pour la recherche')),
                ('estimated_time', models.IntegerField(default=15, help_text='Temps estimé en minutes')),
                ('points', models.IntegerField(default=10, help_text='Points attribués')),
                ('is_active', models.BooleanField(default=True)),
                ('is_public', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='exercises.exercisecategory')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_exercises', to=settings.AUTH_USER_MODEL)),
                ('difficulty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='exercises.difficultylevel')),
                ('exercise_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercises', to='exercises.exercisetype')),
            ],
            options={
                'verbose_name': 'Exercice',
                'verbose_name_plural': 'Exercices',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_answer', models.JSONField(help_text='Réponse de l\'étudiant')),
                ('is_correct', models.BooleanField(default=False)),
                ('score', models.FloatField(default=0.0, help_text='Score obtenu (0-100)')),
                ('time_spent', models.IntegerField(default=0, help_text='Temps passé en secondes')),
                ('hints_used', models.JSONField(blank=True, default=list, help_text='Indices utilisés')),
                ('attempts_count', models.IntegerField(default=1, help_text='Nombre de tentatives')),
                ('started_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attempts', to='exercises.exercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_attempts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Tentative d'exercice",
                'verbose_name_plural': "Tentatives d'exercices",
                'ordering': ['-started_at'],
            },
        ),
        migrations.CreateModel(
            name='ExerciseSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
                ('exercise_count', models.IntegerField(default=5)),
                ('time_limit', models.IntegerField(blank=True, help_text='Limite de temps en minutes', null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('total_score', models.FloatField(default=0.0)),
                ('completed_exercises', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='exercises.exercisecategory')),
                ('difficulty', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='exercises.difficultylevel')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exercise_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Session d'exercices",
                'verbose_name_plural': "Sessions d'exercices",
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SessionExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(default=0)),
                ('is_completed', models.BooleanField(default=False)),
                ('score', models.FloatField(default=0.0)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.exercisesession')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='AIExerciseGeneration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prompt', models.TextField()),
                ('count', models.IntegerField(default=1)),
                ('success', models.BooleanField(default=False)),
                ('error_message', models.TextField(blank=True)),
                ('processing_time', models.FloatField(default=0.0, help_text='Temps de traitement en secondes')),
                ('ai_model', models.CharField(default='gpt-3.5-turbo', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.exercisecategory')),
                ('difficulty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.difficultylevel')),
                ('exercise_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exercises.exercisetype')),
                ('generated_exercises', models.ManyToManyField(blank=True, to='exercises.exercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_generations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Génération IA d'exercices",
                'verbose_name_plural': "Générations IA d'exercices",
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='exercise',
            index=models.Index(fields=['category', 'difficulty'], name='exercises_e_category_2b8c8a_idx'),
        ),
        migrations.AddIndex(
            model_name='exercise',
            index=models.Index(fields=['is_active', 'is_public'], name='exercises_e_is_acti_8a4b2a_idx'),
        ),
        migrations.AddIndex(
            model_name='exercise',
            index=models.Index(fields=['created_at'], name='exercises_e_created_9b8c8a_idx'),
        ),
        migrations.AddIndex(
            model_name='exerciseattempt',
            index=models.Index(fields=['user', 'exercise'], name='exercises_e_user_id_8a4b2a_idx'),
        ),
        migrations.AddIndex(
            model_name='exerciseattempt',
            index=models.Index(fields=['is_correct', 'score'], name='exercises_e_is_corr_8a4b2a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='exerciseattempt',
            unique_together={('user', 'exercise')},
        ),
        migrations.AlterUniqueTogether(
            name='sessionexercise',
            unique_together={('session', 'exercise')},
        ),
    ]
