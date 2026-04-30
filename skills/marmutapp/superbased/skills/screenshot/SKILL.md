---
name: screenshot
description: Auto-capture the screen when Claude needs to see what the user sees. Use when debugging visual issues, verifying UI changes, reading on-screen content, or answering questions about what's visible.
---

When you need to see the user's screen to answer a question, debug a visual issue, or verify a UI change, use the `superbased_capture_image` tool.

**Default parameters:**
- `mode: "fullscreen"`
- `resolution: "half"` (saves ~4x tokens vs full resolution)

**Resolution guide:**
- General overview, layout checks: `resolution: "half"` (~691 tokens for 1080p)
- Reading small text or fine details: `resolution: "high"`
- Pixel-perfect comparisons: `resolution: "full"` (~2,765 tokens for 1080p)
- Just checking presence/layout: `resolution: "quarter"` (~173 tokens)

**Targeting a specific window:**
1. Call `superbased_window_list` to see all open windows
2. Call `superbased_capture_image` with `window: "substring"` -- SuperBased activates the window (restores if minimized), captures, then restores focus

**Reading clipboard images:**
If the user says "look at what I copied", use `superbased_clipboard` with `action: "readImage"`.

After capturing, describe what you observe and relate it to the user's question.
