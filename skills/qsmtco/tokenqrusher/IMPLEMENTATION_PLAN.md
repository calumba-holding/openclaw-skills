# tokenQrusher v2.0 - Implementation Plan

**Version:** 2.0  
**Status:** Planning  
**Date:** February 15, 2026  
**Author:** Lieutenant Qrusher

---

## Executive Summary

This document outlines a phased approach to transform tokenQrusher from an advisory-only toolkit into an **operational cost-optimization system** for OpenClaw. The plan leverages OpenClaw's native features (hooks, cron, config) to achieve actual cost reductions without requiring core OpenClaw modifications.

---

## Research Findings

### OpenClaw Native Capabilities Discovered

| Capability | Purpose | Our Use Case |
|-----------|---------|--------------|
| **Hooks: `agent:bootstrap`** | Mutate context files before injection | Control which files load |
| **Hooks: `command:new`** | Run code on `/new` | Optimize new sessions |
| **Cron Jobs** | Schedule background tasks | Periodic optimization |
| **Model Selection** | `/model` or config | Route to appropriate model |
| **Usage Tracking** | Built-in via `/usage cost` | Track actual spending |
| **Session State** | `sessions.json` | Monitor token usage |
| **HEARTBEAT.md** | Heartbeat config | Reduce polling frequency |

### Key Insight

**We don't need core OpenClaw changes.** OpenClaw already has:
1. A hooks system that can mutate bootstrap files
2. A cron system that can run isolated sessions with specific models
3. Built-in usage tracking from providers
4. A heartbeat system we can optimize

---

## Architectural Approach: "The Hook Strategy"

Instead of trying to intercept OpenClaw's internal processing, we **leverage existing extension points**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw Native Features                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. HOOK: agent:bootstrap                                       │
│     └── Mutate which context files load                          │
│         → Our hook filters files based on prompt analysis         │
│                                                                  │
│  2. HOOK: command:new                                           │
│     └── On /new, optimize the fresh session                     │
│         → Our hook can set initial model, context level          │
│                                                                  │
│  3. CRON: Periodic optimizer                                    │
│     └── Run optimization analysis on schedule                    │
│         → Analyze usage, suggest/configure better settings        │
│                                                                  │
│  4. HEARTBEAT.md: Optimized heartbeat                           │
│     └── Already supports HEARTBEAT_OK pattern                   │
│         → Just need to use it properly                          │
│                                                                  │
│  5. USAGE TRACKING: Built-in                                    │
│     └── /usage cost shows actual spending                        │
│         → No need to build our own tracker                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Map

| Phase | Focus | Deliverable | Complexity |
|-------|-------|-------------|-----------|
| **Phase 1** | Context Hook | Working `agent:bootstrap` hook that filters context | Medium |
| **Phase 2** | Model Router Hook | Hook that selects model based on task | Medium |
| **Phase 3** | Usage Integration | Connect to OpenClaw's usage tracking | Low |
| **Phase 4** | Cron Optimizer | Periodic analysis and auto-tuning | High |
| **Phase 5** | Heartbeat Integration | Optimized heartbeat using native system | Low |
| **Phase 6** | CLI Unification | Single CLI for all operations | Medium |
| **Phase 7** | Testing & Polish | Comprehensive testing, error handling | Medium |
| **Phase 8** | Documentation | User guide, API docs, examples | Low |

---

## Phase 1: Context Hook Implementation

### Objective

Create an OpenClaw hook that **filters which context files load** based on the incoming message/prompt.

### OpenClaw Feature Used

- **Hook:** `agent:bootstrap`
- **Capability:** Can mutate `context.bootstrapFiles`

### Technical Approach

```typescript
// hooks/token-context/handler.ts
import type { HookHandler } from "../../src/hooks/hooks.js";

const CONTEXT_RULES = {
  // Simple messages: minimal context
  simple: ["SOUL.md", "IDENTITY.md"],
  
  // Standard work: add today's memory
  standard: ["SOUL.md", "IDENTITY.md", "USER.md"],
  
  // Complex: full context
  complex: ["SOUL.md", "IDENTITY.md", "USER.md", "TOOLS.md", "AGENTS.md", "MEMORY.md"]
};

const handler: HookHandler = async (event) => {
  if (event.type !== "agent" || event.action !== "bootstrap") {
    return;
  }

  // Get the user's message from context
  const message = extractUserMessage(event.context);
  const complexity = classifyMessage(message);
  
  // Filter bootstrap files
  const allowedFiles = CONTEXT_RULES[complexity];
  event.context.bootstrapFiles = event.context.bootstrapFiles
    .filter(f => allowedFiles.includes(f.name));
    
  console.log(`[token-context] Loaded ${allowedFiles.length} files for ${complexity} task`);
};

export default handler;
```

### Deliverables

- [ ] Hook directory: `~/.openclaw/hooks/token-context/`
- [ ] `HOOK.md` with metadata
- [ ] `handler.ts` implementation
- [ ] Classification logic (simple/standard/complex)
- [ ] Test cases

### Estimated Tokens Saved

- Simple (hi, thanks): 50,000 → 500 tokens = **99% reduction**
- Standard (write code): 50,000 → 5,000 tokens = **90% reduction**
- Complex (architect): 50,000 → 50,000 tokens = **0% (full context)**

---

## Phase 2: Model Router Hook

### Objective

Create a hook that **selects the appropriate AI model** based on task complexity.

### OpenClaw Features Used

- **Hook:** `command:new` or `agent:bootstrap`  
- **Config:** `agents.defaults.model` (can be overridden)

### Technical Approach

```typescript
// hooks/model-selector/handler.ts
const TIER_MODELS = {
  quick: "openrouter/stepfun/step-3.5-flash:free",
  standard: "anthropic/claude-haiku-4",
  deep: "openrouter/minimax/minimax-m2.5"
};

const handler: HookHandler = async (event) => {
  // Determine tier based on message
  const message = extractUserMessage(event.context);
  const tier = classifyForModel(message);
  
  // Note: Model selection in hooks is limited
  // We may need to use /model command or config
  console.log(`[model-selector] Recommended tier: ${tier}`);
};
```

### Challenge & Solution

**Challenge:** Hooks can't directly change the model mid-session.

**Solution Options:**
1. **Pre-session config** - Set default model in config, use `/model` to override
2. **Cron-based model rotation** - Change config periodically based on time of day
3. **Directive-based** - User includes model hint in message

**Recommended:** Use **cron-based model rotation** - during work hours (9-5), use Standard; off-hours use Quick.

### Deliverables

- [ ] Hook: `~/.openclaw/hooks/model-selector/`
- [ ] Classification logic (reuse from v1)
- [ ] Cron job to rotate model based on time
- [ ] Documentation

---

## Phase 3: Usage Integration

### Objective

Connect to OpenClaw's **built-in usage tracking** instead of building our own stub.

### OpenClaw Features Used

- **CLI:** `openclaw status --usage`
- **Chat:** `/usage cost`
- **Session:** Token counts in `sessions.json`

### Technical Approach

```python
# scripts/usage_monitor.py
import subprocess
import json

def get_usage():
    """Get current usage from OpenClaw."""
    result = subprocess.run(
        ["openclaw", "status", "--usage"],
        capture_output=True, text=True
    )
    # Parse output or use --json if available
    return parse_usage(result.stdout)

def get_daily_cost():
    """Get today's cost from session logs."""
    # Read from sessions.json, filter by date
    pass

def check_budget():
    """Check if approaching limit."""
    usage = get_usage()
    if usage["cost_today"] > DAILY_LIMIT:
        alert_admin()
        switch_to_cheaper_model()
```

### Deliverables

- [ ] `usage_monitor.py` - Integrates with OpenClaw's tracking
- [ ] Budget alert system
- [ ] Auto-downgrade logic when budget exceeded

---

## Phase 4: Cron Optimizer

### Objective

Create a **periodic optimization job** that analyzes usage and automatically tunes settings.

### OpenClaw Features Used

- **Cron:** `openclaw cron add`
- **Isolated sessions:** Run analysis in separate session

### Technical Approach

```bash
# Create cron job for optimization
openclaw cron add \
  --name "token-optimizer" \
  --cron "0 * * *" \
  --session isolated \
  --message "Run token optimization analysis" \
  --model "openrouter/stepfun/step-3.5-flash:free"
```

```python
# optimization_task.py
def run_optimization():
    # 1. Analyze yesterday's usage
    usage = get_daily_usage()
    
    # 2. Identify optimization opportunities
    if usage["expensive_model_ratio"] > 0.5:
        suggest_model_change()
    
    # 3. Check context loading efficiency
    if usage["avg_context"] > 20000:
        suggest_context_filtering()
    
    # 4. Adjust heartbeat intervals
    if usage["heartbeat_calls"] > 100:
        reduce_heartbeat_frequency()
    
    # 5. Generate report
    send_report(usage)
```

### Optimization Actions

| Condition | Action |
|-----------|--------|
| >50% requests are simple | Switch default to Quick |
| >30% context is unused | Enable aggressive filtering |
| >$10/day spend | Alert + suggest changes |
| Heartbeat >100/day | Reduce to every 2 hours |

### Deliverables

- [ ] Cron job definition
- [ ] Optimization analysis script
- [ ] Auto-tuning logic (config changes)
- [ ] Report generation

---

## Phase 5: Heartbeat Integration

### Objective

Optimize heartbeat using **native HEARTBEAT.md** system.

### OpenClaw Feature Used

- **HEARTBEAT.md** - Already supports `HEARTBEAT_OK` pattern

### Technical Approach

The native heartbeat system already supports our use case. We need to:

1. **Install optimized HEARTBEAT.md** in workspace
2. **Use heartbeat_optimizer.py** to plan checks
3. **Leverage HEARTBEAT_OK** to skip unnecessary work

```markdown
<!-- HEARTBEAT.md -->
# Heartbeat

## Check Schedule
Run `heartbeat_optimizer.py plan` to determine what to check.

## Quiet Hours
Skip all checks 23:00-08:00.

## Response
If nothing to report: `HEARTBEAT_OK`
```

### Deliverables

- [ ] Optimized HEARTBEAT.md template
- [ ] Integration with heartbeat_optimizer.py
- [ ] Documentation

---

## Phase 6: CLI Unification

### Objective

Create a **single CLI** that wraps all functionality.

### Technical Approach

```bash
# Unified CLI
tokenqrusher context "hello world"    # Recommend context
tokenqrusher model "write code"       # Recommend model  
tokenqrusher budget                   # Check budget
tokenqrusher optimize                 # Run optimization
tokenqrusher status                   # Full status
```

### Implementation

```python
#!/usr/bin/env python3
# bin/tokenqrusher

import sys
import argparse
from commands import context, model, budget, optimize, status

def main():
    parser = argparse.ArgumentParser(prog="tokenqrusher")
    subparsers = parser.add_subparsers()
    
    # Add subcommands
    context_parser = subparsers.add_parser("context")
    context_parser.add_argument("prompt")
    
    model_parser = subparsers.add_parser("model")
    model_parser.add_argument("prompt")
    
    # ... etc
    
    args = parser.parse_args()
    # Route to appropriate command

if __name__ == "__main__":
    main()
```

### Deliverables

- [ ] `bin/tokenqrusher` CLI
- [ ] Subcommands: context, model, budget, optimize, status
- [ ] Help documentation

---

## Phase 7: Testing & Polish

### Objective

Ensure reliability through comprehensive testing.

### Test Categories

| Category | Tests | Focus |
|----------|-------|-------|
| Unit | 50+ | Individual functions |
| Integration | 20+ | Hook + OpenClaw |
| End-to-end | 10+ | Full workflow |
| Edge cases | 30+ | Error handling |

### Test Plan

- [ ] Mock OpenClaw hooks API
- [ ] Test classification accuracy
- [ ] Test config modification
- [ ] Test cron job execution
- [ ] Error handling tests

---

## Phase 8: Documentation

### Objective

Create comprehensive documentation for users and developers.

### Documentation Plan

| Document | Audience | Content |
|----------|----------|---------|
| README.md | Users | Quick start, examples |
| SKILL.md | Users | Full reference |
| ARCHITECTURE.md | Developers | Design decisions |
| API.md | Developers | CLI reference |
| EXAMPLES.md | Users | Use cases |

---

## Implementation Order & Dependencies

```
Phase 1: Context Hook
    │
    ├─→ Phase 2: Model Router Hook
    │        │
    │        └─→ Phase 3: Usage Integration
    │                 │
    │                 └─→ Phase 4: Cron Optimizer
    │                          │
    │                          └─→ Phase 6: CLI Unification
    │
    └─→ Phase 5: Heartbeat Integration
              │
              └─→ Phase 7: Testing & Polish
                       │
                       └─→ Phase 8: Documentation
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Hook API changes | Low | High | Version check, graceful degradation |
| Context filtering breaks functionality | Medium | High | Whitelist critical files |
| Model selection not enforced | High | Medium | Use cron + config instead |
| Usage API unavailable | Low | Low | Fallback to estimation |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Context reduction (simple) | 90%+ | `/context list` before/after |
| Context reduction (standard) | 50%+ | `/context list` before/after |
| Model cost reduction | 50%+ | `/usage cost` before/after |
| Heartbeat API calls | -75% | Count per day |
| Hook reliability | 99%+ | Error rate in logs |

---

## Alternative Approaches Considered

### Approach A: Direct Core Modification
- **Pros:** Full control
- **Cons:** Requires Asif's buy-in, ongoing maintenance
- **Verdict:** Not pursued

### Approach B: Middleware Proxy
- **Pros:** Complete control
- **Cons:** Complex, breaks some features
- **Verdict:** Not pursued

### Approach C: Native Hooks (Chosen)
- **Pros:** Uses existing OpenClaw features, maintainable
- **Cons:** Limited by hook capabilities
- **Verdict:** Primary approach

---

## Open Questions

1. **Can hooks actually mutate bootstrapFiles?** Documentation says yes, need to verify
2. **Can we change model mid-session via hook?** Likely no, need cron-based solution
3. **How to detect "first message" vs "continuation"?** Need to check session state

---

## Next Steps

1. **Verify hook capabilities** - Test `agent:bootstrap` mutation
2. **Build Phase 1** - Context hook implementation
3. **Iterate** - Based on testing results

---

## References

- OpenClaw Hooks: `/automation/hooks.md`
- OpenClaw Context: `/concepts/context.md`
- OpenClaw Models: `/concepts/models.md`
- OpenClaw Cron: `/automation/cron-jobs.md`
- OpenClaw Usage: `/concepts/usage-tracking.md`

---

*This document is a working plan. It will be updated as implementation progresses.*
