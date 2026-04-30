---
name: superbased
description: Eyes AND hands for OpenClaw — capture, AI vision, OCR, recording, voice dictation, and full GUI automation via 72 MCP tools. Use when the agent needs to see the user's screen OR drive their desktop (click / type / scroll / drag / form-fill / sequence) AND when the user mentions screenshots, screen recording, visual regression, OCR, voice transcription, or asks to automate a UI workflow.
---

SuperBased gives OpenClaw agents both eyes (screen capture, AI vision, OCR) and hands (full GUI automation with humanization v2 + CAPTCHA-solving guidance) on the user's desktop. The actual capabilities are exposed through 72 MCP tools served by the SuperBased MCP server (`superbased mcp`); this skill bundle teaches the agent **when** to reach for which tool.

## Two-step install (run once)

```bash
# 1. Install this skills bundle from ClawHub
openclaw skills install superbased

# 2. Register the SuperBased MCP server
openclaw mcp set superbased '{"command":"superbased","args":["mcp"]}'

# 3. (Pre-req) the SuperBased CLI on PATH
npm install -g superbased
```

Optional: install the SuperBased desktop app from [superbased.app](https://superbased.app) for a GUI to browse captures, configure providers, and manage the gallery. When the desktop app is running, `superbased mcp` auto-bridges to it via a PID file at `~/.superbased/`, so OpenClaw and the desktop share state.

## When to use SuperBased

Trigger SuperBased when the user's request involves any of:

- **Seeing what's on screen** — "look at this", "what's on my screen", "describe what I'm seeing", "read this dialog"
- **Verifying a UI change** — "did the button update?", "is the error gone?"
- **Reading content that's hidden behind scroll** — "what are all the settings?", "walk me through the sidebar"
- **Visual regression testing** — "record a baseline of the login flow", "did anything change visually?"
- **Watching for issues during long-running processes** — "monitor my deploy for errors", "let me know if anything fails"
- **Extracting text from images / screen** — "OCR this", "extract the text from this region"
- **Voice input** — "transcribe what I'm about to say", "type via dictation"
- **Compressing large text into images** — "send this 5K-token block as one image"
- **Annotating / redacting screenshots** — "highlight the broken thing", "redact the API key before sharing"
- **Driving the desktop UI** — "click that button", "type into the email field", "fill out this form", "press Cmd+S"
- **Multi-step workflow automation** — "open File menu, pick Open, type the path, press Enter, screenshot the result"
- **Solving in-flow CAPTCHA challenges** — "this drag puzzle is blocking me", "select all squares with traffic lights"
- **Fighting bot detection** — when an automation flow on a hardened site needs cursor-trajectory humanization

## Sub-skills (use these as the agent's working knowledge)

The 11 SKILL.md files in this bundle each cover one trigger category. Read the relevant one first when the user request matches its description:

| File | Use when |
|---|---|
| [skills/screenshot/SKILL.md](./skills/screenshot/SKILL.md) | Capturing the screen at the right resolution / window / region |
| [skills/visual-qa/SKILL.md](./skills/visual-qa/SKILL.md) | Record-baseline → make-changes → record-again → diff workflow |
| [skills/monitor/SKILL.md](./skills/monitor/SKILL.md) | Proactive screen watching during deploys, tests, builds |
| [skills/walkthrough/SKILL.md](./skills/walkthrough/SKILL.md) | Reading a scrollable section end-to-end via `superbased_scroll_capture` |
| [skills/compress/SKILL.md](./skills/compress/SKILL.md) | Converting large text to token-efficient images |
| [skills/redact/SKILL.md](./skills/redact/SKILL.md) | Auto-redacting secrets / PII before sharing |
| [skills/dictation/SKILL.md](./skills/dictation/SKILL.md) | Voice input, audio transcription, speech-to-text |
| [skills/annotate/SKILL.md](./skills/annotate/SKILL.md) | Highlighting areas, marking regressions, drawing on captures |
| [skills/gui-automation/SKILL.md](./skills/gui-automation/SKILL.md) | Click / type / scroll / drag / form-fill / sequence — driving the desktop |
| [skills/captcha-solving/SKILL.md](./skills/captcha-solving/SKILL.md) | reCAPTCHA / Cloudflare Turnstile / drag puzzles / rotation puzzles / image grids |
| [skills/humanization/SKILL.md](./skills/humanization/SKILL.md) | Picking the right `humanize` profile (off / light / human / paranoid) per call |

## The 72 MCP tools at a glance

Capture & View (5): `superbased_screenshot`, `_capture_image`, `_capture`, `_gallery_image`, `_window_list`

AI & OCR (8): `superbased_ai`, `_ai_usage`, `_ocr`, `_transcribe`, `_compress_text`, `_project`, `_workspace_sync`, `_stt_status`

Gallery (2): `superbased_gallery`, `_gallery_update`

Privacy & Annotations (2): `superbased_redact`, `_annotate`

Dictation & Voice (2): `superbased_dictate`, `_dictation_history`

Recording & Visual QA (7): `superbased_recording`, `_sessions`, `_describe_frames`, `_narrate`, `_diff`, `_baseline`, `_export`

Settings, Auth & System (6): `superbased_settings`, `_presets`, `_auth`, `_license`, `_health`, `_clipboard`

GUI Automation (40): `superbased_ui_dump`, `_scroll_capture`, `_scroll_to`, `_sequence`, `_click`, `_type`, `_hotkey`, `_scroll`, `_drag`, `_drag_file`, `_hover`, `_context_menu_select`, `_form_fill`, `_dialog_handle`, `_open_url`, `_find_in_page`, `_tab_management`, `_tray_click`, `_virtual_desktop`, `_window_state`, `_resize_window`, `_focus_window`, `_window_bounds`, `_find_title_bar_drag_region`, `_display_list`, `_launch_app`, `_find_image`, `_capture_template`, `_pixel_color`, `_ax_invoke`, `_accessibility_tree`, `_locate`, `_wait`, `_wait_for`, `_mouse_position`, `_dry_run`, `_replay`, `_doctor_gui_automation`, `_undo_last`, `_tools`

## Safety rails (for the GUI automation surface)

Before any state-modifying GUI action (click, type, drag, sequence, form_fill, etc.):

1. The master toggle (Settings > GUI Automation > Enabled) must be on. Run `superbased_doctor_gui_automation` to verify.
2. Per-action toggles (click, type, hotkey, scroll, drag, hover) must each be enabled.
3. Every state-modifying call must pass `confirm: true` — the server refuses without it.
4. Protected-apps blocklist + NDJSON audit log are server-side; users can audit every action you took.

## When to bump humanization

Default `humanize: 'light'` is enough for most consumer sites. Bump to `'human'` for sites with active bot detection (Cloudflare-fronted, reCAPTCHA-gated). Bump to `'paranoid'` for hardened targets (banking, ticketing, social media bot crackdowns). See `skills/humanization/SKILL.md` for the full picker.

## Links

- [SuperBased](https://superbased.app) — Desktop app + npm CLI
- [npm: superbased](https://www.npmjs.com/package/superbased) — The CLI providing the MCP server
- [Source-of-truth Claude Code plugin](https://github.com/marmutapp/superbased-claude-code-plugin) — Where shared content (skills) is mastered
- [OpenClaw](https://openclaw.ai) + [ClawHub](https://clawhub.ai) — The runtime + registry
