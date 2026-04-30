# SuperBased — Eyes AND Hands for OpenClaw

Screenshot capture, AI vision, OCR, screen recording, voice dictation, **and full GUI automation with humanization v2** — all via 72 MCP tools, directly inside [OpenClaw](https://openclaw.ai).

This is a [ClawHub](https://clawhub.ai) skill bundle that ships proactive guidance for SuperBased's MCP toolkit. The actual 72 tools come from the SuperBased MCP server — the skill bundle tells the OpenClaw agent **when** to use them and **how**.

## Install (two steps)

### 1. Install the skill bundle from ClawHub

```bash
openclaw skills install superbased
```

This downloads the 11 SKILL.md files into your OpenClaw workspace's `skills/` directory.

### 2. Register the SuperBased MCP server

```bash
openclaw mcp set superbased '{"command":"superbased","args":["mcp"]}'
```

This points OpenClaw at the SuperBased CLI for the actual tool calls.

### 3. (One-time) install the SuperBased CLI

```bash
npm install -g superbased
```

This is the binary that the MCP server invocation runs.

### 4. (Optional) install the SuperBased desktop app

The desktop app for Windows/macOS gives you a GUI for browsing captures, configuring providers, and managing the gallery. When the desktop app is running, `superbased mcp` auto-detects it via the PID file at `~/.superbased/` and acts as a stdio↔HTTP bridge — so OpenClaw and the desktop share the same gallery / sessions / settings.

Download from [superbased.app](https://superbased.app).

## Skills (11)

| Skill | When OpenClaw Uses It |
|-------|-----------------------|
| **screenshot** | OpenClaw needs to see what's on the user's screen |
| **visual-qa** | Visual regression testing: record baseline → make changes → record again → diff |
| **monitor** | Proactive screen watching during deploys, tests, builds |
| **compress** | Large text content (>500 tokens) that would be cheaper as an image |
| **redact** | Screenshots that may contain API keys, tokens, or PII before sharing |
| **dictation** | Voice input, audio transcription, or speech-to-text |
| **annotate** | Highlighting areas, marking regressions, creating annotated screenshots |
| **walkthrough** | Multi-frame product walkthrough: capture, narrate, export |
| **gui-automation** | "Click that", "type into this", "fill the form" — drives the desktop with click/type/hotkey/scroll/drag/form-fill/sequence |
| **captcha-solving** | reCAPTCHA / Cloudflare Turnstile / drag puzzles / rotation puzzles / image grids |
| **humanization** | Sites with bot detection — picks the right humanization profile (off/light/human/paranoid) |

## Humanization v2

GUI automation actions (`click`, `type`, `drag`, `hover`) ship with a humanization layer to reduce the bot-detection signal: sin-shaped velocity envelope on cursor walks, gaussian click-target jitter, gamma-distributed pre-click settle dwell, 50–110 ms click hold variation, 45–95 ms key hold, wired typo simulation with QWERTY same-row neighbors, pre-click tremor on the target element, occasional 2–4× micro-pauses, per-process cross-session salt mixed into seeds, inter-action catch-up pause, and opt-in idle cursor drift.

Four profiles selectable per call: `humanize: 'off' | 'light' | 'human' | 'paranoid'`. Default `light`. Bump to `human` or `paranoid` for sites with active bot detection — see the **humanization** skill.

## CAPTCHA solving

Plugin ships proactive guidance for the four CAPTCHA classes: image grids (vision identifies, batched click sequence), drag puzzles (one-motion drag with `humanize: 'light'`), rotation puzzles (calibrate-then-execute), and checkbox-only Turnstile. Plus the honest "what humanization can't defeat" list (server-side fingerprinting, audio CAPTCHAs, hCaptcha enterprise mode). See the **captcha-solving** skill.

## MCP Tools (72)

The 72 tools come from the SuperBased MCP server. Categories: Capture & View (5), AI & OCR (8), Gallery (2), Privacy & Annotations (2), Dictation & Voice (2), Recording & Visual QA (7), Settings/Auth/System (6), and **GUI Automation (40)**.

See [the source-of-truth Claude Code plugin README](https://github.com/marmutapp/superbased-claude-code-plugin#mcp-tools-72) for the full categorized list with collapsibles.

## Why two install steps?

ClawHub registers **skills** (when/how to use a tool) and **plugins** (TypeScript code), but does NOT register MCP servers directly. The clean split:

- **Skills bundle (this package)** — published to ClawHub, installable via `openclaw skills install superbased`. Tells the agent when to reach for SuperBased and what's possible.
- **MCP server (`superbased mcp`)** — registered separately via `openclaw mcp set superbased '...'`. Provides the actual 72 tools.

There is no built-in OpenClaw plugin from us. ClawHub doesn't list MCP servers via the plugin wrapper, so a wrapper plugin would just add ceremony without unlocking discoverability. If we ship one later, it'll be for OpenClaw-specific lifecycle hooks (e.g. auto-capture on chat-app message events).

## Verifying the install

```bash
openclaw mcp list                         # superbased should be listed
openclaw mcp show superbased              # see the registered config
openclaw skills list                      # superbased skills should appear
openclaw skills check                     # validates the local skill environment
superbased --version                      # confirms CLI is on PATH
```

## Links

- [SuperBased](https://superbased.app) — Desktop app + npm CLI
- [npm: superbased](https://www.npmjs.com/package/superbased) — The CLI providing the MCP server
- [Source-of-truth Claude Code plugin](https://github.com/marmutapp/superbased-claude-code-plugin) — Where shared content (skills) is mastered
- [OpenClaw](https://openclaw.ai) + [ClawHub](https://clawhub.ai) — The runtime + registry
