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
    
    # 1vs1 Challenge Views
    path('challenge/', views.challenge_home, name='challenge_home'),
    path('challenge/create/', views.create_game_room, name='create_game_room'),
    path('challenge/join/', views.join_game_room, name='join_game_room'),
    path('challenge/room/<str:room_code>/', views.game_room, name='game_room'),
    path('challenge/room/<str:room_code>/results/', views.game_results, name='game_results'),
    path('challenge/my-matches/', views.my_matches, name='my_matches'),
    path('challenge/rematch/<str:room_code>/', views.rematch, name='rematch'),
    
    # 1vs1 Challenge API
    path('api/challenge/room/<str:room_code>/status/', views.api_room_status, name='api_room_status'),
    path('api/challenge/room/<str:room_code>/start/', views.api_start_game, name='api_start_game'),
    path('api/challenge/room/<str:room_code>/answer/', views.api_submit_answer, name='api_submit_answer'),
    
    # API Routes
    path('', include(router.urls)),
]