import json
import time
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import ChatSession, ChatMessage, EducationalSubject
from .services import GroqChatService
import logging

logger = logging.getLogger(__name__)


class ChatbotView(LoginRequiredMixin, View):
    """Vue principale du chatbot"""
    
    def get(self, request):
        # Récupérer les sessions de chat de l'utilisateur
        sessions = ChatSession.objects.filter(user=request.user, is_active=True)
        
        # Récupérer les sujets éducatifs
        subjects = EducationalSubject.objects.filter(is_active=True)
        
        context = {
            'sessions': sessions,
            'subjects': subjects,
        }
        return render(request, 'chatbot/chat.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class ChatAPIView(LoginRequiredMixin, View):
    """API pour gérer les messages du chatbot"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id')
            
            if not message:
                return JsonResponse({'error': 'Message vide'}, status=400)
            
            # Récupérer ou créer une session
            if session_id:
                session = get_object_or_404(ChatSession, id=session_id, user=request.user)
            else:
                session = ChatSession.objects.create(
                    user=request.user,
                    title=message[:50] + "..." if len(message) > 50 else message
                )
            
            # Enregistrer le message de l'utilisateur
            user_message = ChatMessage.objects.create(
                session=session,
                message_type='user',
                content=message
            )
            
            # Détecter le sujet éducatif
            detected_subject = self._detect_educational_subject(message)
            if detected_subject:
                user_message.subject_detected = detected_subject
                user_message.save()
            
            # Obtenir la réponse du chatbot
            start_time = time.time()
            chat_service = GroqChatService()
            
            # Récupérer l'historique de la conversation
            conversation_history = self._get_conversation_history(session)
            
            response = chat_service.get_response(message, conversation_history, detected_subject)
            response_time = time.time() - start_time
            
            # Enregistrer la réponse du chatbot
            assistant_message = ChatMessage.objects.create(
                session=session,
                message_type='assistant',
                content=response,
                subject_detected=detected_subject,
                response_time=response_time
            )
            
            return JsonResponse({
                'success': True,
                'response': response,
                'session_id': session.id,
                'message_id': assistant_message.id,
                'response_time': round(response_time, 2)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Données JSON invalides'}, status=400)
        except Exception as e:
            logger.error(f"Erreur dans ChatAPIView: {str(e)}")
            return JsonResponse({'error': 'Erreur interne du serveur'}, status=500)
    
    def _detect_educational_subject(self, message):
        """Détecte le sujet éducatif basé sur le contenu du message"""
        message_lower = message.lower()
        
        subjects = EducationalSubject.objects.filter(is_active=True)
        for subject in subjects:
            for keyword in subject.keyword_list:
                if keyword.lower() in message_lower:
                    return subject.name
        
        return None
    
    def _get_conversation_history(self, session):
        """Récupère l'historique de la conversation"""
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        history = []
        
        for msg in messages:
            role = "user" if msg.message_type == "user" else "assistant"
            history.append({
                "role": role,
                "content": msg.content
            })
        
        return history


@method_decorator(csrf_exempt, name='dispatch')
class ChatSessionAPIView(LoginRequiredMixin, View):
    """API pour gérer les sessions de chat"""
    
    def get(self, request, session_id):
        """Récupérer les messages d'une session"""
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
        
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'type': msg.message_type,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'subject': msg.subject_detected
            })
        
        return JsonResponse({
            'session': {
                'id': session.id,
                'title': session.title,
                'created_at': session.created_at.isoformat()
            },
            'messages': messages_data
        })
    
    def delete(self, request, session_id):
        """Supprimer une session"""
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        session.is_active = False
        session.save()
        
        return JsonResponse({'success': True})


@login_required
def chatbot_widget(request):
    """Widget du chatbot pour la navbar"""
    return render(request, 'chatbot/widget.html')