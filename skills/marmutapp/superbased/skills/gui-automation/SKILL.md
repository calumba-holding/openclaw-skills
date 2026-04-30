---
name: gui-automation
description: Drive the user's desktop with click / type / hotkey / scroll / drag / form-fill primitives. Use when the user asks you to "click X", "type into Y", "fill out this form", "automate this workflow", or any task that needs you to operate their actual UI rather than just describe it.
---

When the user wants you to ACT on their screen — click a button, type into a field, fill a form, drag a slider, send a hotkey — use the SuperBased GUI automation tools instead of just describing what they should do.

## Safety rails (verify before first action in a session)

1. **Master toggle**: Settings > GUI Automation > Enabled. If `superbased_doctor_gui_automation` reports `enabled: false`, surface that to the user and ask them to flip it on. Do not attempt to bypass.
2. **Always pass `confirm: true`** on any tool that modifies UI state (click / type / hotkey / scroll / drag / sequence / form_fill / dialog_handle / context_menu_select / ax_invoke / tab_management / virtual_desktop / tray_click). Tools refuse to fire without it.
3. **Per-action toggles**: each action class (click, type, hotkey, scroll, drag, hover) has its own enable/disable. The doctor tool reports which are off.
4. **Protected apps blocklist** + **NDJSON audit log** are server-side; you don't manage them, but they're why the user can audit what you did.

## The reliability pyramid (use the most reliable target you can find)

Order matters — always pick the first option that works for the target element:

1. **`automationId`** (Windows: AutomationId / macOS: AXIdentifier) — set by the app developer, never changes between layout shifts. Most reliable.
2. **`role` + `name`** — e.g. `role: "button", name: "Submit"`. Survives layout changes; can break if app re-labels.
3. **Visible label / OCR text** — what the user sees. Brittle on minor wording tweaks but works on apps with no AX surface.
4. **`coords: { x, y }`** — last resort. Survives nothing; only use when AX has no entry for the element (canvas widgets, custom-rendered controls, web-embedded iframes the AX layer skips).

Always call `superbased_ui_dump` first on a new app — it returns the AX tree with `automationId` / `role` / `name` / `center.{x,y}` so you can pick the right targeting strategy without guessing.

## The "always end with screenshot" rule for `superbased_sequence`

When you compose multiple steps via `superbased_sequence`, the last step **must** be a `screenshot` step. Why: without a final screenshot you have no proof the sequence reached the intended end-state, and the audit log shows N actions with no visible outcome. The screenshot step is cheap (one extra capture) and gives you/the user the verification frame.

```json
{
  "confirm": true,
  "steps": [
    { "type": "click", "name": "File", "role": "menuitem" },
    { "type": "click", "name": "Open...", "role": "menuitem" },
    { "type": "type", "text": "/path/to/file.txt" },
    { "type": "hotkey", "keys": "Enter" },
    { "type": "screenshot", "resolution": "half" }
  ]
}
```

## Decision guide (which tool for which task)

| User asks for... | Use |
|---|---|
| "Click that button" | `superbased_click` (look up via `_ui_dump` first) |
| "Type into that field" | `superbased_click` to focus, then `superbased_type` |
| "Fill out this form" | `superbased_form_fill` with `{label: value}` map |
| "Press Cmd+S / Ctrl+Tab" | `superbased_hotkey` |
| "Scroll down to the End User License" | `superbased_scroll_to` with the target text |
| "Walk me through the Settings page" | `superbased_scroll_capture` (one approval, all frames) |
| "Drag the slider to the gap" | `superbased_drag` (set `humanize: 'light'` for puzzles) |
| "Right-click and pick Inspect" | `superbased_context_menu_select` |
| "Confirm/dismiss this dialog" | `superbased_dialog_handle` |
| "Open https://..." | `superbased_open_url` |
| "Multi-step workflow" | `superbased_sequence` with screenshot last step |
| "Click that thing in the system tray" | `superbased_tray_click` |
| "Switch to virtual desktop 2" | `superbased_virtual_desktop` |
| Element has no AX entry, only a visible icon | `superbased_find_image` (template match) |

## When something fails

- If a click misses, run `superbased_ui_dump` again and inspect the actual `center.{x,y}` and `role` — the app may have re-rendered.
- If `superbased_doctor_gui_automation` reports a per-action toggle off, don't retry; tell the user to enable it.
- If the action needs a wait for UI to settle, use `superbased_wait_for` (waits for a predicate) over `superbased_wait` (blind sleep).
- For "I want to see what would happen but not actually do it", `superbased_dry_run` simulates without firing input events.

## Sites with bot detection

If the target is a webapp with active bot detection (e.g. Cloudflare-fronted, reCAPTCHA-gated), see the **humanization** skill for picking the right `humanize` profile. Default `light` is enough for most consumer sites; bump to `human` or `paranoid` for hardened targets.

For CAPTCHA challenges that block your flow, see the **captcha-solving** skill.
