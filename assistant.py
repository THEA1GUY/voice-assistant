"""Core pipeline: record → transcribe → clean → act. Thread-safe, UI-agnostic."""

import ctypes
import threading
import time
import keyboard
import pyperclip

from config import (
    HOTKEY_DICTATE, HOTKEY_ASSISTANT, HOTKEY_SWITCH_MODEL,
    OLLAMA_MODEL_DEFAULT, OLLAMA_MODEL_FAST,
)
from audio_utils import record_audio
from stt         import transcribe_audio
from llm         import ask, clean_transcript
from tts         import speak

# ─── State ────────────────────────────────────────────────────────────────────
_recording    = False
_mode         = None
_stt_mode     = "local"
_llm_provider = "ollama"
_llm_model    = OLLAMA_MODEL_DEFAULT
_lock         = threading.Lock()

_stop_event   = threading.Event()   # set to stop the recording loop
_paste_hwnd   = None                # window that had focus when recording started

_status_cb    = None
_model_cb     = None

# debounce: track last hotkey fire time per key
_hotkey_last: dict[str, float] = {}

SAMPLE_RATE_MIN = 1600
HOTKEY_DEBOUNCE = 0.35  # seconds — ignore repeat within this window


# ─── Public API ───────────────────────────────────────────────────────────────

def set_callbacks(status_cb=None, model_cb=None):
    global _status_cb, _model_cb
    _status_cb = status_cb
    _model_cb  = model_cb


def set_stt_mode(mode: str):
    global _stt_mode
    _stt_mode = mode


def set_llm(provider: str, model: str):
    global _llm_provider, _llm_model
    with _lock:
        if _recording:
            return
        _llm_provider = provider
        _llm_model    = model
    if _model_cb:
        _model_cb(provider, model)


def switch_model():
    with _lock:
        if _recording or _llm_provider != "ollama":
            return
    new = OLLAMA_MODEL_FAST if _llm_model == OLLAMA_MODEL_DEFAULT else OLLAMA_MODEL_DEFAULT
    set_llm("ollama", new)


def toggle(mode: str):
    """Press once → start recording. Press again → stop and process."""
    global _recording, _mode, _paste_hwnd
    with _lock:
        if _recording:
            # Already recording — signal stop, pipeline continues on its own
            _stop_event.set()
            _recording = False
            return
        # Start recording
        _paste_hwnd = ctypes.windll.user32.GetForegroundWindow()
        _recording  = True
        _mode       = mode
        _stop_event.clear()
    threading.Thread(target=_process, daemon=True).start()


def stop_recording():
    """Stop button in the recording pill."""
    global _recording
    with _lock:
        if _recording:
            _stop_event.set()
            _recording = False


# ─── Hotkey registration ───────────────────────────────────────────────────────

def register_hotkeys():
    import settings_store
    dk = settings_store.get("hotkey_dictate")   or HOTKEY_DICTATE
    ak = settings_store.get("hotkey_assistant") or HOTKEY_ASSISTANT
    sk = settings_store.get("hotkey_switch")    or HOTKEY_SWITCH_MODEL

    keyboard.add_hotkey(dk, lambda: _debounced_toggle("dictate",   dk))
    keyboard.add_hotkey(ak, lambda: _debounced_toggle("assistant", ak))
    keyboard.add_hotkey(sk, switch_model)


def reload_hotkeys():
    keyboard.unhook_all()
    register_hotkeys()


def _debounced_toggle(mode: str, key: str):
    """Prevent key-repeat from toggling multiple times."""
    now = time.monotonic()
    if now - _hotkey_last.get(key, 0) < HOTKEY_DEBOUNCE:
        return
    _hotkey_last[key] = now
    toggle(mode)


# ─── Pipeline ─────────────────────────────────────────────────────────────────

def _notify(key: str):
    if _status_cb:
        _status_cb(key)


def _focus_and_paste(hwnd):
    try:
        if hwnd:
            ctypes.windll.user32.AllowSetForegroundWindow(-1)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            time.sleep(0.25)
    except Exception:
        pass
    keyboard.send("ctrl+v")


def _process():
    global _recording
    current_paste_target = _paste_hwnd

    _notify("recording")
    audio = record_audio(_stop_event)

    with _lock:
        _recording = False   # ensure clean state regardless of how loop ended
        current_mode     = _mode
        current_stt      = _stt_mode
        current_provider = _llm_provider
        current_model    = _llm_model

    if audio is None or len(audio) < SAMPLE_RATE_MIN:
        _notify("ready")
        return

    _notify("transcribing")
    raw_text = transcribe_audio(audio, mode=current_stt)

    if not raw_text.strip() or raw_text.startswith("["):
        _notify("ready")
        return

    _notify("cleaning")
    text = clean_transcript(raw_text, provider=current_provider, model=current_model)

    if current_mode == "dictate":
        pyperclip.copy(text)
        _focus_and_paste(current_paste_target)
        _notify("ready")

    elif current_mode == "assistant":
        _notify("thinking")
        reply = ask(text, provider=current_provider, model=current_model)
        _notify("speaking")
        speak(reply)
        _notify("ready")
