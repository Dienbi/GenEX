"""Service for real-time pronunciation practice using Vosk API"""
import os
import json
import wave
import subprocess
import tempfile
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    Model = None
    KaldiRecognizer = None
from django.conf import settings
import difflib


class PronunciationService:
    """Handle real-time pronunciation evaluation"""
    
    def __init__(self):
        self.models = {}
        # Lazy loading: don't load models at init to save memory
        # Models will be loaded on first use
        self.model_paths = None
    
    def _load_models(self):
        """Load Vosk models for supported languages"""
        if not VOSK_AVAILABLE:
            print("Vosk not available. Pronunciation service disabled.")
            return
            
        # Models should be downloaded and placed in ml_models/vosk/
        vosk_path = os.path.join(settings.BASE_DIR, 'ml_models', 'vosk')
        
        if self.model_paths is None:
            self.model_paths = {
                'en': os.path.join(vosk_path, 'vosk-model-small-en-us-0.15'),
                'fr': os.path.join(vosk_path, 'vosk-model-small-fr-0.22'),
            }
        
        for lang, path in self.model_paths.items():
            if lang in self.models:  # Already loaded
                continue
                
            if os.path.exists(path):
                try:
                    self.models[lang] = Model(path)
                    print(f"Loaded Vosk model for {lang}")
                except Exception as e:
                    print(f"Error loading Vosk model for {lang}: {e}")
            else:
                print(f"Vosk model not found at {path}")
                print(f"Please download from: https://alphacephei.com/vosk/models")
    
    def _convert_to_wav(self, audio_path):
        """
        Convert audio file to proper WAV format for Vosk (16kHz, mono, 16-bit PCM)
        
        Args:
            audio_path: Path to input audio file
            
        Returns:
            Path to converted WAV file (temporary)
        """
        try:
            # Try using ffmpeg if available
            temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_wav.close()
            
            # Convert using ffmpeg
            cmd = [
                'ffmpeg', '-i', audio_path,
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',       # Mono
                '-sample_fmt', 's16',  # 16-bit
                '-y',             # Overwrite
                temp_wav.name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return temp_wav.name
            else:
                # If ffmpeg fails, try to open as is
                return None
                
        except Exception as e:
            print(f"Audio conversion error: {e}")
            return None
    
    def transcribe_audio(self, audio_path, language='en'):
        """
        Transcribe audio file using Vosk
        
        Args:
            audio_path: Path to audio file
            language: Language code ('en' or 'fr')
            
        Returns:
            dict with 'success', 'text', and optional 'error'
        """
        if language not in self.models:
            return {
                'success': False,
                'error': f'Vosk model for {language} not loaded. Please download from https://alphacephei.com/vosk/models'
            }
        
        converted_path = None
        try:
            # Try to convert audio to proper format
            converted_path = self._convert_to_wav(audio_path)
            if converted_path:
                audio_to_use = converted_path
            else:
                audio_to_use = audio_path
            
            # Open audio file
            wf = wave.open(audio_to_use, "rb")
            
            # Check format - if not correct, inform about conversion
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                wf.close()
                return {
                    'success': False,
                    'error': 'Audio format incompatible. Please install FFmpeg for automatic conversion: https://ffmpeg.org/download.html'
                }
            
            # Create recognizer
            rec = KaldiRecognizer(self.models[language], wf.getframerate())
            rec.SetWords(True)
            
            # Process audio
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if 'text' in result:
                        results.append(result['text'])
            
            # Final result
            final_result = json.loads(rec.FinalResult())
            if 'text' in final_result:
                results.append(final_result['text'])
            
            # Combine all results
            full_text = ' '.join(results).strip()
            
            wf.close()
            
            return {
                'success': True,
                'text': full_text
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            # Clean up temporary converted file
            if converted_path and os.path.exists(converted_path):
                try:
                    os.remove(converted_path)
                except:
                    pass
    
    def compare_texts(self, expected_text, spoken_text):
        """
        Compare expected text with spoken text word by word
        
        Args:
            expected_text: The text the user should say
            spoken_text: What the user actually said
            
        Returns:
            dict with comparison data including matched words and accuracy
        """
        # Normalize texts
        expected_words = expected_text.lower().split()
        spoken_words = spoken_text.lower().split()
        
        # Use difflib for sequence matching
        matcher = difflib.SequenceMatcher(None, expected_words, spoken_words)
        
        # Build comparison data
        comparison = []
        matches = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Words match
                for i in range(i1, i2):
                    comparison.append({
                        'expected': expected_words[i],
                        'spoken': spoken_words[j1 + (i - i1)],
                        'match': True
                    })
                    matches += 1
            elif tag == 'replace':
                # Words don't match
                for i in range(i1, i2):
                    spoken_word = spoken_words[j1 + (i - i1)] if (j1 + (i - i1)) < j2 else ''
                    comparison.append({
                        'expected': expected_words[i],
                        'spoken': spoken_word,
                        'match': False
                    })
            elif tag == 'delete':
                # Expected word missing
                for i in range(i1, i2):
                    comparison.append({
                        'expected': expected_words[i],
                        'spoken': '',
                        'match': False
                    })
            elif tag == 'insert':
                # Extra word spoken
                for j in range(j1, j2):
                    comparison.append({
                        'expected': '',
                        'spoken': spoken_words[j],
                        'match': False
                    })
        
        # Calculate accuracy
        total_expected = len(expected_words)
        accuracy = (matches / total_expected * 100) if total_expected > 0 else 0
        
        return {
            'comparison': comparison,
            'matched_words': matches,
            'total_words': total_expected,
            'accuracy_score': round(accuracy, 2),
            'spoken_word_count': len(spoken_words)
        }
    
    def get_practice_texts(self, language, difficulty='medium'):
        """
        Get practice texts for pronunciation training
        
        Args:
            language: Language code ('en' or 'fr')
            difficulty: 'easy', 'medium', or 'hard'
            
        Returns:
            list of practice texts
        """
        texts = {
            'en': {
                'easy': [
                    "Hello, my name is Sarah. I am a student.",
                    "The weather is nice today. The sun is shining.",
                    "I like to read books and watch movies.",
                    "My favorite color is blue. What is yours?",
                    "I wake up early every morning."
                ],
                'medium': [
                    "Communication skills are essential in today's interconnected world.",
                    "Technology has transformed the way we learn and work together.",
                    "Practicing pronunciation regularly will improve your speaking confidence.",
                    "The ability to express ideas clearly is valuable in any profession.",
                    "Learning a new language opens doors to different cultures and perspectives."
                ],
                'hard': [
                    "Sophisticated linguistic competence requires consistent practice and dedication to mastering nuanced pronunciation patterns.",
                    "The juxtaposition of theoretical knowledge and practical application yields comprehensive understanding.",
                    "Contemporary educational methodologies emphasize interactive and experiential learning approaches.",
                    "Articulating complex concepts necessitates both vocabulary breadth and grammatical precision.",
                    "Interdisciplinary collaboration fosters innovative solutions to multifaceted challenges."
                ]
            },
            'fr': {
                'easy': [
                    "Bonjour, je m'appelle Marie. Je suis étudiante.",
                    "Il fait beau aujourd'hui. Le soleil brille.",
                    "J'aime lire des livres et regarder des films.",
                    "Ma couleur préférée est le bleu. Et vous?",
                    "Je me réveille tôt chaque matin."
                ],
                'medium': [
                    "Les compétences en communication sont essentielles dans le monde d'aujourd'hui.",
                    "La technologie a transformé notre façon d'apprendre et de travailler ensemble.",
                    "Pratiquer la prononciation régulièrement améliorera votre confiance à l'oral.",
                    "La capacité d'exprimer clairement ses idées est précieuse dans toute profession.",
                    "Apprendre une nouvelle langue ouvre des portes vers différentes cultures."
                ],
                'hard': [
                    "La compétence linguistique sophistiquée nécessite une pratique constante et un dévouement.",
                    "La juxtaposition de connaissances théoriques et d'application pratique génère une compréhension complète.",
                    "Les méthodologies éducatives contemporaines mettent l'accent sur l'apprentissage interactif.",
                    "Articuler des concepts complexes nécessite à la fois une richesse de vocabulaire et une précision grammaticale.",
                    "La collaboration interdisciplinaire favorise des solutions innovantes aux défis multidimensionnels."
                ]
            }
        }
        
        return texts.get(language, {}).get(difficulty, [])
    
    def get_app_recommendations(self, level, language):
        """
        Get app recommendations based on user's level
        
        Args:
            level: User's current level (A1-C2)
            language: Language code
            
        Returns:
            list of recommended apps
        """
        recommendations = [
            {
                'name': 'Duolingo',
                'description': 'Popular language learning app with gamified lessons',
                'url': 'https://www.duolingo.com',
                'icon': '🦉',
                'recommended_for': ['A1', 'A2', 'B1']
            },
            {
                'name': 'Babbel',
                'description': 'Structured courses designed by language experts',
                'url': 'https://www.babbel.com',
                'icon': '📚',
                'recommended_for': ['A2', 'B1', 'B2']
            },
            {
                'name': 'HelloTalk',
                'description': 'Practice with native speakers through text and voice',
                'url': 'https://www.hellotalk.com',
                'icon': '💬',
                'recommended_for': ['B1', 'B2', 'C1']
            },
            {
                'name': 'Tandem',
                'description': 'Language exchange with native speakers worldwide',
                'url': 'https://www.tandem.net',
                'icon': '🌍',
                'recommended_for': ['B1', 'B2', 'C1', 'C2']
            },
            {
                'name': 'Pimsleur',
                'description': 'Audio-based method focusing on conversation skills',
                'url': 'https://www.pimsleur.com',
                'icon': '🎧',
                'recommended_for': ['A1', 'A2', 'B1', 'B2']
            },
            {
                'name': 'Memrise',
                'description': 'Vocabulary building with spaced repetition',
                'url': 'https://www.memrise.com',
                'icon': '🧠',
                'recommended_for': ['A1', 'A2', 'B1']
            },
            {
                'name': 'iTalki',
                'description': 'One-on-one lessons with professional teachers',
                'url': 'https://www.italki.com',
                'icon': '👨‍🏫',
                'recommended_for': ['B1', 'B2', 'C1', 'C2']
            },
            {
                'name': 'Busuu',
                'description': 'Comprehensive courses with social learning features',
                'url': 'https://www.busuu.com',
                'icon': '🎓',
                'recommended_for': ['A1', 'A2', 'B1', 'B2']
            }
        ]
        
        # Filter recommendations based on level
        filtered = [app for app in recommendations if level in app['recommended_for']]
        
        return filtered if filtered else recommendations[:4]


# Global instance
pronunciation_service = PronunciationService()
