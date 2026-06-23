"""Entry point — wires together tray, window, recording tab, and assistant."""

import threading

import assistant
import settings_store
from stt             import load_model as load_whisper
from tts             import init_tts
from window          import VoiceAssistantWindow
from tray            import TrayIcon
from recording_tab   import RecordingTab
from settings_window import open_settings


def main():
    settings_store.load()

    # ── Main window ───────────────────────────────────────────────────────────
    window = VoiceAssistantWindow(
        on_dictate    = lambda: assistant.toggle("dictate"),
        on_assistant  = lambda: assistant.toggle("assistant"),
        on_llm_change = assistant.set_llm,
        on_stt_change = assistant.set_stt_mode,
        on_settings   = lambda: open_settings(window),
    )

    # ── Recording overlay (floats on screen during active states) ─────────────
    rec_tab = RecordingTab(parent=window, on_stop=assistant.stop_recording)

    # ── Wire assistant status → both window and recording tab ─────────────────
    def _on_status(key: str):
        window.after(0, lambda k=key: window.set_status(k))
        window.after(0, lambda k=key: rec_tab.update(k))

    def _on_model(provider: str, model: str):
        window.after(0, lambda p=provider, m=model: window.set_llm_display(p, m))

    assistant.set_callbacks(status_cb=_on_status, model_cb=_on_model)

    # ── Tray ──────────────────────────────────────────────────────────────────
    def quit_app(icon=None, item=None):
        tray.stop()
        window.after(0, window.destroy)

    tray = TrayIcon(
        on_show      = lambda icon, item: window.after(0, window.show),
        on_dictate   = lambda icon, item: assistant.toggle("dictate"),
        on_assistant = lambda icon, item: assistant.toggle("assistant"),
        on_quit      = quit_app,
    )
    tray.start()

    # ── Hotkeys ───────────────────────────────────────────────────────────────
    assistant.register_hotkeys()

    # ── Load models in background ─────────────────────────────────────────────
    def _load():
        whisper_ok = load_whisper()
        try:
            init_tts()
        except Exception:
            pass
        window.after(0, lambda: window.set_status("ready"))
        msg = "Ready." if whisper_ok else "Ready — use Groq STT (local Whisper not loaded)."
        tray.notify("Voice Assistant", msg)

    threading.Thread(target=_load, daemon=True).start()

    window.mainloop()


if __name__ == "__main__":
    main()
