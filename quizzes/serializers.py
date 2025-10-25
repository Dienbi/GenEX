from rest_framework import serializers
from .models import Quiz, Question, QuizAttempt


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'order']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'subject', 'user_prompt', 'created_by', 'created_by_username', 'created_at', 'is_active', 'questions']
        read_only_fields = ['created_by', 'created_at']


class QuizAttemptSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'quiz_title', 'user', 'username', 'score', 'total_questions', 'percentage', 'answers', 'completed_at']
        read_only_fields = ['user', 'score', 'total_questions', 'percentage', 'completed_at']

