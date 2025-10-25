# 🚀 Quick Start - AI Quiz Generator

## ⚡ 3-Step Setup

### 1️⃣ Get Your Gemini API Key
Visit: https://makersuite.google.com/app/apikey

### 2️⃣ Add to Environment
Create `.env` file in project root:
```
GEMINI_API_KEY=your-key-here
```

### 3️⃣ Start Using!
```bash
python manage.py runserver
```

Go to: http://localhost:8000/quizzes/

## 🎯 Quick Usage

1. Click "Generate New Quiz"
2. Enter subject: `Python Programming`
3. Enter prompt: `Create questions about Python functions, loops, and data structures for beginners`
4. Click "Generate Quiz" (wait 10-20 seconds)
5. Answer all 10 questions
6. Submit and see your score!

## 📍 URLs

- **Quiz Hub**: `/quizzes/`
- **Generate**: `/quizzes/generate/`
- **Dashboard**: `/` (has link to quizzes)
- **Admin**: `/admin/` (manage quizzes)

## ✨ Features

- ✅ AI-generated quizzes on ANY topic
- ✅ 10 multiple-choice questions
- ✅ Instant results with detailed review
- ✅ Save and retake quizzes
- ✅ Track your progress
- ✅ Beautiful UI matching GenEX design

## 🎨 Example Prompts

```
"Create a quiz about World War II focusing on key battles and dates"

"Generate questions about JavaScript ES6 features like arrow functions, promises, and async/await"

"Test my knowledge of photosynthesis and cellular respiration for high school level"

"Create questions about Django models, views, and templates for intermediate developers"
```

## 🔧 Tech Stack

- **AI Model**: Google Gemini 2.0 Flash
- **Framework**: Django 4.2+
- **Frontend**: Vanilla JS + CSS (matching GenEX design)
- **Database**: SQLite (default)

Done! You're ready to generate quizzes! 🎉

