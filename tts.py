import threading
import pyttsx3
from config import TTS_RATE, TTS_VOLUME

_engine: pyttsx3.Engine | None = None
_lock = threading.Lock()


def init_tts() -> None:
    global _engine
    _engine = pyttsx3.init()
    _engine.setProperty("rate",   TTS_RATE)
    _engine.setProperty("volume", TTS_VOLUME)

    # Pick the first English voice available on this system
    for voice in _engine.getProperty("voices"):
        if "english" in voice.name.lower() or "en_" in voice.id.lower():
            _engine.setProperty("voice", voice.id)
            break


def speak(text: str) -> None:
    global _engine
    if _engine is None:
        init_tts()
    with _lock:
        _engine.say(text)
        _engine.runAndWait()
