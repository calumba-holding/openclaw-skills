---
name: IMA Studio Music Generation
version: 1.2.2
category: file-generation
author: IMA Studio (imastudio.com)
keywords: imastudio, ai music, text_to_music, Suno, DouBao, GenBGM, GenSong
description: >
  Generate music from text with IMA Open API. Supports Suno (sonic), DouBao BGM (GenBGM),
  and DouBao Song (GenSong). Uses only api.imastudio.com.
requires:
  env:
    - IMA_API_KEY
  primaryCredential: IMA_API_KEY
  credentialNote: IMA_API_KEY is sent only to api.imastudio.com for authentication.
persistence:
  readWrite: []
  retention: No local preferences or logs are written by this skill script.
---

# IMA Voice AI Creation

## Capability

This skill generates music/audio from text prompts (`text_to_music`) through IMA Open API.

Supported model IDs:
- `sonic` (Suno)
- `GenBGM` (DouBao BGM)
- `GenSong` (DouBao Song)

## Network and Credential Transparency

- API domain used: `https://api.imastudio.com`
- Required key: `IMA_API_KEY` (environment variable)
- The script does not call secondary upload domains.
- The script does not read other skills' files.

## Runtime Rules

1. Always query `/open/v1/product/list` first.
2. Resolve `attribute_id`, `credit`, and latest `model_version` from product list.
3. Create task via `/open/v1/tasks/create`.
4. Poll `/open/v1/tasks/detail` until completed or timeout.

## Defaults and Timeouts

- Task type is fixed to `text_to_music`.
- Poll interval: 5 seconds.
- Max poll wait: 8 minutes.
- If `--model-id` is omitted, default model is `sonic`.

## User Input Mapping

- BGM / instrumental / 背景音乐 / 纯音乐 -> `GenBGM`
- Song / lyrics / 人声 / 歌曲 -> `sonic` or `GenSong`
- If unspecified -> default `sonic`

## Script Invocation

Set key first:

```bash
export IMA_API_KEY="ima_your_key_here"
```

```bash
python3 {baseDir}/scripts/ima_voice_create.py \
  --model-id sonic \
  --prompt "upbeat lo-fi hip hop, 90 BPM, no vocals" \
  --output-json
```

List models:

```bash
python3 {baseDir}/scripts/ima_voice_create.py \
  --list-models
```

## Error Handling Policy

- Return user-friendly error summaries in plain language.
- Include practical next step suggestions (retry, switch model, check API key/credits).
- Do not expose raw internal payloads unless debugging is explicitly requested.

## Expected Output

On success, return:
- task id
- result URL
- model id/model name
- credit used

If `--output-json` is enabled, parse JSON from script output.
