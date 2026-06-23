import threading
import numpy as np
import sounddevice as sd
from config import SAMPLE_RATE, MAX_RECORD_SECONDS, SILENCE_THRESHOLD, SILENCE_DURATION


def record_audio(stop_event: threading.Event) -> np.ndarray:
    """
    Record from the default microphone.

    Stops when:
      - stop_event is set (Stop button, hotkey toggle, or toggle() call)
      - silence longer than SILENCE_DURATION after speech detected
      - MAX_RECORD_SECONDS elapsed
    """
    chunk_secs  = 0.05
    chunk_size  = int(SAMPLE_RATE * chunk_secs)
    max_chunks  = int(MAX_RECORD_SECONDS / chunk_secs)
    silence_lim = int(SILENCE_DURATION   / chunk_secs)

    frames      = []
    silence_cnt = 0
    has_speech  = False

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32") as stream:
        for _ in range(max_chunks):
            if stop_event.is_set():
                break

            chunk, _ = stream.read(chunk_size)
            frames.append(chunk.copy())

            rms = float(np.sqrt(np.mean(chunk ** 2)))
            if rms >= SILENCE_THRESHOLD:
                has_speech  = True
                silence_cnt = 0
            elif has_speech:
                silence_cnt += 1
                if silence_cnt >= silence_lim:
                    break

    if not frames:
        return np.array([], dtype=np.float32)

    audio = np.concatenate(frames, axis=0).flatten()
    return _trim_silence(audio)


def _trim_silence(audio: np.ndarray) -> np.ndarray:
    """Remove leading and trailing silence so Whisper processes only real speech."""
    chunk = int(SAMPLE_RATE * 0.05)   # 50 ms windows
    if len(audio) < chunk:
        return audio
    n = len(audio) // chunk
    rms = np.array([
        float(np.sqrt(np.mean(audio[i * chunk:(i + 1) * chunk] ** 2)))
        for i in range(n)
    ])
    voiced = rms >= SILENCE_THRESHOLD
    if not voiced.any():
        return audio
    first = int(np.argmax(voiced))
    last  = int(n - np.argmax(voiced[::-1]))
    # Keep 1 chunk of padding on each side
    start = max(0, (first - 1) * chunk)
    end   = min(len(audio), (last + 1) * chunk)
    return audio[start:end]
