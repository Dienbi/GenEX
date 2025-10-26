#!/usr/bin/env python3
"""
Script de test pour la fonctionnalité Text-to-Speech
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GenEX.settings')
django.setup()

from courses.tts_service import TTSService
from courses.models import Course

def test_tts_service():
    """Teste le service TTS"""
    print("🧪 Test du service TTS...")
    
    try:
        # Initialiser le service
        tts = TTSService()
        print("✅ Service TTS initialisé")
        
        # Tester le nettoyage de texte
        test_text = "<h1>Introduction</h1><p>Ceci est un <strong>test</strong> de TTS.</p>"
        clean_text = tts.clean_text_for_speech(test_text)
        print(f"✅ Nettoyage de texte: '{clean_text}'")
        
        # Tester la division en chunks
        long_text = "Ceci est un texte très long. " * 50
        chunks = tts.split_text_into_chunks(long_text)
        print(f"✅ Division en chunks: {len(chunks)} chunks générés")
        
        # Tester la génération de nom de fichier
        filename = tts.generate_audio_filename(1, "Test Section", "fr")
        print(f"✅ Nom de fichier généré: {filename}")
        
        # Tester les langues disponibles
        languages = tts.get_available_languages()
        print(f"✅ Langues disponibles: {languages}")
        
        print("🎉 Tous les tests du service TTS ont réussi!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test TTS: {e}")
        return False

def test_course_audio_generation():
    """Teste la génération d'audio pour un cours"""
    print("\n🎤 Test de génération d'audio pour un cours...")
    
    try:
        # Chercher un cours existant
        course = Course.objects.first()
        if not course:
            print("⚠️  Aucun cours trouvé. Créez d'abord un cours.")
            return False
        
        print(f"📚 Test avec le cours: {course.title}")
        
        # Initialiser le service TTS
        tts = TTSService()
        
        # Tester la génération d'audio avec un texte simple
        test_content = """
        Introduction à la programmation Python.
        Python est un langage de programmation puissant et facile à apprendre.
        Il est utilisé dans de nombreux domaines comme le développement web, 
        la science des données, et l'intelligence artificielle.
        """
        
        audio_path = tts.generate_section_audio(
            course_id=course.pk,
            section_title="Test Audio",
            content=test_content,
            language=course.language
        )
        
        if audio_path and os.path.exists(audio_path):
            print(f"✅ Audio généré avec succès: {audio_path}")
            
            # Tester les informations audio
            audio_info = tts.get_audio_info(audio_path)
            if audio_info:
                print(f"✅ Informations audio: {audio_info}")
            
            # Tester l'URL
            audio_url = tts.get_audio_url(audio_path)
            print(f"✅ URL audio: {audio_url}")
            
            print("🎉 Test de génération d'audio réussi!")
            return True
        else:
            print("❌ Échec de la génération d'audio")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de génération: {e}")
        return False

def test_dependencies():
    """Teste les dépendances requises"""
    print("📦 Test des dépendances...")
    
    dependencies = [
        ('gtts', 'gTTS'),
        ('pydub', 'pydub'),
        ('pygame', 'pygame')
    ]
    
    all_ok = True
    
    for module_name, display_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {display_name} disponible")
        except ImportError:
            print(f"❌ {display_name} manquant - installez avec: pip install {module_name}")
            all_ok = False
    
    return all_ok

def main():
    print("🎤 Test de la fonctionnalité Text-to-Speech")
    print("=" * 50)
    
    # Test des dépendances
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Certaines dépendances sont manquantes.")
        print("Installez-les avec: python install_tts_dependencies.py")
        return
    
    # Test du service TTS
    service_ok = test_tts_service()
    
    if not service_ok:
        print("\n❌ Le service TTS a des problèmes.")
        return
    
    # Test de génération d'audio
    audio_ok = test_course_audio_generation()
    
    print("\n" + "=" * 50)
    if service_ok and audio_ok:
        print("🎉 Tous les tests ont réussi!")
        print("La fonctionnalité TTS est prête à être utilisée.")
    else:
        print("⚠️  Certains tests ont échoué.")
        print("Vérifiez les erreurs ci-dessus.")

if __name__ == "__main__":
    main()
