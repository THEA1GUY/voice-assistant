# ─── Local STT (Whisper) ──────────────────────────────────────────────────────
WHISPER_MODEL  = "base"               # tiny | base | small | medium
WHISPER_DEVICE = "cpu"                # "cpu" or "cuda" (NVIDIA GPU)

# ─── Local LLM (Ollama) ───────────────────────────────────────────────────────
OLLAMA_MODEL_DEFAULT = "gemma4:e4b"   # default
OLLAMA_MODEL_FAST    = "gemma4:e2b"   # lighter
OLLAMA_URL           = "http://localhost:11434"

# ─── Cloud STT — Groq Whisper ─────────────────────────────────────────────────
GROQ_API_KEY       = ""
GROQ_WHISPER_MODEL = "whisper-large-v3"   # full large model, better accuracy

# ─── Cloud STT — Deepgram Nova-2 ──────────────────────────────────────────────
DEEPGRAM_API_KEY   = ""
DEEPGRAM_MODEL     = "nova-2"

# ─── Cloud LLM — DeepSeek ─────────────────────────────────────────────────────
# Get a key at platform.deepseek.com
DEEPSEEK_API_KEY = ""
DEEPSEEK_MODEL   = "deepseek-chat"    # deepseek-chat | deepseek-reasoner

# ─── Hotkeys ──────────────────────────────────────────────────────────────────
HOTKEY_DICTATE      = "ctrl+shift+d"
HOTKEY_ASSISTANT    = "ctrl+shift+a"
HOTKEY_SWITCH_MODEL = "ctrl+shift+m"

# ─── Audio ────────────────────────────────────────────────────────────────────
SAMPLE_RATE        = 16000   # Hz  (Whisper expects 16 kHz)
MAX_RECORD_SECONDS = 60
SILENCE_THRESHOLD  = 0.02    # RMS level below which counts as silence (0.0–1.0)
SILENCE_DURATION   = 3.0     # Seconds of silence before auto-stopping

# ─── TTS ──────────────────────────────────────────────────────────────────────
TTS_RATE   = 180   # Words per minute
TTS_VOLUME = 1.0   # 0.0–1.0
