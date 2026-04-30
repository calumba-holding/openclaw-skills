---
name: captcha-solving
description: Solve in-flow CAPTCHA challenges (reCAPTCHA, Cloudflare Turnstile, drag-puzzles, rotation puzzles, image grids) using vision + GUI automation. Use when an automation flow gets blocked by a verification challenge.
---

When a GUI automation flow hits a CAPTCHA, don't give up — most consumer-facing CAPTCHAs are solvable with the SuperBased vision + automation toolkit. Pick the pattern that matches the challenge type.

## Pattern 1: Image-grid challenges (reCAPTCHA, Cloudflare Turnstile)

"Select all squares with traffic lights / crosswalks / buses".

1. `superbased_screenshot` — capture the challenge.
2. `superbased_ai` — ask the model "Which of these 9 tiles contain a `<X>`? Return as a list of 1-indexed grid positions." (the underlying vision call returns coordinates reliably for typical 3×3 / 4×4 grids).
3. `superbased_ui_dump` on the challenge widget — get the per-tile `center.{x,y}`.
4. `superbased_sequence` — one batched click sequence selecting the matched tiles, ending with a click on Verify and a final `screenshot` step.

Critical: do NOT click tiles one-by-one with separate approvals; batch into a single sequence so the click cadence matches what a human does (reCAPTCHA scores cadence).

## Pattern 2: Drag puzzles (slider-to-fit, "drag piece to gap")

1. `superbased_screenshot` — capture the puzzle.
2. `superbased_ai` — "What is the horizontal pixel offset from the puzzle piece's current position to the gap?" Vision returns a delta.
3. `superbased_drag` with `humanize: 'light'` — drag the slider/piece by that delta in **one motion**. Never split into multiple sub-drags — drop velocity is the main bot signal here. The `light` profile gives a sin-shaped velocity envelope that reads as human; `'off'` will fail almost every time.
4. End with `superbased_screenshot` to confirm the puzzle accepted the drop.

## Pattern 3: Rotation puzzles ("rotate the image upright")

This is the **calibrate-then-execute** pattern:

1. `superbased_screenshot` — capture the puzzle.
2. `superbased_ai` — "What's the rotation angle in degrees needed to make this image upright?" Vision returns an angle.
3. Look up the puzzle widget's geometry via `superbased_ui_dump` — you need the rotation handle's start position and the rotation axis.
4. `superbased_drag` from the handle's start to the calibrated end position, **in one motion**, `humanize: 'light'`.
5. `superbased_screenshot` to verify acceptance.

The "calibrate first, then execute in one drag" pattern is what makes this work — re-calibrating mid-drag (multiple sub-drags) signals automation.

## Pattern 4: Checkbox-only Turnstile / "I'm not a robot"

Often passes on the first click if the cursor approach was sufficiently human:

1. `superbased_click` on the checkbox with `humanize: 'human'` (bump from default `light`).
2. `superbased_wait_for` with a predicate matching the success state (checkmark visible) or escalation (image grid appears — fall back to Pattern 1).

## What humanization CANNOT defeat (be honest with the user)

- **Server-side device fingerprinting** — cookies, IP reputation, TLS fingerprint, browser fingerprint. SuperBased operates the user's real browser, so it inherits the user's reputation. If the user's IP is on a residential proxy / VPN that's been flagged, no humanization will help.
- **Audio CAPTCHAs** — SuperBased can detect the audio button but the audio decoding pipeline is not built into the toolkit. The user has to solve those manually.
- **hCaptcha enterprise mode** — uses behavioral signals SuperBased can't fully mimic (mouse trajectory variance, typing rhythm, focus events). May work; may not. Try Pattern 1 with `humanize: 'paranoid'` once; if it loops, escalate to the user.
- **Phone / SMS / email verification** — not a CAPTCHA, but the same place users hit a wall. Surface to the user and ask them to complete the step.

## Important: don't loop blindly

If a CAPTCHA fails, capture, summarize what you tried (which pattern, which humanize profile, what the model said), and ask the user before retrying. A second-and-third automated CAPTCHA attempt looks more like a bot than a single failed attempt.
