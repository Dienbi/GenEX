#!/usr/bin/env python
"""
Test pour vérifier que les administrateurs peuvent voir les cours individuels
"""
import os
import sys
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GenEX.settings')
django.setup()

from users.middleware import AdminAccessMiddleware

def test_middleware_logic():
    """Test de la logique du middleware pour les cours individuels"""
    print("Test de la logique du middleware pour les cours individuels...")
    
    middleware = AdminAccessMiddleware(lambda req: None)
    
    # URLs à tester
    test_urls = [
        ('/courses/', 'Liste des cours (devrait être restreint)'),
        ('/courses/5/', 'Cours individuel (devrait être autorisé)'),
        ('/courses/5/edit/', 'Édition de cours (devrait être restreint)'),
        ('/courses/admin/', 'Admin des cours (devrait être autorisé)'),
        ('/courses/admin/create/', 'Création de cours (devrait être autorisé)'),
        ('/courses/5/audio/1/', 'Audio de cours (devrait être restreint)'),
    ]
    
    print("\nTest des URLs :")
    for url, description in test_urls:
        # Simuler la logique du middleware
        is_allowed = any(url.startswith(allowed) for allowed in middleware.allowed_paths)
        import re
        is_individual_course = (url.startswith('/courses/') and 
                               url.endswith('/') and 
                               url != '/courses/' and
                               re.match(r'^/courses/\d+/$', url))
        
        # Check if path is restricted (but allow individual courses)
        is_restricted = False
        for restricted in middleware.restricted_paths:
            if url.startswith(restricted):
                # Si c'est /courses/, vérifier si c'est un cours individuel
                if restricted == '/courses/' and is_individual_course:
                    continue  # Ne pas considérer comme restreint
                is_restricted = True
                break
        
        will_redirect = is_restricted and not is_allowed
        
        status = "AUTORISE" if not will_redirect else "REDIRIGE"
        print(f"  {url:<25} -> {status:<10} ({description})")
        
        if is_individual_course:
            print(f"    -> Détecté comme cours individuel: {is_individual_course}")
        
        # Debug pour /courses/5/
        if url == '/courses/5/':
            print(f"    -> Debug: is_allowed={is_allowed}, is_restricted={is_restricted}, is_individual_course={is_individual_course}")
            print(f"    -> restricted_paths: {middleware.restricted_paths}")
            print(f"    -> allowed_paths: {middleware.allowed_paths}")

if __name__ == '__main__':
    print("Test du middleware pour la visualisation des cours...")
    print("=" * 70)
    
    test_middleware_logic()
    
    print("\n" + "=" * 70)
    print("Si 'Cours individuel' est AUTORISE, le lien 'Voir' devrait fonctionner.")
