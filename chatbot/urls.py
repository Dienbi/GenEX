from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.ChatbotView.as_view(), name='chat'),
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
    path('api/session/<int:session_id>/', views.ChatSessionAPIView.as_view(), name='session_api'),
    path('api/upload/', views.upload_file, name='upload_file'),
    path('api/files/<int:session_id>/', views.get_uploaded_files, name='get_files'),
    path('api/generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('api/theme-toggle/', views.ThemeToggleView.as_view(), name='theme_toggle'),
    path('widget/', views.chatbot_widget, name='widget'),
]
