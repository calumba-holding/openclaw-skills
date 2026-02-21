---
name: ai-voice-chat
description: Hands-free AI voice conversations via AirPods or any Bluetooth headset. Local Whisper STT + Kokoro-ONNX TTS with OpenClaw agent streaming. Auto-starts on headset connect, supports mid-conversation language switching (English, Spanish, French, Japanese, Chinese). Use when setting up voice chat, voice assistant, voice interaction, configuring voice loop, troubleshooting audio, or enabling hands-free voice conversation with an AI agent. Zero cost for voice processing — only LLM API tokens.
os:
  - darwin
requires:
  bins:
    - whisper
    - python3
    - security
  env:
    - VL_OPENCLAW_API_TOKEN
    - VL_OPENCLAW_SESSION_TO
---

# Voice Loop

Hands-free voice conversation: speak → Whisper transcribes (local) → OpenClaw streams response (SSE) → Kokoro speaks sentence-by-sentence (local).

## Architecture

```
Microphone → Whisper STT (local, ~2s) → OpenClaw API (cloud, ~4-10s) → Kokoro TTS (local, <1s) → Speakers
```

Streaming TTS speaks each sentence as it arrives — first audio in ~3s, not 13s.

## Setup

Run the setup script to install dependencies and download models:

```bash
bash scripts/setup.sh
```

This creates a `.venv`, installs Python packages (`numpy`, `sounddevice`, `soundfile`, `kokoro-onnx`), and downloads Kokoro models (~136MB total).

### Prerequisites

- macOS on Apple Silicon (M1–M4)
- Python 3.11+
- Whisper CLI: `brew install openai-whisper`
- OpenClaw running: `openclaw gateway status`

### Token Storage (Recommended: macOS Keychain)

Store your OpenClaw API token securely in macOS Keychain instead of plaintext:

```bash
security add-generic-password -a "$USER" -s "voice-loop-openclaw-token" -w "YOUR_TOKEN_HERE" -U
```

The voice loop reads from Keychain automatically. To also set the session target:

```bash
security add-generic-password -a "$USER" -s "voice-loop-session-to" -w "+1XXXXXXXXXX" -U
```

Alternatively, set environment variables (`VL_OPENCLAW_API_TOKEN`, `VL_OPENCLAW_SESSION_TO`) — these take precedence over Keychain if both exist.

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VL_OPENCLAW_API_TOKEN` | Yes* | Keychain | OpenClaw API token (from `openclaw gateway status`). *Falls back to Keychain `voice-loop-openclaw-token` |
| `VL_OPENCLAW_SESSION_TO` | Yes* | Keychain | Target phone number or user ID. *Falls back to Keychain `voice-loop-session-to` |
| `VL_OPENCLAW_API_URL` | No | `http://127.0.0.1:18789/v1/chat/completions` | OpenClaw API endpoint (localhost only — remote endpoints are blocked) |
| `VL_SILENCE_THRESHOLD` | No | `0.015` | RMS level for silence detection |
| `VL_SILENCE_DURATION` | No | `1.2` | Seconds of silence before sending |
| `VL_KOKORO_SPEED` | No | `1.15` | TTS playback speed (1.0 = natural) |
| `VL_DEFAULT_LANG` | No | `en` | Starting language |
| `VL_DEFAULT_GENDER` | No | `female` | Voice gender (female/male) |
| `VL_WHISPER_MODEL_EN` | No | `base.en` | English Whisper model |
| `VL_WHISPER_MODEL_MULTI` | No | `small` | Multilingual Whisper model |
| `VL_HEADSET_NAME` | No | `AirPods` | Bluetooth device name substring to watch |
| `VL_POLL_INTERVAL` | No | `5` | Headset poll interval in seconds |

## Running

### Manual start

```bash
export VL_OPENCLAW_API_TOKEN="your-token"
export VL_OPENCLAW_SESSION_TO="+1XXXXXXXXXX"
.venv/bin/python scripts/voice_loop.py
```

### Auto-start on headset connect

```bash
.venv/bin/python scripts/airpods_watcher.py
```

The watcher polls audio devices every 5s. When a device matching `VL_HEADSET_NAME` appears as input, it starts the voice loop. On disconnect, it stops. On crash, it restarts.

### Auto-start on boot (launchd)

Create `~/Library/LaunchAgents/com.voice-loop.watcher.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voice-loop.watcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>VENV_PYTHON_PATH</string>
        <string>WATCHER_SCRIPT_PATH</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/voice-loop-watcher.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/voice-loop-watcher.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

Replace `VENV_PYTHON_PATH` and `WATCHER_SCRIPT_PATH`. No tokens in the plist — they're read from Keychain at runtime. Then:

```bash
launchctl load ~/Library/LaunchAgents/com.voice-loop.watcher.plist
```

## Language Switching

Say any of these mid-conversation:

- **Spanish:** "switch to Spanish", "Spanish mode", "habla en español"
- **French:** "switch to French", "French mode", "parle en français"
- **Japanese:** "switch to Japanese", "Japanese mode"
- **Chinese:** "switch to Chinese", "Chinese mode", "speak Mandarin"
- **Back to English:** "back to English", "English mode", "stop Spanish"

On switch: Whisper model changes (`base.en` → `small` multilingual), Kokoro voice and language change, LLM prompt includes language context. A spoken confirmation plays in the target language.

## Voice Options

**English:** af_heart ⭐ (female), am_puck ⭐ (male), af_bella, af_nova, af_sarah, am_adam, am_eric
**Spanish:** ef_dora ⭐ (female), em_alex (male)
**French:** ff_siwis
**Japanese:** jf_alpha (female), jm_beta (male)
**Chinese:** zf_xiaobei (female), zm_yunjian (male)

Override default gender: `export VL_DEFAULT_GENDER=male`

## Tuning

- **Faster STT:** `VL_WHISPER_MODEL_EN=tiny.en` (~1s vs ~2s, less accurate)
- **Snappier response:** `VL_SILENCE_DURATION=0.8` (may cut off mid-pause)
- **Faster LLM:** Use Sonnet instead of Opus (~4s vs ~10s)
- **Noise issues:** Raise `VL_SILENCE_THRESHOLD` (try `0.02` or `0.03`)
- **Speed:** `VL_KOKORO_SPEED=1.2` for faster speech, `1.0` for natural

## Troubleshooting

**"Audio device issue"** — Headphones not connected or not set as default. Check System Settings > Sound.

**Empty transcriptions / hallucinations** — Whisper generating phantom text from background noise. Script auto-filters utterances under 3 words and known hallucination phrases. Raise `VL_SILENCE_THRESHOLD` if persistent.

**"Streaming error"** — OpenClaw not running or token invalid. Check `openclaw gateway status`.

**Kokoro model not found** — Run `bash scripts/setup.sh` to download models to `~/.cache/kokoro-onnx/`.

**Multilingual transcription garbled** — Whisper `small` model with real microphone input can struggle with non-English audio quality. Works well with clear audio. For best results: speak clearly, minimize background noise.

## Cost

$0 for voice processing. Whisper and Kokoro run locally. Only cost is LLM API tokens (same as texting your agent).

## Latency

| Component | Time | Local/Cloud |
|-----------|------|-------------|
| Whisper STT | ~2s | Local |
| LLM (Opus) | ~8-10s | Cloud |
| LLM (Sonnet) | ~3-5s | Cloud |
| Kokoro TTS | <1s | Local |
| **First speech (streaming)** | **~3s** | — |

## Security

- **Tokens**: Stored in macOS Keychain, not plaintext files or environment variables in plists. The script reads from Keychain at runtime via `security find-generic-password`.
- **API endpoint locked to localhost**: The script **refuses to connect** to non-local API endpoints. If `VL_OPENCLAW_API_URL` points to a remote address, the script exits immediately. There is no override — localhost only.
- **Sandboxed subprocess environment**: The watcher only passes `VL_*` env vars, `PATH`, and `HOME` to the voice loop process — not your full environment.
- **No arbitrary executable paths**: Whisper and Python paths are resolved from PATH or the skill's own venv — not user-configurable via env vars.
- **Audio**: All audio capture and TTS happen locally. No audio data leaves your machine. Only the text transcription is sent to the LLM via localhost.
- **No data exfiltration**: The scripts make no network calls except to localhost. Remote endpoints cannot be enabled.

## Credits

- [Kokoro-ONNX](https://github.com/thewh1teagle/kokoro-onnx) — local neural TTS
- [OpenAI Whisper](https://github.com/openai/whisper) — local speech-to-text
- [OpenClaw](https://github.com/openclaw/openclaw) — AI agent framework
