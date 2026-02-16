# Phase 5: Heartbeat Integration Specification

**Phase:** 5 of 8  
**Title:** Optimized Heartbeat System  
**Objective:** Leverage OpenClaw's native HEARTBEAT.md system for efficient polling  
**Status:** Draft  
**Dependencies:** Phase 4

---

## 1. Overview

### Purpose

This phase implements an **optimized heartbeat system** using OpenClaw's native HEARTBEAT.md mechanism. This reduces unnecessary API calls by only running checks when needed.

### Why This Phase After Phase 4

Phase 4 (Cron Optimizer) can adjust heartbeat intervals. Phase 5 implements the actual heartbeat logic.

### Expected Impact

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Heartbeat calls/day | 48 | 12 | **75%** |
| Heartbeat tokens/day | ~5000 | ~1250 | **75%** |

---

## 2. Technical Analysis

### OpenClaw Heartbeat System

From HEARTBEAT.md research:

**Key Features:**
- `HEARTBEAT_OK` response skips message generation
- HEARTBEAT.md in workspace configures behavior
- Integrates with heartbeat_optimizer.py

**Current Implementation:**
- Runs every 30 minutes by default
- No smart filtering
- Always generates response (wastes tokens)

---

## 3. Implementation

### 3.1 HEARTBEAT.md Template

```markdown
# tokenQrusher Heartbeat

## Configuration
- **Check interval**: 2 hours (via heartbeat_optimizer.py)
- **Quiet hours**: 23:00 - 08:00 (skip all checks)
- **Model**: Quick tier (free)

## Check Types

### Email (every 2 hours)
```bash
heartbeat_optimizer.py check email
```

### Calendar (every 4 hours)
```bash
heartbeat_optimizer.py check calendar
```

### Weather (every 4 hours)
```bash
heartbeat_optimizer.py check weather
```

### Monitoring (every 2 hours)
```bash
heartbeat_optimizer.py check monitoring
```

## Response Protocol

**No alerts**: `HEARTBEAT_OK`

**Alerts present**:
```
🔔 [Type]: [Summary]
→ [Action]
```

## Optimization

This heartbeat uses tokenQrusher's heartbeat_optimizer.py to determine which checks to run:
- Skips checks during quiet hours
- Only runs checks at configured intervals
- Returns HEARTBEAT_OK when nothing to report
```

### 3.2 Heartbeat Logic

```bash
#!/bin/bash
# token-heartbeat.sh - Optimized heartbeat script

# Get current hour
HOUR=$(date +%H)

# Check quiet hours (23:00 - 08:00)
if [ "$HOUR" -ge 23 ] || [ "$HOUR" -lt 8 ]; then
    echo "HEARTBEAT_OK"
    exit 0
fi

# Plan checks using optimizer
PLAN=$(python3 ~/.openclaw/workspace/skills/tokenQrusher/scripts/heartbeat_optimizer.py plan)

# Check if any checks needed
SHOULD_RUN=$(echo "$PLAN" | grep -o '"should_run": *[^,]*' | cut -d':' -f2 | tr -d ' ')

if [ "$SHOULD_RUN" = "false" ]; then
    echo "HEARTBEAT_OK"
    exit 0
fi

# Run planned checks
echo "$PLAN" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for check in data.get('planned', []):
    print(f'Running: {check[\"type\"]}')
    # Run actual check logic here
"

# Record checks
python3 ~/.openclaw/workspace/skills/tokenQrusher/scripts/heartbeat_optimizer.py record email
```

---

## 4. Configuration

### Intervals

| Check Type | Default | Optimized |
|------------|---------|-----------|
| Email | 60 min | 120 min |
| Calendar | 60 min | 240 min |
| Weather | 60 min | 240 min |
| Monitoring | 30 min | 120 min |

### Quiet Hours

- Start: 23:00
- End: 08:00
- Action: Skip all checks

---

## 5. Integration

### With Phase 3 (Usage Tracking)

- Track heartbeat token usage
- Adjust intervals based on usage

### With Phase 4 (Cron)

- Cron can override heartbeat settings

---

## 6. Acceptance Criteria

- [ ] HEARTBEAT.md installed in workspace
- [ ] Quiet hours skip all checks
- [ ] Intervals enforced correctly
- [ ] HEARTBEAT_OK returned when nothing to do
- [ ] Token usage reduced by 75%

---

## 7. References

- OpenClaw Heartbeat: `/automation/cron-vs-heartbeat.md`
- HEARTBEAT.md in workspace

---

*This specification defines Phase 5 implementation. See IMPLEMENTATION_PLAN.md for phase dependencies.*
