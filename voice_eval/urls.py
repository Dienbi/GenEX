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
    
    # Web interface
    path('', views.voice_eval_home, name='voice-eval-home'),
    path('record/', views.voice_eval_record, name='voice-eval-record'),
    path('<int:pk>/', views.voice_eval_detail, name='voice-eval-detail'),
]