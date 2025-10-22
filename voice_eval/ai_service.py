"""
AI Service for Voice Evaluation
Handles speech-to-text, NLP analysis, audio analysis, and originality checking
"""
from __future__ import annotations
import os
import numpy as np
import json
from typing import Dict, List, Tuple, Optional
import tempfile


class VoiceEvaluationService:
    """Main service class for voice evaluation processing"""
    
    def __init__(self):
        self.whisper_model = None
        self.nlp_en = None
        self.nlp_fr = None
        self.sentence_model = None
        
    def initialize_models(self):
        """Lazy load models to avoid loading on import"""
        try:
            # Import here to avoid loading on module import
            import whisper
            from sentence_transformers import SentenceTransformer
            
            if self.whisper_model is None:
                print("Loading Whisper model...")
                self.whisper_model = whisper.load_model("base")
            
            # Try to load spaCy, but use fallback if unavailable
            if self.nlp_en is None:
                try:
                    import spacy
                    print("Loading English spaCy model...")
                    self.nlp_en = spacy.load("en_core_web_sm")
                except (ImportError, OSError) as e:
                    print(f"spaCy not available ({e}), using fallback NLP")
                    self.nlp_en = None
            
            if self.nlp_fr is None:
                try:
                    import spacy
                    print("Loading French spaCy model...")
                    self.nlp_fr = spacy.load("fr_core_news_sm")
                except (ImportError, OSError) as e:
                    print(f"French model not available ({e}), using fallback NLP")
                    self.nlp_fr = None
            
            if self.sentence_model is None:
                print("Loading sentence transformer...")
                self.sentence_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
                
        except ImportError as e:
            print(f"Error importing required libraries: {e}")
            raise
    
    def _check_transcription_quality(self, text: str, confidence: float) -> List[str]:
        """
        Check transcription quality and identify potential issues
        
        Args:
            text: Transcribed text
            confidence: Average transcription confidence (0-1)
        
        Returns:
            List of quality issue warnings
        """
        import re
        
        issues = []
        
        # 1. Check confidence score
        if confidence < 0.5:
            issues.append("LOW_CONFIDENCE: Transcription confidence is very low. Poor audio quality suspected.")
        elif confidence < 0.7:
            issues.append("MEDIUM_CONFIDENCE: Transcription may have some errors. Check audio quality.")
        
        # 2. Check for gibberish patterns
        words = text.lower().split()
        if len(words) > 5:
            # Check for excessive repetition
            unique_words = set(words)
            if len(unique_words) / len(words) < 0.3:
                issues.append("REPETITIVE_TEXT: Too many repeated words detected.")
            
            # Check for nonsensical word combinations
            nonsense_patterns = [
                r'\b(\w+)\s+and\s+\1\s+and\b',  # "book and book and"
                r'\b(a|an|the)\s+(a|an|the)\s+(a|an|the)\b',  # "a a the"
                r'\b\w{1,2}\s+\w{1,2}\s+\w{1,2}\s+\w{1,2}\s+\w{1,2}\b',  # Too many short words
            ]
            
            for pattern in nonsense_patterns:
                if re.search(pattern, text.lower()):
                    issues.append("NONSENSICAL_PATTERN: Unusual word patterns detected. May indicate transcription errors.")
                    break
        
        # 3. Check for very short or empty transcription
        if len(text.strip()) < 10:
            issues.append("TOO_SHORT: Transcription is too short. Audio may be unclear or silent.")
        
        # 4. Check for missing punctuation (might indicate poor segmentation)
        if len(text) > 50 and not re.search(r'[.!?,;:]', text):
            issues.append("NO_PUNCTUATION: No punctuation detected. Transcription quality may be poor.")
        
        # 5. Check for excessive numbers or random characters
        if len(words) > 5:
            number_count = sum(1 for w in words if w.isdigit())
            if number_count / len(words) > 0.3:
                issues.append("EXCESSIVE_NUMBERS: Too many numbers detected. May indicate audio noise.")
        
        return issues
    
    def transcribe_audio(self, audio_path: str, language: str = 'en') -> Dict:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to audio file
            language: Language code ('en' or 'fr')
        
        Returns:
            Dict with transcription and metadata including confidence scores
        """
        import os
        
        # Check if file exists
        if not os.path.exists(audio_path):
            return {
                'text': '',
                'error': f'Audio file not found: {audio_path}',
                'success': False
            }
        
        self.initialize_models()
        
        try:
            print(f"Transcribing audio file: {audio_path}")
            print(f"File size: {os.path.getsize(audio_path)} bytes")
            
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                task='transcribe',
                verbose=False,
                word_timestamps=True  # Get word-level confidence
            )
            
            # Calculate average confidence from segments
            avg_confidence = 0.0
            if 'segments' in result and result['segments']:
                confidences = []
                for segment in result['segments']:
                    if 'words' in segment and segment['words']:
                        word_probs = [w.get('probability', 0.0) for w in segment['words'] if 'probability' in w]
                        if word_probs:
                            confidences.extend(word_probs)
                    elif 'avg_logprob' in segment:
                        # Convert log probability to probability (approximate)
                        import math
                        confidences.append(math.exp(segment['avg_logprob']))
                
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
            
            transcribed_text = result['text'].strip()
            
            # Quality check: Detect poor transcription
            quality_issues = self._check_transcription_quality(transcribed_text, avg_confidence)
            
            return {
                'text': transcribed_text,
                'language': result.get('language', language),
                'segments': result.get('segments', []),
                'confidence': avg_confidence,
                'quality_issues': quality_issues,
                'success': True
            }
        except FileNotFoundError as e:
            error_msg = "FFmpeg not found. Please install FFmpeg to process audio files. See INSTALL_FFMPEG.md for instructions."
            print(f"FFmpeg error: {error_msg}")
            return {
                'text': '',
                'error': error_msg,
                'success': False
            }
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Transcription error: {error_details}")
            
            # Check if it's an FFmpeg-related error
            if 'ffmpeg' in str(e).lower() or 'No such file' in str(e):
                error_msg = f"FFmpeg error: {str(e)}. Please install FFmpeg (see INSTALL_FFMPEG.md)"
            else:
                error_msg = str(e)
            
            return {
                'text': '',
                'error': error_msg,
                'success': False
            }
    
    def analyze_verbal_communication(self, text: str, language: str = 'en', quality_issues: List[str] = None) -> Dict:
        """
        Analyze verbal communication aspects with quality awareness
        
        Args:
            text: Transcribed text
            language: Language code
            quality_issues: List of transcription quality issues
        
        Returns:
            Dict with fluency, vocabulary, and structure scores
        """
        self.initialize_models()
        
        nlp = self.nlp_en if language == 'en' else self.nlp_fr
        
        if nlp is None:
            # Use fallback simple NLP when spaCy is not available
            return self._analyze_verbal_simple(text, language, quality_issues)
        
        doc = nlp(text)
        
        # Fluency Analysis
        fluency_score = self._analyze_fluency(doc, text)
        
        # Vocabulary Analysis
        vocabulary_score = self._analyze_vocabulary(doc, language)
        
        # Structure Analysis
        structure_score = self._analyze_structure(doc)
        
        # Calculate overall verbal score
        verbal_score = (fluency_score + vocabulary_score + structure_score) / 3
        
        return {
            'fluency_score': round(fluency_score, 2),
            'vocabulary_score': round(vocabulary_score, 2),
            'structure_score': round(structure_score, 2),
            'verbal_score': round(verbal_score, 2),
            'details': {
                'word_count': len([token for token in doc if not token.is_punct]),
                'sentence_count': len(list(doc.sents)),
                'unique_words': len(set([token.lemma_.lower() for token in doc if not token.is_punct and not token.is_stop])),
            }
        }
    
    def _analyze_verbal_simple(self, text: str, language: str, quality_issues: List[str] = None) -> Dict:
        """
        Simple verbal analysis without spaCy (fallback method)
        Uses basic text processing with quality awareness
        
        Args:
            text: Transcribed text
            language: Language code
            quality_issues: List of transcription quality issues
        """
        import re
        import string
        
        # Tokenize into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Tokenize into words
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words (basic list)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'le', 'la', 'les', 'un', 'une', 'des', 'de', 'et', 'ou', 'dans', 'sur'}
        
        content_words = [w for w in words if w not in stop_words and len(w) > 2]
        unique_words = set(content_words)
        
        # Apply quality penalty if there are transcription issues
        quality_penalty = 1.0
        if quality_issues:
            # Reduce scores based on severity of issues
            severe_issues = [i for i in quality_issues if 'LOW_CONFIDENCE' in i or 'NONSENSICAL' in i]
            medium_issues = [i for i in quality_issues if 'MEDIUM_CONFIDENCE' in i or 'REPETITIVE' in i]
            
            if severe_issues:
                quality_penalty = 0.4  # 60% penalty for severe issues
            elif medium_issues:
                quality_penalty = 0.7  # 30% penalty for medium issues
            else:
                quality_penalty = 0.85  # 15% penalty for minor issues
        
        # Fluency Analysis (simplified)
        fluency_score = 50.0
        word_count = len(words)
        
        if 100 <= word_count <= 300:
            fluency_score += 20
        elif 50 <= word_count < 100 or 300 < word_count <= 500:
            fluency_score += 10
        
        if len(sentences) > 0:
            avg_sentence_length = word_count / len(sentences)
            if 10 <= avg_sentence_length <= 20:
                fluency_score += 15
            elif 5 <= avg_sentence_length < 10 or 20 < avg_sentence_length <= 30:
                fluency_score += 5
        
        # Check for filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'euh', 'ben']
        filler_count = sum(text.lower().count(filler) for filler in filler_words)
        fluency_score -= min(filler_count * 2, 20)
        
        # Vocabulary Analysis (simplified)
        vocabulary_score = 50.0
        
        if len(words) > 0:
            ttr = len(unique_words) / len(content_words) if content_words else 0
            vocabulary_score += min(ttr * 30, 25)
        
        if content_words:
            avg_word_length = sum(len(w) for w in content_words) / len(content_words)
            if avg_word_length >= 5:
                vocabulary_score += 15
            elif avg_word_length >= 4:
                vocabulary_score += 10
            elif avg_word_length >= 3:
                vocabulary_score += 5
        
        # Structure Analysis (simplified)
        structure_score = 50.0
        
        if len(sentences) > 0:
            # Check for varied sentence lengths
            sent_lengths = [len(s.split()) for s in sentences]
            if len(set(sent_lengths)) > 1:
                structure_score += 15
            
            # Check for proper capitalization
            capitalized = sum(1 for s in sentences if s and s[0].isupper())
            structure_score += (capitalized / len(sentences)) * 20
        
        # Check for basic punctuation
        if any(p in text for p in '.!?,;'):
            structure_score += 15
        
        # Ensure scores are in valid range
        fluency_score = max(0, min(100, fluency_score))
        vocabulary_score = max(0, min(100, vocabulary_score))
        structure_score = max(0, min(100, structure_score))
        
        # Apply quality penalty to all scores
        fluency_score *= quality_penalty
        vocabulary_score *= quality_penalty
        structure_score *= quality_penalty
        
        verbal_score = (fluency_score + vocabulary_score + structure_score) / 3
        
        result = {
            'fluency_score': round(fluency_score, 2),
            'vocabulary_score': round(vocabulary_score, 2),
            'structure_score': round(structure_score, 2),
            'verbal_score': round(verbal_score, 2),
            'details': {
                'word_count': len(words),
                'sentence_count': len(sentences),
                'unique_words': len(unique_words),
                'note': 'Using fallback NLP (spaCy not available)'
            }
        }
        
        # Add quality warning if penalty was applied
        if quality_penalty < 1.0:
            result['quality_warning'] = f"Scores reduced due to poor transcription quality (confidence: {quality_penalty*100:.0f}%)"
            result['quality_issues'] = quality_issues
        
        return result
    
    def _analyze_fluency(self, doc, text: str) -> float:
        """
        Analyze fluency based on:
        - Speech length
        - Sentence coherence
        - Filler words detection
        - Repetitions
        """
        score = 50.0  # Base score
        
        # Word count bonus (ideal: 100-300 words)
        word_count = len([token for token in doc if not token.is_punct])
        if 100 <= word_count <= 300:
            score += 20
        elif 50 <= word_count < 100 or 300 < word_count <= 500:
            score += 10
        elif word_count < 50:
            score -= 10
        
        # Sentence length variation (good fluency has varied sentence lengths)
        sent_lengths = [len([t for t in sent if not t.is_punct]) for sent in doc.sents]
        if sent_lengths:
            avg_length = np.mean(sent_lengths)
            std_dev = np.std(sent_lengths)
            if 10 <= avg_length <= 20 and std_dev > 3:
                score += 15
            elif 5 <= avg_length < 10 or 20 < avg_length <= 30:
                score += 5
        
        # Check for common filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'basically', 'actually', 'euh', 'ben', 'donc']
        text_lower = text.lower()
        filler_count = sum(text_lower.count(filler) for filler in filler_words)
        score -= min(filler_count * 2, 20)  # Penalize up to 20 points
        
        # Check for repetitions
        words = [token.text.lower() for token in doc if not token.is_punct and not token.is_stop]
        if len(words) > 0:
            repetition_ratio = 1 - (len(set(words)) / len(words))
            score -= repetition_ratio * 15
        
        return max(0, min(100, score))
    
    def _analyze_vocabulary(self, doc, language: str) -> float:
        """
        Analyze vocabulary richness:
        - Lexical diversity
        - Word complexity
        - Use of advanced vocabulary
        """
        score = 50.0  # Base score
        
        words = [token for token in doc if not token.is_punct and not token.is_stop]
        
        if len(words) == 0:
            return 0
        
        # Lexical diversity (Type-Token Ratio)
        unique_words = set([token.lemma_.lower() for token in words])
        ttr = len(unique_words) / len(words) if len(words) > 0 else 0
        score += min(ttr * 30, 25)  # Up to 25 points
        
        # Average word length (complexity indicator)
        avg_word_length = np.mean([len(token.text) for token in words])
        if avg_word_length >= 5:
            score += 15
        elif avg_word_length >= 4:
            score += 10
        elif avg_word_length >= 3:
            score += 5
        
        # Part of speech diversity
        pos_tags = set([token.pos_ for token in words])
        pos_diversity = len(pos_tags) / 10  # Normalize by typical POS tag count
        score += min(pos_diversity * 15, 10)
        
        return max(0, min(100, score))
    
    def _analyze_structure(self, doc) -> float:
        """
        Analyze grammatical structure:
        - Complete sentences
        - Proper punctuation
        - Grammar correctness
        """
        score = 50.0  # Base score
        
        sentences = list(doc.sents)
        if len(sentences) == 0:
            return 0
        
        # Check for complete sentences (has subject and verb)
        complete_sentences = 0
        for sent in sentences:
            has_verb = any(token.pos_ == 'VERB' for token in sent)
            has_subject = any(token.dep_ in ['nsubj', 'nsubjpass'] for token in sent)
            if has_verb and has_subject:
                complete_sentences += 1
        
        completeness_ratio = complete_sentences / len(sentences)
        score += completeness_ratio * 25
        
        # Sentence variety (different sentence structures)
        sentence_patterns = set()
        for sent in sentences:
            pattern = '-'.join([token.pos_ for token in sent if not token.is_punct][:5])  # First 5 POS tags
            sentence_patterns.add(pattern)
        
        variety_score = min(len(sentence_patterns) / len(sentences) * 15, 15)
        score += variety_score
        
        # Check for proper capitalization and punctuation
        proper_sentences = sum(1 for sent in sentences if sent[0].text[0].isupper() and sent[-1].is_punct)
        punctuation_score = (proper_sentences / len(sentences)) * 10
        score += punctuation_score
        
        return max(0, min(100, score))
    
    def analyze_paraverbal_communication(self, audio_path: str) -> Dict:
        """
        Analyze paraverbal communication using librosa
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Dict with pitch, pace, energy scores
        """
        try:
            import librosa
            
            # Load audio
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Pitch analysis
            pitch_score = self._analyze_pitch(y, sr)
            
            # Pace analysis
            pace_score = self._analyze_pace(y, sr, duration)
            
            # Energy analysis
            energy_score = self._analyze_energy(y)
            
            # Overall paraverbal score
            paraverbal_score = (pitch_score + pace_score + energy_score) / 3
            
            # Extract audio features for storage
            audio_features = self._extract_audio_features(y, sr)
            
            return {
                'pitch_score': round(pitch_score, 2),
                'pace_score': round(pace_score, 2),
                'energy_score': round(energy_score, 2),
                'paraverbal_score': round(paraverbal_score, 2),
                'duration': round(duration, 2),
                'audio_features': audio_features,
                'success': True
            }
            
        except Exception as e:
            return {
                'pitch_score': 0,
                'pace_score': 0,
                'energy_score': 0,
                'paraverbal_score': 0,
                'duration': 0,
                'audio_features': {},
                'error': str(e),
                'success': False
            }
    
    def _analyze_pitch(self, y, sr) -> float:
        """Analyze pitch variation and range"""
        import librosa
        
        score = 50.0
        
        try:
            # Extract pitch using piptrack
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            
            # Get pitch values where magnitude is highest
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 0:
                # Pitch variation (good speakers vary their pitch)
                pitch_std = np.std(pitch_values)
                if pitch_std > 50:
                    score += 25
                elif pitch_std > 30:
                    score += 15
                elif pitch_std > 10:
                    score += 5
                
                # Pitch range
                pitch_range = np.max(pitch_values) - np.min(pitch_values)
                if pitch_range > 200:
                    score += 25
                elif pitch_range > 100:
                    score += 15
                elif pitch_range > 50:
                    score += 5
            
        except Exception:
            pass
        
        return max(0, min(100, score))
    
    def _analyze_pace(self, y, sr, duration) -> float:
        """Analyze speaking pace"""
        import librosa
        
        score = 50.0
        
        try:
            # Detect onsets (beginnings of sounds/syllables)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
            
            # Calculate speaking rate (onsets per second as proxy for syllables/second)
            speaking_rate = len(onsets) / duration if duration > 0 else 0
            
            # Ideal speaking rate: 3-6 syllables per second
            if 3 <= speaking_rate <= 6:
                score += 30
            elif 2 <= speaking_rate < 3 or 6 < speaking_rate <= 8:
                score += 15
            elif speaking_rate < 2 or speaking_rate > 8:
                score -= 10
            
            # Pace consistency
            if len(onsets) > 1:
                onset_times = librosa.frames_to_time(onsets, sr=sr)
                intervals = np.diff(onset_times)
                consistency = 1 / (np.std(intervals) + 0.1)  # Lower std = more consistent
                score += min(consistency * 10, 20)
            
        except Exception:
            pass
        
        return max(0, min(100, score))
    
    def _analyze_energy(self, y) -> float:
        """Analyze voice energy and dynamics"""
        score = 50.0
        
        try:
            # RMS energy
            import librosa
            rms = librosa.feature.rms(y=y)[0]
            
            # Energy variation (good speakers vary their volume)
            energy_std = np.std(rms)
            if energy_std > 0.02:
                score += 25
            elif energy_std > 0.01:
                score += 15
            elif energy_std > 0.005:
                score += 5
            
            # Average energy (not too quiet, not too loud)
            avg_energy = np.mean(rms)
            if 0.05 <= avg_energy <= 0.3:
                score += 25
            elif 0.02 <= avg_energy < 0.05 or 0.3 < avg_energy <= 0.5:
                score += 10
            
        except Exception:
            pass
        
        return max(0, min(100, score))
    
    def _extract_audio_features(self, y, sr) -> Dict:
        """Extract audio features for storage"""
        import librosa
        
        try:
            features = {
                'spectral_centroid': float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))),
                'spectral_rolloff': float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))),
                'zero_crossing_rate': float(np.mean(librosa.feature.zero_crossing_rate(y))),
                'rms_mean': float(np.mean(librosa.feature.rms(y=y))),
                'rms_std': float(np.std(librosa.feature.rms(y=y))),
            }
            return features
        except Exception:
            return {}
    
    def check_originality(self, text: str, language: str, reference_texts: List[Dict]) -> Dict:
        """
        Check originality by comparing with reference texts
        
        Args:
            text: Input text to check
            language: Language code
            reference_texts: List of reference texts with embeddings
        
        Returns:
            Dict with originality score and similar texts
        """
        self.initialize_models()
        
        try:
            # Generate embedding for input text
            input_embedding = self.sentence_model.encode(text)
            
            # Calculate similarity with reference texts
            similarities = []
            similar_texts = []
            
            for ref in reference_texts:
                if ref.get('language') == language and ref.get('embedding'):
                    ref_embedding = np.array(ref['embedding'])
                    
                    # Cosine similarity
                    similarity = np.dot(input_embedding, ref_embedding) / (
                        np.linalg.norm(input_embedding) * np.linalg.norm(ref_embedding)
                    )
                    similarities.append(similarity)
                    
                    if similarity > 0.7:  # High similarity threshold
                        similar_texts.append({
                            'theme': ref.get('theme', 'Unknown'),
                            'similarity': float(similarity),
                            'text_preview': ref.get('text', '')[:100] + '...'
                        })
            
            # Calculate originality score
            if similarities:
                max_similarity = max(similarities)
                avg_similarity = np.mean(similarities)
                
                # Higher similarity = lower originality
                originality_score = 100 * (1 - max_similarity * 0.7 - avg_similarity * 0.3)
            else:
                # No references to compare with
                originality_score = 75.0  # Neutral score
            
            return {
                'originality_score': max(0, min(100, round(originality_score, 2))),
                'max_similarity': round(max(similarities), 3) if similarities else 0,
                'similar_texts': sorted(similar_texts, key=lambda x: x['similarity'], reverse=True)[:3],
                'success': True
            }
            
        except Exception as e:
            return {
                'originality_score': 0,
                'error': str(e),
                'success': False
            }
    
    def generate_text_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text"""
        self.initialize_models()
        embedding = self.sentence_model.encode(text)
        return embedding.tolist()
    
    def calculate_language_level(self, scores: Dict) -> str:
        """
        Determine CEFR language level based on scores
        
        Args:
            scores: Dict with all evaluation scores
        
        Returns:
            CEFR level code (A1, A2, B1, B2, C1, C2)
        """
        total_score = scores.get('total_score', 0)
        verbal_score = scores.get('verbal_score', 0)
        
        if total_score >= 90 and verbal_score >= 85:
            return 'C2'
        elif total_score >= 80 and verbal_score >= 75:
            return 'C1'
        elif total_score >= 70 and verbal_score >= 65:
            return 'B2'
        elif total_score >= 55 and verbal_score >= 50:
            return 'B1'
        elif total_score >= 40 and verbal_score >= 35:
            return 'A2'
        else:
            return 'A1'
    
    def generate_feedback(self, scores: Dict, language: str) -> Dict:
        """
        Generate detailed feedback for the user
        
        Args:
            scores: All evaluation scores
            language: Language code
        
        Returns:
            Dict with structured feedback
        """
        feedback = {
            'overall': '',
            'strengths': [],
            'areas_for_improvement': [],
            'recommendations': []
        }
        
        total_score = scores.get('total_score', 0)
        verbal_score = scores.get('verbal_score', 0)
        paraverbal_score = scores.get('paraverbal_score', 0)
        originality_score = scores.get('originality_score', 0)
        
        # Overall feedback
        if total_score >= 80:
            feedback['overall'] = "Excellent performance! You demonstrate strong communication skills."
        elif total_score >= 60:
            feedback['overall'] = "Good performance! You show solid communication abilities with room for growth."
        elif total_score >= 40:
            feedback['overall'] = "Fair performance. With practice, you can significantly improve."
        else:
            feedback['overall'] = "Keep practicing! There's substantial room for improvement."
        
        # Identify strengths
        if scores.get('fluency_score', 0) >= 70:
            feedback['strengths'].append("Your speech is fluent and natural")
        if scores.get('vocabulary_score', 0) >= 70:
            feedback['strengths'].append("You demonstrate good vocabulary range")
        if scores.get('structure_score', 0) >= 70:
            feedback['strengths'].append("Your grammar and sentence structure are solid")
        if scores.get('pitch_score', 0) >= 70:
            feedback['strengths'].append("Good pitch variation and intonation")
        if scores.get('pace_score', 0) >= 70:
            feedback['strengths'].append("Appropriate speaking pace")
        if originality_score >= 70:
            feedback['strengths'].append("Your content shows creativity and originality")
        
        # Areas for improvement
        if scores.get('fluency_score', 0) < 60:
            feedback['areas_for_improvement'].append("Work on fluency and reducing pauses")
        if scores.get('vocabulary_score', 0) < 60:
            feedback['areas_for_improvement'].append("Expand your vocabulary range")
        if scores.get('structure_score', 0) < 60:
            feedback['areas_for_improvement'].append("Focus on grammar and sentence structure")
        if scores.get('pitch_score', 0) < 60:
            feedback['areas_for_improvement'].append("Add more pitch variation to sound more engaging")
        if scores.get('pace_score', 0) < 60:
            feedback['areas_for_improvement'].append("Adjust your speaking pace")
        if originality_score < 60:
            feedback['areas_for_improvement'].append("Try to be more original and creative in your content")
        
        # Recommendations
        if verbal_score < 60:
            feedback['recommendations'].append("Read more in the target language to improve vocabulary and structure")
            feedback['recommendations'].append("Practice speaking regularly, even if just to yourself")
        if paraverbal_score < 60:
            feedback['recommendations'].append("Record yourself and listen back to improve your delivery")
            feedback['recommendations'].append("Practice with varied intonation and emphasis")
        if originality_score < 60:
            feedback['recommendations'].append("Think critically and develop your own perspectives")
            feedback['recommendations'].append("Explore diverse topics and ideas")
        
        return feedback


# Global service instance
voice_service = VoiceEvaluationService()
