
# 🧱 ARCHITECTURE_GUIDELINES.md

## 📂 Project Overview
This repository follows a **Django project structure**.  
The architecture must remain clean, modular, and respect Django’s MVC (Model-View-Template) pattern.

---

## 📁 Directory Structure (Generic)
```
project_root/
│
├── manage.py
├── db.sqlite3
├── requirements.txt
├── README.md
│
├── media/                  # Uploaded files (images, audio, etc.)
│
├── app_name/               # Example: quizzes, users, voice_eval, etc.
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│
├── templates/
│   ├── app_name/
│   │   ├── example.html
│   │   └── widget.html
│
├── venv/                   # Virtual environment (ignored in Git)
│
└── .gitignore
```

---

## ⚙️ App Focus — `quizzes`

### Purpose:
The **`quizzes`** app manages quiz data, including models, views, serializers, and API routes.

### Files Responsibilities:
- **`models.py`** → Define all database models related to quizzes.  
- **`serializers.py`** → Handle data conversion between Python objects and JSON for API use.  
- **`views.py`** → Define logic for handling quiz-related requests (CRUD operations, API endpoints).  
- **`urls.py`** → Register local routes (e.g., `/api/quizzes/`, `/api/quizzes/<id>/`).  
- **`tests.py`** → Contain unit tests for all `quizzes` features.  
- **`admin.py`** → Register models for the Django admin panel.  

All code must follow Django’s standard **app separation** rules — no mixing templates, logic, or models from other apps unless imported properly.

---

## 🧩 Templates Guidelines
- Store HTML files under `templates/<app_name>/`.
- Each app manages its own templates folder.
- Use `{% extends "base.html" %}` when applicable.
- Static resources (CSS/JS) must be referenced using `{% load static %}` and placed in `/static/<app_name>/`.

---

## 🧠 Development Rules
- All Django imports must follow the standard order:  
  ```python
  from django.shortcuts import render, get_object_or_404
  from django.http import JsonResponse
  from rest_framework import serializers, viewsets
  ```
- Use **class-based views** when possible.
- Use **Django REST Framework (DRF)** conventions if API endpoints are required.
- Follow **PEP8** Python style guide.

---

## 🧪 Testing
Each feature added to `quizzes` must include a test function in `tests.py`.  
Example:
```python
from django.test import TestCase
from .models import Quiz

class QuizModelTest(TestCase):
    def test_quiz_creation(self):
        quiz = Quiz.objects.create(title="Sample Quiz")
        self.assertEqual(str(quiz), "Sample Quiz")
```

---

## 🧭 General Constraints
- Never modify core Django settings unless explicitly required.
- Keep migrations in sync with models using:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
- All new endpoints must be registered in the app’s `urls.py` and included in the project-level `urls.py`.

---

## ⚙️ Useful Commands

### Run Development Server
```bash
python manage.py runserver
```

### Create a New App
```bash
python manage.py startapp <app_name>
```

### Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run Tests
```bash
python manage.py test
```

---

## ✅ Summary of Rules for Cursor
1. Always respect Django folder structure and naming conventions.  
2. Focus development inside the **`quizzes`** app when working on quiz-related logic.  
3. Do not break app encapsulation — each app manages its own models, views, templates, and URLs.  
4. Ensure Python code is **syntax-valid**, **PEP8 compliant**, and **Django-compatible**.  
5. All database-related changes go through Django’s ORM and migrations system.
