from django.contrib import admin
from .models import (
    ExerciseCategory, ExerciseType, DifficultyLevel, Exercise,
    ExerciseAttempt, ExerciseSession, SessionExercise, AIExerciseGeneration
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
    list_display = ['title', 'category', 'difficulty', 'exercise_type', 'is_ai_generated', 'is_public', 'created_at']
    list_filter = ['category', 'difficulty', 'exercise_type', 'is_ai_generated', 'is_public', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

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