"""Main application window."""

import customtkinter as ctk
from config import OLLAMA_MODEL_DEFAULT, OLLAMA_MODEL_FAST, DEEPSEEK_MODEL

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

_STATUS = {
    "loading":      ("Loading models…",   "#9ca3af", "#6b7280"),
    "ready":        ("Ready",             "#16a34a", "#111827"),
    "recording":    ("Recording…",        "#dc2626", "#dc2626"),
    "transcribing": ("Transcribing…",     "#d97706", "#d97706"),
    "cleaning":     ("Cleaning up…",      "#0891b2", "#0891b2"),
    "thinking":     ("Thinking…",         "#2563eb", "#2563eb"),
    "speaking":     ("Speaking…",         "#7c3aed", "#7c3aed"),
}

_LLM_OPTIONS: dict[str, tuple[str, str]] = {
    "gemma4:e4b  —  local":        ("ollama",   "gemma4:e4b"),
    "gemma4:e2b  —  local":        ("ollama",   "gemma4:e2b"),
    "gemma4:12b  —  local":        ("ollama",   "gemma4:12b"),
    "deepseek-chat  —  cloud":     ("deepseek", "deepseek-chat"),
    "deepseek-reasoner  —  cloud": ("deepseek", "deepseek-reasoner"),
}
_LLM_LABELS = list(_LLM_OPTIONS.keys())

_STT_OPTIONS: dict[str, str] = {
    "Local Whisper  —  offline":  "local",
    "Groq Whisper  —  cloud":     "groq",
    "Deepgram Nova-2  —  cloud":  "deepgram",
}
_STT_LABELS = list(_STT_OPTIONS.keys())


class VoiceAssistantWindow(ctk.CTk):
    def __init__(self, on_dictate, on_assistant, on_llm_change,
                 on_stt_change, on_settings):
        super().__init__()

        self.title("Voice Assistant")
        self.geometry("480x560")
        self.minsize(480, 560)
        self.resizable(False, False)
        self.configure(fg_color="#ffffff")
        self.protocol("WM_DELETE_WINDOW", self.hide)

        self._build(on_dictate, on_assistant, on_llm_change,
                    on_stt_change, on_settings)

    def _build(self, on_dictate, on_assistant, on_llm_change,
               on_stt_change, on_settings):
        pad = 32

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="#f9fafb", corner_radius=0, height=72)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="Voice Assistant",
                     font=ctk.CTkFont(size=17, weight="bold"),
                     text_color="#111827",
                     ).place(x=pad, y=16)

        status_row = ctk.CTkFrame(header, fg_color="transparent")
        status_row.place(x=pad, y=42)

        self._dot = ctk.CTkLabel(status_row, text="●",
                                  font=ctk.CTkFont(size=12),
                                  text_color="#9ca3af", width=16)
        self._dot.pack(side="left")

        self._status_lbl = ctk.CTkLabel(status_row, text="Loading models…",
                                         font=ctk.CTkFont(size=12),
                                         text_color="#6b7280")
        self._status_lbl.pack(side="left", padx=(5, 0))

        # ── Divider ───────────────────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color="#e5e7eb").pack(fill="x")

        # ── Body ──────────────────────────────────────────────────────────────
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=pad, pady=24)

        # AI Model
        ctk.CTkLabel(body, text="AI MODEL",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#9ca3af",
                     ).pack(anchor="w", pady=(0, 6))

        self._llm_var = ctk.StringVar(value=_LLM_LABELS[0])
        ctk.CTkOptionMenu(
            body, variable=self._llm_var, values=_LLM_LABELS,
            command=lambda v: on_llm_change(*_LLM_OPTIONS[v]),
            fg_color="#f9fafb", button_color="#e5e7eb",
            button_hover_color="#d1d5db", text_color="#111827",
            dropdown_fg_color="#ffffff", dropdown_text_color="#111827",
            dropdown_hover_color="#f3f4f6",
            width=416, height=40, corner_radius=8,
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w")

        ctk.CTkFrame(body, height=1, fg_color="#f3f4f6").pack(fill="x", pady=20)

        # Speech-to-Text
        ctk.CTkLabel(body, text="SPEECH TO TEXT",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#9ca3af",
                     ).pack(anchor="w", pady=(0, 6))

        self._stt_var = ctk.StringVar(value=_STT_LABELS[0])
        ctk.CTkOptionMenu(
            body, variable=self._stt_var, values=_STT_LABELS,
            command=lambda v: on_stt_change(_STT_OPTIONS[v]),
            fg_color="#f9fafb", button_color="#e5e7eb",
            button_hover_color="#d1d5db", text_color="#111827",
            dropdown_fg_color="#ffffff", dropdown_text_color="#111827",
            dropdown_hover_color="#f3f4f6",
            width=416, height=40, corner_radius=8,
            font=ctk.CTkFont(size=13),
        ).pack(anchor="w")

        ctk.CTkFrame(body, height=1, fg_color="#f3f4f6").pack(fill="x", pady=20)

        # Action buttons
        ctk.CTkLabel(body, text="ACTIONS",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     text_color="#9ca3af",
                     ).pack(anchor="w", pady=(0, 6))

        btn_row = ctk.CTkFrame(body, fg_color="transparent")
        btn_row.pack(fill="x")

        ctk.CTkButton(btn_row, text="Dictate", command=on_dictate,
                      fg_color="#111827", hover_color="#374151",
                      text_color="#ffffff", width=200, height=48,
                      corner_radius=10, font=ctk.CTkFont(size=14, weight="bold"),
                      ).pack(side="left", padx=(0, 16))

        ctk.CTkButton(btn_row, text="Ask AI", command=on_assistant,
                      fg_color="#2563eb", hover_color="#1d4ed8",
                      text_color="#ffffff", width=200, height=48,
                      corner_radius=10, font=ctk.CTkFont(size=14, weight="bold"),
                      ).pack(side="left")

        # ── Footer ────────────────────────────────────────────────────────────
        ctk.CTkFrame(self, height=1, fg_color="#e5e7eb").pack(fill="x")

        footer = ctk.CTkFrame(self, fg_color="#f9fafb", corner_radius=0, height=56)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        ctk.CTkButton(footer, text="Settings",
                      command=on_settings,
                      fg_color="transparent", hover_color="#f3f4f6",
                      text_color="#6b7280", border_color="#e5e7eb", border_width=1,
                      width=100, height=32, corner_radius=8,
                      font=ctk.CTkFont(size=12),
                      ).place(x=pad, y=12)

    # ── Public ────────────────────────────────────────────────────────────────

    def set_status(self, key: str):
        text, dot_color, lbl_color = _STATUS.get(key, _STATUS["ready"])
        self._dot.configure(text_color=dot_color)
        self._status_lbl.configure(text=text, text_color=lbl_color)

    def set_llm_display(self, provider: str, model: str):
        for label, (p, m) in _LLM_OPTIONS.items():
            if p == provider and m == model:
                self._llm_var.set(label)
                break

    def show(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def hide(self):
        self.withdraw()
