from __future__ import annotations
from rest_framework import serializers
from .models import (
    VoiceEvaluation, ReferenceText, VoiceEvaluationHistory,
    Certificate, PronunciationPractice, TestingCenter
)


class VoiceEvaluationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = VoiceEvaluation
        fields = [
            'id', 'username', 'audio_file', 'language', 'theme',
            'transcription', 'fluency_score', 'vocabulary_score', 
            'structure_score', 'verbal_score', 'pitch_score', 
            'pace_score', 'energy_score', 'paraverbal_score',
            'originality_score', 'total_score', 'estimated_level',
            'feedback', 'duration', 'created_at', 'processing_status'
        ]
        read_only_fields = [
            'transcription', 'fluency_score', 'vocabulary_score',
            'structure_score', 'verbal_score', 'pitch_score',
            'pace_score', 'energy_score', 'paraverbal_score',
            'originality_score', 'total_score', 'estimated_level',
            'feedback', 'duration', 'created_at', 'processing_status'
        ]


class VoiceEvaluationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceEvaluation
        fields = ['audio_file', 'language', 'theme']


class VoiceEvaluationDetailSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = VoiceEvaluation
        fields = '__all__'


class ReferenceTextSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferenceText
        fields = ['id', 'language', 'theme', 'text', 'source', 'created_at']
        read_only_fields = ['embedding', 'created_at']


class VoiceEvaluationHistorySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    evaluation_date = serializers.DateTimeField(source='evaluation.created_at', read_only=True)
    
    class Meta:
        model = VoiceEvaluationHistory
        fields = [
            'id', 'username', 'evaluation_date', 'previous_level',
            'new_level', 'improvement_score', 'created_at'
        ]


class CertificateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    evaluation_score = serializers.FloatField(source='evaluation.total_score', read_only=True)
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'username', 'certificate_id', 'pdf_file', 'issued_date',
            'language', 'level', 'score', 'evaluation_score'
        ]
        read_only_fields = ['certificate_id', 'issued_date']


class PronunciationPracticeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    accuracy_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = PronunciationPractice
        fields = [
            'id', 'username', 'expected_text', 'spoken_text', 'audio_file',
            'comparison_data', 'accuracy_score', 'matched_words', 'total_words',
            'accuracy_percentage', 'created_at'
        ]
        read_only_fields = [
            'spoken_text', 'comparison_data', 'accuracy_score',
            'matched_words', 'total_words', 'created_at'
        ]
    
    def get_accuracy_percentage(self, obj):
        if obj.total_words > 0:
            return f"{(obj.matched_words / obj.total_words * 100):.1f}%"
        return "0%"


class TestingCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestingCenter
        fields = [
            'id', 'name', 'address', 'city', 'country', 'latitude', 'longitude',
            'phone', 'email', 'website', 'languages', 'certifications', 'is_active'
        ]

