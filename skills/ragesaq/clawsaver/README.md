# ClawSaver

> Stop paying for round-trips. Batch related asks, save real money.

ClawSaver is an OpenClaw skill that reduces AI API costs by teaching your assistant to recognize when multiple questions or tasks can be answered together — instead of paying for each one separately.

---

## Why ClawSaver?

Every message to an AI model costs money: API overhead, context re-sent, response tokens. When you're asking 3 related things in 3 separate turns, you're paying for that context 3 times.

ClawSaver fixes this by making the assistant proactively notice when tasks can be merged — and handle them in a single well-structured response.

**Typical results:**
- ~30–50% fewer API requests per session
- ~20–35% fewer tokens consumed
- No quality loss — batched responses are structured, not compressed

---

## What It Does

When ClawSaver is loaded, the assistant:

1. **Detects batchable asks** — multiple questions on the same topic, follow-ups within a few turns, redundant tool calls
2. **Groups them intelligently** — merges into one structured response with clear per-question sections
3. **Skips when it shouldn't** — sequential dependencies, unrelated domains, and explicit opt-outs are respected
4. **Shows the savings** (optional) — a one-liner like `💸 Batched 3 asks → 1 response`

---

## Batch vs. Don't Batch

| Scenario | ClawSaver Action |
|----------|-----------------|
| "Explain X, also check Y, and what about Z?" (same topic) | ✅ Batch → 1 response |
| Code review + next steps + test suggestions | ✅ Batch → 1 response |
| "What's the status?" then 2 turns later "What should I do next?" | ✅ Offer to consolidate |
| Task A whose output is required for Task B | ❌ Keep separate |
| Two completely unrelated topics | ❌ Keep separate |
| "Answer each one separately" | ❌ Defer to user |

---

## Response Format (Batched)

```
## Code Review

**Correctness**
No bugs found. The null check on line 14 is correct.

**Performance**
The nested loop on line 47 is O(n²) — consider a Map for O(n).

**Test Coverage**
Missing edge case: empty array input.

---
💸 Batched 3 asks → 1 response. Est. savings: ~2 API calls, ~600 tokens.
```

---

## Decision Rules

| Signal | Action |
|--------|--------|
| 2+ questions in one message, same topic | Always batch |
| Follow-up ≤3 turns on same subject | Offer to batch |
| Redundant data fetch (same file/URL twice) | Cache & reuse |
| Clarifying question preemptable from context | Anticipate & answer |
| Sequential dependency (A feeds B) | Keep separate |
| >3 unrelated domains | Keep separate |

---

## Savings Estimate Table

| Session Type | Requests Saved | Tokens Saved |
|-------------|---------------|-------------|
| 3-part code review | ~67% | ~30% |
| Research + summary + action | ~67% | ~25% |
| Config/setup questions (5) | ~60% | ~35% |
| Status check + next steps | ~50% | ~20% |
| Unrelated mixed tasks | 0% | 0% |

---

## Installation

```bash
clawhub install clawsaver
```

---

## Safety Model

ClawSaver never:
- Merges tasks with sequential dependencies
- Compresses responses in ways that lose meaning
- Assumes missing context to force a batch
- Overrides explicit user instructions to keep things separate

---

## About the Name

**ClawSaver** — because it saves your claws (and your cash) for what matters.

*CLAVSAVER: Combines Linked Asks into Well-structured Sets for Affordable, Verified, Efficient Responses*

---

## Version

**1.0.0** — Initial release

---

*Built for [OpenClaw](https://openclaw.ai) · Listed on [ClawHub](https://clawhub.ai)*
