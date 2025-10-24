from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'voice_eval'

# API router
router = DefaultRouter()
router.register(r'evaluations', views.VoiceEvaluationViewSet, basename='voice-evaluation')
router.register(r'references', views.ReferenceTextViewSet, basename='reference-text')

# Web + API URLs
urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    path('api/languages/', views.get_supported_languages, name='supported-languages'),
    path('api/pronunciation/process/', views.process_pronunciation_api, name='process-pronunciation'),
    
    # Web interface
    path('', views.voice_eval_home, name='home'),
    path('record/', views.voice_eval_record, name='record'),
    path('<int:pk>/', views.voice_eval_detail, name='detail'),
    
    # Certificate features (high scores)
    path('<int:evaluation_id>/certificate/', views.generate_certificate_view, name='generate-certificate'),
    path('<int:evaluation_id>/certificate/map/', views.certificate_map_view, name='certificate-map'),
    
    # Practice features (low scores)
    path('practice/', views.pronunciation_practice_view, name='pronunciation-practice'),
    path('<int:evaluation_id>/practice/', views.pronunciation_practice_view, name='pronunciation-practice-eval'),
    path('<int:evaluation_id>/recommendations/', views.app_recommendations_view, name='app-recommendations'),
    path('sound-practice/', views.sound_practice_view, name='sound-practice'),
]