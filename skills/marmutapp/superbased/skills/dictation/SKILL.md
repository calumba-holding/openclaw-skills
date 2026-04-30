---
name: dictation
description: Voice input and audio transcription. Use when the user wants to speak instead of type, transcribe audio files, or work with voice recordings.
---

**Live microphone recording:**
Use `superbased_dictate` with `mic: true` and `duration` in seconds (default 10). Set `cleanup: true` to remove filler words and duplicates.

**Audio file transcription:**
- With cleanup: `superbased_dictate` with `audioPath`
- Raw Whisper output: `superbased_transcribe` with `audioPath`

**Transcription history:**
Use `superbased_dictation_history` to query past transcriptions (default limit 20).

**When to use dictate vs transcribe:**
- `superbased_dictate`: adds filler word removal, deduplication, and supports mic recording
- `superbased_transcribe`: raw Whisper output only, for when exact transcription is needed

Supported audio formats: wav, mp3, webm.
