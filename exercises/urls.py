from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'exercises'

router = DefaultRouter()
router.register(r'categories', views.ExerciseCategoryViewSet, basename='exercise-category')
router.register(r'types', views.ExerciseTypeViewSet, basename='exercise-type')
router.register(r'difficulties', views.DifficultyLevelViewSet, basename='difficulty-level')
router.register(r'exercises', views.ExerciseViewSet, basename='exercise')
router.register(r'attempts', views.ExerciseAttemptViewSet, basename='exercise-attempt')
router.register(r'sessions', views.ExerciseSessionViewSet, basename='exercise-session')
router.register(r'ai-generations', views.AIExerciseGenerationViewSet, basename='ai-generation')

urlpatterns = [
    # Interface utilisateur
    path('', views.exercise_dashboard, name='exercise-dashboard'),
    path('<int:exercise_id>/', views.exercise_detail, name='exercise-detail'),
    path('<int:exercise_id>/solve/', views.exercise_solve, name='exercise-solve'),
    path('results/<int:submission_id>/', views.exercise_results, name='exercise-results'),
    
    # API
    path('api/', include(router.urls)),
]