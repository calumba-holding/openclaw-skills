---
name: codecast
description: Stream coding agent sessions (Claude Code, Codex, Gemini CLI, etc.) to a Discord channel in real-time via webhook. Use when invoking coding agents and wanting transparent, observable dev sessions — no black box. Parses Claude Code's stream-json output into clean formatted Discord messages showing tool calls, file writes, bash commands, and results with zero AI token burn. Use when asked to "stream to Discord", "relay agent output", or "make dev sessions visible".
metadata: {"openclaw":{"emoji":"🎬","requires":{"anyBins":["unbuffer","python3"]}}}
---

# Codecast

Live-stream coding agent sessions to Discord. No black box — see every tool call, file write, and bash command as it happens. Zero AI tokens burned.

## How It Works

```
┌──────────┐  stream-json  ┌──────────────┐  platform  ┌──────────┐
│ Claude   │ ────────────→ │ parse-stream │ ────────→ │ Discord  │
│ Code -p  │               │ .py          │           │ #channel │
└──────────┘               └──────────────┘           └──────────┘
┌──────────┐    --json     │              │           │          │
│ Codex    │ ────────────→ │  (auto-      │ ────────→ │          │
│ exec     │               │   detected)  │           │          │
└──────────┘               └──────────────┘           └──────────┘
```

- Claude Code runs in `-p` (print) mode with `--output-format stream-json --verbose`
- Codex runs with `--json` flag for structured JSONL event output (auto-detected)
- `parse-stream.py` reads JSON lines, auto-detects agent format, posts formatted messages via a platform adapter
- Platform adapters (currently Discord) handle message delivery and threading
- `unbuffer` (from `expect`) provides PTY to prevent stdout buffering (Claude Code only)
- Non-Claude/non-Codex agents fall back to ANSI-stripped raw output relay
- Rate limiting (default 25 posts/60s, configurable via `-r`) with automatic batching prevents webhook throttling
- Stale relay dirs older than 7 days are cleaned up on startup

## First-Time Setup

Run these steps once after installing the skill:

### 1. Make scripts executable

```bash
chmod +x {baseDir}/scripts/dev-relay.sh {baseDir}/scripts/parse-stream.py
```

### 2. Create a Discord webhook

Create a webhook in the target Discord channel via the Discord API or Server Settings → Integrations → Webhooks.

To create via API (if the bot has MANAGE_WEBHOOKS):
```bash
curl -s -X POST "https://discord.com/api/v10/channels/<CHANNEL_ID>/webhooks" \
  -H "Authorization: Bot <BOT_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Codecast"}'
```

Store the webhook URL:
```bash
echo "https://discord.com/api/webhooks/<ID>/<TOKEN>" > {baseDir}/scripts/.webhook-url
chmod 600 {baseDir}/scripts/.webhook-url
```

### 3. Skip the permissions prompt (Claude Code only)

Create `~/.claude/settings.json` if it doesn't exist:
```json
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": ["*"]
  }
}
```

### 4. Install unbuffer (required)

```bash
brew install expect    # macOS
apt install expect     # Linux
```

### 5. Bot token (optional, for --thread mode)

**Recommended: macOS Keychain (no plaintext on disk)**
```bash
security add-generic-password -s discord-bot-token -a codecast -w YOUR_BOT_TOKEN
```

Then export before running codecast:
```bash
export CODECAST_BOT_TOKEN=$(security find-generic-password -s discord-bot-token -a codecast -w)
```

**Fallback: file-based storage**
```bash
echo "YOUR_BOT_TOKEN" > {baseDir}/scripts/.bot-token
chmod 600 {baseDir}/scripts/.bot-token
```

### 6. Validate setup

```bash
bash {baseDir}/scripts/test-smoke.sh
```

Checks webhook reachability, required binaries, script permissions, and platform adapter loading.

## Invocation

After installing, run `chmod +x` on the scripts once:
```bash
chmod +x {baseDir}/scripts/dev-relay.sh {baseDir}/scripts/parse-stream.py
```

### From OpenClaw (recommended)

**⚠️ Always use `nohup` — see [Agent Integration](#agent-integration) for why `exec background:true` kills long sessions.**

```bash
exec command:"nohup {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Build a REST API for todos. When finished, run: openclaw system event --text \"Done: built REST API\" --mode now' > /tmp/codecast.log 2>&1 & echo PID:\$!"
```

### Direct

```bash
bash {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Build auth module. When finished, run: openclaw system event --text "Done: auth module built" --mode now'
```

### Options

| Flag | Description | Default |
|------|------------|---------|
| `-w <dir>` | Working directory | Current dir |
| `-t <sec>` | Timeout | 1800 (30min) |
| `-h <sec>` | Hang threshold | 120 |
| `-i <sec>` | Post interval | 10 |
| `-n <name>` | Agent display name | Auto-detected |
| `-r <n>` | Rate limit (posts per 60s) | 25 |
| `-P <platform>` | Chat platform | discord |
| `--thread` | Post into a Discord thread | Off |
| `--skip-reads` | Hide Read tool events | Off |
| `--resume <dir>` | Replay session from relay dir | — |
| `--review <url>` | PR review mode (see below) | — |
| `--parallel <file>` | Parallel tasks mode (see below) | — |

### Thread Mode

Post all messages into a single Discord thread for cleaner channel history:
```bash
bash {baseDir}/scripts/dev-relay.sh --thread -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Refactor auth'
```

### Session Resume

Replay a previous session's events (e.g., to a different channel or after a webhook change):
```bash
bash {baseDir}/scripts/dev-relay.sh --resume /tmp/dev-relay.XXXXXX
```

The relay dir path is printed at session start (`📂 Relay: /tmp/dev-relay.XXXXXX`).

### Codex with Structured Output

Codex CLI supports structured JSONL output via `--json`. When detected, `parse-stream.py` auto-parses Codex events (commands, file changes, messages, reasoning) into the same formatted Discord output as Claude Code:

```bash
bash {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- codex exec --json --full-auto 'Fix all test failures. When finished, run: openclaw system event --text "Done: tests fixed" --mode now'
```

The parser auto-detects the stream format from the first JSON event — no extra flags needed.

### PR Review Mode

Review a pull request with a coding agent and stream the review to Discord:

```bash
bash {baseDir}/scripts/dev-relay.sh --review https://github.com/owner/repo/pull/123
```

This will:
1. Clone the repo to a temp directory
2. Checkout the PR branch
3. Run a coding agent with a review prompt
4. Stream the review to Discord as usual
5. Optionally post the review as a `gh pr comment`

**Options for review mode** (pass before the PR URL):

| Flag | Description | Default |
|------|------------|---------|
| `-a <agent>` | Agent to use (claude, codex) | claude |
| `-p <prompt>` | Custom review prompt | Standard code review |
| `-c` | Post review as `gh pr comment` | Off |

**Examples:**
```bash
# Review with default Claude Code agent
bash {baseDir}/scripts/dev-relay.sh --review https://github.com/owner/repo/pull/123

# Review with Codex, post comment, in a thread
bash {baseDir}/scripts/dev-relay.sh --thread --review https://github.com/owner/repo/pull/123 -- -a codex -c

# Custom review prompt
bash {baseDir}/scripts/dev-relay.sh --review https://github.com/owner/repo/pull/123 -- -p "Focus on security vulnerabilities and SQL injection"
```

The agent writes its review to `/tmp/pr-review-<NUM>.md`. With `-c`, it's posted as a PR comment.

### Parallel Tasks Mode

Run multiple codecast sessions concurrently across git worktrees:

```bash
bash {baseDir}/scripts/dev-relay.sh --parallel tasks.txt
```

**Tasks file format** (one task per line: `directory | prompt`):
```
~/projects/api | Build user authentication endpoint
~/projects/web | Add dark mode toggle to settings page
~/projects/docs | Update API documentation for v3
```

Each task gets its own Discord thread, relay directory, and session. A summary message is posted when all tasks complete.

**Options for parallel mode:**

| Flag | Description | Default |
|------|------------|---------|
| `-a <agent>` | Agent (claude, codex) | claude |
| `--worktree` | Use git worktrees from each dir | Off |
| `--skip-reads` | Hide Read events | Off |
| `-r <n>` | Rate limit per task | 25 |
| `-t <sec>` | Timeout per task | 1800 |

**Example:**
```bash
bash {baseDir}/scripts/dev-relay.sh --parallel tasks.txt -- -a codex --worktree
```

Lines starting with `#` are ignored. Each task automatically gets `--thread` for separation.

### Discord Bridge (Interactive)

Run a companion process that forwards Discord messages to active codecast agent sessions:

```bash
python3 {baseDir}/scripts/discord-bridge.py --channel CHANNEL_ID --users USER_ID1,USER_ID2
```

**Commands from Discord:**

| Command | Description |
|---------|------------|
| `!status` | Show active codecast sessions |
| `!kill <PID>` | Kill a session |
| `!log [PID]` | Show recent output (PID optional if one session) |
| `!send [PID] <msg>` | Forward message to agent stdin |
| *(plain text)* | Auto-forwarded if only one session active |

**Environment variables:**

| Variable | Description |
|----------|------------|
| `BRIDGE_CHANNEL_ID` | Discord channel to watch |
| `BRIDGE_ALLOWED_USERS` | Comma-separated user IDs (empty = all) |

**Requires:** `websocket-client` Python package (`pip install websocket-client`) and a Discord bot token with MESSAGE_CONTENT intent.

## What Discord Sees

For Claude Code (stream-json mode):
- ⚙️ Model info and permission mode
- 📝 File writes with line count and smart content preview
- ✏️ File edits
- 🖥️ Bash commands
- 📤 Bash command output (truncated to 800 chars)
- 👁️ File reads (hide with `--skip-reads`)
- 🔍 Web searches
- 💬 Assistant messages
- ✅/❌ Completion summary with turns, duration, cost, and session stats

For Codex (--json mode):
- ⚙️ Session thread ID
- 🖥️ Command executions
- 📤 Command output (truncated to 800 chars)
- 📝 File creates / ✏️ File modifications
- 🧠 Reasoning traces
- 🔍 Web searches / 🔧 MCP tool calls / 📋 Plan updates
- 💬 Agent messages
- 📊 Token usage per turn
- ✅ Session summary with cost and stats

For other agents (raw mode):
- Output in code blocks with ANSI stripping
- Hang detection warnings
- Completion/error status

### End Summary

Every session ends with a summary block showing:
- Files created and edited (with counts)
- Bash commands run
- Tool usage breakdown
- Total cost

## Architecture

```
scripts/
├── dev-relay.sh          # Shell entry point, flag parsing, process management
├── parse-stream.py       # Multi-agent JSON stream parser (Claude + Codex)
├── review-pr.sh          # PR review mode (--review)
├── parallel-tasks.sh     # Parallel worktree tasks (--parallel)
├── discord-bridge.py     # Discord → stdin bridge (companion process)
├── test-smoke.sh         # Pre-flight validation (webhook, deps, permissions)
├── strip-ansi.sh         # ANSI escape code stripper
├── .webhook-url          # Discord webhook URL (gitignored)
└── platforms/
    ├── __init__.py       # Platform adapter loader
    └── discord.py        # Discord webhook + thread support
```

## Prompt Template

Always append the completion notification to your inner agent's prompt. This ensures OpenClaw wakes immediately when the agent finishes instead of waiting for the next heartbeat.

```
<your task description here>

When completely finished, run: openclaw system event --text "Done: <brief summary>" --mode now
```

**Full example:**
```bash
exec command:"nohup {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Refactor the auth module to use JWT tokens. Add tests. When completely finished, run: openclaw system event --text \"Done: refactored auth to JWT with tests\" --mode now' > /tmp/codecast.log 2>&1 & echo PID:\$!"
```

## Agent Support

| Agent | Output Mode | Status |
|-------|------------|--------|
| Claude Code | stream-json (parsed) | Full support |
| Codex | --json JSONL (parsed) | Full support |
| Codex (no --json) | Raw ANSI | Basic support |
| Gemini CLI | Raw ANSI | Basic support |
| Any CLI | Raw ANSI | Basic support |

## Interactive Input

During an active session, forward input to the agent:
- From OpenClaw: `process:submit sessionId:<id> data:"your message"`
- Session info stored at `/tmp/dev-relay-sessions/<PID>.json` (one file per concurrent session)

## Agent Integration

When an AI agent (e.g., OpenClaw) invokes codecast programmatically:

**⚠️ Do NOT use `exec background:true` for codecast sessions.** OpenClaw's background exec is designed for short tasks (builds, tests). Long-running processes like Claude Code sessions get SIGKILL'd ~15-20 seconds after the agent turn ends. This is by design — OpenClaw works in turns, not continuous runs. See: [Community discussion](https://www.answeroverflow.com/m/1469280591886286899)

**Use `nohup` instead:**
```bash
nohup {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Your task here' > /tmp/codecast.log 2>&1 &
```

**Completion detection:**
- `dev-relay.sh` calls `openclaw gateway wake` on exit (triggers a heartbeat)
- Include in your prompt: `When finished, run: openclaw system event --text 'Done: [summary]' --mode now`
- Monitor `/tmp/dev-relay-sessions/<PID>.json` — file is removed when session ends
- Check `ps -p <PID>` to poll process status

> **WARNING:** `exec background:true` sessions die on OpenClaw gateway restart.
> *'Sessions are lost on process restart.'* — Agents must not run `config.patch`
> while a codecast session is active, as this triggers a gateway restart and kills
> the background process.

**Post-session workflow:**
After the session completes (wake event received), the invoking agent should:
1. Read `#dev-session` or `process:log` to check what was built
2. Verify the deliverable works (run the tool, check output)
3. Report results to the user

**Wake notification:** Include this in the inner agent's prompt for immediate completion notification:
```
When completely finished, run: openclaw system event --text 'Done: [summary]' --mode now
```

**Example (OpenClaw agent invoking codecast):**
```bash
# Step 1: Launch via nohup (decoupled from agent turn lifecycle)
exec command:"nohup {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Build auth module. When finished, run: openclaw system event --text \"Done: auth module built\" --mode now' > /tmp/codecast.log 2>&1 & echo PID:$!"
# Step 2: Note the PID from output, monitor via ps or wait for wake event
```

### Agent Launch Checklist (MANDATORY for OpenClaw agents)

Every time you launch a codecast session, do ALL of these:

1. **Start the nohup session** → note the PID from output
2. **Post to the dev channel** → announce agent name, workdir, task
3. **Create a watcher cron job** to detect completion and report back:
   ```
   cron add → every 120000ms → isolated agentTurn →
   "Run: bash {baseDir}/scripts/codecast-watch.sh <PID> <relay-dir>
   If output is STILL_RUNNING → reply HEARTBEAT_OK
   If output starts with ✅ or ❌ or ⚠️ → post the output to <invoking-channel-id>, then delete this cron job (cron remove <this-job-id>)"
   ```
4. **Log to daily memory** → PID, relay dir, invoking channel, cron job ID

The relay dir is printed at launch: `📂 Relay: /tmp/dev-relay.XXXXXX`.

**Why the cron job is mandatory:** `openclaw system event` only queues for the main session heartbeat — it does NOT wake the active chat session. The cron job is the only reliable way to get notified in the channel that launched the codecast.

## Session Tracking

- **Active session info:** `/tmp/dev-relay-sessions/<PID>.json` — one file per concurrent session, contains PID, agent name, start time, and relay dir for `process:submit` input forwarding. Automatically removed on session end.
- **Raw event log:** Relay dir at `/tmp/dev-relay.XXXXXX` (path printed at session start) — contains all raw events for replay via `--resume`. Dirs older than 7 days are auto-cleaned on startup.

## Environment Variables

| Variable | Description | Default |
|----------|------------|---------|
| `CODECAST_BOT_TOKEN` | Discord bot token for `--thread` mode and bridge | Falls back to `.bot-token` file |
| `CODECAST_RATE_LIMIT` | Max posts per 60s window | `25` |
| `BRIDGE_CHANNEL_ID` | Discord channel for bridge to watch | All channels |
| `BRIDGE_ALLOWED_USERS` | Comma-separated Discord user IDs for bridge | All users |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Output is garbled or empty | Missing PTY allocation | Set `pty:true` in exec call. For direct use, ensure `unbuffer` is installed. |
| Agent seems to hang | Agent idle beyond threshold | Check `process:log` for status. Increase hang threshold with `-h <seconds>`. |
| Webhook rate limited | Too many posts in window | No action needed — auto-batched. Lower rate with `-r 15` if persistent. |
| No Discord messages | Bad or missing webhook URL | Run `{baseDir}/scripts/test-smoke.sh` to validate setup. |

## Completion Notification

On finish, the relay calls `openclaw gateway wake` to notify OpenClaw immediately.
