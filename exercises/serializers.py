from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ExerciseCategory, ExerciseType, DifficultyLevel, Exercise,
    ExerciseAttempt, ExerciseSession, SessionExercise, AIExerciseGeneration,
    ExerciseSubmission, ExerciseCollection, ExerciseFavorite, ExerciseHistory, 
    ExerciseWishlist, ExerciseInCollection
)

User = get_user_model()

class ExerciseCategorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour les catégories d'exercices"""
    exercise_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ExerciseCategory
        fields = ['id', 'name', 'description', 'icon', 'color', 'exercise_count', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_exercise_count(self, obj):
        return obj.exercises.filter(is_active=True, is_public=True).count()

class ExerciseTypeSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les types d'exercices"""
    
    class Meta:
        model = ExerciseType
        fields = ['id', 'name', 'description', 'template', 'is_interactive', 'created_at']
        read_only_fields = ['id', 'created_at']

class DifficultyLevelSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les niveaux de difficulté"""
    
    class Meta:
        model = DifficultyLevel
        fields = ['id', 'name', 'level', 'description', 'color']
        read_only_fields = ['id']

class ExerciseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les exercices"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    exercise_type_name = serializers.CharField(source='exercise_type.name', read_only=True)
    difficulty_name = serializers.CharField(source='difficulty.name', read_only=True)
    difficulty_level = serializers.IntegerField(source='difficulty.level', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    content_preview = serializers.SerializerMethodField()
    attempt_count = serializers.SerializerMethodField()
    success_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'description', 'content', 'solution', 'hints',
            'category', 'category_name', 'exercise_type', 'exercise_type_name',
            'difficulty', 'difficulty_name', 'difficulty_level', 'created_by',
            'created_by_username', 'is_ai_generated', 'ai_prompt', 'tags',
            'estimated_time', 'points', 'is_active', 'is_public',
            'created_at', 'updated_at', 'content_preview', 'attempt_count', 'success_rate'
        ]
        read_only_fields = [
            'id', 'created_by', 'created_at', 'updated_at',
            'content_preview', 'attempt_count', 'success_rate'
        ]
    
    def get_content_preview(self, obj):
        return obj.get_content_preview()
    
    def get_attempt_count(self, obj):
        return obj.attempts.count()
    
    def get_success_rate(self, obj):
        attempts = obj.attempts.all()
        if attempts:
            successful = attempts.filter(is_correct=True).count()
            return round((successful / attempts.count()) * 100, 2)
        return 0

class ExerciseListSerializer(serializers.ModelSerializer):
    """Sérialiseur simplifié pour la liste des exercices"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_name = serializers.CharField(source='difficulty.name', read_only=True)
    difficulty_level = serializers.IntegerField(source='difficulty.level', read_only=True)
    content_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = Exercise
        fields = [
            'id', 'title', 'description', 'category_name', 'difficulty_name',
            'difficulty_level', 'estimated_time', 'points', 'is_ai_generated',
            'created_at', 'content_preview'
        ]
    
    def get_content_preview(self, obj):
        return obj.get_content_preview()

class ExerciseAttemptSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les tentatives d'exercices"""
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)
    exercise_category = serializers.CharField(source='exercise.category.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    time_spent_display = serializers.SerializerMethodField()
    
    class Meta:
        model = ExerciseAttempt
        fields = [
            'id', 'user', 'user_username', 'exercise', 'exercise_title',
            'exercise_category', 'user_answer', 'is_correct', 'score',
            'time_spent', 'time_spent_display', 'hints_used', 'attempts_count',
            'started_at', 'completed_at'
        ]
        read_only_fields = ['id', 'started_at']
    
    def get_time_spent_display(self, obj):
        if obj.completed_at:
            return obj.calculate_time_spent()
        return obj.time_spent

class ExerciseSessionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les sessions d'exercices"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_name = serializers.CharField(source='difficulty.name', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    exercises_list = serializers.SerializerMethodField()
    
    class Meta:
        model = ExerciseSession
        fields = [
            'id', 'user', 'user_username', 'name', 'description',
            'category', 'category_name', 'difficulty', 'difficulty_name',
            'exercise_count', 'time_limit', 'is_active', 'is_completed',
            'total_score', 'completed_exercises', 'progress_percentage',
            'exercises_list', 'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'total_score', 'completed_exercises',
            'progress_percentage', 'exercises_list', 'created_at'
        ]
    
    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()
    
    def get_exercises_list(self, obj):
        session_exercises = obj.sessionexercise_set.select_related('exercise').order_by('order')
        return [
            {
                'id': se.exercise.id,
                'title': se.exercise.title,
                'order': se.order,
                'is_completed': se.is_completed,
                'score': se.score
            }
            for se in session_exercises
        ]

class SessionExerciseSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les exercices dans une session"""
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)
    exercise_content = serializers.JSONField(source='exercise.content', read_only=True)
    
    class Meta:
        model = SessionExercise
        fields = [
            'id', 'session', 'exercise', 'exercise_title', 'exercise_content',
            'order', 'is_completed', 'score'
        ]
        read_only_fields = ['id']

class AIExerciseGenerationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les générations d'exercices par IA"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_name = serializers.CharField(source='difficulty.name', read_only=True)
    exercise_type_name = serializers.CharField(source='exercise_type.name', read_only=True)
    generated_exercises_list = serializers.SerializerMethodField()
    
    class Meta:
        model = AIExerciseGeneration
        fields = [
            'id', 'user', 'user_username', 'prompt', 'category', 'category_name',
            'difficulty', 'difficulty_name', 'exercise_type', 'exercise_type_name',
            'count', 'success', 'error_message', 'processing_time', 'ai_model',
            'generated_exercises_list', 'created_at'
        ]
        read_only_fields = [
            'id', 'user', 'success', 'error_message', 'processing_time',
            'generated_exercises_list', 'created_at'
        ]
    
    def get_generated_exercises_list(self, obj):
        exercises = obj.generated_exercises.all()
        return [
            {
                'id': ex.id,
                'title': ex.title,
                'category': ex.category.name,
                'difficulty': ex.difficulty.name
            }
            for ex in exercises
        ]

class ExerciseGenerationRequestSerializer(serializers.Serializer):
    """Sérialiseur pour les requêtes de génération d'exercices"""
    subject = serializers.CharField(max_length=200, help_text="Matière ou cours pour lequel générer des exercices")
    difficulty = serializers.PrimaryKeyRelatedField(queryset=DifficultyLevel.objects.all())
    exercise_type = serializers.PrimaryKeyRelatedField(queryset=ExerciseType.objects.all())
    count = serializers.IntegerField(min_value=1, max_value=10, default=1)
    custom_prompt = serializers.CharField(required=False, allow_blank=True)
    user_level = serializers.CharField(required=False, allow_blank=True)
    specific_topics = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        allow_empty=True
    )
    
    def validate_count(self, value):
        if value > 5:
            raise serializers.ValidationError("Maximum 5 exercices par génération")
        return value

class ExerciseAttemptSubmissionSerializer(serializers.Serializer):
    """Sérialiseur pour la soumission d'une tentative d'exercice"""
    user_answer = serializers.JSONField()
    hints_used = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        default=list
    )
    time_spent = serializers.IntegerField(min_value=0, default=0)
    
    def validate_user_answer(self, value):
        if not value:
            raise serializers.ValidationError("La réponse ne peut pas être vide")
        return value

class ExerciseRecommendationSerializer(serializers.Serializer):
    """Sérialiseur pour les recommandations d'exercices"""
    category = serializers.PrimaryKeyRelatedField(
        queryset=ExerciseCategory.objects.all(),
        required=False
    )
    difficulty = serializers.PrimaryKeyRelatedField(
        queryset=DifficultyLevel.objects.all(),
        required=False
    )
    limit = serializers.IntegerField(min_value=1, max_value=20, default=5)
    exclude_attempted = serializers.BooleanField(default=True)


class ExerciseCollectionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les collections d'exercices"""
    exercise_count = serializers.SerializerMethodField()
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ExerciseCollection
        fields = ['id', 'name', 'description', 'color', 'icon', 'is_public', 
                 'exercise_count', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_exercise_count(self, obj):
        return obj.exercises.count()


class ExerciseFavoriteSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les exercices favoris"""
    exercise = ExerciseSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ExerciseFavorite
        fields = ['id', 'exercise', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class ExerciseHistorySerializer(serializers.ModelSerializer):
    """Sérialiseur pour l'historique des exercices"""
    exercise = ExerciseSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ExerciseHistory
        fields = ['id', 'exercise', 'user', 'viewed_at', 'time_spent']
        read_only_fields = ['id', 'user', 'viewed_at']


class ExerciseWishlistSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la liste de souhaits"""
    exercise = ExerciseSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ExerciseWishlist
        fields = ['id', 'exercise', 'user', 'added_at', 'priority', 'notes']
        read_only_fields = ['id', 'user', 'added_at']


class ExerciseInCollectionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les exercices dans une collection"""
    exercise = ExerciseSerializer(read_only=True)
    collection = ExerciseCollectionSerializer(read_only=True)
    
    class Meta:
        model = ExerciseInCollection
        fields = ['id', 'exercise', 'collection', 'added_at', 'order']
        read_only_fields = ['id', 'added_at']


class AdvancedCorrectionSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la correction avancée des exercices"""
    exercise = ExerciseSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ExerciseSubmission
        fields = [
            'id', 'exercise', 'user', 'user_answer', 'submission_time',
            'is_correct', 'score', 'feedback', 'suggestions',
            'detailed_correction', 'video_explanation_url', 'comparison_answers',
            'personalized_feedback', 'improvement_areas', 'strengths',
            'correction_time', 'ai_model', 'confidence_score'
        ]
        read_only_fields = [
            'id', 'user', 'submission_time', 'is_correct', 'score', 'feedback',
            'suggestions', 'detailed_correction', 'video_explanation_url',
            'comparison_answers', 'personalized_feedback', 'improvement_areas',
            'strengths', 'correction_time', 'ai_model', 'confidence_score'
        ]
