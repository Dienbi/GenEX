from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.ChatbotView.as_view(), name='chat'),
    path('api/chat/', views.ChatAPIView.as_view(), name='chat_api'),
    path('api/session/<int:session_id>/', views.ChatSessionAPIView.as_view(), name='session_api'),
    path('widget/', views.chatbot_widget, name='widget'),
]
