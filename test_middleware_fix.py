#!/usr/bin/env python
"""
Script de test pour vérifier que le middleware permet l'accès aux URLs d'administration des cours
"""
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GenEX.settings')
django.setup()

from django.test import Client, RequestFactory
from users.models import User
from users.middleware import AdminAccessMiddleware

def test_middleware():
    """Test du middleware AdminAccessMiddleware"""
    print("Test du middleware AdminAccessMiddleware...")
    
    # Créer un utilisateur admin de test
    admin_user, created = User.objects.get_or_create(
        username='test_admin',
        defaults={
            'is_superuser': True,
            'is_staff': True,
            'user_type': 'admin'
        }
    )
    
    # Créer un client de test
    client = Client()
    client.force_login(admin_user)
    
    # URLs à tester
    test_urls = [
        ('/courses/admin/', 'Administration des cours'),
        ('/courses/admin/create/', 'Création de cours'),
        ('/backoffice/', 'Backoffice'),
    ]
    
    print("\nTest des URLs pour utilisateur admin :")
    for url, description in test_urls:
        try:
            response = client.get(url)
            status = response.status_code
            if status == 200:
                print(f"✅ {url} ({description}) -> Status: {status} - OK")
            elif status == 302:
                redirect_url = response.url
                print(f"⚠️  {url} ({description}) -> Status: {status} - Redirection vers: {redirect_url}")
            else:
                print(f"❌ {url} ({description}) -> Status: {status} - ERREUR")
        except Exception as e:
            print(f"❌ {url} ({description}) -> ERREUR: {e}")
    
    # Test direct du middleware
    print("\nTest direct du middleware :")
    factory = RequestFactory()
    middleware = AdminAccessMiddleware(lambda req: None)
    
    # Simuler une requête vers /courses/admin/
    request = factory.get('/courses/admin/')
    request.user = admin_user
    
    try:
        response = middleware(request)
        if hasattr(response, 'url'):
            print(f"⚠️  Middleware redirige vers: {response.url}")
        else:
            print("✅ Middleware permet l'accès")
    except Exception as e:
        print(f"❌ Erreur middleware: {e}")

def test_regular_user():
    """Test avec un utilisateur normal"""
    print("\nTest avec utilisateur normal :")
    
    # Créer un utilisateur normal
    regular_user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'user_type': 'student'}
    )
    
    client = Client()
    client.force_login(regular_user)
    
    try:
        response = client.get('/courses/admin/')
        status = response.status_code
        if status == 200:
            print("✅ Utilisateur normal peut accéder à l'administration des cours")
        elif status == 302:
            print("⚠️  Utilisateur normal redirigé (normal si pas d'authentification requise)")
        else:
            print(f"❌ Status inattendu: {status}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    print("Démarrage des tests du middleware...")
    print("=" * 60)
    
    test_middleware()
    test_regular_user()
    
    print("\n" + "=" * 60)
    print("Tests terminés !")
    print("\nSi le middleware fonctionne correctement,")
    print("le lien 'Courses' devrait maintenant fonctionner.")
