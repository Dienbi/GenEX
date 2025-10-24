# GenEx Voice Evaluation - New Features Setup Guide

## 🎉 New Features Added

### For High Scores (≥70%)

1. **PDF Certificate Generation** with QR code
2. **Interactive Map** showing testing centers for professional certification
3. **LinkedIn Sharing** capability

### For Low Scores (<70%)

1. **Real-time Pronunciation Trainer** with Vosk API
2. **Word-by-word Comparison** (green for correct, red for incorrect)
3. **Sound Practice Exercises** with text-to-speech
4. **App Recommendations** (Duolingo, Babbel, etc.)

## 📦 Installation Steps

### 1. Install Required Python Packages

All dependencies are already in `requirements.txt`. Install them:

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

Key packages installed:

- `reportlab` - PDF generation
- `qrcode` - QR code generation
- `Pillow` - Image processing
- `vosk` - Real-time speech recognition
- `folium` - Interactive maps

### 2. Download Vosk Models

Vosk requires language models for speech recognition. Download them:

**English Model:**

```powershell
# Create directory
mkdir ml_models\vosk

# Download (visit https://alphacephei.com/vosk/models)
# Download: vosk-model-small-en-us-0.15.zip
# Extract to: ml_models\vosk\vosk-model-small-en-us-0.15\
```

**French Model:**

```powershell
# Download: vosk-model-small-fr-0.22.zip
# Extract to: ml_models\vosk\vosk-model-small-fr-0.22\
```

**Direct download links:**

- English: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
- French: https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip

### 3. Create Database Migrations

```powershell
python manage.py makemigrations voice_eval
python manage.py migrate
```

### 4. Create Testing Centers (Optional)

Add some testing centers via Django admin or shell:

```powershell
python manage.py shell
```

```python
from voice_eval.models import TestingCenter

# Example for Tunisia (ESPRIT location)
TestingCenter.objects.create(
    name="ESPRIT - École Supérieure Privée d'Ingénierie et de Technologies",
    address="Rue Kazem Radhia, Ariana",
    city="Tunis",
    country="Tunisia",
    latitude=36.8986,
    longitude=10.1899,
    phone="+216 71 250 000",
    email="info@esprit.tn",
    website="https://esprit.tn",
    languages=["en", "fr"],
    certifications=["TOEFL", "TOEIC", "DELF", "DALF"],
    is_active=True
)

# Add more centers for different countries
TestingCenter.objects.create(
    name="British Council Paris",
    address="9 Rue de Constantine",
    city="Paris",
    country="France",
    latitude=48.8534,
    longitude=2.3488,
    phone="+33 1 49 55 73 00",
    email="exams@britishcouncil.fr",
    website="https://www.britishcouncil.fr",
    languages=["en", "fr"],
    certifications=["IELTS", "Cambridge English", "TOEFL"],
    is_active=True
)
```

### 5. Start the Development Server

```powershell
python manage.py runserver
```

## 🎯 How to Use New Features

### Testing High Score Features (Score ≥ 70%)

1. **Upload a voice evaluation** that will score ≥70%
2. **View results** - You'll see a green "Félicitations" section with:

   - 📜 Download PDF Certificate button
   - 🗺️ View Testing Centers Map button
   - 🔗 Share on LinkedIn button

3. **Generate Certificate:**

   - Click "Télécharger mon Certificat PDF"
   - PDF includes: Your name, score, level, QR code, GenEx branding
   - QR code links to platform homepage

4. **View Testing Centers:**

   - Click "Centres d'Examen"
   - Interactive map with markers
   - Click markers for center details

5. **Share on LinkedIn:**
   - Click "Partager sur LinkedIn"
   - Opens LinkedIn share dialog
   - Customize your post

### Testing Low Score Features (Score < 70%)

1. **Upload a voice evaluation** that scores <70%
2. **View results** - You'll see a blue "Continuez à Progresser" section with:

   - 🎤 Pronunciation Practice
   - 🔊 Sound Exercises
   - 📱 App Recommendations

3. **Pronunciation Practice:**

   - Click "Entraînement Prononciation"
   - Select a text to practice
   - Record your pronunciation
   - See word-by-word comparison (green/red)
   - Get accuracy score

4. **Sound Practice:**

   - Click "Exercices de Sons"
   - Practice difficult sounds (TH, R, L, etc.)
   - Click to hear pronunciation
   - Use text-to-speech for practice

5. **App Recommendations:**
   - Click "Applications Recommandées"
   - See personalized app suggestions
   - Based on your level (A1-C2)
   - Direct links to Duolingo, Babbel, etc.

## 🔧 Configuration

### Update Site URL (for production):

In `GenEX/settings.py`:

```python
# Change this to your production URL
SITE_URL = 'https://your-domain.com'
```

### Customize Testing Centers:

Add via Django Admin:

1. Go to `http://127.0.0.1:8000/admin/`
2. Navigate to Voice Eval → Testing Centers
3. Add New Testing Center

## 📁 File Structure

New files added:

```
voice_eval/
├── certificate_service.py      # PDF certificate generation
├── pronunciation_service.py    # Vosk-based pronunciation practice
├── map_service.py             # Folium map generation
└── models.py                  # New models: Certificate, PronunciationPractice, TestingCenter

templates/voice_eval/
├── detail.html                # Updated with conditional sections
├── certificate_map.html       # Testing centers map page
├── pronunciation_practice.html # Pronunciation trainer
├── app_recommendations.html   # App suggestions
└── sound_practice.html        # Sound exercises
```

## 🐛 Troubleshooting

### Vosk Models Not Loading

**Error:** `Vosk model not found at ...`

**Solution:**

```powershell
# Check if models exist
dir ml_models\vosk\

# Should see:
# - vosk-model-small-en-us-0.15\
# - vosk-model-small-fr-0.22\

# If not, download and extract from:
# https://alphacephei.com/vosk/models
```

### PDF Generation Error

**Error:** `No module named 'reportlab'`

**Solution:**

```powershell
pip install reportlab qrcode Pillow
```

### Map Not Displaying

**Error:** Map shows blank or doesn't load

**Solution:**

1. Check internet connection (needs OpenStreetMap tiles)
2. Check browser console for JavaScript errors
3. Ensure testing centers exist in database

### Microphone Access Denied

**Error:** `Permission denied` when recording

**Solution:**

1. Allow microphone access in browser settings
2. Use HTTPS in production (required for getUserMedia API)
3. Check Windows microphone permissions

## 🎨 Customization

### Change Certificate Design:

Edit `voice_eval/certificate_service.py`:

- Colors: Search for `#dc3545` (red) and `#000` (black)
- Layout: Modify `_add_*` methods
- Logo: Add image in `_add_header` method

### Add More Practice Texts:

Edit `voice_eval/pronunciation_service.py`:

- Method: `get_practice_texts()`
- Add texts for different difficulty levels

### Customize App Recommendations:

Edit `voice_eval/pronunciation_service.py`:

- Method: `get_app_recommendations()`
- Add new apps or modify existing ones

## 📊 Testing

### Test Certificate Generation:

```powershell
python manage.py shell
```

```python
from voice_eval.models import VoiceEvaluation
from users.models import User

# Get a high-scoring evaluation
user = User.objects.first()
eval = VoiceEvaluation.objects.filter(total_score__gte=70).first()

# Generate certificate
from voice_eval.certificate_service import certificate_generator
pdf = certificate_generator.generate_certificate(user, eval, eval.id)
print("Certificate generated successfully!")
```

### Test Pronunciation Service:

```python
from voice_eval.pronunciation_service import pronunciation_service

# Test text comparison
result = pronunciation_service.compare_texts(
    "Hello world how are you",
    "Hello world how you"
)
print(f"Accuracy: {result['accuracy_score']}%")
print(f"Matches: {result['matched_words']}/{result['total_words']}")
```

## 🚀 Next Steps

1. **Add more testing centers** worldwide
2. **Collect user feedback** on practice features
3. **Enhance certificate design** with your branding
4. **Add analytics** to track feature usage
5. **Implement email notifications** for certificates
6. **Add social media sharing** for other platforms

## 📞 Support

If you encounter any issues:

1. Check Django logs
2. Check browser console (F12)
3. Verify all dependencies are installed
4. Ensure migrations are applied
5. Check file permissions for media uploads

## ✅ Verification Checklist

- [ ] All packages installed from requirements.txt
- [ ] Vosk models downloaded and placed in ml_models/vosk/
- [ ] Migrations created and applied
- [ ] Testing centers added (at least one)
- [ ] High score test (≥70%) shows certificate options
- [ ] Low score test (<70%) shows practice options
- [ ] PDF certificate downloads successfully
- [ ] Map displays testing centers
- [ ] Pronunciation practice records audio
- [ ] Sound practice uses text-to-speech
- [ ] App recommendations display correctly

---

**🎓 All features are now FREE to use and integrated with the ESPRIT university design theme!**
