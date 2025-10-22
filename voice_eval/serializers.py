from __future__ import annotations
from rest_framework import serializers
from .models import VoiceEvaluation, ReferenceText, VoiceEvaluationHistory


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
