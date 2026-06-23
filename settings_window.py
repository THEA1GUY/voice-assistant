"""Settings dialog — API keys and hotkey configuration."""

import threading
import customtkinter as ctk
import keyboard
import settings_store
from config import HOTKEY_DICTATE, HOTKEY_ASSISTANT, HOTKEY_SWITCH_MODEL

_instance = None


def open_settings(parent):
    global _instance
    if _instance is not None and _instance.winfo_exists():
        _instance.lift()
        _instance.focus_force()
        return
    _instance = _SettingsWindow(parent)


class _SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("480x620")
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._build()

    def _build(self):
        # Scrollable body
        scroll = ctk.CTkScrollableFrame(self, fg_color="#ffffff",
                                         scrollbar_button_color="#e5e7eb",
                                         scrollbar_button_hover_color="#d1d5db")
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        pad = 28
        body = ctk.CTkFrame(scroll, fg_color="transparent")
        body.pack(fill="x", padx=pad, pady=pad)

        # ── API Keys section ──────────────────────────────────────────────────
        self._section(body, "API Keys")

        ctk.CTkLabel(body, text="Keys are saved locally on your PC only.",
                     font=ctk.CTkFont(size=11), text_color="#9ca3af",
                     ).pack(anchor="w", pady=(2, 16))

        self._dg_var = ctk.StringVar(value=settings_store.get("deepgram_api_key"))
        self._api_field(body, "Deepgram API Key",
                        "deepgram.com  —  Nova-2 STT, 200 hrs/month free",
                        self._dg_var, "your deepgram key...")

        self._groq_var = ctk.StringVar(value=settings_store.get("groq_api_key"))
        self._api_field(body, "Groq API Key",
                        "console.groq.com  —  enables Groq Whisper STT",
                        self._groq_var, "gsk_...")

        self._ds_var = ctk.StringVar(value=settings_store.get("deepseek_api_key"))
        self._api_field(body, "DeepSeek API Key",
                        "platform.deepseek.com  —  enables DeepSeek cloud AI",
                        self._ds_var, "sk-...")

        # ── Hotkeys section ───────────────────────────────────────────────────
        ctk.CTkFrame(body, height=1, fg_color="#e5e7eb").pack(fill="x", pady=(8, 20))
        self._section(body, "Hotkeys")

        ctk.CTkLabel(body,
                     text='Click "Capture" then press your key combination.',
                     font=ctk.CTkFont(size=11), text_color="#9ca3af",
                     ).pack(anchor="w", pady=(2, 16))

        self._hk_dictate   = ctk.StringVar(
            value=settings_store.get("hotkey_dictate")   or HOTKEY_DICTATE)
        self._hk_assistant = ctk.StringVar(
            value=settings_store.get("hotkey_assistant") or HOTKEY_ASSISTANT)
        self._hk_switch    = ctk.StringVar(
            value=settings_store.get("hotkey_switch")    or HOTKEY_SWITCH_MODEL)

        self._hotkey_row(body, "Dictate  (voice → paste at cursor)",
                         self._hk_dictate)
        self._hotkey_row(body, "Ask AI  (voice → Gemma reply)",
                         self._hk_assistant)
        self._hotkey_row(body, "Switch model",
                         self._hk_switch)

        # ── Save button ───────────────────────────────────────────────────────
        ctk.CTkFrame(body, height=1, fg_color="#e5e7eb").pack(fill="x", pady=(16, 20))

        ctk.CTkButton(body, text="Save",
                      command=self._save,
                      fg_color="#111827", hover_color="#374151",
                      text_color="#ffffff",
                      width=424, height=44, corner_radius=10,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      ).pack()

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _section(self, parent, title: str):
        ctk.CTkLabel(parent, text=title,
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color="#111827",
                     ).pack(anchor="w", pady=(0, 4))

    def _api_field(self, parent, label: str, hint: str,
                   var: ctk.StringVar, placeholder: str):
        ctk.CTkLabel(parent, text=label,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#374151",
                     ).pack(anchor="w")
        ctk.CTkLabel(parent, text=hint,
                     font=ctk.CTkFont(size=11), text_color="#9ca3af",
                     ).pack(anchor="w")
        ctk.CTkEntry(parent, textvariable=var, show="●",
                     placeholder_text=placeholder,
                     width=424, height=38, corner_radius=8,
                     fg_color="#f9fafb", border_color="#e5e7eb",
                     text_color="#111827",
                     ).pack(anchor="w", pady=(6, 16))

    def _hotkey_row(self, parent, label: str, var: ctk.StringVar):
        ctk.CTkLabel(parent, text=label,
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#374151",
                     ).pack(anchor="w")

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(4, 14))

        entry = ctk.CTkEntry(row, textvariable=var,
                              width=300, height=36, corner_radius=8,
                              fg_color="#f9fafb", border_color="#e5e7eb",
                              text_color="#111827", state="readonly",
                              font=ctk.CTkFont(size=12, family="Consolas"),
                              )
        entry.pack(side="left")

        btn = ctk.CTkButton(row, text="Capture",
                             width=100, height=36, corner_radius=8,
                             fg_color="#f9fafb", hover_color="#f3f4f6",
                             text_color="#374151", border_color="#e5e7eb",
                             border_width=1,
                             font=ctk.CTkFont(size=12),
                             )
        btn.pack(side="left", padx=(10, 0))
        btn.configure(command=lambda b=btn, v=var: self._capture(b, v))

    def _capture(self, btn: ctk.CTkButton, var: ctk.StringVar):
        btn.configure(text="Press keys…", state="disabled",
                      fg_color="#eff6ff", border_color="#93c5fd",
                      text_color="#1d4ed8")

        def _listen():
            try:
                combo = keyboard.read_hotkey(suppress=False)
                self.after(0, lambda: var.set(combo))
            except Exception:
                pass
            finally:
                self.after(0, lambda: btn.configure(
                    text="Capture", state="normal",
                    fg_color="#f9fafb", border_color="#e5e7eb",
                    text_color="#374151"))

        threading.Thread(target=_listen, daemon=True).start()

    def _save(self):
        settings_store.save(
            deepgram_api_key  = self._dg_var.get().strip(),
            groq_api_key      = self._groq_var.get().strip(),
            deepseek_api_key  = self._ds_var.get().strip(),
            hotkey_dictate    = self._hk_dictate.get().strip(),
            hotkey_assistant  = self._hk_assistant.get().strip(),
            hotkey_switch     = self._hk_switch.get().strip(),
        )
        import assistant
        assistant.reload_hotkeys()
        self._close()

    def _close(self):
        global _instance
        self.grab_release()
        self.destroy()
        _instance = None
