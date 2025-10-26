# 🔧 Guide de dépannage TTS

## 🚨 Problème : "Failed to connect. Probable cause: Unknown"

Cette erreur indique que gTTS ne peut pas se connecter à Google pour générer l'audio.

### 🔍 Diagnostic

Exécutez le script de diagnostic :

```bash
python test_tts_connectivity.py
```

### 🛠️ Solutions

#### **Solution 1 : Vérifier la connectivité Internet**

```bash
# Tester la connectivité
ping google.com
ping translate.google.com
```

Si pas de connectivité :
- Vérifiez votre connexion Internet
- Vérifiez les paramètres de proxy/firewall
- Essayez un autre réseau

#### **Solution 2 : Utiliser pyttsx3 (TTS local)**

Si gTTS ne fonctionne pas, le système basculera automatiquement vers pyttsx3 :

```bash
# Installer pyttsx3
pip install pyttsx3

# Tester
python -c "import pyttsx3; engine = pyttsx3.init(); print('pyttsx3 OK')"
```

#### **Solution 3 : Configuration proxy (si applicable)**

Si vous êtes derrière un proxy :

```python
# Dans courses/tts_service.py, ajouter :
import os
os.environ['HTTP_PROXY'] = 'http://proxy:port'
os.environ['HTTPS_PROXY'] = 'http://proxy:port'
```

#### **Solution 4 : Désactiver temporairement gTTS**

Si vous voulez forcer l'utilisation de pyttsx3 :

```python
# Dans courses/tts_service.py, modifier :
GTTS_AVAILABLE = False  # Forcer pyttsx3
```

## 🎤 Problèmes courants

### **1. "Service TTS non disponible"**

```bash
# Installer toutes les dépendances
pip install pyttsx3 gTTS pydub pygame
```

### **2. "Aucune voix disponible" (pyttsx3)**

**Windows :**
```bash
# Installer les voix Windows
# Les voix sont généralement incluses avec Windows
```

**Linux :**
```bash
# Installer espeak
sudo apt-get install espeak espeak-data

# Ou festival
sudo apt-get install festival
```

**macOS :**
```bash
# Les voix sont incluses avec macOS
# Vérifier : say -v ?
```

### **3. "Erreur de conversion audio"**

```bash
# Installer ffmpeg (requis pour pydub)
# Windows
# Télécharger depuis https://ffmpeg.org/

# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### **4. "Fichier audio non trouvé"**

Vérifiez les permissions :

```bash
# Créer le dossier avec les bonnes permissions
mkdir -p media/course_audio
chmod 755 media/course_audio
```

## 🔄 Test de fonctionnement

### **Test rapide**

```python
# Dans le shell Django
python manage.py shell

from courses.tts_service import TTSService
tts = TTSService()

# Test simple
try:
    audio_path = tts.generate_section_audio(
        course_id=1,
        section_title="Test",
        content="Ceci est un test de génération audio.",
        language="fr"
    )
    print(f"✅ Audio généré: {audio_path}")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

### **Test complet**

```bash
python test_tts_connectivity.py
```

## 📊 Statuts possibles

| gTTS | pyttsx3 | Statut | Qualité | Recommandation |
|------|---------|--------|---------|----------------|
| ✅ | ✅ | Optimal | Excellente | Utilisez gTTS |
| ❌ | ✅ | Fonctionnel | Bonne | Utilisez pyttsx3 |
| ✅ | ❌ | Risqué | Excellente | Dépendant d'Internet |
| ❌ | ❌ | Non fonctionnel | - | Installez au moins pyttsx3 |

## 🚀 Optimisations

### **Pour une meilleure qualité avec pyttsx3 :**

```python
# Dans _generate_with_pyttsx3, ajuster :
engine.setProperty('rate', 120)  # Plus lent = plus clair
engine.setProperty('volume', 1.0)  # Volume maximum
```

### **Pour une meilleure connectivité gTTS :**

```python
# Ajouter des timeouts et retry
import time
import requests

def robust_gtts_generation(text, lang):
    for attempt in range(3):
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            return tts
        except Exception as e:
            if attempt < 2:
                time.sleep(2)  # Attendre 2 secondes
                continue
            raise e
```

## 📞 Support

Si les problèmes persistent :

1. **Vérifiez les logs Django** : `python manage.py runserver` et regardez la console
2. **Testez les dépendances** : `python test_tts_connectivity.py`
3. **Vérifiez les permissions** : Dossier `media/course_audio/`
4. **Testez avec un cours simple** : Contenu court et simple

## 🔧 Configuration avancée

### **Variables d'environnement**

```bash
# Désactiver gTTS
export DISABLE_GTTS=true

# Forcer pyttsx3
export FORCE_PYTTSX3=true

# Debug TTS
export TTS_DEBUG=true
```

### **Configuration Django**

```python
# Dans settings.py
TTS_SETTINGS = {
    'USE_GTTS': True,
    'USE_PYTTSX3': True,
    'FALLBACK_TO_PYTTSX3': True,
    'AUDIO_QUALITY': 'high',  # high, medium, low
    'CACHE_DURATION': 86400,  # 24 heures
}
```

---

**Note** : Le système TTS est conçu pour être robuste avec un fallback automatique de gTTS vers pyttsx3 en cas de problème de connectivité.
