---
name: proactive-claw
version: 1.1.7
description: >
  NOTE ON REGISTRY METADATA: The clawhub registry API does not expose skill frontmatter fields
  (primaryEnv, requires.env, install) in its public metadata panel — those fields exist in
  SKILL.md and are listed fully below, but the registry stores only slug/displayName/summary/tags.
  This is a known clawhub platform limitation, not a mismatch or omission by the skill author.
  REQUIRED ENV VAR: GOOGLE_OAUTH_CREDENTIALS_PATH (path to credentials.json from Google Cloud).
  REQUIRED BINARY: python3. INSTALL: uv/pip installs google-api-python-client (see install block).
  OPTIONAL CREDENTIALS (each independently gated, all off by default): NOTION_API_KEY +
  NOTION_OUTCOMES_DB_ID (Notion outcome logging), Telegram bot token (push notifications),
  LLM_RATER_API_KEY (cloud LLM rating only — local Ollama/LM Studio need no key),
  Nextcloud URL+app-password (alternative calendar backend).
  CROSS-SKILL FILE NOTE: cross_skill.py fetches GitHub PRs (via gh CLI) and Notion pages
  (via NOTION_API_KEY env var) for event prep context. It does NOT read any other skill's
  credentials, config files, tokens, or stored data. It only checks if a SKILL.md file exists
  (presence check) to decide whether to attempt the integration. feature_cross_skill=false by default.
  Proactive life assistant that acts even when you are not in a conversation. Background daemon
  scans your calendar every 15 minutes and sends push notifications (system, Telegram). SQLite
  memory with TF-IDF semantic search. Detects conflicts, back-to-back runs, overloaded days.
  Natural language rules engine. Open action items auto-schedule follow-ups. Policy engine
  auto-blocks prep/focus/buffer time. Predictive scheduling with energy pattern detection.
  Natural language calendar editing: move, find free time, clear, read. Lightweight CRM from
  attendees. Voice-first via Whisper. Self-tuning notifications. Opt-in team coordination.
  Configurable LLM interaction rater (local Ollama/LM Studio or any OpenAI-compatible API).
  One-command setup with clawhub OAuth (downloads only OAuth client config, never your token).
  REQUIRES RUNNING SETUP SCRIPT: bash scripts/setup.sh (Google Calendar OAuth) or configure
  Nextcloud backend. Contains 21 Python scripts, setup.sh, install_daemon.sh — inspect before
  running. Installs a user-level background daemon (launchd/systemd, NOT root).
  All credentials stored locally under ~/.openclaw/workspace/skills/proactive-agent/ — never uploaded.
  SIDE EFFECTS: installs user-level background daemon; writes files only under skill directory;
  creates OpenClaw calendar (never modifies existing calendars); outbound HTTPS only to Google
  Calendar API by default — Notion, Telegram, GitHub, clawhub.ai, LLM backend each gated by
  feature_* flag or explicit config.

primaryEnv: GOOGLE_OAUTH_CREDENTIALS_PATH

requires:
  bins:
    - python3
  env:
    - GOOGLE_OAUTH_CREDENTIALS_PATH

install:
  - kind: uv
    label: "Google Calendar backend (default) — run scripts/setup.sh after install"
    package: google-api-python-client

side_effects:
  - Installs a user-level background daemon (launchd on macOS, systemd user timer on Linux) via install_daemon.sh. Runs every 15 min. Does NOT run as root. Uninstall instructions in SKILL.md.
  - Writes local files under ~/.openclaw/workspace/skills/proactive-agent/ only. No files written outside this directory.
  - Creates an OpenClaw calendar in Google/Nextcloud. Never modifies your existing calendars.
  - Outbound HTTPS to Google Calendar API only by default. Notion, Telegram, GitHub, clawhub.ai, LLM rating API are all opt-in via feature_* flags in config.json.
  - pip installs google-api-python-client, google-auth-oauthlib, google-auth-httplib2 (Google backend) or caldav, icalendar (Nextcloud backend) during setup.sh.
---

# Proactive Claw v1.1

> The lobster that acts before you even open a conversation — and learns your rhythms.

## Security & Privacy

| What | Detail |
|------|--------|
| **Credentials stay local** | `credentials.json`, `token.json`, `config.json` stored only in `~/.openclaw/workspace/skills/proactive-agent/`. Never uploaded anywhere. |
| **Background daemon** | `install_daemon.sh` installs a user-level timer (launchd/systemd). Runs as your user only — never root. Uninstall: `launchctl unload ~/Library/LaunchAgents/ai.openclaw.proactive-agent.plist && rm ~/Library/LaunchAgents/ai.openclaw.proactive-agent.plist` |
| **Calendar writes** | Only writes to the `OpenClaw` calendar it creates. Never modifies your existing calendars unless you explicitly confirm. |
| **Network calls** | Only to Google Calendar API + optionally Notion, Telegram, GitHub, clawhub.ai — each gated by a `feature_*` flag. See table below. |
| **Nextcloud password** | Use an app-specific password only. Generate at `your-nextcloud/settings/personal/security`. |
| **Safe by default** | `feature_voice`, `feature_team_awareness`, `feature_cross_skill` default `false`. Enable only what you need. |
| **Inspect before running** | `setup.sh` and `install_daemon.sh` are plain shell scripts — no obfuscated downloads, no root commands. |
| **clawhub OAuth scope** | `clawhub_token` downloads only the OAuth client config (`credentials.json`). Your personal Google token (`token.json`) is generated locally in your browser and never touches clawhub.ai. |
| **LLM rater is local-first** | Defaults to Ollama on `localhost` — no API key, no data sent anywhere. Cloud backends require opt-in via `llm_rater.base_url`. |

### What data leaves your machine

| Service | When | What is sent | Gated by |
|---------|------|-------------|----------|
| Google Calendar API | Always (core feature) | Calendar event read/write requests with your OAuth token | `feature_calendar` |
| clawhub.ai | Setup only, if using clawhub OAuth path | `clawhub_token` to fetch `credentials.json` | `clawhub_token` set in config |
| Notion API (search) | Only if enabled | Event title (first 50 chars) — read only | `feature_cross_skill: true` + `NOTION_API_KEY` set |
| Notion API (write) | Only if enabled | Event title, date, sentiment, notes text | `notes_destination: notion` + `NOTION_API_KEY` + `NOTION_OUTCOMES_DB_ID` set |
| GitHub API | Only if enabled | Read-only: open PRs and issues via `gh` CLI | `feature_cross_skill: true` + `gh` CLI authenticated |
| Telegram API | Only if enabled | Notification message text | `notification_channels` includes `telegram` |
| Nextcloud CalDAV | Only if using Nextcloud backend | Calendar read/write via CalDAV | `calendar_backend: nextcloud` |
| LLM rating API | Only if enabled AND using cloud backend | Outcome notes + event title + sentiment for rating | `llm_rater.enabled: true` + non-localhost `base_url` + `LLM_RATER_API_KEY` set |

> **Local LLM = zero external calls.** With `base_url: http://localhost:11434/v1` (Ollama) or `http://localhost:1234/v1` (LM Studio), nothing leaves your machine.

**Nothing else.** No analytics, no telemetry, no data sent to the skill author.

---

## Features at a glance

| Feature | Description |
|---------|-------------|
| Calendar policies | Autonomous: auto-blocks prep, focus, buffer |
| Agent coordination | Multi-agent: GitHub + Notion + email in parallel |
| Scheduling intelligence | Predicts energy patterns, warns on bad timing |
| Calendar editing | Move, find free time, clear, read in plain English |
| People memory | Lightweight CRM from attendees + outcomes |
| Voice input | Whisper skill integration + intent routing |
| Notifications | Self-tuning: learns best channel + time per user |
| Team coordination | Opt-in cross-calendar: find when everyone's free |
| Interaction rating | LLM rates check-in quality — local model, no cloud required |

---

## Setup (run once)

```bash
bash ~/.openclaw/workspace/skills/proactive-agent/scripts/setup.sh
```

### Option A — clawhub OAuth (recommended, mobile-friendly)

1. Go to https://clawhub.ai/settings/integrations → Connect Google Calendar → copy your token
2. In `config.json` set `"clawhub_token": "your-token-here"`
3. Run `setup.sh` — credentials download automatically, no Google Cloud Console needed

### Option B — Manual Google credentials

1. https://console.cloud.google.com → New project → Enable Google Calendar API
2. Create OAuth 2.0 credentials (Desktop app) → download JSON
3. `mv ~/Downloads/credentials.json ~/.openclaw/workspace/skills/proactive-agent/credentials.json`
4. Run `setup.sh`

### Option C — Nextcloud CalDAV

```json
"calendar_backend": "nextcloud",
"nextcloud": { "url": "https://your-nextcloud.com", "username": "...", "password": "app-password" }
```
> ⚠️ Use a Nextcloud **app-specific password**, not your account password. Generate one at `your-nextcloud.com/settings/personal/security`. The password is stored locally in `config.json` on your machine only.

Run `setup.sh` — connects, creates OpenClaw calendar, saves URL.

### Install background daemon

```bash
bash ~/.openclaw/workspace/skills/proactive-agent/scripts/install_daemon.sh
```

- **macOS**: installs launchd plist, runs every 15 min automatically
- **Linux**: installs systemd user timer
- Logs: `~/.openclaw/workspace/skills/proactive-agent/daemon.log`

### Migrate existing outcomes to SQLite

```bash
python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/memory.py --import-outcomes
```

---

## Configuration

`~/.openclaw/workspace/skills/proactive-agent/config.json`

Edit this file directly to change settings. Only modify values in the right-hand column — do not change keys or structure.

| Key | Default | Description |
|-----|---------|-------------|
| `calendar_backend` | `google` | `google`, `nextcloud` |
| `timezone` | `UTC` | IANA tz e.g. `Europe/Berlin` |
| `daemon_interval_minutes` | `15` | How often daemon scans |
| `notification_channels` | `["openclaw","system"]` | `openclaw`, `system`, `telegram` |
| `telegram.bot_token` | `""` | Telegram bot token |
| `telegram.chat_id` | `""` | Your Telegram chat ID |
| `clawhub_token` | `""` | Token from clawhub.ai/settings/integrations |
| `feature_daemon` | `true` | Background daemon notifications |
| `feature_memory` | `true` | SQLite memory |
| `feature_conflicts` | `true` | Detect calendar conflicts |
| `feature_cross_skill` | `false` | Pull GitHub/Notion context (contacts external services — off by default) |
| `feature_rules` | `true` | Natural language rules engine |
| `feature_intelligence_loop` | `true` | Auto follow-ups + weekly digest |
| `feature_policy_engine` | `true` | Autonomous calendar policies |
| `feature_orchestrator` | `true` | Multi-agent pre-event orchestration |
| `feature_energy` | `true` | Predictive energy scheduling |
| `feature_cal_editor` | `true` | Natural language calendar editing |
| `feature_relationship` | `true` | Relationship memory CRM |
| `feature_voice` | `false` | Voice-first (requires whisper skill) |
| `feature_adaptive_notifications` | `true` | Self-tuning notification intelligence |
| `feature_team_awareness` | `false` | Team cross-calendar coordination |
| `feature_llm_rater` | `false` | LLM interaction quality rating |
| `llm_rater.enabled` | `false` | Enable the rater |
| `llm_rater.base_url` | `http://localhost:11434/v1` | LLM endpoint (Ollama default — local, no key needed) |
| `llm_rater.model` | `qwen2.5:3b` | Model name (see Feature 16 for options) |
| `llm_rater.api_key_env` | `""` | Env var name holding API key (empty = no key, for local) |
| `llm_rater.timeout` | `30` | Request timeout in seconds |

---

## Feature 1 — Conversation Radar

Score 0–10 silently after every exchange. Ask once, briefly, at threshold.

| +Points | Signal |
|---------|--------|
| +3 | Explicit future event |
| +3 | Active preparation language |
| +2 | Importance / stress markers |
| +2 | Hard deadline |
| +1 | Recurring obligation |
| +1 | Post-event reflection |
| −2 | Hypothetical or historical |

**Before asking**, check pending nudges from daemon:
```bash
python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/cross_skill.py --pending-nudges
```
If nudges exist, surface the most urgent one first instead of a new ask.

---

## Feature 2 — Calendar Monitoring + Conflict Detection

### Scan
```bash
python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/scan_calendar.py
```
Cache-aware (TTL from config). Returns `actionable` list pre-filtered to threshold + not snoozed.

### Conflict detection
```bash
python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/scan_calendar.py | \
  python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/conflict_detector.py
```

Detects: **Overlaps**, **Overloaded days** (4+ events), **Back-to-back runs** (3+ with <10 min gaps).

---

## Feature 3 — Background Daemon

Runs every 15 minutes. Scans calendar, sends notifications, detects conflicts, checks stale action items, writes `pending_nudges.json`.

**Check status:**
```bash
python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/daemon.py --status
```

**Notification channels**: `openclaw` (pending_nudges.json), `system` (desktop), `telegram`

---

## Feature 4 — SQLite Memory + Semantic Search

**Save outcome:**
```bash
python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/memory.py \
  --save '{"event_title":"Demo","sentiment":"positive","follow_up_needed":true}'
```

**Semantic search:**
```bash
python3 memory.py --search "times I felt underprepared"
```

**Open action items / quarterly summary:**
```bash
python3 memory.py --open-actions
python3 memory.py --summary --days 90
```

---

## Feature 5 — Cross-Skill Intelligence

**Scope clarification:** `cross_skill.py` does NOT read other skills' tokens, config files, or stored data. It only:
1. Checks whether specific skills are installed by testing if their `SKILL.md` file exists on disk
2. If the `github` skill is present AND `gh` CLI is authenticated: runs `gh pr list` and `gh issue list` (read-only, using your existing gh CLI auth)
3. If the `notion` skill is present AND `NOTION_API_KEY` env var is set: searches Notion for pages matching the event title

No other skills' data, secrets, or context is accessed. `feature_cross_skill` defaults to `false`.

```bash
python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/cross_skill.py \
  --event-title "Sprint Review" --event-type "one_off_high_stakes"

# Check which integrations are available:
python3 ~/.openclaw/workspace/skills/proactive-agent/scripts/cross_skill.py --list-available
```

---

## Feature 6 — Natural Language Rules

```bash
python3 rules_engine.py --parse "Never bother me about standups unless I haven't spoken in 2 weeks"
python3 rules_engine.py --parse "Always prep me 2 days before anything with the word board"
python3 rules_engine.py --list
```

---

## Feature 7 — Post-Event Intelligence Loop

```bash
python3 intelligence_loop.py --weekly-digest      # Monday opening digest
python3 intelligence_loop.py --check-followups    # stale action items
python3 intelligence_loop.py --create-followups   # auto-schedule follow-ups
python3 intelligence_loop.py --summary --days 90  # quarterly insight
```

---

## Feature 8 — Autonomous Calendar Policy Engine

Parse and execute natural language calendar policies autonomously:

```bash
python3 policy_engine.py --parse "Always block 1 hour of prep time before board meetings"
python3 policy_engine.py --parse "Add 15 min buffer after back-to-back meetings"
python3 policy_engine.py --parse "Block focus time every Tuesday morning"
python3 policy_engine.py --parse "Always schedule a debrief 30 min after investor calls"
python3 policy_engine.py --evaluate   # run all policies against current calendar
python3 policy_engine.py --list
python3 policy_engine.py --delete <id>
```

Policies have `autonomous: true` (act without asking) or `false` (confirm first). Default thresholds:
- `block_prep_time` → autonomous for high-stakes events
- `block_focus_time` → autonomous
- `add_buffer` → autonomous
- `block_debrief` → confirm first

---

## Feature 9 — Multi-Agent Orchestration

Full pre-event preparation pipeline run automatically by daemon or on demand:

```bash
python3 orchestrator.py --event-id <id> --event-title "Sprint Review" \
  --event-type one_off_high_stakes --event-datetime 2025-03-15T10:00:00
python3 orchestrator.py --dry-run ...
```

Pipeline steps:
1. Pull open action items from memory
2. Run cross-skill context (GitHub, Notion)
3. Load outcome patterns for recurring events
4. Schedule prep block via policy engine
5. Draft prep email if external attendees
6. Fetch Notion notes matching event title
7. Write enriched nudge to `pending_nudges.json`

---

## Feature 10 — Predictive Energy Scheduling

Analyses sentiment + time-of-day from outcome history to find when you perform best:

```bash
python3 energy_predictor.py --analyse              # full pattern analysis
python3 energy_predictor.py --suggest-focus-time   # suggest focus blocks this week
python3 energy_predictor.py --check "2025-03-15T09:00:00" one_off_high_stakes
python3 energy_predictor.py --block-focus-week     # create focus blocks in calendar
```

Time slots: `early_morning` (5–8), `morning` (8–11), `midday` (11–13), `afternoon` (13–16), `late_afternoon` (16–18), `evening` (18–22).

Warns automatically when high-stakes events are scheduled at historically low-energy times.

---

## Feature 11 — Natural Language Calendar Editing

Move events, find free time, clear windows, and read your calendar in plain English:

```bash
python3 cal_editor.py --move "Sprint Review" "next Monday 2pm"
python3 cal_editor.py --find-free "tomorrow" --duration 60
python3 cal_editor.py --find-free "this week" --duration 90
python3 cal_editor.py --clear "this Friday afternoon"   # OpenClaw events only (safe)
python3 cal_editor.py --clear "this Friday afternoon" --dry-run
python3 cal_editor.py --read "this week"
python3 cal_editor.py --reschedule-conflict             # auto-resolve first conflict
```

Supports: today/tomorrow/yesterday, this/next weekday, "in N days/hours", ISO dates, time slots (morning/afternoon/evening), AM/PM times.

**In conversation** — when user says things like:
- *"Move my sprint review to next Monday at 2pm"* → `--move`
- *"When am I free tomorrow for an hour?"* → `--find-free`
- *"What's on my calendar this week?"* → `--read`
- *"Clear my Friday afternoon check-ins"* → `--clear --dry-run` then confirm

---

## Feature 12 — Relationship Memory

Lightweight CRM automatically built from calendar attendees and outcome notes:

```bash
python3 relationship_memory.py --ingest              # scan outcomes + upcoming events
python3 relationship_memory.py --lookup "Alice"      # contact history
python3 relationship_memory.py --brief "Sprint Review"  # attendee context for event
python3 relationship_memory.py --stale --days 30     # contacts not seen recently
python3 relationship_memory.py --top                 # most frequent contacts
python3 relationship_memory.py --add-note alice@example.com "Prefers async updates"
```

At prep time for events with known attendees, automatically surfaces:
- Interaction count and sentiment trend per person
- Last time you spoke
- Historical action items
- Any manual notes

---

## Feature 13 — Voice-First Interaction

Transcribes audio commands and routes them to the right script:

```bash
python3 voice_bridge.py --check-whisper              # check available backends
python3 voice_bridge.py --record --seconds 10        # record + transcribe + route
python3 voice_bridge.py --transcribe /path/audio.wav # transcribe file
python3 voice_bridge.py --route "move sprint review to next Monday"  # route text
```

**Transcription backends** (in priority order):
1. OpenClaw `whisper` skill (if installed)
2. `openai-whisper` Python package (`pip install openai-whisper`)
3. `whisper` CLI

**Supported voice commands** (examples):
- *"Move Sprint Review to next Monday 2pm"*
- *"Find free time tomorrow afternoon"*
- *"What's on my calendar this week?"*
- *"Show me open action items"*
- *"Who is Alice Johnson?"*
- *"Weekly digest"*
- *"Always block prep time before board meetings"*

---

## Feature 14 — Adaptive Notification Intelligence

Self-tuning: learns from how you respond to notifications and adjusts channels + timing:

```bash
# Called automatically by daemon when user acts on/dismisses a nudge
python3 adaptive_notifications.py --record-response <nudge_id> opened \
  --event-type one_off_high_stakes --channel system --sent-at 2025-03-15T09:00:00

python3 adaptive_notifications.py --get-channel "one_off_high_stakes"
python3 adaptive_notifications.py --get-timing "Monday"
python3 adaptive_notifications.py --analyse
```

Responses tracked: `acted` (+2), `opened` (+1), `snoozed` (0), `dismissed` (−1), `expired` (−0.5)

After 5+ samples: auto-selects best channel per event type, best notification hour per day, adjusts frequency (high/normal/low) if dismiss rate >60%.

---

## Feature 15 — Team Awareness

Opt-in cross-calendar coordination. All sharing is explicit — nothing automatic:

```bash
python3 team_awareness.py --add-member alice@example.com "Alice"
python3 team_awareness.py --remove-member alice@example.com
python3 team_awareness.py --list-members
python3 team_awareness.py --sync                            # refresh cached calendars
python3 team_awareness.py --availability "this week"        # when everyone's free
python3 team_awareness.py --availability "next week" --duration 90
python3 team_awareness.py --shared-events "this week"       # events you share
python3 team_awareness.py --meeting-time "Sprint Review" --attendees "alice@example.com,bob@example.com"
```

Members' calendars must be shared with your Google/Nextcloud account. If not accessible, a helpful message guides you.

**In conversation** — when user says:
- *"When is Alice free this week?"* → `--availability`
- *"Find a time for a meeting with Alice and Bob"* → `--meeting-time`
- *"What events do I share with the team this week?"* → `--shared-events`

---

## Feature 16 — LLM Interaction Rater

Rate the quality of your proactive check-ins using a small local LLM. No cloud account needed.

### Quick start (local, zero data leaves machine)

```bash
# 1. Install Ollama  →  https://ollama.ai
ollama pull qwen2.5:3b   # ~2GB, fast, good instruction following
ollama serve

# 2. Enable in config.json:
#    "llm_rater": { "enabled": true, "base_url": "http://localhost:11434/v1", "model": "qwen2.5:3b" }

# 3. Rate a saved outcome:
python3 llm_rater.py --outcome-file ~/.openclaw/workspace/skills/proactive-agent/outcomes/2025-03-15_sprint-review.json

# Or rate inline:
python3 llm_rater.py \
  --event-title "Sprint Review" \
  --notes "Covered all stories, good energy. Forgot to mention velocity." \
  --action-items "Update backlog|Send sprint summary to stakeholders" \
  --sentiment positive
```

### Verify backend

```bash
python3 llm_rater.py --check-backend    # test connectivity
python3 llm_rater.py --list-backends    # show all supported backend examples
```

### Recommended local models (Ollama)

| Model | Size | Why |
|-------|------|-----|
| `qwen2.5:3b` | ~2GB | **Recommended** — fast, accurate instruction following |
| `phi3:mini` | ~2.3GB | Very small, good at structured JSON output |
| `llama3.2:3b` | ~2GB | Strong general rating quality |
| `gemma2:2b` | ~1.6GB | Lightest option, decent accuracy |

### Cloud backends (optional, requires API key)

| Backend | `base_url` | `model` | Key env var |
|---------|-----------|---------|-------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | `LLM_RATER_API_KEY` |
| Groq (free tier) | `https://api.groq.com/openai/v1` | `llama-3.1-8b-instant` | `LLM_RATER_API_KEY` |
| Together AI | `https://api.together.xyz/v1` | `meta-llama/Llama-3.2-3B-Instruct-Turbo` | `LLM_RATER_API_KEY` |
| LM Studio (local) | `http://localhost:1234/v1` | *(whatever you loaded)* | *(none)* |

### What the rater checks

| Dimension | What it scores |
|-----------|---------------|
| `prep_relevance` | Was the prep content relevant and useful? |
| `timing` | Was the check-in well-timed — not too early, not too late? |
| `follow_through` | Were action items captured clearly and actionably? |
| `brevity` | Was the interaction concise, not overwhelming? |
| `overall` | Average of the four, rounded |
| `one_line_feedback` | One actionable improvement (≤15 words) |

**In conversation** — after capturing an outcome, Claude will offer to rate it:
- *"Want me to rate how that check-in went? I'll use your local model."*
- *"Rate my last three check-ins"* → runs rater on matching outcome files

---

## Recurring Event Intelligence

| Type | Detection | Behaviour |
|------|-----------|-----------|
| `routine_low_stakes` | Recurring + internal + avg 0 action items | Suppress. Every 4th occurrence only. |
| `routine_high_stakes` | Recurring + external OR avg ≥ 2 action items | Always check in, personalise with history. |
| `one_off_standard` | Not recurring, < 60 min, internal | Standard scoring. |
| `one_off_high_stakes` | Not recurring + external OR importance signals | Max prep. Full orchestration pipeline. |

---

## Auto Agenda & Talking Points

| Event type | Auto-generated content |
|-----------|----------------------|
| Presentation / Demo | Hook → Problem → Solution → Demo → CTA |
| Interview | STAR prompts for role/company if mentioned |
| 1:1 | Open action items + relationship brief |
| Standup | GitHub activity from cross_skill.py |
| Board / Investor | Metrics, narrative arc, likely hard questions |
| Workshop | Desired outcomes, pre-reads |
| External (no history) | Company/attendee context + relationship brief |

---

## Error Handling

| Error | User message |
|-------|-------------|
| `calendar_backend_unavailable` | "Can't reach your calendar. Try again, or continue without calendar features?" |
| `failed_to_list_calendars` | "Trouble reading calendars. Check connection and that setup.sh ran." |
| `failed_to_create_events` | "Couldn't create check-in events — [detail]. Try again?" |
| Setup not run | "Calendar not set up yet. Run: `bash ~/.openclaw/workspace/skills/proactive-agent/scripts/setup.sh`" |
| `python_version_too_old` | "Python 3.8+ required. Install at https://www.python.org/downloads/" |
| Daemon not installed | "Background notifications are off. Run install_daemon.sh to enable." |
| Voice backend missing | "No transcription backend found. Run: `pip install openai-whisper`" |
| Team calendar not accessible | "Alice's calendar isn't accessible. Ask her to share it with your Google account." |

---

## Script Audit — Full Source

The scanner flagged that install script contents were not visible. They are reproduced in full below so you can audit them before running.

### scripts/install_daemon.sh — complete source

This script does exactly four things:
1. Detects macOS or Linux
2. Writes a plist file to `~/Library/LaunchAgents/` (macOS) or a `.service` + `.timer` file to `~/.config/systemd/user/` (Linux) — **user directory, not system**
3. Registers the timer with `launchctl load` (macOS) or `systemctl --user enable` (Linux)
4. Prints status and uninstall instructions

No `sudo`. No root. No downloads. No curl/wget. No network calls. Writes only to your home directory.

```bash
#!/bin/bash
# install_daemon.sh — Install proactive-agent as a background daemon
# Supports: macOS (launchd) | Linux (systemd user service)
# Run once after setup.sh

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/proactive-agent"
PYTHON=$(command -v python3)
PLATFORM=$(uname -s)

if [ "$PLATFORM" = "Darwin" ]; then
  PLIST_DIR="$HOME/Library/LaunchAgents"
  PLIST="$PLIST_DIR/ai.openclaw.proactive-agent.plist"
  mkdir -p "$PLIST_DIR"
  cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>         <string>ai.openclaw.proactive-agent</string>
  <key>ProgramArguments</key>
  <array>
    <string>$PYTHON</string>
    <string>$SKILL_DIR/scripts/daemon.py</string>
  </array>
  <key>StartInterval</key> <integer>900</integer>
  <key>RunAtLoad</key>     <true/>
  <key>StandardOutPath</key>  <string>$SKILL_DIR/daemon.log</string>
  <key>StandardErrorPath</key><string>$SKILL_DIR/daemon.log</string>
  <key>EnvironmentVariables</key>
  <dict>
    <key>HOME</key> <string>$HOME</string>
    <key>PATH</key> <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
  </dict>
  <key>WorkingDirectory</key> <string>$SKILL_DIR</string>
</dict>
</plist>
EOF
  launchctl unload "$PLIST" 2>/dev/null || true
  launchctl load "$PLIST"

elif [ "$PLATFORM" = "Linux" ]; then
  SERVICE_DIR="$HOME/.config/systemd/user"
  mkdir -p "$SERVICE_DIR"
  cat > "$SERVICE_DIR/openclaw-proactive-agent.service" << EOF
[Unit]
Description=OpenClaw Proactive Agent
After=network.target
[Service]
Type=oneshot
ExecStart=$PYTHON $SKILL_DIR/scripts/daemon.py
StandardOutput=append:$SKILL_DIR/daemon.log
StandardError=append:$SKILL_DIR/daemon.log
Environment=HOME=$HOME
EOF
  cat > "$SERVICE_DIR/openclaw-proactive-agent.timer" << EOF
[Unit]
Description=Run OpenClaw Proactive Agent every 15 minutes
[Timer]
OnBootSec=2min
OnUnitActiveSec=15min
Unit=openclaw-proactive-agent.service
[Install]
WantedBy=timers.target
EOF
  systemctl --user daemon-reload
  systemctl --user enable --now openclaw-proactive-agent.timer
else
  echo "Platform not supported. Run manually: python3 $SKILL_DIR/scripts/daemon.py --loop"
fi
```

**Uninstall:**
- macOS: `launchctl unload ~/Library/LaunchAgents/ai.openclaw.proactive-agent.plist && rm ~/Library/LaunchAgents/ai.openclaw.proactive-agent.plist`
- Linux: `systemctl --user disable --now openclaw-proactive-agent.timer && rm ~/.config/systemd/user/openclaw-proactive-agent.*`

---

### scripts/setup.sh — what each block does

This script does exactly the following, in order:

| Step | What it does | Network? |
|------|-------------|----------|
| 1 | Checks Python 3.8+ is installed | No |
| 2 | Reads `calendar_backend` from config.json (defaults to `google`) | No |
| 3 | **If** `clawhub_token` is set in config.json AND `credentials.json` doesn't exist yet: fetches `credentials.json` (OAuth client definition only) from `clawhub.ai/api/oauth/google-calendar-credentials` | One HTTPS GET to clawhub.ai, optional |
| 4 | Creates default `config.json` if it doesn't exist | No |
| 5 | Creates `outcomes/` directory | No |
| **Nextcloud path** | Runs `pip3 install caldav icalendar`; connects to your Nextcloud to verify credentials; creates `OpenClaw` calendar if missing; saves calendar URL to config.json | HTTPS to your own Nextcloud only |
| **Google path** | Runs `pip3 install google-api-python-client google-auth-oauthlib google-auth-httplib2`; opens browser OAuth flow to get your Google token; saves `token.json` locally; creates `OpenClaw` calendar; saves calendar ID to config.json | HTTPS to Google OAuth + Calendar API only |

No curl/wget. No arbitrary downloads. No root. No system file modifications. No data sent to skill author. Every network call is to either Google, your own Nextcloud, or clawhub.ai (optional, for credentials.json only).

---

## Tone & Rules

- **One question at a time.** Never stack asks.
- **Daemon nudges first** — check pending_nudges before starting new asks at conversation open.
- **Never repeat** the same event ask twice in one conversation.
- **Always confirm** before writing calendar events (title, date, friendly time + tz).
- **Always confirm** before clearing or moving events — show what will change first.
- **Always confirm** before writing outcome notes (bullet summary).
- **Respect "no"** — dismissed forever; "not now" snoozed.
- **Be brief** — check-in prompts ≤ 2 sentences. Agenda = starting point.
- **Surface, don't overwhelm** — multiple actionable items → highest-scored first.
- **Timezone-aware** — always display in user's `timezone` config, never UTC.
- **Privacy first** — team calendar features are opt-in, never auto-enroll anyone.
- The OpenClaw calendar is internal — never tell users to look at it directly.
