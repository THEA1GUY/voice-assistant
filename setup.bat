@echo off
echo ============================================
echo  Voice Assistant -- First-time setup
echo ============================================
echo.
echo [1/3] Installing Python packages...
pip install -r requirements.txt
echo.
echo [2/3] Downloading Gemma 4 E4B (default, ~4.5 GB)...
ollama pull gemma4:e4b
echo.
echo [3/3] Downloading Gemma 4 E2B (fast, ~2.9 GB)...
ollama pull gemma4:e2b
echo.
echo Done! Double-click start.bat to launch.
echo.
pause
