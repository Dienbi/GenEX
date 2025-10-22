# Installing FFmpeg on Windows

FFmpeg is required for the voice evaluation system to process audio files with Whisper.

## Quick Installation (Recommended - via Chocolatey)

1. **Install Chocolatey** (if not already installed):
   - Open PowerShell as Administrator
   - Run: 
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Install FFmpeg**:
   ```powershell
   choco install ffmpeg
   ```

3. **Restart your terminal** and verify:
   ```powershell
   ffmpeg -version
   ```

## Manual Installation

1. **Download FFmpeg**:
   - Go to: https://www.gyan.dev/ffmpeg/builds/
   - Download: `ffmpeg-release-essentials.zip`

2. **Extract and Install**:
   - Extract the zip file to `C:\ffmpeg`
   - Add `C:\ffmpeg\bin` to your System PATH:
     - Search "Environment Variables" in Windows
     - Edit "Path" in System Variables
     - Add new entry: `C:\ffmpeg\bin`
     - Click OK

3. **Restart your terminal** and verify:
   ```powershell
   ffmpeg -version
   ```

## After Installation

1. Close all terminals
2. Restart VS Code
3. Run the server again:
   ```powershell
   .\venv\Scripts\Activate.ps1
   python manage.py runserver
   ```

4. Try uploading a voice file at http://127.0.0.1:8000/voice/record/

## Troubleshooting

If you still get errors after installing FFmpeg:
- Make sure you restarted VS Code completely
- Try running `ffmpeg -version` in a new terminal to verify installation
- Check that FFmpeg is in your PATH by running `where ffmpeg`
