#!/usr/bin/env python3
"""
Voice Loop — hands-free conversation with an OpenClaw agent.

Listens via mic → transcribes with Whisper (local) → streams LLM response
via OpenClaw API (SSE) → speaks sentence-by-sentence with Kokoro TTS (local).

Config via environment variables or the CONFIG section below.
"""

import subprocess
import tempfile
import os
import json
import time
import signal
import re
import numpy as np
import sounddevice as sd
import soundfile as sf
import urllib.request

# ── Config ──────────────────────────────────────────────────────────────────
# Audio capture
SAMPLE_RATE = 16000
CHANNELS = 1
SILENCE_THRESHOLD = float(os.environ.get("VL_SILENCE_THRESHOLD", "0.015"))
SILENCE_DURATION = float(os.environ.get("VL_SILENCE_DURATION", "1.2"))
MIN_SPEECH_DURATION = 0.5
PRE_SPEECH_BUFFER = 0.5
CHUNK_DURATION = 0.1

# Kokoro TTS
KOKORO_VOICES = {
    "en": {"female": "af_heart", "male": "am_puck"},
    "es": {"female": "ef_dora", "male": "em_alex"},
    "fr": {"female": "ff_siwis", "male": "ff_siwis"},
    "ja": {"female": "jf_alpha", "male": "jm_beta"},
    "zh": {"female": "zf_xiaobei", "male": "zm_yunjian"},
}
KOKORO_SPEED = float(os.environ.get("VL_KOKORO_SPEED", "1.15"))
KOKORO_MODEL_DIR = os.path.expanduser(
    os.environ.get("VL_KOKORO_MODEL_DIR", "~/.cache/kokoro-onnx")
)

# Language
CURRENT_LANG = os.environ.get("VL_DEFAULT_LANG", "en")
CURRENT_GENDER = os.environ.get("VL_DEFAULT_GENDER", "female")
WHISPER_MODEL_EN = os.environ.get("VL_WHISPER_MODEL_EN", "base.en")
WHISPER_MODEL_MULTI = os.environ.get("VL_WHISPER_MODEL_MULTI", "small")
WHISPER_LANGS = {"en": "en", "es": "es", "fr": "fr", "ja": "ja", "zh": "zh"}
KOKORO_LANGS = {"en": "en-us", "es": "es", "fr": "fr-fr", "ja": "ja", "zh": "cmn"}

# Whisper binary — resolved from PATH, not user-configurable
WHISPER_BIN = "whisper"


def read_keychain(service: str) -> str:
    """Read a password from macOS Keychain. Returns empty string on failure."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-w"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def validate_api_url(url: str) -> str:
    """Block non-localhost API URLs. Only local connections allowed."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if hostname not in ("127.0.0.1", "localhost", "::1"):
        print(f"❌ Blocked non-local API endpoint: {hostname}", flush=True)
        print(f"   Voice loop only connects to localhost for security.", flush=True)
        raise SystemExit(1)
    return url


# OpenClaw API (streaming SSE) — localhost only
OPENCLAW_API_URL = validate_api_url(os.environ.get(
    "VL_OPENCLAW_API_URL", "http://127.0.0.1:18789/v1/chat/completions"
))
OPENCLAW_API_TOKEN = (
    os.environ.get("VL_OPENCLAW_API_TOKEN", "")
    or read_keychain("voice-loop-openclaw-token")
)
OPENCLAW_SESSION_TO = (
    os.environ.get("VL_OPENCLAW_SESSION_TO", "")
    or read_keychain("voice-loop-session-to")
)

# ── Globals ─────────────────────────────────────────────────────────────────
running = True
kokoro = None


def signal_handler(sig, frame):
    global running
    print("\n🛑 Shutting down...")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def init_kokoro():
    global kokoro
    from kokoro_onnx import Kokoro
    model_path = os.path.join(KOKORO_MODEL_DIR, "kokoro-v1.0.onnx")
    voices_path = os.path.join(KOKORO_MODEL_DIR, "voices-v1.0.bin")
    kokoro = Kokoro(model_path, voices_path)


def get_voice():
    return KOKORO_VOICES.get(CURRENT_LANG, KOKORO_VOICES["en"])[CURRENT_GENDER]

def get_kokoro_lang():
    return KOKORO_LANGS.get(CURRENT_LANG, "en-us")

def get_whisper_lang():
    return WHISPER_LANGS.get(CURRENT_LANG, "en")

def get_whisper_model():
    return WHISPER_MODEL_EN if CURRENT_LANG == "en" else WHISPER_MODEL_MULTI

def rms(audio_chunk: np.ndarray) -> float:
    return float(np.sqrt(np.mean(audio_chunk ** 2)))


# ── Language Switching ──────────────────────────────────────────────────────

LANGUAGE_TRIGGERS = {
    "es": [
        "switch to spanish", "spanish mode", "let's practice spanish",
        "lets practice spanish", "habla en español", "hablemos en español",
        "hablemos español", "go spanish", "speak spanish", "speak in spanish",
    ],
    "fr": [
        "switch to french", "french mode", "let's practice french",
        "speak french", "speak in french", "parle en français",
    ],
    "ja": [
        "switch to japanese", "japanese mode", "speak japanese",
        "speak in japanese",
    ],
    "zh": [
        "switch to chinese", "chinese mode", "speak chinese",
        "speak in chinese", "speak mandarin",
    ],
}

ENGLISH_TRIGGERS = [
    "back to english", "switch to english", "english mode",
    "go english", "speak english", "speak in english", "stop spanish",
    "stop french", "stop japanese", "stop chinese",
]

LANG_CONFIRMATIONS = {
    "es": "¡Modo español activado! Hablemos en español.",
    "fr": "Mode français activé ! Parlons en français.",
    "ja": "日本語モードです。日本語で話しましょう。",
    "zh": "中文模式已启动。让我们用中文对话。",
}


def check_language_switch(text: str) -> bool:
    global CURRENT_LANG
    lower = text.lower().strip()

    # Check for switch TO a language
    for lang, triggers in LANGUAGE_TRIGGERS.items():
        for trigger in triggers:
            if trigger in lower:
                if CURRENT_LANG != lang:
                    CURRENT_LANG = lang
                    print(f"🌍 Switched to {lang} mode (voice: {get_voice()})", flush=True)
                    try:
                        msg = LANG_CONFIRMATIONS.get(lang, f"Switched to {lang}.")
                        samples, sr = kokoro.create(
                            msg, voice=get_voice(), speed=KOKORO_SPEED, lang=get_kokoro_lang()
                        )
                        sd.play(samples, sr)
                        sd.wait()
                    except Exception:
                        pass
                return True

    # Check for switch back to English
    for trigger in ENGLISH_TRIGGERS:
        if trigger in lower:
            if CURRENT_LANG != "en":
                CURRENT_LANG = "en"
                print(f"🇺🇸 Switched to English mode (voice: {get_voice()})", flush=True)
                try:
                    samples, sr = kokoro.create(
                        "Switched back to English.", voice=get_voice(),
                        speed=KOKORO_SPEED, lang="en-us"
                    )
                    sd.play(samples, sr)
                    sd.wait()
                except Exception:
                    pass
            return True

    return False


# ── Audio Capture ───────────────────────────────────────────────────────────

def record_utterance() -> np.ndarray | None:
    chunk_samples = int(SAMPLE_RATE * CHUNK_DURATION)
    pre_buffer_chunks = int(PRE_SPEECH_BUFFER / CHUNK_DURATION)
    silence_chunks_needed = int(SILENCE_DURATION / CHUNK_DURATION)

    pre_buffer = []
    speech_chunks = []
    is_speaking = False
    silence_count = 0

    print("🎤 Listening...", flush=True)

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='float32') as stream:
        while running:
            chunk, _ = stream.read(chunk_samples)
            chunk = chunk.flatten()
            level = rms(chunk)

            if not is_speaking:
                pre_buffer.append(chunk)
                if len(pre_buffer) > pre_buffer_chunks:
                    pre_buffer.pop(0)
                if level > SILENCE_THRESHOLD:
                    is_speaking = True
                    speech_chunks = list(pre_buffer) + [chunk]
                    silence_count = 0
                    print("🗣️  Speech detected...", flush=True)
            else:
                speech_chunks.append(chunk)
                if level < SILENCE_THRESHOLD:
                    silence_count += 1
                    if silence_count >= silence_chunks_needed:
                        break
                else:
                    silence_count = 0

    if not speech_chunks:
        return None

    audio = np.concatenate(speech_chunks)
    duration = len(audio) / SAMPLE_RATE

    if duration < MIN_SPEECH_DURATION:
        print(f"   (too short: {duration:.1f}s, skipping)", flush=True)
        return None

    print(f"   Captured {duration:.1f}s of audio", flush=True)
    return audio


# ── Transcription ───────────────────────────────────────────────────────────

def transcribe(audio: np.ndarray) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
        sf.write(tmp_path, audio, SAMPLE_RATE)

    try:
        print("📝 Transcribing...", flush=True)
        result = subprocess.run(
            [
                WHISPER_BIN, tmp_path,
                "--model", get_whisper_model(),
                "--language", get_whisper_lang(),
                "--output_format", "txt",
                "--output_dir", "/tmp",
            ],
            capture_output=True, text=True, timeout=30
        )

        base = os.path.basename(tmp_path).replace(".wav", ".txt")
        txt_path = os.path.join("/tmp", base)

        if os.path.exists(txt_path):
            with open(txt_path) as f:
                text = f.read().strip()
            os.unlink(txt_path)
            return text
        else:
            return result.stdout.strip()
    finally:
        os.unlink(tmp_path)


# ── TTS ─────────────────────────────────────────────────────────────────────

def clean_text_for_tts(text: str) -> str:
    clean = re.sub(r'[*_`#\[\]]', '', text)
    clean = re.sub(r'\n+', '. ', clean)
    clean = re.sub(r'https?://\S+', 'link', clean)
    clean = re.sub(r'[😀-🙏🌀-🗿🚀-🛿🤀-🧿🩀-🫿]+', '', clean)
    return clean.strip()


def split_into_sentences(text: str) -> list[str]:
    parts = re.split(r'(?<=[.!?¡¿])\s+', text)
    return [p.strip() for p in parts if p.strip()]


def speak_sentence(text: str):
    if not text:
        return
    try:
        samples, sr = kokoro.create(
            text, voice=get_voice(), speed=KOKORO_SPEED, lang=get_kokoro_lang()
        )
        sd.play(samples, sr)
        sd.wait()
    except Exception as e:
        print(f"   ⚠️  Kokoro error: {e}", flush=True)


# ── LLM Streaming ──────────────────────────────────────────────────────────

def stream_and_speak(text: str) -> str:
    """Stream LLM response via SSE and speak sentences as they arrive."""
    print("💬 Streaming from OpenClaw...", flush=True)
    t0 = time.time()

    lang_context = ""
    if CURRENT_LANG != "en":
        lang_names = {"es": "Spanish", "fr": "French", "ja": "Japanese", "zh": "Chinese"}
        lang_name = lang_names.get(CURRENT_LANG, CURRENT_LANG)
        lang_context = f" [{lang_name} mode — respond in {lang_name}, correct my grammar gently]"

    message = f"[Voice from user via microphone]{lang_context} {text}"

    payload = json.dumps({
        "model": "openclaw:main",
        "messages": [{"role": "user", "content": message}],
        "stream": True,
        "user": f"voice-loop-{OPENCLAW_SESSION_TO}",
    }).encode()

    req = urllib.request.Request(
        OPENCLAW_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {OPENCLAW_API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }
    )

    full_response = ""
    sentence_buffer = ""
    sentences_spoken = 0
    first_speech_time = None

    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()

                if not line or not line.startswith("data: "):
                    continue

                data_str = line[6:]
                if data_str == "[DONE]":
                    break

                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")

                    if content:
                        full_response += content
                        sentence_buffer += content

                        sentences = split_into_sentences(sentence_buffer)
                        if len(sentences) > 1:
                            for s in sentences[:-1]:
                                clean = clean_text_for_tts(s)
                                if clean:
                                    if first_speech_time is None:
                                        first_speech_time = time.time()
                                        print(f"   ⚡ First speech at {first_speech_time - t0:.1f}s", flush=True)
                                    trunc = f'"{clean[:60]}..."' if len(clean) > 60 else f'"{clean}"'
                                    print(f"   🔊 {trunc}", flush=True)
                                    speak_sentence(clean)
                                    sentences_spoken += 1
                            sentence_buffer = sentences[-1]

                except json.JSONDecodeError:
                    continue

        # Speak remaining buffer
        if sentence_buffer.strip():
            clean = clean_text_for_tts(sentence_buffer)
            if clean:
                if first_speech_time is None:
                    first_speech_time = time.time()
                    print(f"   ⚡ First speech at {first_speech_time - t0:.1f}s", flush=True)
                trunc = f'"{clean[:60]}..."' if len(clean) > 60 else f'"{clean}"'
                print(f"   🔊 {trunc}", flush=True)
                speak_sentence(clean)
                sentences_spoken += 1

        elapsed = time.time() - t0
        print(f"   Total: {elapsed:.1f}s, {sentences_spoken} sentences spoken", flush=True)

    except Exception as e:
        print(f"   ⚠️  Streaming error: {e}", flush=True)

    return full_response


# ── Hallucination Filter ────────────────────────────────────────────────────

HALLUCINATIONS = {
    "you", "thank you.", "thanks for watching!", "", "okay", "all right",
    "yeah", "sure", "cool", "so", "just", "all", "bye", "gracias",
}


def is_hallucination(text: str) -> bool:
    stripped = text.lower().strip().rstrip('.')
    if stripped in HALLUCINATIONS:
        return True
    if len(stripped.split()) < 3:
        return True
    return False


# ── Main Loop ───────────────────────────────────────────────────────────────

def main():
    if not OPENCLAW_API_TOKEN:
        print("❌ Set VL_OPENCLAW_API_TOKEN (your OpenClaw API token)")
        print("   Find it with: openclaw gateway status")
        return

    print("=" * 60)
    print("🦞 Voice Loop")
    print("=" * 60)
    print(f"  STT:   Whisper {WHISPER_MODEL_EN} / {WHISPER_MODEL_MULTI} (local)")
    print(f"  Brain: OpenClaw (streaming SSE)")
    print(f"  TTS:   Kokoro sentence-by-sentence ({get_voice()})")
    print(f"  Lang:  {CURRENT_LANG} (say 'switch to [language]' to toggle)")
    print(f"  Speed: {KOKORO_SPEED}x")
    print("  Press Ctrl+C to stop\n")

    print("Loading Kokoro model...", flush=True)
    try:
        init_kokoro()
        print("✅ Kokoro loaded\n", flush=True)
    except Exception as e:
        print(f"❌ Failed to load Kokoro: {e}")
        print("   Run the setup script or download models manually.")
        return

    try:
        default_in = sd.query_devices(kind='input')
        print(f"🎙️  Input: {default_in['name']}")
        print(f"🔈 Output: {sd.query_devices(kind='output')['name']}\n")
    except Exception as e:
        print(f"❌ Audio device issue: {e}")
        print("   Connect headphones/AirPods and try again.")
        return

    while running:
        try:
            audio = record_utterance()
            if audio is None:
                continue

            text = transcribe(audio)
            if not text:
                print("   (empty transcription, skipping)", flush=True)
                continue

            if is_hallucination(text):
                print(f"   (filtered: '{text}')", flush=True)
                continue

            print(f"   You: \"{text}\"", flush=True)

            if check_language_switch(text):
                continue

            stream_and_speak(text)

        except Exception as e:
            print(f"⚠️  Error: {e}", flush=True)
            time.sleep(1)

    print("👋 Voice loop ended.")


if __name__ == "__main__":
    main()
