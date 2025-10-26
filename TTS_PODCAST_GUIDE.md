# 🎤 Guide de la fonctionnalité Podcast Audio (Text-to-Speech)

## 📋 Vue d'ensemble

La fonctionnalité **Podcast Audio** permet de convertir automatiquement chaque chapitre de cours en audio, créant ainsi des podcasts éducatifs. Cette fonctionnalité utilise la technologie Text-to-Speech (TTS) pour générer des fichiers audio de haute qualité.

## 🚀 Installation

### 1. Installer les dépendances

```bash
# Exécuter le script d'installation automatique
python install_tts_dependencies.py

# Ou installer manuellement
pip install pyttsx3>=2.90 gTTS>=2.3.0 pydub>=0.25.1 pygame>=2.1.0
```

### 2. Vérifier l'installation

```python
# Tester dans le shell Django
python manage.py shell

# Importer et tester
from courses.tts_service import TTSService
tts = TTSService()
print("✅ Service TTS initialisé avec succès")
```

## 🎯 Utilisation

### Interface utilisateur

1. **Accéder à un cours** : Ouvrez n'importe quel cours généré
2. **Cliquer sur "Podcast Audio"** : Bouton rouge avec icône microphone
3. **Générer l'audio** : Cliquez sur l'icône microphone pour chaque section
4. **Écouter** : Cliquez sur l'icône play pour écouter l'audio généré

### Fonctionnalités

- **Génération automatique** : Conversion texte vers parole
- **Intro podcast** : Chaque audio commence par le titre du chapitre
- **Qualité optimisée** : Audio MP3 128kbps pour un bon compromis qualité/taille
- **Cache intelligent** : Les audios sont mis en cache pour éviter la régénération
- **Multi-langues** : Support du français, anglais, espagnol

## 🔧 Configuration technique

### Structure des fichiers

```
media/
└── course_audio/
    ├── course_1_introduction_abc123.mp3
    ├── course_1_chapitre1_def456.mp3
    └── course_2_les_bases_ghi789.mp3
```

### API Endpoints

- `POST /courses/{id}/audio/{section_index}/` - Générer l'audio d'une section
- `GET /courses/{id}/audio-list/` - Lister les audios disponibles

### Service TTS

Le service `TTSService` gère :
- Nettoyage du texte HTML
- Division en chunks pour éviter les limites API
- Génération avec gTTS (Google Text-to-Speech)
- Combinaison des segments audio
- Ajout d'intro podcast
- Normalisation audio

## 🎨 Personnalisation

### Modifier les voix

```python
# Dans courses/tts_service.py
self.available_voices = {
    'fr': {
        'voice_id': 'fr-FR',
        'name': 'Français',
        'speed': 1.0,  # Vitesse de parole
        'pitch': 1.0   # Hauteur de voix
    }
}
```

### Ajuster la qualité audio

```python
# Dans la méthode generate_section_audio
final_audio.export(audio_path, format="mp3", bitrate="192k")  # Qualité plus élevée
```

### Modifier l'intro

```python
# Personnaliser l'intro podcast
intro_text = f"Bienvenue dans le chapitre: {section_title}. "
```

## 🐛 Dépannage

### Problèmes courants

1. **Erreur "Service TTS non disponible"**
   ```bash
   pip install gTTS pydub pygame
   ```

2. **Audio ne se génère pas**
   - Vérifier la connexion Internet (gTTS nécessite Internet)
   - Vérifier les permissions du dossier media/
   - Consulter les logs Django

3. **Audio de mauvaise qualité**
   - Augmenter le bitrate dans les paramètres
   - Vérifier la qualité du texte source

4. **Fichiers audio trop volumineux**
   - Réduire le bitrate
   - Diviser le contenu en sections plus petites

### Logs et débogage

```python
# Activer les logs détaillés
import logging
logging.getLogger('courses.tts_service').setLevel(logging.DEBUG)
```

## 📊 Performance

### Optimisations

- **Cache** : Les audios sont mis en cache 24h
- **Chunks** : Division automatique pour éviter les timeouts
- **Compression** : MP3 avec compression optimisée
- **Lazy loading** : Génération à la demande

### Limites

- **Taille** : Maximum ~1000 caractères par chunk
- **Durée** : Généralement 1-5 minutes par section
- **Stockage** : ~1-2 MB par section audio

## 🔒 Sécurité

- **Authentification** : Seuls les propriétaires de cours peuvent générer des audios
- **Validation** : Contenu nettoyé avant traitement
- **Isolation** : Fichiers audio isolés par utilisateur

## 🚀 Améliorations futures

- [ ] Support de plus de langues
- [ ] Choix de voix multiples
- [ ] Vitesse de lecture ajustable
- [ ] Export en format podcast (RSS)
- [ ] Intégration avec des services cloud
- [ ] Transcription automatique

## 📞 Support

Pour toute question ou problème :
1. Vérifiez les logs Django
2. Testez avec un cours simple
3. Vérifiez les dépendances
4. Consultez la documentation des bibliothèques utilisées

---

**Note** : Cette fonctionnalité nécessite une connexion Internet pour gTTS et un espace disque suffisant pour stocker les fichiers audio.
