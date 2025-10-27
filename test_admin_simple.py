#!/usr/bin/env python
"""
Script de test simple pour vérifier que les URLs d'administration des cours fonctionnent
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

def test_admin_urls():
    """Test des URLs d'administration des cours"""
    print("Test des URLs d'administration des cours...")
    
    # Test des URLs
    urls_to_test = [
        'courses:admin_course_list',
        'courses:admin_course_create',
    ]
    
    print("\nTest des URLs de base :")
    for url_name in urls_to_test:
        try:
            url = reverse(url_name)
            print(f"OK {url_name} -> {url}")
        except NoReverseMatch as e:
            print(f"ERREUR {url_name} -> {e}")
    
    # Test avec un client HTTP
    print("\nTest avec client HTTP :")
    client = Client()
    
    # Test de l'URL principale
    try:
        response = client.get('/courses/admin/')
        print(f"GET /courses/admin/ -> Status: {response.status_code}")
        if response.status_code == 302:
            print("   -> Redirection detectee (probablement vers login)")
        elif response.status_code == 200:
            print("   -> Page accessible")
    except Exception as e:
        print(f"ERREUR GET /courses/admin/ -> {e}")
    
    # Test de l'URL de creation
    try:
        response = client.get('/courses/admin/create/')
        print(f"GET /courses/admin/create/ -> Status: {response.status_code}")
        if response.status_code == 302:
            print("   -> Redirection detectee (probablement vers login)")
        elif response.status_code == 200:
            print("   -> Page accessible")
    except Exception as e:
        print(f"ERREUR GET /courses/admin/create/ -> {e}")

def test_template_rendering():
    """Test du rendu des templates"""
    print("\nTest du rendu des templates :")
    
    from django.template.loader import get_template
    
    templates_to_test = [
        'courses/admin/course_list.html',
        'courses/admin/course_form.html',
        'courses/admin/course_confirm_delete.html',
    ]
    
    for template_name in templates_to_test:
        try:
            template = get_template(template_name)
            print(f"OK Template {template_name} trouve")
        except Exception as e:
            print(f"ERREUR Template {template_name} -> {e}")

if __name__ == '__main__':
    print("Demarrage des tests d'administration des cours...")
    print("=" * 60)
    
    test_admin_urls()
    test_template_rendering()
    
    print("\n" + "=" * 60)
    print("Tests termines !")
    print("\nSi tout est OK, le lien 'Courses' devrait fonctionner.")
    print("Accedez a http://127.0.0.1:8000/users/backoffice/")
    print("et cliquez sur 'Courses' dans la sidebar.")
