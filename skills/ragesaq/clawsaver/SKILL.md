---
name: clawsaver
version: 1.0.0
description: "Reduce AI costs by batching related asks into fewer, smarter responses. ClawSaver identifies when multiple questions or tasks can be answered together — cutting API calls 30-50% and tokens 20-35% without losing quality."
metadata:
  {"openclaw":{"emoji":"💸","os":["darwin","linux","win32"]}}
---

# ClawSaver v1

> Stop paying for round-trips. When you have 3 related questions, one smart answer beats three dumb ones.

ClawSaver teaches the assistant to **recognize batchable tasks** and handle them in a single well-structured response — fewer requests, less token overhead, same quality.

## When to Use

Use this skill when:
- You're about to ask multiple related questions
- You've been going back and forth with the assistant on a single topic
- You want the assistant to proactively notice when tasks can be merged
- You're monitoring session cost and want to reduce round-trip overhead

Do **not** use when:
- Tasks are genuinely independent and time-sensitive
- You need incremental output (e.g. streaming code you review as it comes)
- Task A's result is required input for task B (sequential dependency)

---

## Core Behavior

When ClawSaver is active, the assistant applies these rules before responding:

### Batch Decision Rules

| Signal | Action |
|--------|--------|
| Same topic, ≥2 questions in one message | Batch into one structured response |
| Follow-up within 3 turns on the same subject | Offer to consolidate: "Want me to address all three at once?" |
| Redundant tool calls (same data fetched twice) | Cache and reuse within the response |
| Short clarifying question that could be preempted | Anticipate and answer proactively |
| Completely unrelated tasks | Keep separate — don't force-batch |

### Batching Thresholds

- **Always batch:** 2+ questions about the same resource/file/topic
- **Offer to batch:** 2+ questions where shared context exists
- **Never batch:** Tasks with sequential dependencies or > 3 unrelated domains

---

## Response Structure (When Batching)

When combining multiple asks, use this structure:

```
## [Topic]

**[Q1 / Task 1]**
Answer here.

**[Q2 / Task 2]**
Answer here.

**[Q3 / Task 3]**
Answer here.

---
💸 *Batched 3 asks → 1 response. Est. savings: ~2 API calls, ~800 tokens.*
```

The savings line is optional — include when it helps the user see the value, skip in high-frequency task flows.

---

## Trigger Phrases

The assistant activates batching mode when it sees phrases like:

- "Also..." / "And one more thing..." / "While you're at it..."
- "Can you also check..." / "What about..."
- Multiple "?" in a single message
- "Before you answer, also tell me..."

---

## Cost Impact Reference

| Scenario | Normal | With ClawSaver | Saved |
|----------|--------|----------------|-------|
| 3-part code review | 3 | 1 | 67% |
| Status check + next steps | 2 | 1 | 50% |
| 5 config questions | 5 | 2 | 60% |
| Research + summary + action | 3 | 1 | 67% |
| Unrelated tasks (2) | 2 | 2 | 0% |

Typical session savings: **30-50% fewer requests**, **20-35% fewer tokens**.

---

## Safety

- **Never merges tasks that require sequential output** — if result A feeds task B, they stay separate
- **Never sacrifices clarity for brevity** — batched responses are structured, not compressed
- **Never assumes context** — if combining asks requires guessing, it asks instead
- **Explicit opt-out:** Say "answer each one separately" and ClawSaver defers

---

## Installation

```bash
clawhub install clawsaver
```

---

## Version History

- **1.0.0** — Initial release. Batch decision rules, trigger detection, structured response format.
