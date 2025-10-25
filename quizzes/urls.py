from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'quizzes'

# API Router
router = DefaultRouter()
router.register(r'api/quizzes', views.QuizViewSet, basename='quiz-api')
router.register(r'api/attempts', views.QuizAttemptViewSet, basename='attempt-api')

urlpatterns = [
    # Web Views
    path('', views.quiz_home, name='home'),
    path('generate/', views.generate_quiz_view, name='generate'),
    path('take/<int:quiz_id>/', views.take_quiz_view, name='take_quiz'),
    path('submit/<int:quiz_id>/', views.submit_quiz_view, name='submit_quiz'),
    path('results/<int:attempt_id>/', views.quiz_results_view, name='quiz_results'),
    
    # API Routes
    path('', include(router.urls)),
]