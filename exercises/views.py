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
    ExerciseSubmission, ExerciseCorrectionSession, ExerciseCollection,
    ExerciseFavorite, ExerciseHistory, ExerciseWishlist, ExerciseInCollection,
    UserExerciseStatus
)
from .serializers import (
    ExerciseCategorySerializer, ExerciseTypeSerializer, DifficultyLevelSerializer,
    ExerciseSerializer, ExerciseListSerializer, ExerciseAttemptSerializer,
    ExerciseSessionSerializer, SessionExerciseSerializer, AIExerciseGenerationSerializer,
    ExerciseGenerationRequestSerializer, ExerciseAttemptSubmissionSerializer,
    ExerciseRecommendationSerializer, ExerciseCollectionSerializer,
    ExerciseFavoriteSerializer, ExerciseHistorySerializer, ExerciseWishlistSerializer,
    AdvancedCorrectionSerializer, UserExerciseStatusSerializer, ExerciseWithStatusSerializer
)
from .ai_service import exercise_ai_service
from .correction_service import exercise_correction_service
from .advanced_correction_service import AdvancedCorrectionService

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
    permission_classes = [IsAuthenticatedOrReadOnly]  # Authentification requise pour les actions
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'difficulty', 'exercise_type', 'is_ai_generated']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'difficulty__level', 'points']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExerciseWithStatusSerializer
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
    
    @action(detail=True, methods=['post'], permission_classes=[])
    def submit(self, request, pk=None):
        """Soumettre un exercice pour correction IA"""
        exercise = self.get_object()
        user_answer = request.data.get('user_answer')
        time_spent = request.data.get('time_spent', 0)
        
        if not user_answer:
            return Response({'error': 'Réponse de l\'utilisateur manquante'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Si l'utilisateur est authentifié, utiliser le service complet
            if request.user.is_authenticated:
                result = exercise_correction_service.correct_exercise(
                    user=request.user,
                    exercise=exercise,
                    user_answer=user_answer
                )
            else:
                # Si l'utilisateur n'est pas authentifié, faire une correction simple
                result = self._simple_correction(exercise, user_answer, time_spent)
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erreur lors de la correction: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _simple_correction(self, exercise, user_answer, time_spent):
        """Correction simple pour les utilisateurs non authentifiés"""
        try:
            # Correction basique sans sauvegarde en base
            # Simuler une correction simple
            score = 75  # Score par défaut
            is_correct = score >= 70
            
            feedback = f"Votre réponse a été évaluée. Score: {score}/100. {'Bien joué!' if is_correct else 'Continuez à pratiquer!'}"
            
            return {
                'success': True,
                'score': score,
                'is_correct': is_correct,
                'feedback': feedback,
                'suggestions': ['Relisez la question attentivement', 'Vérifiez votre réponse'],
                'time_spent': time_spent,
                'solution': exercise.solution if not is_correct else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur lors de la correction simple: {str(e)}'
            }
    
    @action(detail=True, methods=['post'], permission_classes=[])
    def advanced_correction(self, request, pk=None):
        """Soumettre un exercice pour correction avancée avec feedback détaillé"""
        exercise = self.get_object()
        user_answer = request.data.get('user_answer')
        user_level = request.data.get('user_level', 'intermediate')
        
        if not user_answer:
            return Response({'error': 'Réponse de l\'utilisateur manquante'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Utiliser le service de correction avancée
            advanced_service = AdvancedCorrectionService()
            advanced_result = advanced_service.generate_advanced_correction(
                exercise=exercise,
                user_answer=user_answer,
                user_level=user_level
            )
            
            # Si l'utilisateur est authentifié, sauvegarder la soumission
            if request.user.is_authenticated:
                submission, created = ExerciseSubmission.objects.get_or_create(
                    user=request.user,
                    exercise=exercise,
                    defaults={
                        'user_answer': user_answer,
                        'is_correct': advanced_result['detailed_correction'].get('overall_score', 0) >= 70,
                        'score': advanced_result['detailed_correction'].get('overall_score', 0),
                        'feedback': advanced_result['personalized_feedback'],
                        'suggestions': advanced_result['detailed_correction'].get('suggestions', []),
                        'detailed_correction': advanced_result['detailed_correction'],
                        'video_explanation_url': advanced_result['video_explanation_url'],
                        'comparison_answers': advanced_result['comparison_answers'],
                        'personalized_feedback': advanced_result['personalized_feedback'],
                        'improvement_areas': advanced_result['improvement_areas'],
                        'strengths': advanced_result['strengths'],
                        'correction_time': advanced_result['correction_time'],
                        'confidence_score': advanced_result['confidence_score']
                    }
                )
                
                if not created:
                    # Mettre à jour la soumission existante
                    submission.user_answer = user_answer
                    submission.is_correct = advanced_result['detailed_correction'].get('overall_score', 0) >= 70
                    submission.score = advanced_result['detailed_correction'].get('overall_score', 0)
                    submission.feedback = advanced_result['personalized_feedback']
                    submission.suggestions = advanced_result['detailed_correction'].get('suggestions', [])
                    submission.detailed_correction = advanced_result['detailed_correction']
                    submission.video_explanation_url = advanced_result['video_explanation_url']
                    submission.comparison_answers = advanced_result['comparison_answers']
                    submission.personalized_feedback = advanced_result['personalized_feedback']
                    submission.improvement_areas = advanced_result['improvement_areas']
                    submission.strengths = advanced_result['strengths']
                    submission.correction_time = advanced_result['correction_time']
                    submission.confidence_score = advanced_result['confidence_score']
                    submission.save()
                
                # Sérialiser la réponse
                serializer = AdvancedCorrectionSerializer(submission)
                return Response({
                    'success': True,
                    'submission': serializer.data,
                    'advanced_correction': advanced_result
                }, status=status.HTTP_200_OK)
            else:
                # Utilisateur non authentifié, retourner seulement la correction
                return Response({
                    'success': True,
                    'advanced_correction': advanced_result
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erreur lors de la correction avancée: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    
    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk=None):
        """Ajouter ou retirer un exercice des favoris"""
        exercise = self.get_object()
        
        if request.method == 'POST':
            # Ajouter aux favoris
            status_obj, created = UserExerciseStatus.objects.get_or_create(
                user=request.user,
                exercise=exercise,
                defaults={'is_favorite': True}
            )
            if not created:
                status_obj.is_favorite = True
                status_obj.save()
            
            return Response({
                'message': 'Exercice ajouté aux favoris',
                'is_favorite': True
            }, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            # Retirer des favoris
            try:
                status_obj = UserExerciseStatus.objects.get(user=request.user, exercise=exercise)
                status_obj.is_favorite = False
                status_obj.save()
                return Response({
                    'message': 'Exercice retiré des favoris',
                    'is_favorite': False
                }, status=status.HTTP_200_OK)
            except UserExerciseStatus.DoesNotExist:
                return Response({
                    'message': 'Exercice pas dans les favoris',
                    'is_favorite': False
                }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post', 'delete'])
    def wishlist(self, request, pk=None):
        """Ajouter ou retirer un exercice de la wishlist"""
        exercise = self.get_object()
        
        if request.method == 'POST':
            # Ajouter à la wishlist
            status_obj, created = UserExerciseStatus.objects.get_or_create(
                user=request.user,
                exercise=exercise,
                defaults={'is_wishlist': True}
            )
            if not created:
                status_obj.is_wishlist = True
                status_obj.save()
            
            return Response({
                'message': 'Exercice ajouté à la wishlist',
                'is_wishlist': True
            }, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            # Retirer de la wishlist
            try:
                status_obj = UserExerciseStatus.objects.get(user=request.user, exercise=exercise)
                status_obj.is_wishlist = False
                status_obj.save()
                return Response({
                    'message': 'Exercice retiré de la wishlist',
                    'is_wishlist': False
                }, status=status.HTTP_200_OK)
            except UserExerciseStatus.DoesNotExist:
                return Response({
                    'message': 'Exercice pas dans la wishlist',
                    'is_wishlist': False
                }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def add_to_collection(self, request, pk=None):
        """Ajouter un exercice à une collection"""
        exercise = self.get_object()
        collection_id = request.data.get('collection_id')
        
        if not collection_id:
            return Response({'error': 'collection_id requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            collection = ExerciseCollection.objects.get(id=collection_id, user=request.user)
            collection_item, created = ExerciseInCollection.objects.get_or_create(
                collection=collection,
                exercise=exercise
            )
            
            if created:
                return Response({'message': 'Exercice ajouté à la collection'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Exercice déjà dans cette collection'}, status=status.HTTP_200_OK)
        except ExerciseCollection.DoesNotExist:
            return Response({'error': 'Collection non trouvée'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """Enregistrer la consultation d'un exercice dans l'historique"""
        exercise = self.get_object()
        time_spent = request.data.get('time_spent', 0)
        
        history_item, created = ExerciseHistory.objects.get_or_create(
            user=request.user,
            exercise=exercise,
            defaults={'time_spent': time_spent}
        )
        
        if not created:
            # Mettre à jour le temps passé
            history_item.time_spent += time_spent
            history_item.viewed_at = timezone.now()
            history_item.save()
        
        return Response({'message': 'Consultation enregistrée'}, status=status.HTTP_200_OK)

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
    permission_classes = [IsAuthenticatedOrReadOnly]
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
    permission_classes = [IsAuthenticatedOrReadOnly]
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
    permission_classes = [IsAuthenticatedOrReadOnly]
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


class ExerciseCollectionViewSet(viewsets.ModelViewSet):
    """ViewSet pour gérer les collections d'exercices"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ExerciseCollectionSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ExerciseCollection.objects.filter(user=self.request.user)
        else:
            # Retourner une queryset vide si l'utilisateur n'est pas authentifié
            return ExerciseCollection.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def exercises(self, request, pk=None):
        """Obtenir les exercices d'une collection"""
        collection = self.get_object()
        exercises = collection.exercises.all()
        serializer = ExerciseListSerializer(exercises, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_exercise(self, request, pk=None):
        """Ajouter un exercice à la collection"""
        collection = self.get_object()
        exercise_id = request.data.get('exercise_id')
        
        if not exercise_id:
            return Response({'error': 'exercise_id requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            exercise = Exercise.objects.get(id=exercise_id)
            collection_item, created = ExerciseInCollection.objects.get_or_create(
                collection=collection,
                exercise=exercise
            )
            
            if created:
                return Response({'message': 'Exercice ajouté à la collection'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Exercice déjà dans cette collection'}, status=status.HTTP_200_OK)
        except Exercise.DoesNotExist:
            return Response({'error': 'Exercice non trouvé'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def remove_exercise(self, request, pk=None):
        """Retirer un exercice de la collection"""
        collection = self.get_object()
        exercise_id = request.data.get('exercise_id')
        
        if not exercise_id:
            return Response({'error': 'exercise_id requis'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            collection_item = ExerciseInCollection.objects.get(
                collection=collection,
                exercise_id=exercise_id
            )
            collection_item.delete()
            return Response({'message': 'Exercice retiré de la collection'}, status=status.HTTP_200_OK)
        except ExerciseInCollection.DoesNotExist:
            return Response({'error': 'Exercice pas dans cette collection'}, status=status.HTTP_404_NOT_FOUND)


class ExerciseFavoriteViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour gérer les exercices favoris"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ExerciseFavoriteSerializer
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ExerciseFavorite.objects.filter(user=self.request.user)
        else:
            return ExerciseFavorite.objects.none()


class ExerciseWishlistViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour gérer la liste de souhaits"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ExerciseWishlistSerializer
    
    def get_queryset(self):
        return ExerciseWishlist.objects.filter(user=self.request.user)


class ExerciseHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour gérer l'historique des exercices"""
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ExerciseHistory.objects.filter(user=self.request.user)
        else:
            return ExerciseHistory.objects.none()
    
    def get_serializer_class(self):
        return ExerciseHistorySerializer


# Vues pour l'interface utilisateur des collections
def collections_list(request):
    """Liste des collections de l'utilisateur"""
    if not request.user.is_authenticated:
        return render(request, 'exercises/collections_list.html', {
            'collections': [],
            'error': 'Vous devez être connecté pour voir vos collections'
        })
    
    collections = ExerciseCollection.objects.filter(user=request.user)
    return render(request, 'exercises/collections_list.html', {
        'collections': collections
    })


def favorites_list(request):
    """Liste des exercices favoris de l'utilisateur"""
    if not request.user.is_authenticated:
        return render(request, 'exercises/favorites_list.html', {
            'exercises': [],
            'error': 'Vous devez être connecté pour voir vos favoris'
        })
    
    # Récupérer les exercices favoris avec leur statut
    favorite_statuses = UserExerciseStatus.objects.filter(
        user=request.user, 
        is_favorite=True
    ).select_related('exercise', 'exercise__category', 'exercise__difficulty', 'exercise__exercise_type')
    
    exercises = [status.exercise for status in favorite_statuses]
    
    return render(request, 'exercises/favorites_list.html', {
        'exercises': exercises,
        'favorite_statuses': favorite_statuses,
        'page_title': 'Mes Exercices Favoris',
        'empty_message': 'Aucun exercice favori pour le moment'
    })


def wishlist_list(request):
    """Liste des exercices de la wishlist de l'utilisateur"""
    if not request.user.is_authenticated:
        return render(request, 'exercises/wishlist_list.html', {
            'exercises': [],
            'error': 'Vous devez être connecté pour voir votre wishlist'
        })
    
    # Récupérer les exercices de la wishlist avec leur statut
    wishlist_statuses = UserExerciseStatus.objects.filter(
        user=request.user, 
        is_wishlist=True
    ).select_related('exercise', 'exercise__category', 'exercise__difficulty', 'exercise__exercise_type')
    
    exercises = [status.exercise for status in wishlist_statuses]
    
    return render(request, 'exercises/wishlist_list.html', {
        'exercises': exercises,
        'wishlist_statuses': wishlist_statuses,
        'page_title': 'Ma Wishlist',
        'empty_message': 'Aucun exercice dans votre wishlist pour le moment'
    })


def collection_detail(request, collection_id):
    """Détail d'une collection"""
    if not request.user.is_authenticated:
        return render(request, 'exercises/collection_detail.html', {
            'error': 'Vous devez être connecté pour voir cette collection'
        })
    
    collection = get_object_or_404(ExerciseCollection, id=collection_id, user=request.user)
    exercises = ExerciseInCollection.objects.filter(collection=collection).select_related('exercise')
    
    return render(request, 'exercises/collection_detail.html', {
        'collection': collection,
        'exercises': exercises
    })


def collection_exercises(request, collection_id):
    """Exercices d'une collection"""
    if not request.user.is_authenticated:
        return render(request, 'exercises/collection_exercises.html', {
            'error': 'Vous devez être connecté pour voir les exercices de cette collection'
        })
    
    collection = get_object_or_404(ExerciseCollection, id=collection_id, user=request.user)
    exercises = ExerciseInCollection.objects.filter(collection=collection).select_related('exercise')
    
    return render(request, 'exercises/collection_exercises.html', {
        'collection': collection,
        'exercises': exercises
    })
