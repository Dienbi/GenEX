from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ExerciseCategory, ExerciseType, DifficultyLevel, Exercise,
    ExerciseAttempt, ExerciseSession, SessionExercise, AIExerciseGeneration,
    ExerciseSubmission, ExerciseCorrectionSession, ExerciseCollection,
    ExerciseFavorite, ExerciseHistory, ExerciseWishlist, ExerciseInCollection
)

@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']

@admin.register(ExerciseType)
class ExerciseTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_interactive', 'created_at']
    list_filter = ['is_interactive', 'created_at']
    search_fields = ['name', 'description']

@admin.register(DifficultyLevel)
class DifficultyLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'color']
    list_filter = ['level']
    ordering = ['level']

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'exercise_type', 'is_public', 'created_at', 'actions_column']
    list_filter = ['category', 'difficulty', 'exercise_type', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'content']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    ordering = ['-created_at']
    
    # Configuration pour l'ajout d'exercices manuels
    fieldsets = (
        ('📝 Informations de base', {
            'fields': ('title', 'description', 'category', 'difficulty', 'exercise_type'),
            'description': 'Informations essentielles pour identifier l\'exercice'
        }),
        ('📄 Contenu de l\'exercice', {
            'fields': ('content', 'solution', 'hints', 'explanation'),
            'description': 'Le contenu principal de l\'exercice et sa solution',
            'classes': ('wide',)
        }),
        ('⏱️ Paramètres', {
            'fields': ('estimated_time', 'points', 'is_public'),
            'description': 'Configuration de l\'exercice'
        }),
        ('🎥 Médias (optionnel)', {
            'fields': ('image', 'explanation_video_url', 'explanation_video_type'),
            'classes': ('collapse',),
            'description': 'Images et vidéos d\'explication'
        }),
        ('📊 Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Valeurs par défaut pour les nouveaux exercices
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Nouvel exercice
            form.base_fields['is_public'].initial = True
            form.base_fields['estimated_time'].initial = 10
            form.base_fields['points'].initial = 10
        return form
    
    def actions_column(self, obj):
        """Colonne d'actions personnalisées"""
        return format_html(
            '<a href="{}" class="button" target="_blank">👁️ Voir</a> | '
            '<a href="{}" class="button" target="_blank">▶️ Résoudre</a>',
            reverse('exercises:exercise-detail', args=[obj.id]),
            reverse('exercises:exercise-solve', args=[obj.id])
        )
    actions_column.short_description = 'Actions'
    actions_column.allow_tags = True

@admin.register(ExerciseAttempt)
class ExerciseAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'is_correct', 'score', 'started_at']
    list_filter = ['is_correct', 'started_at']
    search_fields = ['user__username', 'exercise__title']

@admin.register(ExerciseSession)
class ExerciseSessionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'difficulty', 'is_active', 'is_completed', 'created_at']
    list_filter = ['category', 'difficulty', 'is_active', 'is_completed', 'created_at']
    search_fields = ['name', 'description', 'user__username']

@admin.register(SessionExercise)
class SessionExerciseAdmin(admin.ModelAdmin):
    list_display = ['session', 'exercise', 'order', 'is_completed', 'score']
    list_filter = ['is_completed', 'session__category']
    ordering = ['session', 'order']

@admin.register(AIExerciseGeneration)
class AIExerciseGenerationAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'difficulty', 'exercise_type', 'count', 'success', 'created_at']
    list_filter = ['category', 'difficulty', 'exercise_type', 'success', 'created_at']
    search_fields = ['user__username', 'prompt']
    readonly_fields = ['created_at', 'processing_time']

# === NOUVEAUX MODÈLES POUR LES EXERCICES ===

@admin.register(ExerciseSubmission)
class ExerciseSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'score', 'is_correct', 'submitted_at']
    list_filter = ['is_correct', 'submitted_at', 'exercise__category']
    search_fields = ['user__username', 'exercise__title', 'user_answer']
    readonly_fields = ['submitted_at']
    list_per_page = 25
    ordering = ['-submitted_at']

@admin.register(ExerciseCollection)
class ExerciseCollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'exercise_count', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def exercise_count(self, obj):
        return obj.exercises.count()
    exercise_count.short_description = 'Nb Exercices'

@admin.register(ExerciseInCollection)
class ExerciseInCollectionAdmin(admin.ModelAdmin):
    list_display = ['collection', 'exercise', 'added_at']
    list_filter = ['collection', 'added_at']
    search_fields = ['collection__name', 'exercise__title']
    ordering = ['collection', 'added_at']

@admin.register(ExerciseFavorite)
class ExerciseFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'added_at']
    list_filter = ['added_at', 'exercise__category']
    search_fields = ['user__username', 'exercise__title']
    ordering = ['-added_at']

@admin.register(ExerciseHistory)
class ExerciseHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'completed_at', 'score']
    list_filter = ['completed_at', 'exercise__category']
    search_fields = ['user__username', 'exercise__title']
    ordering = ['-completed_at']

@admin.register(ExerciseWishlist)
class ExerciseWishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'added_at']
    list_filter = ['added_at', 'exercise__category']
    search_fields = ['user__username', 'exercise__title']
    ordering = ['-added_at']

@admin.register(ExerciseCorrectionSession)
class ExerciseCorrectionSessionAdmin(admin.ModelAdmin):
    list_display = ['submission', 'corrector', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['submission__exercise__title', 'corrector__username']
    readonly_fields = ['created_at', 'updated_at']