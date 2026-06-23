import requests
from config import (
    OLLAMA_MODEL_DEFAULT, OLLAMA_MODEL_FAST, OLLAMA_URL,
    DEEPSEEK_API_KEY, DEEPSEEK_MODEL,
)

_SYSTEM = (
    "You are a helpful AI assistant. "
    "Give concise, clear answers. "
    "Keep responses short so they are comfortable to listen to."
)

_CLEAN_PROMPT = """\
You are an AI that turns raw speech-to-text output into the text the person actually intended to write or say.

Speech-to-text makes mistakes. People also think aloud, correct themselves, and change their minds mid-sentence. Your job is to produce the final, polished text the person would want to see — not a transcript of the sounds they made.

── STEP 1: RESOLVE INTENT ──
Find what the person actually meant to say at the end.
- "scratch that", "actually", "no wait", "cancel that", "never mind" → discard everything before and keep what comes after
- Self-corrections: keep only the corrected version
- Stutters and repeated words → collapse to one
- Filler words (um, uh, like, you know, basically, right, so, hmm) → remove
- If they trailed off mid-thought, keep the last coherent intent

── STEP 2: FIX STT ERRORS ──
Speech-to-text mishears words — use context to correct them.
- Numbers: "to" → "2", "for" → "4", "ate" → "8", "won" → "1", "cello" in a time context → "6"
- Common mishears: "their/there/they're", "your/you're", "its/it's"
- If a word makes no sense but a similar-sounding word does, use the sensible word

PRESERVE — do not alter, remove, or paraphrase:
- Proper nouns: names of people, places, companies, organisations
- Product and brand names: app names, software, tools (e.g. LocalSend, Notion, WhatsApp, DeepSeek)
- Technical terms, acronyms, project names
- Any word the person clearly intended even if uncommon

── STEP 3: DETECT CONTEXT ──
Infer what kind of text this is and format it accordingly:
- TEXT MESSAGE / CHAT → casual, conversational, no need for full sentences
- EMAIL / FORMAL NOTE → proper grammar, complete sentences, appropriate tone
- TO-DO / REMINDER → concise, action-oriented ("Buy milk", "Call John at 3pm")
- PROMPT / INSTRUCTION → clear, specific, imperative ("Write a Python function that...")
- QUESTION → preserve as a question with correct punctuation
- GENERAL / UNCLEAR → clean, natural written English

── OUTPUT ──
Return ONLY the final text — no labels, no explanation, no quotes, no "Cleaned:" prefix. Just the text itself.

Raw transcription:
{text}"""


# ─── Public API ───────────────────────────────────────────────────────────────

def ask(prompt: str, provider: str = "ollama", model: str | None = None) -> str:
    target = model or (OLLAMA_MODEL_DEFAULT if provider == "ollama" else DEEPSEEK_MODEL)
    full   = f"{_SYSTEM}\n\nUser: {prompt}\nAssistant:"
    try:
        return _call(full, provider, target, max_tokens=300, temperature=0.7)
    except Exception as exc:
        return _friendly_error(provider, exc)


def clean_transcript(text: str, provider: str = "ollama", model: str | None = None) -> str:
    """Return AI-cleaned text, or raw text if the LLM is unavailable."""
    if not text.strip():
        return text
    target = model or (OLLAMA_MODEL_FAST if provider == "ollama" else DEEPSEEK_MODEL)
    try:
        result = _call(_CLEAN_PROMPT.format(text=text), provider, target,
                       max_tokens=200, temperature=0.0)
        if result.strip():
            return result
    except Exception:
        pass
    return text   # silent fallback — raw transcript is better than an error string


# ─── Backends ─────────────────────────────────────────────────────────────────

def _call(prompt: str, provider: str, model: str,
          max_tokens: int, temperature: float) -> str:
    if provider == "deepseek":
        return _call_deepseek(prompt, model, max_tokens, temperature)
    return _call_ollama(prompt, model, max_tokens, temperature)


def _call_ollama(prompt: str, model: str, max_tokens: int, temperature: float) -> str:
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model":   model,
            "prompt":  prompt,
            "stream":  False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"].strip()


def _call_deepseek(prompt: str, model: str, max_tokens: int, temperature: float) -> str:
    import settings_store
    api_key = settings_store.get("deepseek_api_key") or DEEPSEEK_API_KEY
    if not api_key:
        raise ValueError("DeepSeek API key not set — open Settings in the app")
    resp = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json",
        },
        json={
            "model":       model,
            "messages":    [{"role": "user", "content": prompt}],
            "max_tokens":  max_tokens,
            "temperature": temperature,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _friendly_error(provider: str, exc: Exception) -> str:
    msg = str(exc)
    if provider == "ollama":
        if "404" in msg or "Not Found" in msg:
            return "Ollama model not downloaded yet. Run: ollama pull gemma4:e2b"
        if "Connection" in msg or "refused" in msg:
            return "Ollama is not running. Start it or switch to a cloud model."
        return f"Ollama error — {msg}"
    if provider == "deepseek":
        if "API key" in msg:
            return "DeepSeek API key not set. Open Settings and add your key."
        return f"DeepSeek error — {msg}"
    return f"Error — {msg}"


