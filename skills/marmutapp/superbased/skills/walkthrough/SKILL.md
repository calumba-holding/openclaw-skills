---
name: walkthrough
description: Walk through a scrollable section (settings panel, long list, long page) and report what's there. Use when the user asks "what's in Settings", "show me the whole page", "walk me through X", "capture the whole sidebar", or any task that requires reading content that extends below the viewport.
---

When the user wants you to READ a scrollable section end-to-end — settings panels, long forms, long lists, long scrollable content — use the `superbased_scroll_capture` MCP tool. **Do NOT chain `superbased_scroll` + screenshot calls in a loop** — each step in that chain costs its own user approval, so a 6-page section = 6 approval prompts. `superbased_scroll_capture` is ONE approval that returns all N frames back to you inline.

**When to use this skill:**
- "What are all the settings in the GUI Automation page?"
- "Walk me through the Dictation settings"
- "Show me the whole Settings page"
- "What options are in the sidebar / menu / panel?"
- Any task where the answer requires scrolling through a section you can't see all of at once

**The one-call invocation:**

```
superbased_scroll_capture
  anchorX=<x inside the scroll container>
  anchorY=<y inside the scroll container>
  processName="<target app>"   # or hwnd=..., or window="<title>"
  maxPages=8                    # default 8; bump to 12-16 for very long sections
  confirm=true
```

**Getting the anchor coords:**
1. First: `superbased_ui_dump processName="<target>"` — returns `textElements` with screen-space `center.{x,y}`.
2. Pick a `textElement` whose `center.{x,y}` sits INSIDE the scrollable container (NOT in a sidebar / header / toolbar — those scroll separately). An element in the middle-right of the content panel is usually safe.
3. Pass those coords as `anchorX` / `anchorY`.

**What you get back:**
- N image content blocks, one per captured viewport (typically 3–6 for a typical settings page).
- Text metadata: `framesCaptured`, `pagesScrolled`, `atEnd`, `atEndReason` (`'no_movement'` / `'max_pages'` / `'error'`), `calibration` (pixels-per-tick, score, cache hit), per-frame `scrolledPx`.

**Behavior characteristics:**
- **Inline calibration** — the first scroll IS the measurement. No visible "scroll down then scroll back up" rewind. User sees natural forward scrolling only.
- **Heuristic fallback** — if measurement is noisy (solid-background anchor, sparse content), the tool falls back to 40 px/tick with `calibration.lowConfidence: true` and keeps returning frames. Never hard-fails on calibration alone.
- **atEnd detection** — stops when consecutive frames differ by < 3 px (viewport didn't move = end of content). Pixel-offset measurement, not byte similarity.
- **Windows only** — uses Win32 `mouse_event` + PrintWindow. Cross-platform coming later.

**When NOT to use:**
- Page fits in the viewport — `superbased_ui_dump` is cheaper (no scrolling needed).
- You know a specific label to find — `superbased_scroll_to` stops at the match.
- The content isn't scrollable (modal dialogs, single-page forms).

**Anti-pattern — the loop this skill replaces:**

Do NOT do this:
```
superbased_click ...                   # navigate to settings
superbased_scroll amount=1 unit=page   # approval #1
superbased_screenshot ...              # approval #2
superbased_scroll amount=1 unit=page   # approval #3
superbased_screenshot ...              # approval #4
... (etc, 5-10+ approvals)
```

Instead:
```
superbased_click ...                   # navigate to settings (1 approval)
superbased_ui_dump ...                 # get anchor coords (1 approval)
superbased_scroll_capture anchor=...   # the whole walkthrough (1 approval, N frames back)
```
