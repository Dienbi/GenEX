from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from .models import (
    ExerciseCategory, ExerciseType, DifficultyLevel, Exercise,
    ExerciseAttempt, ExerciseSession, SessionExercise, AIExerciseGeneration,
    ExerciseSubmission, ExerciseCorrectionSession
)
from .serializers import (
    ExerciseCategorySerializer, ExerciseTypeSerializer, DifficultyLevelSerializer,
    ExerciseSerializer, ExerciseListSerializer, ExerciseAttemptSerializer,
    ExerciseSessionSerializer, SessionExerciseSerializer, AIExerciseGenerationSerializer,
    ExerciseGenerationRequestSerializer, ExerciseAttemptSubmissionSerializer,
    ExerciseRecommendationSerializer
)
from .ai_service import exercise_ai_service
from .correction_service import exercise_correction_service

class ExerciseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Vue pour les catégories d'exercices"""
    queryset = ExerciseCategory.objects.all()
    serializer_class = ExerciseCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ExerciseTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """Vue pour les types d'exercices"""
    queryset = ExerciseType.objects.all()
    serializer_class = ExerciseTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class DifficultyLevelViewSet(viewsets.ReadOnlyModelViewSet):
    """Vue pour les niveaux de difficulté"""
    queryset = DifficultyLevel.objects.all()
    serializer_class = DifficultyLevelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ExerciseViewSet(viewsets.ModelViewSet):
    """Vue principale pour les exercices"""
    queryset = Exercise.objects.all()  # Voir tous les exercices temporairement
    permission_classes = []  # Pas de restriction d'authentification
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty', 'exercise_type', 'is_ai_generated']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'difficulty__level', 'points']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExerciseListSerializer
        return ExerciseSerializer
    
    def get_queryset(self):
        """Filtre les exercices selon les permissions"""
        queryset = super().get_queryset()
        
        # Si l'utilisateur n'est pas admin, ne montrer que les exercices publics
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_public=True)
        
        return queryset
    
    def perform_create(self, serializer):
        """Associe l'exercice à l'utilisateur créateur"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def attempt(self, request, pk=None):
        """Soumettre une tentative d'exercice"""
        exercise = self.get_object()
        serializer = ExerciseAttemptSubmissionSerializer(data=request.data)
        
        if serializer.is_valid():
            # Récupérer ou créer la tentative
            attempt, created = ExerciseAttempt.objects.get_or_create(
                user=request.user,
                exercise=exercise,
                defaults={
                    'user_answer': serializer.validated_data['user_answer'],
                    'hints_used': serializer.validated_data.get('hints_used', []),
                    'time_spent': serializer.validated_data.get('time_spent', 0)
                }
            )
            
            if not created:
                # Mettre à jour la tentative existante
                attempt.user_answer = serializer.validated_data['user_answer']
                attempt.hints_used = serializer.validated_data.get('hints_used', [])
                attempt.time_spent = serializer.validated_data.get('time_spent', 0)
                attempt.attempts_count += 1
                attempt.completed_at = timezone.now()
            
            # Évaluer la réponse
            is_correct, score = self._evaluate_answer(exercise, attempt.user_answer)
            attempt.is_correct = is_correct
            attempt.score = score
            attempt.save()
            
            return Response({
                'success': True,
                'is_correct': is_correct,
                'score': score,
                'attempt_id': attempt.id,
                'solution': exercise.solution if is_correct else None
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Soumettre un exercice pour correction IA"""
        exercise = self.get_object()
        user_answer = request.data.get('user_answer')
        
        if not user_answer:
            return Response({'error': 'Réponse de l\'utilisateur manquante'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Utiliser le service de correction IA
        result = exercise_correction_service.correct_exercise(
            user=request.user,
            exercise=exercise,
            user_answer=user_answer
        )
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """Obtenir les soumissions d'un exercice"""
        exercise = self.get_object()
        submissions = ExerciseSubmission.objects.filter(
            exercise=exercise,
            user=request.user
        ).order_by('-submission_time')
        
        data = []
        for submission in submissions:
            data.append({
                'id': submission.id,
                'score': submission.score,
                'is_correct': submission.is_correct,
                'submission_time': submission.submission_time,
                'feedback': submission.feedback,
                'suggestions': submission.suggestions
            })
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def my_progress(self, request):
        """Obtenir les progrès de l'utilisateur"""
        progress = exercise_correction_service.get_user_progress(request.user)
        return Response(progress)
    
    def _evaluate_answer(self, exercise, user_answer):
        """Évalue la réponse de l'utilisateur"""
        # Logique d'évaluation basique
        # Dans un vrai système, cela serait plus sophistiqué
        solution = exercise.solution
        
        if isinstance(solution, dict):
            correct_answer = solution.get('answer', '')
        else:
            correct_answer = str(solution)
        
        # Comparaison simple (à améliorer selon le type d'exercice)
        if isinstance(user_answer, str):
            is_correct = user_answer.lower().strip() == correct_answer.lower().strip()
        else:
            is_correct = str(user_answer) == str(correct_answer)
        
        score = 100 if is_correct else 0
        return is_correct, score
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Obtenir des recommandations d'exercices"""
        serializer = ExerciseRecommendationSerializer(data=request.query_params)
        
        if serializer.is_valid():
            category = serializer.validated_data.get('category')
            limit = serializer.validated_data.get('limit', 5)
            
            # Utiliser le service IA pour les recommandations
            recommendations = exercise_ai_service.get_exercise_recommendations(
                user=request.user,
                category=category,
                limit=limit
            )
            
            serializer = ExerciseListSerializer(recommendations, many=True)
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def generate_ai(self, request):
        """Générer des exercices avec l'IA"""
        serializer = ExerciseGenerationRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            result = exercise_ai_service.generate_exercises(
                user=request.user,
                subject=serializer.validated_data['subject'],
                difficulty=serializer.validated_data['difficulty'],
                exercise_type=serializer.validated_data['exercise_type'],
                count=serializer.validated_data.get('count', 1),
                custom_prompt=serializer.validated_data.get('custom_prompt', ''),
                user_level=serializer.validated_data.get('user_level', ''),
                specific_topics=serializer.validated_data.get('specific_topics', [])
            )
            
            if result['success']:
                exercise_serializer = ExerciseSerializer(result['exercises'], many=True)
                return Response({
                    'success': True,
                    'exercises': exercise_serializer.data,
                    'generation_id': result.get('generation_id'),
                    'processing_time': result.get('processing_time')
                })
            else:
                return Response({
                    'success': False,
                    'error': result['error']
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExerciseAttemptViewSet(viewsets.ReadOnlyModelViewSet):
    """Vue pour les tentatives d'exercices"""
    serializer_class = ExerciseAttemptSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['exercise', 'is_correct']
    ordering_fields = ['started_at', 'score']
    ordering = ['-started_at']
    
    def get_queryset(self):
        """Filtre les tentatives par utilisateur"""
        return ExerciseAttempt.objects.filter(user=self.request.user)

class ExerciseSessionViewSet(viewsets.ModelViewSet):
    """Vue pour les sessions d'exercices"""
    serializer_class = ExerciseSessionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty', 'is_active', 'is_completed']
    ordering_fields = ['created_at', 'total_score']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtre les sessions par utilisateur"""
        return ExerciseSession.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associe la session à l'utilisateur"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Démarrer une session d'exercices"""
        session = self.get_object()
        
        if session.is_active and not session.started_at:
            session.started_at = timezone.now()
            session.save()
            
            return Response({
                'success': True,
                'message': 'Session démarrée',
                'session_id': session.id
            })
        
        return Response({
            'success': False,
            'error': 'Session déjà démarrée ou inactive'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Terminer une session d'exercices"""
        session = self.get_object()
        
        if session.is_active and session.started_at:
            session.is_completed = True
            session.completed_at = timezone.now()
            session.is_active = False
            
            # Calculer le score total
            session_exercises = session.sessionexercise_set.all()
            if session_exercises:
                total_score = sum(se.score for se in session_exercises)
                session.total_score = total_score / len(session_exercises)
                session.completed_exercises = session_exercises.filter(is_completed=True).count()
            
            session.save()
            
            return Response({
                'success': True,
                'message': 'Session terminée',
                'total_score': session.total_score,
                'completed_exercises': session.completed_exercises
            })
        
        return Response({
            'success': False,
            'error': 'Session non démarrée ou déjà terminée'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Obtenir le progrès d'une session"""
        session = self.get_object()
        
        return Response({
            'session_id': session.id,
            'progress_percentage': session.get_progress_percentage(),
            'completed_exercises': session.completed_exercises,
            'total_exercises': session.exercise_count,
            'total_score': session.total_score,
            'is_completed': session.is_completed
        })

class AIExerciseGenerationViewSet(viewsets.ReadOnlyModelViewSet):
    """Vue pour l'historique des générations IA"""
    serializer_class = AIExerciseGenerationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty', 'exercise_type', 'success']
    ordering_fields = ['created_at', 'processing_time']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtre les générations par utilisateur"""
        return AIExerciseGeneration.objects.filter(user=self.request.user)

# Vues pour l'interface utilisateur
@login_required
def exercise_dashboard(request):
    """Page principale des exercices"""
    # Récupérer les données pour les sélecteurs
    categories = ExerciseCategory.objects.all()
    difficulties = DifficultyLevel.objects.all()
    types = ExerciseType.objects.all()
    
    context = {
        'categories': categories,
        'difficulties': difficulties,
        'types': types,
    }
    
    return render(request, 'exercises/base.html', context)

@login_required
def exercise_detail(request, exercise_id):
    """Détail d'un exercice"""
    exercise = get_object_or_404(Exercise, id=exercise_id, is_active=True)
    
    # Vérifier si l'utilisateur peut voir cet exercice
    if not exercise.is_public and exercise.created_by != request.user and not request.user.is_staff:
        return render(request, 'exercises/access_denied.html')
    
    # Récupérer les tentatives de l'utilisateur
    attempts = ExerciseAttempt.objects.filter(user=request.user, exercise=exercise).order_by('-started_at')
    
    context = {
        'exercise': exercise,
        'attempts': attempts,
        'has_attempted': attempts.exists(),
        'best_score': attempts.aggregate(best=Avg('score'))['best'] or 0
    }
    
    return render(request, 'exercises/detail.html', context)

@login_required
def exercise_solve(request, exercise_id):
    """Interface de résolution d'un exercice"""
    exercise = get_object_or_404(Exercise, id=exercise_id, is_active=True)
    
    # Vérifier les permissions
    if not exercise.is_public and exercise.created_by != request.user and not request.user.is_staff:
        return render(request, 'exercises/access_denied.html')
    
    # Vérifier s'il y a déjà une tentative existante
    existing_attempt = ExerciseAttempt.objects.filter(
        user=request.user,
        exercise=exercise
    ).first()
    
    context = {
        'exercise': exercise,
        'attempt': existing_attempt,
        'is_new_attempt': existing_attempt is None
    }
    
    return render(request, 'exercises/solve.html', context)

@login_required
def exercise_results(request, submission_id):
    """Page de résultats d'une soumission"""
    submission = get_object_or_404(ExerciseSubmission, id=submission_id, user=request.user)
    
    # Récupérer les progrès de l'utilisateur
    user_progress = exercise_correction_service.get_user_progress(request.user)
    
    context = {
        'submission': submission,
        'user_progress': user_progress
    }
    
    return render(request, 'exercises/results.html', context)
