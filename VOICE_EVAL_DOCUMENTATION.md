# Voice Evaluation Module - Documentation

## Overview

The Voice Evaluation Module is an AI-powered system that evaluates spoken language skills in English and French. It provides comprehensive feedback on verbal communication, paraverbal communication, and content originality.

## Features

### 1. **Speech-to-Text Transcription**

- Uses **OpenAI Whisper** (base model) for accurate transcription
- Supports English and French
- Returns full transcription with timestamps

### 2. **Verbal Communication Analysis**

Evaluates three key aspects:

#### **Fluency (0-100)**

- Speech length and coherence
- Sentence variation
- Filler words detection (um, uh, like, euh, ben, etc.)
- Word repetitions

#### **Vocabulary (0-100)**

- Lexical diversity (Type-Token Ratio)
- Word complexity (average word length)
- Part-of-speech variety
- Use of advanced vocabulary

#### **Structure (0-100)**

- Complete sentences (subject + verb)
- Sentence variety
- Proper capitalization and punctuation
- Grammatical correctness

### 3. **Paraverbal Communication Analysis**

Uses **librosa** for audio feature extraction:

#### **Pitch Score (0-100)**

- Pitch variation (intonation)
- Pitch range
- Emotional expressiveness

#### **Pace Score (0-100)**

- Speaking rate (syllables per second)
- Ideal: 3-6 syllables/second
- Pace consistency

#### **Energy Score (0-100)**

- Voice energy and volume
- Dynamic range
- Vocal presence

### 4. **Originality Check**

- Compares content with reference texts in database
- Uses **sentence-transformers** (multilingual-MiniLM-L12-v2)
- Calculates cosine similarity
- Identifies similar content

### 5. **Language Level Determination**

Assigns CEFR levels based on performance:

- **C2** (Proficient): Total ≥90, Verbal ≥85
- **C1** (Advanced): Total ≥80, Verbal ≥75
- **B2** (Upper Intermediate): Total ≥70, Verbal ≥65
- **B1** (Intermediate): Total ≥55, Verbal ≥50
- **A2** (Elementary): Total ≥40, Verbal ≥35
- **A1** (Beginner): Below A2 threshold

### 6. **Personalized Feedback**

- Overall assessment
- Strengths identification
- Areas for improvement
- Specific recommendations

## API Endpoints

### Create Evaluation

```
POST /voice/api/evaluations/
Content-Type: multipart/form-data

Fields:
- audio_file: Audio file (MP3, WAV, M4A, OGG)
- language: 'en' or 'fr'
- theme: (optional) Topic description

Response:
- Complete evaluation with all scores
- Transcription
- Feedback
- Estimated level
```

### List User Evaluations

```
GET /voice/api/evaluations/
Authorization: Token <your-token>

Response:
- List of user's evaluations
- Processing status
- Scores and levels
```

### Get Evaluation Detail

```
GET /voice/api/evaluations/{id}/
Authorization: Token <your-token>

Response:
- Complete evaluation details
- Full transcription
- All scores and metrics
- Feedback
```

### User Progress

```
GET /voice/api/evaluations/my_progress/
Authorization: Token <your-token>

Response:
- Recent evaluations
- History of level changes
- Statistics (average score, improvement, etc.)
```

### Manage Reference Texts (Admin Only)

```
POST /voice/api/references/
Authorization: Token <admin-token>

Fields:
- language: 'en' or 'fr'
- theme: Topic/category
- text: Reference text content
- source: (optional) Source attribution
```

## Web Interface

### Pages

1. **/voice/** - Home page with evaluation history
2. **/voice/record/** - Recording/upload interface
3. **/voice/{id}/** - Detailed evaluation results

### Features

- Live audio recording using browser's MediaRecorder API
- File upload support
- Real-time feedback display
- Progress tracking

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Download spaCy Models

```bash
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
```

### 3. Run Migrations

```bash
python manage.py makemigrations voice_eval
python manage.py migrate
```

### 4. (Optional) Add Reference Texts

Use Django admin or API to add reference texts for originality checking.

## Technical Stack

### AI/ML Libraries

- **openai-whisper**: Speech-to-text transcription
- **spacy**: Natural language processing and analysis
- **sentence-transformers**: Text embedding for similarity
- **librosa**: Audio feature extraction
- **torch**: Deep learning framework (required by above)

### Audio Processing

- **soundfile**: Audio file I/O
- **audioread**: Audio format support
- **numpy**: Numerical computing
- **scipy**: Scientific computing

## Scoring Algorithm

### Total Score Calculation

```
Total Score = (Verbal × 0.4) + (Paraverbal × 0.3) + (Originality × 0.3)

Where:
- Verbal = (Fluency + Vocabulary + Structure) / 3
- Paraverbal = (Pitch + Pace + Energy) / 3
- Originality = Based on similarity with references
```

## Performance Considerations

### First Run

- Models are downloaded/loaded on first use
- Whisper base model: ~140MB
- spaCy models: ~15MB each
- Sentence transformer: ~120MB

### Processing Time

- Transcription: ~1-2 seconds per minute of audio
- NLP analysis: <1 second
- Audio analysis: ~2-3 seconds
- Originality check: <1 second
- **Total**: ~5-10 seconds for 1 minute of audio

### Optimization Tips

1. Use asynchronous task queues (Celery) for production
2. Cache loaded models in memory
3. Implement batch processing for multiple evaluations
4. Consider using lighter Whisper models (tiny, small)

## Database Models

### VoiceEvaluation

Main model storing evaluation results with:

- Audio file reference
- Transcription
- All scores (fluency, vocabulary, structure, etc.)
- Feedback JSON
- Processing status

### ReferenceText

Stores texts for originality comparison with:

- Language and theme
- Text content
- Pre-computed embedding vector

### VoiceEvaluationHistory

Tracks user progress over time with:

- Level changes
- Improvement scores
- Timestamps

## Security Considerations

1. **File Upload Limits**: Set max file size (default: 10MB)
2. **File Type Validation**: Only accept audio formats
3. **Authentication**: All endpoints require authentication
4. **User Isolation**: Users can only access their own evaluations
5. **Admin-Only**: Reference text management requires admin role

## Future Enhancements

1. **More Languages**: Add Spanish, German, Arabic, etc.
2. **Video Support**: Analyze video for non-verbal communication
3. **Pronunciation Analysis**: Detailed phonetic feedback
4. **Real-time Feedback**: Live evaluation during recording
5. **Comparative Analysis**: Compare with native speakers
6. **Practice Mode**: Targeted exercises for improvement
7. **Speech Emotion Recognition**: Detect emotions in speech
8. **Accent Analysis**: Identify and provide feedback on accent

## Troubleshooting

### Common Issues

**Issue**: ModuleNotFoundError for whisper/spacy/etc.
**Solution**: Install requirements: `pip install -r requirements.txt`

**Issue**: spaCy model not found
**Solution**: Download models: `python -m spacy download en_core_web_sm`

**Issue**: Audio file processing fails
**Solution**: Ensure ffmpeg is installed for audio format support

**Issue**: Out of memory errors
**Solution**: Use smaller Whisper model (tiny/small) or increase system RAM

**Issue**: Slow processing
**Solution**: Use GPU acceleration with CUDA-enabled torch

## API Usage Examples

### Python

```python
import requests

# Login to get token
response = requests.post('http://localhost:8000/users/api/login/', json={
    'username': 'student1',
    'password': 'password123'
})
token = response.json()['token']

# Upload audio for evaluation
with open('my_speech.mp3', 'rb') as audio_file:
    response = requests.post(
        'http://localhost:8000/voice/api/evaluations/',
        files={'audio_file': audio_file},
        data={'language': 'en', 'theme': 'My Daily Routine'},
        headers={'Authorization': f'Token {token}'}
    )

evaluation = response.json()
print(f"Total Score: {evaluation['total_score']}")
print(f"Level: {evaluation['estimated_level']}")
print(f"Feedback: {evaluation['feedback']}")
```

### JavaScript (Fetch API)

```javascript
// Upload audio
const formData = new FormData();
formData.append("audio_file", audioBlob, "recording.wav");
formData.append("language", "en");
formData.append("theme", "My Hobby");

const response = await fetch("/voice/api/evaluations/", {
  method: "POST",
  body: formData,
  headers: {
    Authorization: "Token " + userToken,
    "X-CSRFToken": csrfToken,
  },
});

const evaluation = await response.json();
console.log("Score:", evaluation.total_score);
```

## Support

For issues or questions:

1. Check this documentation
2. Review code comments in ai_service.py
3. Check Django logs for errors
4. Ensure all dependencies are installed correctly

## License

This module uses several open-source libraries. Ensure compliance with their licenses:

- Whisper: MIT License
- spaCy: MIT License
- sentence-transformers: Apache 2.0
- librosa: ISC License
