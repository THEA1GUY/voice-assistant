# Voice Assistant

A personal AI voice assistant for Windows. Press a hotkey to dictate text anywhere on your PC, or ask a question and get a spoken reply — all without switching windows.

## Features

- **Dictate mode** — speak, then the cleaned text is pasted wherever your cursor is
- **Ask AI mode** — ask a question out loud and hear the answer spoken back
- **Local or cloud** — works fully offline with Ollama + Whisper, or faster with cloud APIs
- **System tray** — runs quietly in the background, always one hotkey away
- **Floating status pill** — small on-screen indicator shows recording/thinking state without stealing focus
- **Configurable hotkeys** — change all shortcuts in Settings

## Quick Start

**1. Clone and install**

```bash
git clone https://github.com/Johnadebread/voice-assistant.git
cd voice-assistant
setup.bat
```

Or manually:

```bash
pip install -r requirements.txt
```

**2. Run**

```bash
python app.py
```

The app starts minimised to the system tray. Right-click the tray icon or use hotkeys directly.

## Hotkeys

| Action | Default | Description |
|--------|---------|-------------|
| Dictate | `Ctrl+Shift+D` | Record speech → clean → paste at cursor |
| Ask AI | `Ctrl+Shift+A` | Record speech → get spoken AI reply |
| Switch model | `Ctrl+Shift+M` | Cycle between fast/default local models |

All hotkeys are configurable in **Settings** inside the app.

## Speech-to-Text Options

| Option | Speed | Notes |
|--------|-------|-------|
| Local Whisper | Slower | Fully offline, no API key needed |
| Groq Whisper | Fast (~1s) | Free tier available at groq.com |
| Deepgram Nova-2 | Fast | Most accurate, paid |

Switch between them in the app's STT dropdown.

## AI Model Options

| Model | Type | Notes |
|-------|------|-------|
| gemma4:e2b | Local (Ollama) | Fastest, lightest |
| gemma4:e4b | Local (Ollama) | Default — better quality |
| gemma4:12b | Local (Ollama) | Best local quality |
| deepseek-chat | Cloud | Fast cloud AI |
| deepseek-reasoner | Cloud | Slower, thinks through complex questions |

## Prerequisites

- **Windows 10 or 11**
- **Python 3.10+** — download at python.org
- **Microphone**
- **Ollama** (for local AI) — download at [ollama.com](https://ollama.com)

## Setup for Local AI (Ollama)

1. Install Ollama from [ollama.com](https://ollama.com)
2. Pull a model:

```bash
ollama pull gemma4:e2b
```

3. Ollama runs automatically in the background. The app connects to it at `localhost:11434`.

## API Keys (Cloud Options)

Add keys in the app under **Settings**. You can also pre-populate `settings.json` (copy from `settings.example.json`).

| Service | Free tier | Get key at |
|---------|-----------|------------|
| Groq (STT + LLM) | Yes | console.groq.com |
| DeepSeek (LLM) | Paid | platform.deepseek.com |
| Deepgram (STT) | Yes | console.deepgram.com |

> **Note:** `settings.json` is gitignored and will never be committed. Keep your keys safe.

## Project Structure

```
app.py              — entry point
assistant.py        — recording pipeline, hotkeys, state
audio_utils.py      — microphone capture, silence detection
stt.py              — speech-to-text (Whisper / Groq / Deepgram)
llm.py              — AI responses + transcript cleaning
tts.py              — text-to-speech
window.py           — main UI window
recording_tab.py    — floating status pill
tray.py             — system tray icon
settings_window.py  — settings dialog
settings_store.py   — JSON key-value settings storage
config.py           — default configuration values
```
