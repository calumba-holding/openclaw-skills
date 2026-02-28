---
name: openclaw-model-router-skill
description: Deterministic model routing for OpenClaw with prefix routing (@codex/@mini), timezone-aware schedule switching, verify-after-switch, rollback, lock protection, and JSONL audit logs.
---

# OpenClaw Model Router Skill

## What this skill provides

- Prefix routing:
  - `@codex` -> `openai-codex/gpt-5.3-codex`
  - `@mini` -> `minimax/MiniMax-M2.5`
  - aliases: `@c`, `@m`
- Time-based scheduler from `router.schedule.json`
- Production-safe schedule switching:
  - `schedule apply` / `schedule end`
  - auth env checks (`auth.requiredEnv`)
  - switch + readback verification
  - rollback on failure
  - lock file for concurrency
  - audit logs (`router.log.jsonl`)

## Quick commands

```bash
node src/cli.js validate
node src/cli.js route "@codex implement this" --json
node src/cli.js schedule validate
node src/cli.js schedule apply --json
node src/cli.js schedule end --id workday_codex --json
```

## Config files

- `router.config.json`
- `router.schedule.json`

## Tests

```bash
node --test
```
