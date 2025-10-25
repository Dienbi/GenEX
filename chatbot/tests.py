from django.test import TestCase, Client
from django.urls import reverse
from .models import ChatSession, ChatMessage
from users.models import User
import json


class ChatDeleteTestCase(TestCase):
    """Tests pour la fonctionnalité de suppression de chat"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.force_login(self.user)
        
        # Créer une session de test
        self.session = ChatSession.objects.create(
            user=self.user,
            title="Test Session",
            is_active=True
        )
        
        # Créer quelques messages
        ChatMessage.objects.create(
            session=self.session,
            message_type='user',
            content="Message de test"
        )
        
        ChatMessage.objects.create(
            session=self.session,
            message_type='assistant',
            content="Réponse de test"
        )
    
    def test_delete_session_api(self):
        """Test de l'API de suppression de session"""
        # Vérifier que la session existe et est active
        self.assertTrue(self.session.is_active)
        self.assertEqual(self.session.messages.count(), 2)
        
        # Appeler l'API de suppression
        response = self.client.delete(
            reverse('chatbot:delete_session', args=[self.session.id])
        )
        
        # Vérifier la réponse
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        # Vérifier que la session est marquée comme inactive
        self.session.refresh_from_db()
        self.assertFalse(self.session.is_active)
        
        # Vérifier que les messages existent toujours (soft delete)
        self.assertEqual(self.session.messages.count(), 2)
    
    def test_delete_nonexistent_session(self):
        """Test de suppression d'une session inexistante"""
        response = self.client.delete(
            reverse('chatbot:delete_session', args=[99999])
        )
        self.assertEqual(response.status_code, 404)
    
    def test_delete_session_unauthorized(self):
        """Test de suppression d'une session d'un autre utilisateur"""
        # Créer un autre utilisateur
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Créer une session pour l'autre utilisateur
        other_session = ChatSession.objects.create(
            user=other_user,
            title="Other Session",
            is_active=True
        )
        
        # Essayer de supprimer la session de l'autre utilisateur
        response = self.client.delete(
            reverse('chatbot:delete_session', args=[other_session.id])
        )
        
        # Doit retourner 404 (session non trouvée pour cet utilisateur)
        self.assertEqual(response.status_code, 404)
    
    def test_session_list_excludes_inactive(self):
        """Test que les sessions inactives n'apparaissent pas dans la liste"""
        # Marquer la session comme inactive
        self.session.is_active = False
        self.session.save()
        
        # Accéder à la page principale
        response = self.client.get(reverse('chatbot:chat'))
        
        # Vérifier que la session inactive n'apparaît pas dans le contexte
        self.assertEqual(response.status_code, 200)
        sessions = response.context['sessions']
        self.assertEqual(len(sessions), 0)
