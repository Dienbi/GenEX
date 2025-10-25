from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Quiz, Question, QuizAttempt
from .serializers import QuizSerializer, QuestionSerializer, QuizAttemptSerializer
from .ai_service import GeminiQuizGenerator
from .streak_utils import check_and_update_streak, update_streak_on_quiz_completion, get_streak_status_message, get_time_until_streak_expires
import json


# ============= Web Views (HTML) =============

@login_required
def quiz_home(request):
    """Main quiz page - shows user's quiz history and option to generate new quiz"""
    # Check and update streak if needed
    streak_info = check_and_update_streak(request.user)
    time_info = get_time_until_streak_expires(request.user)
    
    user_quizzes = Quiz.objects.filter(created_by=request.user)
    user_attempts = QuizAttempt.objects.filter(user=request.user)[:5]
    
    # Get leaderboard data
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Top 10 Current Streaks (active users only, current_streak > 0)
    top_current_streaks = User.objects.filter(
        current_streak__gt=0
    ).order_by('-current_streak', '-last_quiz_date')[:10]
    
    # Top 10 Longest Streaks (all-time bests)
    top_longest_streaks = User.objects.filter(
        longest_streak__gt=0
    ).order_by('-longest_streak', '-current_streak')[:10]
    
    context = {
        'user_quizzes': user_quizzes,
        'user_attempts': user_attempts,
        'current_streak': streak_info['current_streak'],
        'longest_streak': streak_info['longest_streak'],
        'streak_status': streak_info['status'],
        'time_until_expires': time_info,
        'top_current_streaks': top_current_streaks,
        'top_longest_streaks': top_longest_streaks,
    }
    return render(request, 'quizzes/home.html', context)


@login_required
def generate_quiz_view(request):
    """View to generate a new quiz"""
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        user_prompt = request.POST.get('user_prompt', '').strip()
        
        if not subject or not user_prompt:
            messages.error(request, 'Please provide both subject and description.')
            return render(request, 'quizzes/generate.html')
        
        try:
            # Generate quiz using Gemini AI
            generator = GeminiQuizGenerator()
            quiz_data = generator.generate_quiz(subject, user_prompt)
            
            # Save quiz and questions to database
            with transaction.atomic():
                quiz = Quiz.objects.create(
                    title=quiz_data.get('title', f'{subject} Quiz'),
                    subject=subject,
                    user_prompt=user_prompt,
                    created_by=request.user
                )
                
                # Create questions
                for idx, q_data in enumerate(quiz_data['questions'], 1):
                    Question.objects.create(
                        quiz=quiz,
                        question_text=q_data['question_text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_answer=q_data['correct_answer'].upper(),
                        order=idx
                    )
            
            messages.success(request, f'Quiz generated successfully! {quiz.questions.count()} questions created.')
            return redirect('quizzes:take_quiz', quiz_id=quiz.id)
            
        except Exception as e:
            messages.error(request, f'Error generating quiz: {str(e)}')
            return render(request, 'quizzes/generate.html')
    
    return render(request, 'quizzes/generate.html')


@login_required
def take_quiz_view(request, quiz_id):
    """View to take a quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    questions = quiz.questions.all()
    
    context = {
        'quiz': quiz,
        'questions': questions,
    }
    return render(request, 'quizzes/take_quiz.html', context)


@login_required
@require_http_methods(["POST"])
def submit_quiz_view(request, quiz_id):
    """Handle quiz submission and show results"""
    quiz = get_object_or_404(Quiz, id=quiz_id, is_active=True)
    
    # Collect user answers
    answers = {}
    for question in quiz.questions.all():
        answer_key = f'question_{question.id}'
        user_answer = request.POST.get(answer_key, '').upper()
        if user_answer:
            answers[str(question.id)] = user_answer
    
    # Create quiz attempt
    attempt = QuizAttempt.objects.create(
        quiz=quiz,
        user=request.user,
        answers=answers
    )
    
    # Calculate score
    attempt.calculate_score()
    
    # Update user's streak
    streak_info = update_streak_on_quiz_completion(request.user)
    streak_message = get_streak_status_message(streak_info)
    
    # Add streak message to session to show on results page
    messages.success(request, streak_message)
    
    return redirect('quizzes:quiz_results', attempt_id=attempt.id)


@login_required
def quiz_results_view(request, attempt_id):
    """View to show quiz results"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, user=request.user)
    
    # Get detailed results for each question
    questions_with_results = []
    for question in attempt.quiz.questions.all():
        user_answer = attempt.answers.get(str(question.id), '')
        is_correct = user_answer.upper() == question.correct_answer
        
        questions_with_results.append({
            'question': question,
            'user_answer': user_answer,
            'is_correct': is_correct,
        })
    
    context = {
        'attempt': attempt,
        'questions_with_results': questions_with_results,
    }
    return render(request, 'quizzes/results.html', context)


# ============= API ViewSets (Optional - for REST API) =============

class QuizViewSet(viewsets.ModelViewSet):
    """API ViewSet for Quiz operations"""
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own quizzes
        return Quiz.objects.filter(created_by=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate(self, request):
        """API endpoint to generate a new quiz"""
        subject = request.data.get('subject')
        user_prompt = request.data.get('user_prompt')
        
        if not subject or not user_prompt:
            return Response(
                {'error': 'Both subject and user_prompt are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            generator = GeminiQuizGenerator()
            quiz_data = generator.generate_quiz(subject, user_prompt)
            
            with transaction.atomic():
                quiz = Quiz.objects.create(
                    title=quiz_data.get('title', f'{subject} Quiz'),
                    subject=subject,
                    user_prompt=user_prompt,
                    created_by=request.user
                )
                
                for idx, q_data in enumerate(quiz_data['questions'], 1):
                    Question.objects.create(
                        quiz=quiz,
                        question_text=q_data['question_text'],
                        option_a=q_data['option_a'],
                        option_b=q_data['option_b'],
                        option_c=q_data['option_c'],
                        option_d=q_data['option_d'],
                        correct_answer=q_data['correct_answer'].upper(),
                        order=idx
                    )
            
            serializer = self.get_serializer(quiz)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """API ViewSet for Quiz Attempts"""
    queryset = QuizAttempt.objects.all()
    serializer_class = QuizAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        attempt = serializer.save(user=self.request.user)
        attempt.calculate_score()
        return attempt
