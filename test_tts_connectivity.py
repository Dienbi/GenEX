#!/usr/bin/env python3
"""
Script de test pour vérifier la connectivité TTS et les options disponibles
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GenEX.settings')
django.setup()

def test_internet_connectivity():
    """Teste la connectivité Internet"""
    print("🌐 Test de connectivité Internet...")
    
    try:
        import urllib.request
        import urllib.error
        
        # Tester la connectivité vers Google
        try:
            urllib.request.urlopen('https://www.google.com', timeout=5)
            print("✅ Connexion Internet OK")
            return True
        except urllib.error.URLError as e:
            print(f"❌ Problème de connectivité Internet: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test de connectivité: {e}")
        return False

def test_gtts():
    """Teste gTTS"""
    print("\n🎤 Test de gTTS...")
    
    try:
        from gtts import gTTS
        
        # Test simple
        tts = gTTS(text="Test de connectivité gTTS", lang='fr', slow=False)
        
        # Créer un fichier temporaire
        temp_file = "test_gtts.mp3"
        tts.save(temp_file)
        
        if os.path.exists(temp_file):
            print("✅ gTTS fonctionne correctement")
            os.remove(temp_file)  # Nettoyer
            return True
        else:
            print("❌ gTTS n'a pas pu créer le fichier")
            return False
            
    except Exception as e:
        print(f"❌ Erreur gTTS: {e}")
        return False

def test_pyttsx3():
    """Teste pyttsx3"""
    print("\n🔊 Test de pyttsx3...")
    
    try:
        import pyttsx3
        
        # Initialiser le moteur
        engine = pyttsx3.init()
        
        # Tester les voix disponibles
        voices = engine.getProperty('voices')
        print(f"📢 Voix disponibles: {len(voices)}")
        
        for i, voice in enumerate(voices[:3]):  # Afficher les 3 premières
            print(f"   {i+1}. {voice.name} ({voice.id})")
        
        # Test de génération
        temp_file = "test_pyttsx3.wav"
        engine.save_to_file("Test de pyttsx3", temp_file)
        engine.runAndWait()
        
        if os.path.exists(temp_file):
            print("✅ pyttsx3 fonctionne correctement")
            os.remove(temp_file)  # Nettoyer
            return True
        else:
            print("❌ pyttsx3 n'a pas pu créer le fichier")
            return False
            
    except Exception as e:
        print(f"❌ Erreur pyttsx3: {e}")
        return False

def test_pydub():
    """Teste pydub"""
    print("\n🎵 Test de pydub...")
    
    try:
        from pydub import AudioSegment
        from pydub.effects import normalize
        
        # Créer un segment audio silencieux
        silence = AudioSegment.silent(duration=1000)  # 1 seconde
        
        # Tester l'export
        temp_file = "test_pydub.wav"
        silence.export(temp_file, format="wav")
        
        if os.path.exists(temp_file):
            print("✅ pydub fonctionne correctement")
            os.remove(temp_file)  # Nettoyer
            return True
        else:
            print("❌ pydub n'a pas pu créer le fichier")
            return False
            
    except Exception as e:
        print(f"❌ Erreur pydub: {e}")
        return False

def test_tts_service():
    """Teste le service TTS complet"""
    print("\n🔧 Test du service TTS...")
    
    try:
        from courses.tts_service import TTSService
        
        tts = TTSService()
        
        # Test de nettoyage de texte
        test_text = "<h1>Test</h1><p>Ceci est un <strong>test</strong>.</p>"
        clean_text = tts.clean_text_for_speech(test_text)
        print(f"✅ Nettoyage de texte: '{clean_text}'")
        
        # Test de division en chunks
        long_text = "Ceci est un texte de test. " * 20
        chunks = tts.split_text_into_chunks(long_text)
        print(f"✅ Division en chunks: {len(chunks)} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur service TTS: {e}")
        return False

def main():
    print("🧪 Test de connectivité et fonctionnalités TTS")
    print("=" * 60)
    
    # Tests de connectivité
    internet_ok = test_internet_connectivity()
    
    # Tests des bibliothèques
    gtts_ok = test_gtts()
    pyttsx3_ok = test_pyttsx3()
    pydub_ok = test_pydub()
    
    # Test du service
    service_ok = test_tts_service()
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS:")
    print(f"🌐 Internet: {'✅ OK' if internet_ok else '❌ KO'}")
    print(f"🎤 gTTS: {'✅ OK' if gtts_ok else '❌ KO'}")
    print(f"🔊 pyttsx3: {'✅ OK' if pyttsx3_ok else '❌ KO'}")
    print(f"🎵 pydub: {'✅ OK' if pydub_ok else '❌ KO'}")
    print(f"🔧 Service TTS: {'✅ OK' if service_ok else '❌ KO'}")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS:")
    
    if not internet_ok:
        print("⚠️  Problème de connectivité Internet - gTTS ne fonctionnera pas")
        print("   Solution: Vérifiez votre connexion Internet ou utilisez pyttsx3")
    
    if not gtts_ok and not pyttsx3_ok:
        print("❌ Aucun moteur TTS ne fonctionne")
        print("   Solution: Installez au moins pyttsx3: pip install pyttsx3")
    elif not gtts_ok:
        print("⚠️  gTTS ne fonctionne pas - utilisation de pyttsx3 (qualité moindre)")
    elif not pyttsx3_ok:
        print("⚠️  pyttsx3 ne fonctionne pas - dépendance totale à gTTS")
    else:
        print("✅ Tous les moteurs TTS fonctionnent - système robuste")
    
    if not pydub_ok:
        print("⚠️  pydub ne fonctionne pas - pas de conversion audio avancée")
    
    # Statut final
    if (gtts_ok or pyttsx3_ok) and service_ok:
        print("\n🎉 Le système TTS est fonctionnel!")
    else:
        print("\n❌ Le système TTS a des problèmes à résoudre")

if __name__ == "__main__":
    main()
