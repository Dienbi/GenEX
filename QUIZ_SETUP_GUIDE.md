# 🎯 AI Quiz Generator - Setup Guide

## 📋 Overview
The AI Quiz Generator is now fully integrated into GenEX! It uses Google's Gemini 2.0 Flash model to generate custom quizzes on any topic.

## ✅ What Has Been Implemented

### 1. **Database Models** (`quizzes/models.py`)
- `Quiz`: Stores quiz information (title, subject, creator, prompt)
- `Question`: Stores individual questions with 4 options (A, B, C, D) and correct answer
- `QuizAttempt`: Tracks user attempts, scores, and answers

### 2. **AI Service** (`quizzes/ai_service.py`)
- `GeminiQuizGenerator`: Integrates with Google Gemini API
- Generates 10 multiple-choice questions based on user prompt
- Returns structured JSON responses

### 3. **Views & Logic** (`quizzes/views.py`)
- `quiz_home`: Main quiz hub showing user's quizzes and attempts
- `generate_quiz_view`: Form to generate new quizzes with AI
- `take_quiz_view`: Display all 10 questions at once
- `submit_quiz_view`: Process answers and calculate score
- `quiz_results_view`: Show detailed results with correct/incorrect answers
- REST API endpoints (optional)

### 4. **Beautiful Templates**
- `home.html`: Quiz hub with user's quizzes and recent attempts
- `generate.html`: AI quiz generation form with examples
- `take_quiz.html`: Interactive quiz interface with progress tracker
- `results.html`: Detailed results page with score breakdown

### 5. **Admin Panel** (`quizzes/admin.py`)
- Full admin interface for managing quizzes, questions, and attempts
- Inline question editing
- Read-only attempt viewing

## 🚀 Setup Instructions

### Step 1: Install Dependencies
The required package has already been installed, but if you need to reinstall:
```bash
pip install google-generativeai
```

### Step 2: Get Gemini API Key
1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### Step 3: Configure API Key
Create a `.env` file in your project root (or set environment variable):
```bash
GEMINI_API_KEY=your-api-key-here
```

Or add it directly to `GenEX/settings.py` (not recommended for production):
```python
GEMINI_API_KEY = 'your-api-key-here'
```

### Step 4: Run the Server
```bash
python manage.py runserver
```

### Step 5: Access the Quiz System
- **Main Quiz Hub**: http://localhost:8000/quizzes/
- **Generate Quiz**: http://localhost:8000/quizzes/generate/
- **Dashboard**: http://localhost:8000/ (has link to Quiz Generator)

## 🎮 How to Use

### Generating a Quiz
1. Click "Generate New Quiz" button
2. Enter a subject (e.g., "Python Programming")
3. Provide detailed description:
   - Topics you want covered
   - Difficulty level
   - Any special focus areas
4. Click "Generate Quiz"
5. Wait 10-20 seconds for AI to create 10 questions
6. Start taking the quiz immediately!

### Taking a Quiz
1. All 10 questions appear at once
2. Select one answer (A, B, C, or D) for each question
3. Progress tracker shows how many questions you've answered
4. Click "Submit Quiz" when done
5. Results appear immediately!

### Viewing Results
- See your score percentage
- View each question with:
  - Your answer
  - Correct answer (if you got it wrong)
  - Visual indicators (✓ or ✗)
- Option to retake the quiz or generate a new one

## 📁 File Structure
```
GenEX/
├── quizzes/
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── urls.py             # URL patterns
│   ├── serializers.py      # REST API serializers
│   ├── admin.py            # Admin configuration
│   ├── ai_service.py       # Gemini AI integration
│   └── migrations/
│       └── 0001_initial.py # Database schema
├── templates/
│   └── quizzes/
│       ├── home.html       # Quiz hub
│       ├── generate.html   # Generation form
│       ├── take_quiz.html  # Quiz interface
│       └── results.html    # Results display
└── .env                    # Environment variables (create this)
```

## 🔧 Configuration

### Gemini Model Settings
Currently using: `gemini-2.0-flash-exp` (fast and efficient)

To change the model, edit `quizzes/ai_service.py`:
```python
self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
```

Available models:
- `gemini-2.0-flash-exp` (recommended - fast)
- `gemini-1.5-pro` (more advanced but slower)
- `gemini-1.5-flash` (balanced)

## 🎨 Features

### Quiz Generation
- ✅ AI-powered question generation
- ✅ 10 multiple-choice questions
- ✅ 4 options per question (A, B, C, D)
- ✅ Only one correct answer per question
- ✅ Customizable by subject and requirements
- ✅ Stores quiz in database for reuse

### Quiz Taking
- ✅ All questions displayed at once
- ✅ Progress tracker
- ✅ Visual feedback on selection
- ✅ Prevents accidental page close
- ✅ Instant score calculation

### Results
- ✅ Percentage score with visual indicator
- ✅ Correct/incorrect breakdown
- ✅ Detailed review of each question
- ✅ Shows user's answer vs correct answer
- ✅ Color-coded results (green/red)
- ✅ Retake option

### History & Tracking
- ✅ View all your generated quizzes
- ✅ See recent attempts with scores
- ✅ Track progress over time
- ✅ Quiz stored permanently

## 🛠️ Troubleshooting

### "GEMINI_API_KEY not found"
**Solution**: Make sure you've set the API key in `.env` file or as environment variable

### "Error generating quiz"
**Possible causes**:
1. Invalid API key
2. API quota exceeded (check Google Cloud Console)
3. Network issues
4. Prompt too vague

**Solution**: Try a more specific prompt with clear requirements

### Quiz not generating
**Check**:
1. API key is valid
2. `google-generativeai` package is installed
3. Internet connection is working
4. Check console logs for error details

## 🔐 Security Notes

- **Never commit** `.env` file to Git
- **Never share** your API key publicly
- Use environment variables in production
- Consider rate limiting for production use

## 📊 Database Schema

### Quiz Table
- id, title, subject, user_prompt, created_by, created_at, is_active

### Question Table
- id, quiz_id, question_text, option_a, option_b, option_c, option_d, correct_answer, order

### QuizAttempt Table
- id, quiz_id, user_id, score, total_questions, percentage, answers (JSON), completed_at

## 🚀 Next Steps

### Suggested Enhancements
1. Add timer for quizzes
2. Leaderboards
3. Categories/tags for quizzes
4. Difficulty levels
5. Share quizzes with other users
6. Export results as PDF
7. Analytics dashboard
8. Question explanations

## 📞 Support

If you encounter any issues:
1. Check the error message in browser console
2. Review `GEMINI_API_KEY` setup
3. Ensure all migrations are applied
4. Check Django logs for detailed errors

## 🎉 Success!

Your AI Quiz Generator is now ready to use! Start by:
1. Adding your Gemini API key
2. Visiting `/quizzes/`
3. Generating your first quiz!

Enjoy learning with AI-powered quizzes! 🧠✨

