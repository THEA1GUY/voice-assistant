# Voice Assistant

A personal AI voice assistant for Windows. Press a hotkey to dictate text anywhere on your PC, or ask questions and get spoken replies — all running locally or via cloud APIs.

## Features

- **Dictate mode** — speak, text is cleaned by AI and pasted wherever your cursor is
- **Ask AI mode** — speak a question, get a spoken answer
- **Local-first** — runs fully offline with Whisper (STT) + Ollama (LLM)
- **Cloud options** — Groq Whisper, Deepgram Nova-2, DeepSeek for faster/smarter results
- **Floating status pill** — small always-on-top indicator during recording, never steals focus
- **System tray** — lives in your taskbar, hotkeys work system-wide

---

## Quick Start

**1. Clone**
```bash
git clone https://github.com/Johnadebread/voice-assistant.git
cd voice-assistant
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```
Or double-click setup.bat on Windows.

**3. Install Ollama (local AI — recommended)**

Download from [ollama.com](https://ollama.com), then pull a model:
```bash
ollama pull gemma4:e2b
```

**4. Run**
```bash
python app.py
```

---

## Hotkeys

| Key | Action |
|---|---|
| Ctrl+Shift+D | Start / stop dictation — pastes cleaned text at cursor |
| Ctrl+Shift+A | Start / stop Ask AI — speaks reply aloud |
| Ctrl+Shift+M | Toggle between default and fast Ollama model |

All hotkeys are configurable in **Settings** inside the app.

---

## AI Models

### Speech-to-Text (STT)

| Option | Speed | Notes |
|---|---|---|
| Local Whisper | Slow (CPU) | Fully offline, no key needed |
| Groq Whisper | Fast | Free tier at [console.groq.com](https://console.groq.com) |
| Deepgram Nova-2 | Fast | 200 hrs/month free at [deepgram.com](https://deepgram.com) |

### Language Model (LLM)

| Option | Notes |
|---|---|
| gemma4:e2b (Ollama) | Lightweight, fast, offline |
| gemma4:e4b (Ollama) | Default, better quality |
| gemma4:12b (Ollama) | High quality, needs more RAM |
| DeepSeek cloud | Fast, smart — needs API key |

Switch model anytime with Ctrl+Shift+M or the dropdown in the app.

---

## API Keys (optional)

Open **Settings** in the app to add keys. They are saved locally and never leave your machine.

- **Groq** — [console.groq.com](https://console.groq.com) (free)
- **Deepgram** — [deepgram.com](https://deepgram.com) (free tier)
- **DeepSeek** — [platform.deepseek.com](https://platform.deepseek.com)

Copy settings.example.json to settings.json and fill in keys manually if you prefer.

---

## Requirements

- Windows 10 or 11
- Python 3.10 or later
- Microphone
- [Ollama](https://ollama.com) (optional, for local AI)
