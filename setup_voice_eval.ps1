# Installation and Setup Script for Voice Evaluation Module

Write-Host "=== GenEX Voice Evaluation Module Setup ===" -ForegroundColor Green
Write-Host ""

# Check if virtual environment is activated
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
}

Write-Host "Installing Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "Downloading spaCy language models..." -ForegroundColor Yellow
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm

Write-Host ""
Write-Host "Running migrations..." -ForegroundColor Yellow
python manage.py makemigrations voice_eval
python manage.py migrate

Write-Host ""
Write-Host "=== Setup Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "To test the voice evaluation module:" -ForegroundColor Cyan
Write-Host "  1. Start the server: python manage.py runserver" -ForegroundColor White
Write-Host "  2. Visit: http://127.0.0.1:8000/voice/" -ForegroundColor White
Write-Host "  3. Or use API: http://127.0.0.1:8000/voice/api/evaluations/" -ForegroundColor White
Write-Host ""
Write-Host "Note: First run may be slow as AI models are loaded" -ForegroundColor Yellow
