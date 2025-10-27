from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import json

User = get_user_model()

class ExerciseCategory(models.Model):
    """Catégories d'exercices (Mathématiques, Physique, Chimie, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Nom de l'icône (ex: 'math', 'physics')")
    color = models.CharField(max_length=7, default='#007bff', help_text="Code couleur hexadécimal")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Catégorie d'exercice"
        verbose_name_plural = "Catégories d'exercices"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ExerciseType(models.Model):
    """Types d'exercices (QCM, Calcul, Rédaction, etc.)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    template = models.TextField(help_text="Template JSON pour la structure de l'exercice")
    is_interactive = models.BooleanField(default=False)
    icon = models.CharField(max_length=50, default='fas fa-question-circle', help_text="Icône FontAwesome")
    color = models.CharField(max_length=7, default='#007bff', help_text="Couleur hexadécimale")
    supports_images = models.BooleanField(default=False, help_text="Supporte les images")
    supports_drawing = models.BooleanField(default=False, help_text="Supporte le dessin")
    supports_audio = models.BooleanField(default=False, help_text="Supporte l'audio")
    supports_video = models.BooleanField(default=False, help_text="Supporte la vidéo")
    difficulty_level = models.IntegerField(default=1, help_text="Niveau de complexité (1-5)")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Type d'exercice"
        verbose_name_plural = "Types d'exercices"
        ordering = ['difficulty_level', 'name']
    
    def __str__(self):
        return self.name

class DifficultyLevel(models.Model):
    """Niveaux de difficulté"""
    name = models.CharField(max_length=20, unique=True)
    level = models.IntegerField(unique=True, help_text="Niveau numérique (1-5)")
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#28a745')
    
    class Meta:
        verbose_name = "Niveau de difficulté"
        verbose_name_plural = "Niveaux de difficulté"
        ordering = ['level']
    
    def __str__(self):
        return f"{self.name} (Niveau {self.level})"

class Exercise(models.Model):
    """Modèle principal pour les exercices"""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    content = models.JSONField(help_text="Contenu structuré de l'exercice")
    solution = models.JSONField(help_text="Solution de l'exercice")
    hints = models.JSONField(default=list, blank=True, help_text="Indices pour l'exercice")
    
    # Vidéo d'explication
    explanation_video_url = models.URLField(blank=True, help_text="URL de la vidéo d'explication (YouTube, Vimeo, etc.)")
    explanation_video_type = models.CharField(
        max_length=20, 
        choices=[
            ('youtube', 'YouTube'),
            ('vimeo', 'Vimeo'),
            ('custom', 'Vidéo personnalisée'),
            ('auto', 'Génération automatique'),
        ],
        default='auto',
        help_text="Type de vidéo d'explication"
    )
    
    # Relations
    category = models.ForeignKey(ExerciseCategory, on_delete=models.CASCADE, related_name='exercises')
    exercise_type = models.ForeignKey(ExerciseType, on_delete=models.CASCADE, related_name='exercises')
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE, related_name='exercises')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exercises')
    
    # Métadonnées
    is_ai_generated = models.BooleanField(default=False)
    ai_prompt = models.TextField(blank=True, help_text="Prompt utilisé pour générer l'exercice")
    tags = models.JSONField(default=list, blank=True, help_text="Tags pour la recherche")
    estimated_time = models.IntegerField(default=15, help_text="Temps estimé en minutes")
    points = models.IntegerField(default=10, help_text="Points attribués")
    
    # Statut
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'difficulty']),
            models.Index(fields=['is_active', 'is_public']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.category.name})"
    
    def get_difficulty_display(self):
        return self.difficulty.name
    
    def get_content_preview(self):
        """Retourne un aperçu du contenu"""
        if isinstance(self.content, dict):
            return self.content.get('question', str(self.content))[:100] + "..."
        return str(self.content)[:100] + "..."

class ExerciseAttempt(models.Model):
    """Tentatives de résolution d'exercices par les étudiants"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_attempts')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='attempts')
    
    # Réponse de l'étudiant
    user_answer = models.JSONField(help_text="Réponse de l'étudiant")
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0.0, help_text="Score obtenu (0-100)")
    
    # Métadonnées
    time_spent = models.IntegerField(default=0, help_text="Temps passé en secondes")
    hints_used = models.JSONField(default=list, blank=True, help_text="Indices utilisés")
    attempts_count = models.IntegerField(default=1, help_text="Nombre de tentatives")
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Tentative d'exercice"
        verbose_name_plural = "Tentatives d'exercices"
        ordering = ['-started_at']
        unique_together = ['user', 'exercise']
        indexes = [
            models.Index(fields=['user', 'exercise']),
            models.Index(fields=['is_correct', 'score']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} ({self.score}%)"
    
    def calculate_time_spent(self):
        """Calcule le temps passé sur l'exercice"""
        if self.completed_at:
            delta = self.completed_at - self.started_at
            return int(delta.total_seconds())
        return 0

class ExerciseSession(models.Model):
    """Sessions d'exercices pour regrouper plusieurs exercices"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_sessions')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Configuration de la session
    category = models.ForeignKey(ExerciseCategory, on_delete=models.SET_NULL, null=True, blank=True)
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.SET_NULL, null=True, blank=True)
    exercise_count = models.IntegerField(default=5)
    time_limit = models.IntegerField(null=True, blank=True, help_text="Limite de temps en minutes")
    
    # Exercices de la session
    exercises = models.ManyToManyField(Exercise, through='SessionExercise')
    
    # Statut
    is_active = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    
    # Résultats
    total_score = models.FloatField(default=0.0)
    completed_exercises = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Session d'exercices"
        verbose_name_plural = "Sessions d'exercices"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def get_progress_percentage(self):
        """Calcule le pourcentage de progression"""
        if self.exercise_count > 0:
            return (self.completed_exercises / self.exercise_count) * 100
        return 0

class SessionExercise(models.Model):
    """Exercices dans une session"""
    session = models.ForeignKey(ExerciseSession, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    score = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['order']
        unique_together = ['session', 'exercise']

class AIExerciseGeneration(models.Model):
    """Historique des générations d'exercices par IA"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_generations')
    
    # Paramètres de génération
    prompt = models.TextField()
    category = models.ForeignKey(ExerciseCategory, on_delete=models.CASCADE)
    difficulty = models.ForeignKey(DifficultyLevel, on_delete=models.CASCADE)
    exercise_type = models.ForeignKey(ExerciseType, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)
    
    # Résultat
    generated_exercises = models.ManyToManyField(Exercise, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # Métadonnées
    processing_time = models.FloatField(default=0.0, help_text="Temps de traitement en secondes")
    ai_model = models.CharField(max_length=50, default='gpt-3.5-turbo')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Génération IA d'exercices"
        verbose_name_plural = "Générations IA d'exercices"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Génération IA - {self.user.username} ({self.created_at.strftime('%d/%m/%Y %H:%M')})"


class ExerciseSubmission(models.Model):
    """Soumission d'un exercice par un utilisateur avec correction IA"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_submissions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='submissions')
    
    # Réponse de l'utilisateur
    user_answer = models.TextField(help_text="Réponse soumise par l'utilisateur")
    submission_time = models.DateTimeField(auto_now_add=True)
    
    # Correction IA
    ai_correction = models.JSONField(default=dict, help_text="Correction automatique par l'IA")
    is_correct = models.BooleanField(default=False)
    score = models.FloatField(default=0.0, help_text="Score sur 100")
    feedback = models.TextField(blank=True, help_text="Feedback détaillé de l'IA")
    suggestions = models.JSONField(default=list, help_text="Suggestions d'amélioration")
    
    # Correction avancée
    detailed_correction = models.JSONField(default=dict, help_text="Correction ligne par ligne détaillée")
    video_explanation_url = models.URLField(blank=True, help_text="URL de la vidéo d'explication")
    comparison_answers = models.JSONField(default=list, help_text="Comparaison avec d'autres bonnes réponses")
    personalized_feedback = models.TextField(blank=True, help_text="Feedback personnalisé adapté au niveau")
    improvement_areas = models.JSONField(default=list, help_text="Domaines d'amélioration identifiés")
    strengths = models.JSONField(default=list, help_text="Points forts identifiés")
    
    # Métadonnées de correction
    correction_time = models.FloatField(default=0.0, help_text="Temps de correction en secondes")
    ai_model = models.CharField(max_length=50, default='llama-3.1-8b-instant')
    confidence_score = models.FloatField(default=0.0, help_text="Niveau de confiance de la correction (0-1)")
    
    class Meta:
        verbose_name = "Soumission d'exercice"
        verbose_name_plural = "Soumissions d'exercices"
        ordering = ['-submission_time']
        unique_together = ['user', 'exercise']
    
    def __str__(self):
        return f"Soumission - {self.user.username} - {self.exercise.title} ({self.score}/100)"


class ExerciseCorrectionSession(models.Model):
    """Session de correction d'exercices avec l'IA"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='correction_sessions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='correction_sessions')
    
    # État de la session
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Données de la session
    attempts = models.IntegerField(default=0)
    best_score = models.FloatField(default=0.0)
    total_time = models.FloatField(default=0.0, help_text="Temps total en minutes")
    
    # Feedback cumulatif
    cumulative_feedback = models.TextField(blank=True)
    improvement_areas = models.JSONField(default=list)
    
    class Meta:
        verbose_name = "Session de correction"
        verbose_name_plural = "Sessions de correction"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Session correction - {self.user.username} - {self.exercise.title}"


class ExerciseCollection(models.Model):
    """Collection personnalisée d'exercices créée par un utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_collections')
    name = models.CharField(max_length=100, help_text="Nom de la collection")
    description = models.TextField(blank=True, help_text="Description de la collection")
    color = models.CharField(max_length=7, default='#dc3545', help_text="Couleur de la collection (hex)")
    icon = models.CharField(max_length=50, default='fas fa-folder', help_text="Icône FontAwesome")
    
    # Métadonnées
    is_public = models.BooleanField(default=False, help_text="Collection visible par d'autres utilisateurs")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Collection d'exercices"
        verbose_name_plural = "Collections d'exercices"
        ordering = ['-updated_at']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class ExerciseFavorite(models.Model):
    """Exercice marqué comme favori par un utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Exercice favori"
        verbose_name_plural = "Exercices favoris"
        ordering = ['-created_at']
        unique_together = ['user', 'exercise']
    
    def __str__(self):
        return f"Favori - {self.user.username} - {self.exercise.title}"


class ExerciseInCollection(models.Model):
    """Exercice ajouté à une collection"""
    collection = models.ForeignKey(ExerciseCollection, on_delete=models.CASCADE, related_name='exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='in_collections')
    added_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage dans la collection")
    
    class Meta:
        verbose_name = "Exercice dans collection"
        verbose_name_plural = "Exercices dans collections"
        ordering = ['order', '-added_at']
        unique_together = ['collection', 'exercise']
    
    def __str__(self):
        return f"{self.exercise.title} dans {self.collection.name}"


class ExerciseHistory(models.Model):
    """Historique des exercices consultés par un utilisateur"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_history')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='viewed_by')
    viewed_at = models.DateTimeField(auto_now_add=True)
    time_spent = models.FloatField(default=0.0, help_text="Temps passé sur l'exercice en secondes")
    
    class Meta:
        verbose_name = "Historique d'exercice"
        verbose_name_plural = "Historiques d'exercices"
        ordering = ['-viewed_at']
        unique_together = ['user', 'exercise']
    
    def __str__(self):
        return f"Historique - {self.user.username} - {self.exercise.title}"


class ExerciseWishlist(models.Model):
    """Liste de souhaits d'exercices à faire plus tard"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_wishlist')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='in_wishlists')
    added_at = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(default=1, help_text="Priorité (1=haute, 5=basse)")
    notes = models.TextField(blank=True, help_text="Notes personnelles sur l'exercice")
    
    class Meta:
        verbose_name = "Exercice en liste de souhaits"
        verbose_name_plural = "Exercices en liste de souhaits"
        ordering = ['priority', '-added_at']
        unique_together = ['user', 'exercise']
    
    def __str__(self):
        return f"Liste de souhaits - {self.user.username} - {self.exercise.title}"


class UserExerciseStatus(models.Model):
    """Statut des exercices pour chaque utilisateur (favoris, à faire plus tard, etc.)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_statuses')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='user_statuses')
    
    # Statuts
    is_favorite = models.BooleanField(default=False, help_text="Exercice marqué comme favori")
    is_wishlist = models.BooleanField(default=False, help_text="Exercice ajouté à la liste de souhaits")
    is_completed = models.BooleanField(default=False, help_text="Exercice terminé")
    is_in_progress = models.BooleanField(default=False, help_text="Exercice en cours")
    
    # Métadonnées
    added_to_favorites_at = models.DateTimeField(null=True, blank=True)
    added_to_wishlist_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    
    # Score et notes
    score = models.FloatField(null=True, blank=True, help_text="Score obtenu (0-100)")
    notes = models.TextField(blank=True, help_text="Notes personnelles de l'utilisateur")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Statut d'exercice utilisateur"
        verbose_name_plural = "Statuts d'exercices utilisateurs"
        unique_together = ['user', 'exercise']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} ({'Favori' if self.is_favorite else 'Normal'})"
    
    def save(self, *args, **kwargs):
        # Mettre à jour les timestamps automatiquement
        if self.is_favorite and not self.added_to_favorites_at:
            self.added_to_favorites_at = timezone.now()
        if self.is_wishlist and not self.added_to_wishlist_at:
            self.added_to_wishlist_at = timezone.now()
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        if self.is_in_progress and not self.started_at:
            self.started_at = timezone.now()
        
        super().save(*args, **kwargs)
