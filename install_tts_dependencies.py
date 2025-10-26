#!/usr/bin/env python3
"""
Script d'installation des dépendances pour la fonctionnalité Text-to-Speech
"""

import subprocess
import sys
import os

def install_package(package):
    """Installe un package Python"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation de {package}: {e}")
        return False

def main():
    print("🎤 Installation des dépendances Text-to-Speech...")
    print("=" * 50)
    
    # Liste des packages requis
    packages = [
        "pyttsx3>=2.90",
        "gTTS>=2.3.0", 
        "pydub>=0.25.1",
        "pygame>=2.1.0"  # Pour la lecture audio
    ]
    
    success_count = 0
    
    for package in packages:
        print(f"📦 Installation de {package}...")
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Résultat: {success_count}/{len(packages)} packages installés")
    
    if success_count == len(packages):
        print("🎉 Toutes les dépendances TTS ont été installées avec succès!")
        print("\n📋 Prochaines étapes:")
        print("1. Redémarrez votre serveur Django")
        print("2. Testez la fonctionnalité 'Podcast Audio' dans un cours")
        print("3. Vérifiez que les fichiers audio sont générés dans media/course_audio/")
    else:
        print("⚠️  Certaines dépendances n'ont pas pu être installées.")
        print("Veuillez les installer manuellement:")
        for package in packages:
            print(f"   pip install {package}")
    
    print("\n🔧 Configuration système requise:")
    print("- Python 3.7+")
    print("- Connexion Internet (pour gTTS)")
    print("- Espace disque suffisant pour les fichiers audio")
    print("- Navigateur supportant HTML5 Audio")

if __name__ == "__main__":
    main()
