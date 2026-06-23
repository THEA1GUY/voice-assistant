import io
import numpy as np
import scipy.io.wavfile as wav
from config import (
    WHISPER_MODEL, WHISPER_DEVICE, SAMPLE_RATE,
    GROQ_API_KEY, GROQ_WHISPER_MODEL,
    DEEPGRAM_API_KEY, DEEPGRAM_MODEL,
)

_local_model = None


def load_model() -> bool:
    """Load local Whisper model. Returns True on success, False if unavailable."""
    global _local_model
    try:
        from faster_whisper import WhisperModel
        _local_model = WhisperModel(WHISPER_MODEL, device=WHISPER_DEVICE, compute_type="int8")
        return True
    except Exception:
        return False


def transcribe_audio(audio: np.ndarray, mode: str = "local") -> str:
    if mode == "groq":
        return _transcribe_groq(audio)
    if mode == "deepgram":
        return _transcribe_deepgram(audio)
    return _transcribe_local(audio)


# ─── Local ────────────────────────────────────────────────────────────────────

def _transcribe_local(audio: np.ndarray) -> str:
    if _local_model is None:
        ok = load_model()
        if not ok:
            return "[Local Whisper unavailable — switch to Groq STT in Settings]"
    try:
        segments, _ = _local_model.transcribe(audio, beam_size=5, language="en")
        return " ".join(seg.text for seg in segments).strip()
    except Exception as exc:
        return f"[STT error: {exc}]"


# ─── Groq cloud ───────────────────────────────────────────────────────────────

def _transcribe_groq(audio: np.ndarray) -> str:
    import settings_store
    api_key = settings_store.get("groq_api_key") or GROQ_API_KEY
    if not api_key:
        return "[Groq API key not set — open Settings in the app]"

    audio_int16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    buf = io.BytesIO()
    wav.write(buf, SAMPLE_RATE, audio_int16)
    buf.seek(0)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        result = client.audio.transcriptions.create(
            file=("audio.wav", buf, "audio/wav"),
            model=GROQ_WHISPER_MODEL,
            language="en",
        )
        return result.text.strip()
    except Exception as exc:
        return f"[Groq STT error: {exc}]"


# ─── Deepgram Nova-2 ──────────────────────────────────────────────────────────

def _transcribe_deepgram(audio: np.ndarray) -> str:
    import requests as _req
    import settings_store
    api_key = settings_store.get("deepgram_api_key") or DEEPGRAM_API_KEY
    if not api_key:
        return "[Deepgram API key not set — open Settings in the app]"

    audio_int16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    buf = io.BytesIO()
    wav.write(buf, SAMPLE_RATE, audio_int16)

    try:
        resp = _req.post(
            "https://api.deepgram.com/v1/listen",
            headers={
                "Authorization": f"Token {api_key}",
                "Content-Type":  "audio/wav",
            },
            params={
                "model":        DEEPGRAM_MODEL,
                "language":     "en",
                "smart_format": "true",
                "punctuate":    "true",
                "disfluencies": "false",
            },
            data=buf.getvalue(),
            timeout=30,
        )
        resp.raise_for_status()
        transcript = (resp.json()["results"]["channels"][0]
                      ["alternatives"][0]["transcript"])
        return transcript.strip()
    except Exception as exc:
        return f"[Deepgram STT error: {exc}]"
