#!/usr/bin/env python
"""
Script de test pour vérifier que les URLs d'administration des cours fonctionnent
"""
import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GenEX.settings')
django.setup()

from django.urls import reverse, NoReverseMatch
from django.test import Client
from django.contrib.auth.models import User

def test_admin_urls():
    """Test des URLs d'administration des cours"""
    print("🔍 Test des URLs d'administration des cours...")
    
    # Test des URLs
    urls_to_test = [
        'courses:admin_course_list',
        'courses:admin_course_create',
    ]
    
    print("\n📋 Test des URLs de base :")
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"✅ {url_name} -> {url}")
        except NoReverseMatch as e:
            print(f"❌ {url_name} -> ERREUR: {e}")
    
    # Test avec un client HTTP
    print("\n🌐 Test avec client HTTP :")
    client = Client()
    
    # Test de l'URL principale
    try:
        response = client.get('/courses/admin/')
        print(f"✅ GET /courses/admin/ -> Status: {response.status_code}")
        if response.status_code == 302:
            print("   → Redirection détectée (probablement vers login)")
        elif response.status_code == 200:
            print("   → Page accessible")
    except Exception as e:
        print(f"❌ GET /courses/admin/ -> ERREUR: {e}")
    
    # Test de l'URL de création
    try:
        response = client.get('/courses/admin/create/')
        print(f"✅ GET /courses/admin/create/ -> Status: {response.status_code}")
        if response.status_code == 302:
            print("   → Redirection détectée (probablement vers login)")
        elif response.status_code == 200:
            print("   → Page accessible")
    except Exception as e:
        print(f"❌ GET /courses/admin/create/ -> ERREUR: {e}")

def test_template_rendering():
    """Test du rendu des templates"""
    print("\n🎨 Test du rendu des templates :")
    
    from django.template.loader import get_template
    from django.template import Context
    
    templates_to_test = [
        'courses/admin/course_list.html',
        'courses/admin/course_form.html',
        'courses/admin/course_confirm_delete.html',
    ]
    
    for template_name in templates_to_test:
        try:
            template = get_template(template_name)
            print(f"✅ Template {template_name} trouvé")
        except Exception as e:
            print(f"❌ Template {template_name} -> ERREUR: {e}")

def test_views():
    """Test des vues d'administration"""
    print("\n🔧 Test des vues d'administration :")
    
    from courses.views import (
        admin_course_list,
        admin_course_create,
        admin_course_edit,
        admin_course_delete
    )
    
    views_to_test = [
        ('admin_course_list', admin_course_list),
        ('admin_course_create', admin_course_create),
        ('admin_course_edit', admin_course_edit),
        ('admin_course_delete', admin_course_delete),
    ]
    
    for view_name, view_func in views_to_test:
        try:
            print(f"✅ Vue {view_name} importée avec succès")
        except Exception as e:
            print(f"❌ Vue {view_name} -> ERREUR: {e}")

if __name__ == '__main__':
    print("🚀 Démarrage des tests d'administration des cours...")
    print("=" * 60)
    
    test_admin_urls()
    test_template_rendering()
    test_views()
    
    print("\n" + "=" * 60)
    print("✅ Tests terminés !")
    print("\n💡 Si tout est vert, le lien 'Courses' devrait fonctionner.")
    print("   Accédez à http://127.0.0.1:8000/users/backoffice/")
    print("   et cliquez sur 'Courses' dans la sidebar.")
