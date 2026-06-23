"""System tray icon using pystray."""

import threading
import pystray
from PIL import Image, ImageDraw


def _build_icon_image(size: int = 64) -> Image.Image:
    """Draw a minimal microphone icon programmatically."""
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx   = size // 2
    ink  = "#111827"
    lw   = max(2, size // 20)

    # Mic body (rounded rectangle)
    draw.rounded_rectangle(
        [cx - size // 7, size // 8, cx + size // 7, size // 2 + size // 12],
        radius=size // 8,
        fill=ink,
    )
    # Stand arc (half-circle below body)
    pad = size // 6
    draw.arc(
        [pad, size // 3, size - pad, size // 3 + size // 3],
        start=0, end=180,
        fill=ink, width=lw,
    )
    # Pole
    draw.line([(cx, size // 3 + size // 3), (cx, size - size // 8)],
              fill=ink, width=lw)
    # Base
    draw.line(
        [(cx - size // 6, size - size // 8), (cx + size // 6, size - size // 8)],
        fill=ink, width=lw,
    )
    return img


class TrayIcon:
    def __init__(self, on_show, on_dictate, on_assistant, on_quit):
        img  = _build_icon_image(64)
        menu = pystray.Menu(
            pystray.MenuItem("Show window",    on_show,      default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Dictate",        on_dictate),
            pystray.MenuItem("Ask AI",         on_assistant),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit",           on_quit),
        )
        self._icon = pystray.Icon("VoiceAssistant", img, "Voice Assistant", menu)

    def start(self):
        threading.Thread(target=self._icon.run, daemon=True).start()

    def stop(self):
        self._icon.stop()

    def notify(self, title: str, message: str):
        try:
            self._icon.notify(message, title)
        except Exception:
            pass
