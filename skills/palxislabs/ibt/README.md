# IBT v2.5 — Instinct + Behavior + Trust

Deterministic execution discipline for agents with an **instinct layer** — pre-execution observation, takes, and genuine opinions. v2.5 adds the complete framework including trust layer and human ambiguity handling.

## Why IBT v2.5?

IBT v1 handled reliability. IBT v2 adds agency. IBT v2.2 adds OpenClaw integration. IBT v2.3 adds trust. IBT v2.5 adds **human ambiguity handling** — knowing when to ask instead of assume.

## What's Included

| File | Description |
|------|-------------|
| SKILL.md | Complete skill definition (v1 + v2 + v2.2 + v2.3 + v2.5) |
| POLICY.md | Instinct layer rules |
| TEMPLATE.md | Full drop-in policy |
| EXAMPLES.md | Before/after demonstrations |

## Core Loop

**Observe → Parse → Plan → Commit → Act → Verify → Update → Stop**

### Quick Reference

1. **Observe** — Pre-execution pause (Notice, Take, Hunch, Suggest)
2. **Parse** — Extract goals, understand WHAT must be true
3. **Plan** — Shortest verifiable path
4. **Commit** — Commit before acting
5. **Act** — Execute
6. **Verify** — Evidence-based checks
7. **Update** — Patch smallest failed step
8. **Stop** — Stop when done or blocked

### Key Features

- **Human Ambiguity**: When unclear, ask — don't assume
- **Trust Contract**: Define relationship explicitly
- **Session Realignment**: After gaps, summarize where you left off
- **Stop = Stop**: Always halt when asked

## Install

```bash
clawhub install ibt
```

## License

MIT
