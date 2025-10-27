🎓 Smart Educational Hub

The Smart Educational Hub is an AI-powered Django web platform designed to enhance the learning experience by integrating smart educational tools such as voice evaluation and intelligent chat assistance. The system leverages Whisper AI for speech recognition and provides a scalable, modular environment suitable for educational institutions and students.

⚙️ Installation and Setup

Follow these steps to set up and run the project after cloning it.

1️⃣ Clone the Repository
git clone <repository_url>
cd <project_directory>

2️⃣ Create a Virtual Environment
python -m venv venv
.\venv\Scripts\Activate.ps1

3️⃣ Upgrade pip and Install Dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

🧠 Whisper AI & FFmpeg Setup (Required)

Whisper AI requires FFmpeg to process audio files.
Please follow these steps carefully to ensure everything works correctly:

Download FFmpeg from: https://www.gyan.dev/ffmpeg/builds/

Download ffmpeg-release-essentials.zip

Extract the contents to C:\ffmpeg (or any location you prefer)

Add C:\ffmpeg\bin to your System PATH environment variable

Restart your terminal or VS Code

🗄️ Database Configuration

The project uses PostgreSQL as the database.

Connection string:

postgresql://genex:0DEnijZnqX3lSqkeTjzjbJtiFPQvrIPU@dpg-d3vacn1r0fns73caqrf0-a/genex

Ensure PostgreSQL is installed and running before continuing.

🧩 Database Migration

Run the following commands to create and apply migrations:

python manage.py makemigrations
python manage.py migrate

👤 Create an Admin User
python manage.py createsuperuser

Then follow the prompts to set a username and password.

🎙️ Media Directory Setup

Create directories to store recorded voice evaluations:

mkdir media
mkdir media\voice_evaluations

🔊 Download Whisper AI Model

Run the Django shell and load the Whisper model:

python manage.py shell

Then enter:

import whisper
model = whisper.load_model("base")
exit()

▶️ Run the Server

Finally, start the Django development server:

python manage.py runserver

Now open your browser and visit:
👉 http://127.0.0.1:8000/
or visit the render deployment link:
👉 https://genex-1.onrender.com/
