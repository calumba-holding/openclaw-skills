---
name: qwen-image-plus-sophnet
description: Generate images via Sophnet Qwen-Image-Plus and poll for task completion. Use when the user asks for Sophnet image generation, Qwen-Image-Plus, or requests an image from the Sophnet API.
---

# Qwen-Image-Plus (Sophnet) Image Generation

Use the Sophnet image generator API to create an image task, poll until it
finishes, then return the image URL.

## Quick Start

Set the API key (preferred):
```bash
export SOPHNET_API_KEY="YOUR_API_KEY"
```

Run the script with an absolute path (do NOT cd to the skill directory):
```bash
bash /home/shutongshan/.openclaw/workspace/skills/qwen-image-plus-sophnet/scripts/generate_image.sh --prompt "your prompt"
```

## Script Options

- `--prompt` (required): user prompt
- `--negative-prompt` (optional)
- `--size` (optional, default `1024*1024`)
- `--n` (optional, default `1`)
- `--watermark` (optional, default `false`)
- `--prompt-extend` (optional, default `true`)
- `--api-key` (optional, overrides `SOPHNET_API_KEY`)
- `--poll-interval` (optional, default `2`)
- `--max-wait` (optional, default `300`)

## Output Contract

The script prints:
- `TASK_ID=...`
- `STATUS=succeeded`
- `IMAGE_URL=...` (one or more lines)

Use the `IMAGE_URL` value to respond to the user.

## Workflow

1. POST create-task with `model=Qwen-Image-Plus` and user prompt
2. Poll GET task status until `SUCCEEDED`
3. Extract `url` and return to the user

## Real Example (captured run)

Prompt:
```text
A scenic mountain landscape in ink wash style
```

Command:
```bash
bash /home/shutongshan/.openclaw/workspace/skills/qwen-image-plus-sophnet/scripts/generate_image.sh \
  --prompt "A scenic mountain landscape in ink wash style" \
  --negative-prompt "blurry, low quality" \
  --size "1024*1024" \
  --n 1 \
  --watermark false \
  --prompt-extend true
```

Output:
```text
TASK_ID=7BWFICt0zgLvuaTKg8ZoDg
STATUS=succeeded
<!-- OpenClaw security redaction: secret removed from archive. -->
```

## Common Errors

- `Error: No API key provided.` -> set `SOPHNET_API_KEY` or pass `--api-key`
- `STATUS=failed` -> check key permissions/quota or prompt parameters
- `Error: url not found in response` -> inspect API response manually
