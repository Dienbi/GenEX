from __future__ import annotations
from django.db import models
from django.conf import settings
import uuid
import os


def voice_upload_path(instance, filename):
    """Generate unique path for voice recordings"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('voice_recordings', str(instance.user.id), filename)





class VoiceEvaluation(models.Model):
    """Main model for storing voice evaluation results"""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
    ]
    
    LEVEL_CHOICES = [
        ('A1', 'Beginner - A1'),
        ('A2', 'Elementary - A2'),
        ('B1', 'Intermediate - B1'),
        ('B2', 'Upper Intermediate - B2'),
        ('C1', 'Advanced - C1'),
        ('C2', 'Proficient - C2'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='voice_evaluations')
    audio_file = models.FileField(upload_to=voice_upload_path, max_length=500)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    theme = models.CharField(max_length=200, blank=True, null=True, help_text="Topic or theme of the recording")
    
    # Transcription
    transcription = models.TextField(blank=True, null=True)
    
    # Verbal Communication Scores (0-100)
    fluency_score = models.FloatField(default=0.0, help_text="Fluency evaluation (0-100)")
    vocabulary_score = models.FloatField(default=0.0, help_text="Vocabulary richness (0-100)")
    structure_score = models.FloatField(default=0.0, help_text="Grammar and structure (0-100)")
    verbal_score = models.FloatField(default=0.0, help_text="Overall verbal score (0-100)")
    
    # Paraverbal Communication Scores (0-100)
    pitch_score = models.FloatField(default=0.0, help_text="Pitch variation (0-100)")
    pace_score = models.FloatField(default=0.0, help_text="Speaking pace (0-100)")
    energy_score = models.FloatField(default=0.0, help_text="Voice energy (0-100)")
    paraverbal_score = models.FloatField(default=0.0, help_text="Overall paraverbal score (0-100)")
    
    # Originality Score (0-100)
    originality_score = models.FloatField(default=0.0, help_text="Content originality (0-100)")
    
    # Final Results
    total_score = models.FloatField(default=0.0, help_text="Overall score (0-100)")
    estimated_level = models.CharField(max_length=2, choices=LEVEL_CHOICES, blank=True, null=True)
    
    # Feedback
    feedback = models.JSONField(default=dict, blank=True, help_text="Detailed feedback for the user")
    
    # Audio Analysis Data
    audio_features = models.JSONField(default=dict, blank=True, help_text="Raw audio features from librosa")
    
    # Metadata
    duration = models.FloatField(default=0.0, help_text="Recording duration in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['processing_status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.language} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class ReferenceText(models.Model):
    """Store reference texts for originality comparison"""
    language = models.CharField(max_length=2, choices=VoiceEvaluation.LANGUAGE_CHOICES)
    theme = models.CharField(max_length=200, help_text="Topic or theme")
    text = models.TextField(help_text="Reference text content")
    embedding = models.JSONField(default=list, blank=True, help_text="Text embedding vector")
    source = models.CharField(max_length=200, blank=True, null=True, help_text="Source of the text")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['theme', 'language']
        indexes = [
            models.Index(fields=['language', 'theme']),
        ]
    
    def __str__(self):
        return f"{self.theme} ({self.language})"


class VoiceEvaluationHistory(models.Model):
    """Track user's progress over time"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluation_history')
    evaluation = models.ForeignKey(VoiceEvaluation, on_delete=models.CASCADE)
    previous_level = models.CharField(max_length=2, choices=VoiceEvaluation.LEVEL_CHOICES, blank=True, null=True)
    new_level = models.CharField(max_length=2, choices=VoiceEvaluation.LEVEL_CHOICES, blank=True, null=True)
    improvement_score = models.FloatField(default=0.0, help_text="Improvement since last evaluation")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Voice Evaluation Histories"
    
    def __str__(self):
        return f"{self.user.username} - Progress on {self.created_at.strftime('%Y-%m-%d')}"
