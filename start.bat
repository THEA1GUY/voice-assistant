@echo off
cd /d "%~dp0"
start "" /b ollama serve >nul 2>&1
timeout /t 2 /nobreak >nul
start "" C:\Users\Asus\miniconda3\pythonw.exe launch.pyw
