#!/usr/bin/env python3
"""
Script de test pour vérifier la qualité des fichiers audio générés
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GenEX.settings')
django.setup()

def test_audio_file(audio_path):
    """Teste un fichier audio"""
    print(f"🔍 Test du fichier: {audio_path}")
    
    if not os.path.exists(audio_path):
        print("❌ Fichier non trouvé")
        return False
    
    file_size = os.path.getsize(audio_path)
    print(f"📏 Taille: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
    
    if file_size < 1000:  # Moins de 1KB
        print("⚠️  Fichier très petit - possiblement corrompu")
        return False
    
    # Tester avec pydub si disponible
    try:
        from pydub import AudioSegment
        
        # Charger le fichier audio
        if audio_path.endswith('.mp3'):
            audio = AudioSegment.from_mp3(audio_path)
        elif audio_path.endswith('.wav'):
            audio = AudioSegment.from_wav(audio_path)
        else:
            print("⚠️  Format non supporté")
            return False
        
        duration = len(audio) / 1000.0  # en secondes
        print(f"⏱️  Durée: {duration:.2f} secondes")
        
        if duration < 1:
            print("⚠️  Audio très court - possiblement corrompu")
            return False
        
        # Vérifier le volume
        volume = audio.dBFS
        print(f"🔊 Volume: {volume:.2f} dBFS")
        
        if volume < -60:
            print("⚠️  Volume très faible")
        
        print("✅ Fichier audio valide")
        return True
        
    except ImportError:
        print("⚠️  pydub non disponible - test basique uniquement")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test audio: {e}")
        return False

def test_audio_directory():
    """Teste tous les fichiers audio dans le dossier"""
    print("🎵 Test des fichiers audio générés")
    print("=" * 50)
    
    audio_dir = "media/course_audio"
    
    if not os.path.exists(audio_dir):
        print(f"❌ Dossier {audio_dir} non trouvé")
        return
    
    files = os.listdir(audio_dir)
    audio_files = [f for f in files if f.endswith(('.mp3', '.wav'))]
    
    if not audio_files:
        print("📁 Aucun fichier audio trouvé")
        return
    
    print(f"📁 {len(audio_files)} fichiers audio trouvés")
    print()
    
    valid_files = 0
    total_duration = 0
    
    for audio_file in audio_files:
        audio_path = os.path.join(audio_dir, audio_file)
        if test_audio_file(audio_path):
            valid_files += 1
            try:
                from pydub import AudioSegment
                if audio_path.endswith('.mp3'):
                    audio = AudioSegment.from_mp3(audio_path)
                elif audio_path.endswith('.wav'):
                    audio = AudioSegment.from_wav(audio_path)
                total_duration += len(audio) / 1000.0
            except:
                pass
        print()
    
    print("=" * 50)
    print(f"📊 RÉSUMÉ:")
    print(f"✅ Fichiers valides: {valid_files}/{len(audio_files)}")
    print(f"⏱️  Durée totale: {total_duration/60:.1f} minutes")
    
    if valid_files == len(audio_files):
        print("🎉 Tous les fichiers audio sont valides!")
    else:
        print("⚠️  Certains fichiers audio ont des problèmes")

def test_audio_generation():
    """Teste la génération d'un fichier audio simple"""
    print("\n🎤 Test de génération audio")
    print("=" * 50)
    
    try:
        from courses.tts_service import TTSService
        
        tts = TTSService()
        
        # Test avec un contenu simple
        test_content = """
        Ceci est un test de génération audio.
        Le système devrait créer un fichier audio valide.
        """
        
        audio_path = tts.generate_section_audio(
            course_id=999,  # ID de test
            section_title="Test Audio",
            content=test_content,
            language="fr"
        )
        
        print(f"🎵 Audio généré: {audio_path}")
        
        if test_audio_file(audio_path):
            print("✅ Test de génération réussi!")
            
            # Nettoyer le fichier de test
            try:
                os.remove(audio_path)
                print("🧹 Fichier de test supprimé")
            except:
                pass
        else:
            print("❌ Test de génération échoué")
            
    except Exception as e:
        print(f"❌ Erreur lors du test de génération: {e}")

def main():
    print("🔊 Test de qualité des fichiers audio")
    print("=" * 60)
    
    # Test du dossier audio
    test_audio_directory()
    
    # Test de génération
    test_audio_generation()
    
    print("\n💡 CONSEILS:")
    print("- Si des fichiers sont corrompus, supprimez-les et régénérez")
    print("- Vérifiez les logs Django pour les erreurs de génération")
    print("- Testez avec un contenu plus court si les fichiers sont trop petits")

if __name__ == "__main__":
    main()
