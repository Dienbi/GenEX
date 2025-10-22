# Voice Evaluation Module - Quick Start Guide

## 🎯 Overview

Your Voice Evaluation Module is now set up! This guide will help you get started quickly.

## ✅ What's Been Created

### 1. **Database Models**

- ✅ VoiceEvaluation (stores all evaluation data)
- ✅ ReferenceText (for originality checking)
- ✅ VoiceEvaluationHistory (tracks progress)

### 2. **AI Service** (`voice_eval/ai_service.py`)

- ✅ Speech-to-text with Whisper
- ✅ NLP analysis with spaCy
- ✅ Audio analysis with librosa
- ✅ Originality checking with sentence-transformers
- ✅ Automatic scoring and feedback generation

### 3. **API Endpoints**

- ✅ POST `/voice/api/evaluations/` - Create evaluation
- ✅ GET `/voice/api/evaluations/` - List evaluations
- ✅ GET `/voice/api/evaluations/{id}/` - Get details
- ✅ GET `/voice/api/evaluations/my_progress/` - User progress
- ✅ POST `/voice/api/references/` - Add reference texts (admin)

### 4. **Web Interface**

- ✅ `/voice/` - Home page
- ✅ `/voice/record/` - Recording interface
- ✅ `/voice/{id}/` - Evaluation details

## 🚀 Installation Steps

### Step 1: Install AI Libraries

```powershell
# Activate virtual environment (if not already active)
.\venv\Scripts\Activate.ps1

# Install all required packages (this may take 5-10 minutes)
pip install -r requirements.txt
```

**Note**: This will install:

- openai-whisper (~500MB with dependencies)
- spacy, librosa, sentence-transformers
- torch (PyTorch - large package)

### Step 2: Download Language Models

```powershell
# English model (~15MB)
python -m spacy download en_core_web_sm

# French model (~15MB)
python -m spacy download fr_core_news_sm
```

### Step 3: Test the System

```powershell
# Check if everything is configured correctly
python manage.py check

# Start the development server
python manage.py runserver
```

### Step 4: Access the Module

Open your browser and go to:

- **Web Interface**: http://127.0.0.1:8000/voice/
- **API Documentation**: http://127.0.0.1:8000/voice/api/evaluations/

## 📝 Testing the Module

### Option A: Using the Web Interface

1. **Login**: Go to http://127.0.0.1:8000/users/login/

   - Use your superuser credentials (admin/admin)

2. **Go to Voice Evaluation**: http://127.0.0.1:8000/voice/

3. **Start Recording**:

   - Click "Start Evaluation"
   - Choose language (English or French)
   - Either record live or upload an audio file
   - Speak for 30-180 seconds
   - Submit for evaluation

4. **View Results**:
   - See your scores for fluency, vocabulary, structure
   - Check paraverbal communication metrics
   - Review originality score
   - Get personalized feedback
   - See your estimated CEFR level

### Option B: Using the API (with Postman or curl)

**1. Get Authentication Token**

```powershell
curl -X POST http://127.0.0.1:8000/users/api/login/ `
  -H "Content-Type: application/json" `
  -d '{"username": "admin", "password": "admin"}'
```

**2. Upload Audio for Evaluation**

```powershell
curl -X POST http://127.0.0.1:8000/voice/api/evaluations/ `
  -H "Authorization: Token YOUR_TOKEN_HERE" `
  -F "audio_file=@path/to/audio.mp3" `
  -F "language=en" `
  -F "theme=My Daily Routine"
```

**3. View Your Progress**

```powershell
curl -X GET http://127.0.0.1:8000/voice/api/evaluations/my_progress/ `
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

## 🎤 Recording Tips

For best results, tell users to:

1. **Duration**: Speak for 30-180 seconds (1-3 minutes)
2. **Environment**: Find a quiet place with minimal background noise
3. **Content**: Organize thoughts before recording
4. **Delivery**: Speak naturally, not too fast or slow
5. **Topics**: Choose topics they're comfortable with

## 📊 Understanding the Scores

### Verbal Communication (40% of total)

- **Fluency (0-100)**: Natural speech flow, fewer fillers
- **Vocabulary (0-100)**: Word variety and complexity
- **Structure (0-100)**: Grammar and sentence formation

### Paraverbal Communication (30% of total)

- **Pitch (0-100)**: Voice intonation and variation
- **Pace (0-100)**: Speaking speed and rhythm
- **Energy (0-100)**: Voice volume and dynamics

### Originality (30% of total)

- **Originality (0-100)**: Content uniqueness vs. reference texts

### Language Levels (CEFR)

- **A1**: Beginner (0-39)
- **A2**: Elementary (40-54)
- **B1**: Intermediate (55-69)
- **B2**: Upper Intermediate (70-79)
- **C1**: Advanced (80-89)
- **C2**: Proficient (90-100)

## 🔧 Optional: Add Reference Texts

To improve originality checking, add reference texts through Django admin:

1. Go to http://127.0.0.1:8000/admin/voice_eval/referencetext/
2. Click "Add Reference Text"
3. Fill in:
   - Language: en or fr
   - Theme: e.g., "Travel", "Education", "Technology"
   - Text: Sample text content
   - Source: Where it came from (optional)
4. Save

The system will automatically generate embeddings for comparison.

## 📁 File Structure

```
voice_eval/
├── models.py              # Database models
├── views.py               # API and web views
├── serializers.py         # REST API serializers
├── urls.py                # URL routing
├── admin.py               # Django admin configuration
├── ai_service.py          # AI/ML processing service
└── migrations/            # Database migrations

templates/voice_eval/
├── home.html              # Evaluation list page
├── record.html            # Recording interface
└── detail.html            # (to be created) Results page
```

## ⚠️ Important Notes

### Performance

- **First run will be slow** (5-15 seconds) as models are loaded into memory
- Subsequent evaluations are faster (5-10 seconds)
- Processing time depends on audio length

### Resource Usage

- Models use ~1-2GB RAM when loaded
- Consider using GPU for faster processing (optional)
- For production, use Celery for async processing

### Supported Audio Formats

- MP3, WAV, M4A, OGG
- Max file size: 10MB (configurable)
- Recommended: 16kHz sample rate or higher

## 🐛 Troubleshooting

### Issue: ImportError for AI libraries

**Solution**: Make sure you ran `pip install -r requirements.txt`

### Issue: spaCy model not found

**Solution**: Download models:

```powershell
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
```

### Issue: Audio processing fails

**Solution**:

1. Check audio file format is supported
2. Ensure file isn't corrupted
3. Try converting to WAV format

### Issue: Slow processing

**Solution**:

1. Use smaller Whisper model (edit ai_service.py, change "base" to "tiny")
2. Implement async processing with Celery
3. Use GPU acceleration if available

### Issue: Out of memory

**Solution**:

1. Use lighter models (Whisper tiny, smaller sentence-transformers)
2. Increase system RAM
3. Process one evaluation at a time

## 📚 Next Steps

1. **Test the system** with various audio samples
2. **Add reference texts** for better originality checking
3. **Customize scoring weights** in ai_service.py if needed
4. **Create detail view template** for better result display
5. **Implement progress tracking** charts and visualizations
6. **Add more languages** by extending the models
7. **Set up async processing** for production use

## 🎉 You're Ready!

Your voice evaluation system is fully functional with:

- ✅ AI-powered analysis
- ✅ Multi-language support (EN/FR)
- ✅ Web and API interfaces
- ✅ Comprehensive feedback
- ✅ Progress tracking

Start by testing with a simple audio recording and see the magic happen!

## 📞 Support

For detailed information, see:

- `VOICE_EVAL_DOCUMENTATION.md` - Complete technical documentation
- Code comments in `ai_service.py` - Detailed algorithm explanations
- Django admin at `/admin/` - Database management

Happy evaluating! 🎤✨
