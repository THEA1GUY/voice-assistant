@echo off
echo ============================================
echo   Voice Assistant - Setup
echo ============================================
echo.
echo Installing Python dependencies...
pip install -r requirements.txt
echo.
echo ============================================
echo   Done!
echo.
echo   Run the app:
echo     python app.py
echo.
echo   For local AI (optional):
echo     1. Install Ollama: https://ollama.com
echo     2. Run: ollama pull gemma4:e2b
echo.
echo   Add API keys in the app Settings for
echo   faster cloud STT and AI options.
echo ============================================
pause
