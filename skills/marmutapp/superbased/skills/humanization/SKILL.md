---
name: humanization
description: Pick the right humanize profile for GUI automation on sites with bot detection. Use when actions on a real webapp need to evade automation fingerprinting (Cloudflare-fronted sites, social media, banking, ticketing).
---

GUI automation tools (`click`, `type`, `drag`, `hover`, `sequence`) accept a `humanize` parameter with four profiles. Pick the right one for the target — over-humanizing is slow, under-humanizing gets you flagged.

## The 4 profiles

| Profile | When to use |
|---|---|
| `'off'` | **Internal tools, dev environments, your own app under test.** No humanization — fastest, deterministic. Will fail any consumer site with bot detection. |
| `'light'` | **Default.** Most consumer sites without aggressive detection. Sin-shaped velocity envelope, basic Gaussian click jitter, gamma-distributed pre-click dwell, 50–110 ms click hold variation. Adds ~50–200 ms per action. |
| `'human'` | **Sites with active bot detection** — anything Cloudflare-fronted, reCAPTCHA-gated, or hCaptcha-protected. Adds pre-click tremor on the target element + occasional 2–4× micro-pauses + per-process cross-session salt mixed into seeds (so two runs don't have identical inter-arrival times). Adds ~200–500 ms per action. |
| `'paranoid'` | **Hardened targets** — banking, ticketing (Ticketmaster), social media bot crackdowns. Everything in `human` plus rare "distraction" pauses (1–3 s gaps that look like the user got distracted), wider Gaussian jitter, slower velocity envelope. Adds ~500ms–2s per action. |

## How to choose

```
Internal/dev tool → 'off'
Consumer webapp without obvious bot detection → 'light' (default — don't override)
Site behind Cloudflare / has CAPTCHA gates / is in the "obviously cares about bots" category → 'human'
Banking / ticketing / known-hardened anti-bot target → 'paranoid'
```

When in doubt, start at the default `'light'` and bump up only if you get blocked. Going straight to `'paranoid'` when `'light'` would have worked just makes the automation slow.

## Per-call override

You don't pick one profile for the whole session. Set it per call:

```json
{ "tool": "superbased_click", "name": "Submit", "confirm": true, "humanize": "human" }
```

For `superbased_sequence`, set it on each step that needs it (or set on the sequence root and override per-step).

## Other humanization knobs (for advanced cases)

- **`typoProb`** on `superbased_type` — probability of a typo per character (then immediately corrects with backspace + correct char). QWERTY same-row neighbors. Default 0; bump to 0.01–0.03 for sites that score typing perfection as bot-like.
- **`humanInputIdleDrift`** in app settings — opt-in cursor drift while the agent is idle (between sequence steps the agent isn't actively moving). Off by default; enable for long-running sessions on hardened targets.
- **`humanize: 'light'` is required for CAPTCHA drops** — see the **captcha-solving** skill. Drag puzzles fail with `'off'` because drop velocity is the main signal.

## What humanization is for (and what it's not)

**Is for:** lowering the input-side bot signal — cursor trajectories, click timing, keystroke cadence, drag drop velocity. These are the things behavioral fingerprinting watches.

**Is NOT for:** server-side fingerprinting (TLS, cookies, IP reputation, browser fingerprint). SuperBased drives the user's real browser, so the network-side reputation is the user's reputation. If their IP is on a flagged subnet, no humanization profile will help.

If the user complains "still getting flagged with `paranoid`", the next step is investigating their IP / browser fingerprint / account history, not bumping the profile higher (there is no higher).
