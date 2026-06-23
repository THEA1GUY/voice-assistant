"""Small floating status window that appears during active recording/processing."""

import ctypes
import customtkinter as ctk

_ACTIVE_STATES = {"recording", "transcribing", "cleaning", "thinking", "speaking"}

_STATE_STYLE = {
    "recording":    ("#dc2626", "● Recording"),
    "transcribing": ("#d97706", "● Transcribing"),
    "cleaning":     ("#0891b2", "● Cleaning up"),
    "thinking":     ("#2563eb", "● Thinking"),
    "speaking":     ("#7c3aed", "● Speaking"),
}

# Windows extended style: never steal focus when shown or clicked
_WS_EX_NOACTIVATE  = 0x08000000
_WS_EX_TOOLWINDOW  = 0x00000080
_GWL_EXSTYLE       = -20


def _make_noactivate(hwnd: int):
    """Prevent this window from stealing keyboard focus."""
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, _GWL_EXSTYLE)
        ctypes.windll.user32.SetWindowLongW(
            hwnd, _GWL_EXSTYLE,
            style | _WS_EX_NOACTIVATE | _WS_EX_TOOLWINDOW,
        )
    except Exception:
        pass


class RecordingTab:
    """Small always-on-top window. Appears during active states, hides when ready."""

    def __init__(self, parent, on_stop):
        self._parent  = parent
        self._on_stop = on_stop
        self._win     = None
        self._lbl     = None

    def update(self, status: str):
        if status in _ACTIVE_STATES:
            self._show(status)
        else:
            self._hide()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _show(self, status: str):
        color, text = _STATE_STYLE.get(status, ("#6b7280", f"● {status}"))

        if self._win is None or not self._win.winfo_exists():
            self._build_window()

        self._lbl.configure(text=text, text_color=color)
        self._win.lift()

    def _build_window(self):
        win = ctk.CTkToplevel(self._parent)
        win.title("")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.configure(fg_color="#ffffff")

        w, h = 280, 50
        sw = win.winfo_screenwidth()
        win.geometry(f"{w}x{h}+{sw // 2 - w // 2}+18")

        row = ctk.CTkFrame(win, fg_color="#ffffff", corner_radius=0)
        row.pack(fill="both", expand=True, padx=12, pady=8)

        self._lbl = ctk.CTkLabel(
            row, text="● Recording",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#dc2626",
        )
        self._lbl.pack(side="left")

        ctk.CTkButton(
            row, text="Stop",
            command=self._on_stop,
            width=56, height=30, corner_radius=8,
            fg_color="#111827", hover_color="#374151",
            text_color="#ffffff",
            font=ctk.CTkFont(size=11, weight="bold"),
        ).pack(side="right")

        self._win = win

        # Apply no-activate AFTER the window is fully drawn
        win.after(50, lambda: _make_noactivate(win.winfo_id()))

    def _hide(self):
        if self._win and self._win.winfo_exists():
            self._win.destroy()
        self._win = None
        self._lbl = None
