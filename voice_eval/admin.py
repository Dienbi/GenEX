from django.contrib import admin
from .models import VoiceEvaluation, ReferenceText, VoiceEvaluationHistory


@admin.register(VoiceEvaluation)
class VoiceEvaluationAdmin(admin.ModelAdmin):
    list_display = ('user', 'language', 'estimated_level', 'total_score', 'processing_status', 'created_at')
    list_filter = ('language', 'estimated_level', 'processing_status', 'created_at')
    search_fields = ('user__username', 'transcription', 'theme')
    readonly_fields = (
        'transcription', 'fluency_score', 'vocabulary_score', 'structure_score',
        'verbal_score', 'pitch_score', 'pace_score', 'energy_score',
        'paraverbal_score', 'originality_score', 'total_score',
        'estimated_level', 'feedback', 'audio_features', 'duration', 'created_at'
    )
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'audio_file', 'language', 'theme', 'processing_status', 'error_message')
        }),
        ('Transcription', {
            'fields': ('transcription', 'duration')
        }),
        ('Verbal Communication', {
            'fields': ('fluency_score', 'vocabulary_score', 'structure_score', 'verbal_score')
        }),
        ('Paraverbal Communication', {
            'fields': ('pitch_score', 'pace_score', 'energy_score', 'paraverbal_score')
        }),
        ('Originality', {
            'fields': ('originality_score',)
        }),
        ('Results', {
            'fields': ('total_score', 'estimated_level', 'feedback')
        }),
        ('Technical Data', {
            'fields': ('audio_features', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReferenceText)
class ReferenceTextAdmin(admin.ModelAdmin):
    list_display = ('theme', 'language', 'source', 'created_at')
    list_filter = ('language', 'theme')
    search_fields = ('theme', 'text', 'source')
    readonly_fields = ('embedding', 'created_at')


@admin.register(VoiceEvaluationHistory)
class VoiceEvaluationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'previous_level', 'new_level', 'improvement_score', 'created_at')
    list_filter = ('previous_level', 'new_level', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
