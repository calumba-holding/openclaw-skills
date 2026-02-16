# tokenQrusher - Problem Statement

**Version:** 2.0 (Draft)  
**Status:** Defining the Problem  
**Date:** February 15, 2026

---

## The Problem

OpenClaw is an AI assistant platform that consumes tokens (money) for every conversation. The costs add up quickly when:

1. **Context Loading** - Every session loads 50K+ tokens of files (docs, memory logs, configs) even for simple "hi" messages
2. **Model Selection** - Uses expensive AI models ($3-15/million tokens) for trivial tasks like file reads
3. **Heartbeat Polling** - Runs resource-intensive checks every 30 minutes, even when nothing changes

---

## What We Want

An OpenClaw skill that **actually reduces token costs by 50-80%** by:

| Goal | Current | Target |
|------|---------|--------|
| Context per conversation | 50,000 tokens | 2,000 tokens (96% reduction) |
| Model for simple tasks | $3/MT (Sonnet) | $0/MT (free model) |
| Heartbeat checks | Every 30 min | Every 2-4 hours |
| Monthly cost (100K/day) | $9.00 | $0.90 - $2.70 |

---

## Why Current Approach Fails

The existing skill outputs JSON recommendations like:
```json
{
  "recommended_model": "openrouter/stepfun/step-3.5-flash:free",
  "context_level": "minimal",
  "files": ["SOUL.md", "IDENTITY.md"]
}
```

But **nothing acts on this output**. It's advisory, not operational.

**We need a skill that:**
1. **Hooks into OpenClaw's execution pipeline** - Not just gives advice
2. **Enforces decisions** - Not just suggests them
3. **Tracks actual usage** - Not just estimates

---

## Constraints

- **Must remain a skill** - No core OpenClaw modifications
- **Must be safe** - No unauthorized network calls, no eval/exec
- **Must work offline** - Fallback when APIs unavailable
- **Must be auditable** - All decisions logged

---

## Success Criteria

A working version 2.0 must:

- [ ] Actually control which context files load (not just recommend)
- [ ] Actually select the model (not just suggest)
- [ ] Actually track token usage (not stub)
- [ ] Reduce costs measurably (not just claim to)
- [ ] Work without core OpenClaw changes (skill-only solution)

---

## Technical Approach Options

1. **CLI Shim** - Create a wrapper that intercepts calls
2. **Config Generator** - Auto-generate openclaw.json patches  
3. **Cron Optimizer** - Analyze logs, apply fixes retroactively
4. **Hybrid** - Combination of above

---

*This document defines what we're solving. Next: Define the solution.*
