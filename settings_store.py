"""Persistent key-value store for user settings (API keys etc.)."""

import json
import os

_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
_data: dict = {}


def load() -> None:
    global _data
    try:
        with open(_FILE, "r") as f:
            _data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        _data = {}


def get(key: str, fallback: str = "") -> str:
    return _data.get(key, fallback)


def save(**kwargs) -> None:
    _data.update(kwargs)
    with open(_FILE, "w") as f:
        json.dump(_data, f, indent=2)
