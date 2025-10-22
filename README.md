# 🎓 GenEX - Educational Platform with Voice Evaluation

## Project Overview

**GenEX** is a comprehensive educational platform with an advanced AI-powered voice evaluation system. The platform enables students to improve their language skills through automated speech analysis and personalized feedback.

---

## ✨ Key Features

### 🔐 User Management & Authentication

- Custom user model with role-based access (Admin/Student)
- Token-based API authentication
- Session-based web authentication
- User profiles with skill levels (Weak/Medium/Advanced)
- Progress tracking

### 🎤 Voice Evaluation System (Complete & Functional)

- **AI-Powered Speech Analysis**

  - OpenAI Whisper for speech-to-text
  - spaCy for NLP analysis
  - librosa for audio feature extraction
  - Sentence Transformers for originality detection

- **Multi-dimensional Evaluation**

  - Verbal Communication (Fluency, Vocabulary, Structure)
  - Paraverbal Communication (Pitch, Pace, Energy)
  - Content Originality
  - CEFR Level Assignment (A1-C2)

- **Personalized Feedback**

  - Strengths identification
  - Areas for improvement
  - Specific recommendations
  - Progress tracking over time

- **User-Friendly Interfaces**
  - Web interface with live recording
  - RESTful API for integration
  - Django admin for management

### 📚 Additional Modules (Ready for Development)

- Courses Management
- Interactive Exercises
- Quizzes & Assessments
- AI Chat Tutor
- Progress Analytics

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip
- Virtual environment (venv)

### Installation

1. **Clone the repository**

```powershell
cd "d:\OneDrive\Bureau\GenEX"
```

2. **Activate virtual environment**

```powershell
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Download AI models**

```powershell
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
```

5. **Run migrations**

```powershell
python manage.py migrate
```

6. **Create superuser**

```powershell
python manage.py createsuperuser
```

7. **Start development server**

```powershell
python manage.py runserver
```

8. **Access the platform**

- Main Site: http://127.0.0.1:8000/
- Admin Panel: http://127.0.0.1:8000/admin/
- Voice Evaluation: http://127.0.0.1:8000/voice/

---

## 📁 Project Structure

```
GenEX/
├── GenEX/                      # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── users/                      # User management
│   ├── models.py               # Custom User model
│   ├── views.py                # Auth views
│   ├── serializers.py          # API serializers
│   └── urls.py
│
├── voice_eval/                 # Voice evaluation module
│   ├── models.py               # Evaluation models
│   ├── views.py                # API & web views
│   ├── ai_service.py           # AI processing service
│   ├── serializers.py          # API serializers
│   ├── urls.py
│   └── admin.py
│
├── courses/                    # Courses module
├── exercises/                  # Exercises module
├── quizzes/                    # Quizzes module
├── chat_tutor/                 # AI Chat module
│
├── templates/                  # HTML templates
│   ├── users/
│   └── voice_eval/
│
├── media/                      # User uploads (audio files)
├── manage.py
└── requirements.txt
```

---

## 🔧 Technology Stack

### Backend

- **Framework**: Django 4.2+
- **API**: Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Token-based + Session-based

### AI/ML

- **Speech-to-Text**: OpenAI Whisper
- **NLP**: spaCy (English & French models)
- **Text Embeddings**: Sentence Transformers
- **Audio Analysis**: librosa
- **Deep Learning**: PyTorch

### Frontend

- HTML5, CSS3, JavaScript
- Web Audio API for recording
- Responsive design

---

## 📊 API Endpoints

### Authentication

```
POST /users/api/register/          - Register new user
POST /users/api/login/             - Login and get token
POST /users/api/logout/            - Logout and destroy token
GET  /users/api/profile/           - Get user profile
```

### Voice Evaluation

```
POST /voice/api/evaluations/       - Submit audio for evaluation
GET  /voice/api/evaluations/       - List user's evaluations
GET  /voice/api/evaluations/{id}/  - Get evaluation details
GET  /voice/api/evaluations/my_progress/  - Get progress stats
POST /voice/api/references/        - Add reference text (admin)
GET  /voice/api/languages/         - Get supported languages
```

---

## 🎯 Voice Evaluation Scoring

### Score Components

- **Verbal Communication** (40%)

  - Fluency: Speech flow, coherence
  - Vocabulary: Word diversity, complexity
  - Structure: Grammar, sentence formation

- **Paraverbal Communication** (30%)

  - Pitch: Intonation, variation
  - Pace: Speaking speed, rhythm
  - Energy: Volume, dynamics

- **Content Originality** (30%)
  - Uniqueness vs reference texts
  - Creative expression

### CEFR Levels

| Level | Score Range | Description        |
| ----- | ----------- | ------------------ |
| C2    | 90-100      | Proficient         |
| C1    | 80-89       | Advanced           |
| B2    | 70-79       | Upper Intermediate |
| B1    | 55-69       | Intermediate       |
| A2    | 40-54       | Elementary         |
| A1    | 0-39        | Beginner           |

---

## 📖 Documentation

- **[VOICE_EVAL_QUICKSTART.md](VOICE_EVAL_QUICKSTART.md)** - Quick start guide
- **[VOICE_EVAL_DOCUMENTATION.md](VOICE_EVAL_DOCUMENTATION.md)** - Complete technical docs
- **[VOICE_EVAL_SUMMARY.md](VOICE_EVAL_SUMMARY.md)** - Implementation summary

---

## 🧪 Testing

### Testing the Voice Evaluation

1. **Login** to the platform
2. Navigate to **Voice Evaluation** (`/voice/`)
3. Click **"Start Evaluation"**
4. Choose **language** (English or French)
5. **Record** or **upload** audio (30-180 seconds)
6. Submit and view **results**

### API Testing (with curl)

```powershell
# Login
curl -X POST http://127.0.0.1:8000/users/api/login/ `
  -H "Content-Type: application/json" `
  -d '{"username":"admin","password":"yourpassword"}'

# Upload audio
curl -X POST http://127.0.0.1:8000/voice/api/evaluations/ `
  -H "Authorization: Token YOUR_TOKEN" `
  -F "audio_file=@test.mp3" `
  -F "language=en" `
  -F "theme=My Hobby"
```

---

## 🔒 Security

- ✅ CSRF protection enabled
- ✅ Token-based authentication
- ✅ User data isolation
- ✅ File upload validation
- ✅ Admin-only sensitive operations
- ⚠️ For production: Set DEBUG=False, configure HTTPS, set strong SECRET_KEY

---

## 📦 Dependencies

### Core

```
Django>=4.2.0
djangorestframework>=3.14.0
```

### AI/ML

```
openai-whisper>=20231117
spacy>=3.7.0
sentence-transformers>=2.2.2
librosa>=0.10.0
torch>=2.0.0
transformers>=4.30.0
```

### Audio Processing

```
soundfile>=0.12.1
audioread>=3.0.0
```

### See `requirements.txt` for complete list

---

## 🌍 Supported Languages

Currently supported for voice evaluation:

- 🇬🇧 English
- 🇫🇷 French

**Easy to extend** to other languages by:

1. Adding spaCy language models
2. Updating language choices in models
3. Adding reference texts

---

## 🚦 System Status

| Module           | Status             | Description              |
| ---------------- | ------------------ | ------------------------ |
| User Management  | ✅ Complete        | Auth, profiles, progress |
| Voice Evaluation | ✅ Complete        | Full AI-powered analysis |
| Courses          | 🔧 Structure Ready | Needs implementation     |
| Exercises        | 🔧 Structure Ready | Needs implementation     |
| Quizzes          | 🔧 Structure Ready | Needs implementation     |
| Chat Tutor       | 🔧 Structure Ready | Needs implementation     |

---

## 💡 Future Enhancements

### Voice Evaluation

- [ ] More languages (Spanish, German, Arabic, Chinese)
- [ ] Video analysis with facial expressions
- [ ] Pronunciation analysis
- [ ] Real-time feedback
- [ ] Emotion recognition
- [ ] Accent analysis

### Platform

- [ ] Course content management
- [ ] Interactive exercises
- [ ] Quiz system
- [ ] AI-powered chat tutor
- [ ] Gamification (badges, leaderboards)
- [ ] Mobile app
- [ ] Analytics dashboard

---

## 🤝 Contributing

This is an educational project. Areas that need development:

1. Other module implementations (courses, exercises, quizzes)
2. UI/UX improvements
3. Additional language support
4. Performance optimization
5. Test coverage

---

## ⚠️ Known Issues & Limitations

1. **First run is slow**: AI models need to download/load (one-time)
2. **Memory usage**: ~1-2GB RAM with all models loaded
3. **Processing time**: ~5-10 seconds per evaluation
4. **File size**: Current limit is 10MB for audio files
5. **Languages**: Currently only EN/FR supported

---

## 📝 License

This project uses several open-source libraries. Ensure compliance with:

- Django: BSD License
- Whisper: MIT License
- spaCy: MIT License
- sentence-transformers: Apache 2.0
- librosa: ISC License

---

## 👨‍💻 Development Team

Built for GenEX Educational Platform

---

## 📞 Support

For questions or issues:

1. Check documentation in the project root
2. Review code comments in `voice_eval/ai_service.py`
3. Check Django admin for data management
4. Review error logs in console

---

## 🎉 Getting Started Checklist

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] spaCy models downloaded
- [ ] Database migrated
- [ ] Superuser created
- [ ] Server running
- [ ] Voice evaluation tested
- [ ] Admin panel accessed

---

**Ready to transform language education with AI! 🚀📚🎤**
