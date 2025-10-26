import os
import logging
import hashlib
import time
from django.conf import settings
from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import re
import html

logger = logging.getLogger(__name__)

# Import optionnel des bibliothèques TTS
try:
    from gtts import gTTS
    import pygame
    from pydub import AudioSegment
    from pydub.effects import normalize
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS non disponible. Installez gtts, pygame et pydub.")

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 non disponible. Installez pyttsx3 pour le TTS local.")

TTS_AVAILABLE = GTTS_AVAILABLE or PYTTSX3_AVAILABLE

class TTSService:
    """Service de conversion texte vers parole pour les cours"""
    
    def __init__(self):
        self.available_voices = {
            'fr': {
                'voice_id': 'fr-FR',
                'name': 'Français',
                'speed': 1.0,
                'pitch': 1.0
            },
            'en': {
                'voice_id': 'en-US',
                'name': 'English',
                'speed': 1.0,
                'pitch': 1.0
            },
            'es': {
                'voice_id': 'es-ES',
                'name': 'Español',
                'speed': 1.0,
                'pitch': 1.0
            }
        }
        
        # Configuration des dossiers audio
        self.audio_base_path = os.path.join(settings.MEDIA_ROOT, 'course_audio')
        if not os.path.exists(self.audio_base_path):
            os.makedirs(self.audio_base_path)
    
    def clean_text_for_speech(self, text):
        """Nettoie le texte pour une meilleure synthèse vocale"""
        # Supprimer le HTML
        text = html.unescape(text)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Nettoyer les caractères spéciaux
        text = re.sub(r'[^\w\s.,!?;:()\-]', '', text)
        
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Ajouter des pauses naturelles
        text = text.replace('.', '. ')
        text = text.replace('!', '! ')
        text = text.replace('?', '? ')
        text = text.replace(':', ': ')
        text = text.replace(';', '; ')
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def split_text_into_chunks(self, text, max_chunk_size=1000):
        """Divise le texte en chunks pour éviter les limites de l'API"""
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def generate_audio_filename(self, course_id, section_title, language):
        """Génère un nom de fichier unique pour l'audio"""
        # Créer un hash basé sur le contenu pour éviter les doublons
        content_hash = hashlib.md5(f"{course_id}_{section_title}_{language}".encode()).hexdigest()[:8]
        
        # Nettoyer le titre pour le nom de fichier
        clean_title = re.sub(r'[^\w\s-]', '', section_title)
        clean_title = re.sub(r'\s+', '_', clean_title)[:50]
        
        return f"course_{course_id}_{clean_title}_{content_hash}.mp3"
    
    def generate_section_audio(self, course_id, section_title, content, language='fr'):
        """Génère l'audio pour une section de cours"""
        if not TTS_AVAILABLE:
            raise Exception("Service TTS non disponible. Installez les dépendances requises.")
        
        try:
            # Nettoyer le contenu
            clean_content = self.clean_text_for_speech(content)
            
            if len(clean_content) < 50:
                raise Exception("Contenu trop court pour générer un audio")
            
            # Vérifier le cache
            content_hash = hashlib.md5(f"{course_id}_{section_title}_{clean_content}_{language}".encode()).hexdigest()
            cache_key = f"tts_audio_{content_hash}"
            cached_audio_path = cache.get(cache_key)
            
            if cached_audio_path and os.path.exists(cached_audio_path):
                logger.info(f"Audio trouvé dans le cache: {cached_audio_path}")
                return cached_audio_path
            
            # Générer le nom de fichier
            filename = self.generate_audio_filename(course_id, section_title, language)
            audio_path = os.path.join(self.audio_base_path, filename)
            
            # Essayer d'abord avec gTTS, puis fallback vers pyttsx3
            try:
                if GTTS_AVAILABLE:
                    logger.info("Tentative de génération avec gTTS...")
                    return self._generate_with_gtts(course_id, section_title, clean_content, language, audio_path, cache_key)
                else:
                    raise Exception("gTTS non disponible")
            except Exception as gtts_error:
                logger.warning(f"gTTS a échoué: {gtts_error}")
                if PYTTSX3_AVAILABLE:
                    logger.info("Fallback vers pyttsx3...")
                    return self._generate_with_pyttsx3(course_id, section_title, clean_content, language, audio_path, cache_key)
                else:
                    raise Exception(f"gTTS a échoué et pyttsx3 n'est pas disponible. Erreur gTTS: {gtts_error}")
                
        except Exception as e:
            logger.error(f"Erreur lors de la génération audio: {str(e)}")
            raise Exception(f"Erreur lors de la génération audio: {str(e)}")
    
    def _generate_with_gtts(self, course_id, section_title, clean_content, language, audio_path, cache_key):
        """Génère l'audio avec gTTS"""
        # Diviser le contenu en chunks
        chunks = self.split_text_into_chunks(clean_content)
        
        # Générer l'audio pour chaque chunk
        audio_segments = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Génération audio chunk {i+1}/{len(chunks)}")
            
            # Utiliser gTTS pour générer l'audio
            tts = gTTS(text=chunk, lang=language, slow=False)
            
            # Sauvegarder temporairement
            temp_filename = f"temp_chunk_{i}_{int(time.time())}.mp3"
            temp_path = os.path.join(self.audio_base_path, temp_filename)
            
            tts.save(temp_path)
            
            # Charger avec pydub pour traitement
            audio_segment = AudioSegment.from_mp3(temp_path)
            audio_segments.append(audio_segment)
            
            # Supprimer le fichier temporaire
            os.remove(temp_path)
        
        # Combiner tous les segments
        if audio_segments:
            final_audio = audio_segments[0]
            for segment in audio_segments[1:]:
                # Ajouter une pause de 0.5 seconde entre les segments
                pause = AudioSegment.silent(duration=500)
                final_audio += pause + segment
            
            # Normaliser l'audio
            final_audio = normalize(final_audio)
            
            # Ajouter une intro podcast
            intro_text = f"Chapitre: {section_title}. "
            intro_tts = gTTS(text=intro_text, lang=language, slow=False)
            intro_temp = os.path.join(self.audio_base_path, f"intro_{int(time.time())}.mp3")
            intro_tts.save(intro_temp)
            intro_audio = AudioSegment.from_mp3(intro_temp)
            
            # Combiner intro + contenu
            final_audio = intro_audio + AudioSegment.silent(duration=1000) + final_audio
            
            # Sauvegarder le fichier final
            final_audio.export(audio_path, format="mp3", bitrate="128k")
            
            # Nettoyer l'intro temporaire
            os.remove(intro_temp)
            
            # Mettre en cache
            cache.set(cache_key, audio_path, timeout=86400)  # 24 heures
            
            logger.info(f"Audio généré avec succès avec gTTS: {audio_path}")
            return audio_path
        else:
            raise Exception("Aucun segment audio généré")
    
    def _generate_with_pyttsx3(self, course_id, section_title, clean_content, language, audio_path, cache_key):
        """Génère l'audio avec pyttsx3 (TTS local)"""
        try:
            # Initialiser le moteur TTS
            engine = pyttsx3.init()
            
            # Configurer les propriétés de la voix
            voices = engine.getProperty('voices')
            
            # Sélectionner une voix appropriée selon la langue
            if language == 'fr':
                for voice in voices:
                    if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
            elif language == 'en':
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Configurer la vitesse et le volume
            engine.setProperty('rate', 150)  # Vitesse de parole
            engine.setProperty('volume', 0.9)  # Volume
            
            # Créer le texte complet avec intro
            full_text = f"Chapitre: {section_title}. {clean_content}"
            
            # Sauvegarder dans un fichier temporaire
            temp_filename = f"temp_pyttsx3_{int(time.time())}.wav"
            temp_path = os.path.join(self.audio_base_path, temp_filename)
            
            # Générer l'audio
            engine.save_to_file(full_text, temp_path)
            engine.runAndWait()
            
            # Convertir en MP3 si pydub est disponible
            if GTTS_AVAILABLE:  # Si pydub est disponible
                audio_segment = AudioSegment.from_wav(temp_path)
                audio_segment.export(audio_path, format="mp3", bitrate="128k")
                os.remove(temp_path)  # Supprimer le fichier WAV temporaire
            else:
                # Renommer le fichier WAV en MP3 (pas de conversion)
                os.rename(temp_path, audio_path.replace('.mp3', '.wav'))
                audio_path = audio_path.replace('.mp3', '.wav')
            
            # Mettre en cache
            cache.set(cache_key, audio_path, timeout=86400)  # 24 heures
            
            logger.info(f"Audio généré avec succès avec pyttsx3: {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Erreur avec pyttsx3: {str(e)}")
            raise Exception(f"Erreur avec pyttsx3: {str(e)}")
    
    def get_audio_url(self, audio_path):
        """Retourne l'URL publique de l'audio"""
        if not audio_path or not os.path.exists(audio_path):
            return None
        
        # Convertir le chemin absolu en chemin relatif
        relative_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
        return os.path.join(settings.MEDIA_URL, relative_path).replace('\\', '/')
    
    def delete_audio_file(self, audio_path):
        """Supprime un fichier audio"""
        try:
            if os.path.exists(audio_path):
                os.remove(audio_path)
                logger.info(f"Fichier audio supprimé: {audio_path}")
                return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du fichier audio: {str(e)}")
        return False
    
    def get_available_languages(self):
        """Retourne les langues disponibles pour TTS"""
        return list(self.available_voices.keys())
    
    def get_audio_info(self, audio_path):
        """Retourne les informations sur un fichier audio"""
        if not os.path.exists(audio_path):
            return None
        
        try:
            audio = AudioSegment.from_mp3(audio_path)
            return {
                'duration_seconds': len(audio) / 1000.0,
                'duration_formatted': f"{int(len(audio) / 1000 // 60)}:{(int(len(audio) / 1000) % 60):02d}",
                'file_size': os.path.getsize(audio_path),
                'file_size_mb': round(os.path.getsize(audio_path) / (1024 * 1024), 2)
            }
        except Exception as e:
            logger.error(f"Erreur lors de la lecture des infos audio: {str(e)}")
            return None
