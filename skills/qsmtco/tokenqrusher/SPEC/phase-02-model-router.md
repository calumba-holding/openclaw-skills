# Phase 2: Model Router Hook Specification

**Phase:** 2 of 8  
**Title:** Model Selection Hook  
**Objective:** Create a hook that routes tasks to appropriate AI model tiers based on complexity  
**Status:** Draft  
**Dependencies:** Phase 1 (Context Hook)

---

## 1. Overview

### Purpose

This phase creates the **Model Router Hook** - a system that ensures the appropriate AI model is used for each task. Instead of using expensive models (like Claude Sonnet at $3/MTok) for simple tasks, this system routes to cheaper or free models when appropriate.

### Why This Phase After Phase 1

Phase 1 handles **context reduction** (what files load).
Phase 2 handles **model selection** (which AI model processes the request).

Together they provide **comprehensive cost optimization**:
- Phase 1: Reduces tokens in (context)
- Phase 2: Reduces cost per token (model)

### Expected Impact

| Task Type | Before (Model) | After (Model) | Cost Reduction |
|-----------|---------------|---------------|----------------|
| Simple chat | Sonnet ($3/MT) | Step 3.5 Flash (Free) | **100%** |
| File read | Sonnet ($3/MT) | Haiku ($0.25/MT) | **92%** |
| Code writing | Sonnet ($3/MT) | Haiku ($0.25/MT) | **92%** |
| Complex reasoning | Sonnet ($3/MT) | MiniMax ($0.60/MT) | **80%** |

---

## 2. Technical Analysis

### OpenClaw Model Selection

From research of `/concepts/models.md`:

**Model Selection Order:**
1. Primary model (`agents.defaults.model.primary`)
2. Fallbacks (`agents.defaults.model.fallbacks`)
3. Provider auth failover

**Current Configuration:**
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5",
        "fallbacks": ["anthropic/claude-haiku-4"]
      }
    }
  }
}
```

**Switching Models:**
- `/model` command in chat
- Config file changes
- Cron-based rotation

### Challenge: Hooks Can't Change Models Directly

**The Problem:** OpenClaw hooks run during the bootstrap phase, but model selection happens **before** the hook fires. The model is already selected when our hook runs.

**Solution Options:**

| Approach | Pros | Cons | Chosen? |
|----------|------|------|---------|
| Hook modifies config | Direct | Config changes require restart | No |
| Cron-based rotation | Works | Can't react to message content | Partial |
| Directive-based | Precise | Requires user to specify | No |
| Pre-analysis + fallbacks | Works | Less optimal than routing | **Yes** |

**Our Approach: Pre-Analysis with Fallbacks**

Since we can't change models mid-session via hooks, we'll use a **multi-layered approach**:
1. **Set intelligent fallbacks** - Primary = expensive, Fallbacks = cheap
2. **Use cron for time-based rotation** - Work hours = Standard, Off-hours = Quick
3. **Let user override** - Use `/model` when needed

---

## 3. Architecture

### File Structure

```
~/.openclaw/hooks/
└── token-model/
    ├── HOOK.md              # Hook metadata
    ├── handler.ts           # Main handler (logs recommendation)
    ├── classifier.ts        # Model classification logic
    ├── config.json          # Model tier configuration
    └── tests/
        ├── classifier.test.ts
        └── handler.test.ts
```

### Component Design

```
┌─────────────────────────────────────────────────────────────┐
│                  token-model Hook                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  agent:bootstrap event                                       │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────┐                                        │
│  │ Get User Message│                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Classify        │  quick | standard | deep               │
│  │ Task Type       │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Log             │  Log recommendation to session         │
│  │ Recommendation  │  (Can't change model directly)         │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  Exit (model selection via config/cron)                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Details

### 4.1 HOOK.md

```markdown
---
name: token-model
description: "Routes tasks to appropriate model tiers based on complexity"
homepage: https://github.com/qsmtco/tokenQrusher
metadata: 
  openclaw: 
    emoji: "�模型"
    events: ["agent:bootstrap"]
    requires: 
      config: ["workspace.dir", "agents.defaults.model"]
---

# Token Model Hook

Routes tasks to appropriate AI model tiers based on complexity analysis.

## What It Does

1. Listens for `agent:bootstrap` event
2. Analyzes the user's message
3. Logs model recommendation (can't directly change model)

## Model Tiers

### Quick (Free)
Used for: greetings, acknowledgments, simple queries

Recommended models:
- `openrouter/stepfun/step-3.5-flash:free`
- `anthropic/claude-haiku-4`

### Standard ($0.25/MT)
Used for: code writing, file operations, regular work

Recommended models:
- `anthropic/claude-haiku-4`
- `openai/gpt-4o-mini`

### Deep ($0.60+/MT)
Used for: architecture, complex reasoning, debugging

Recommended models:
- `openrouter/minimax/minimax-m2.5`
- `anthropic/claude-sonnet-4-5`

## How Model Selection Works

**Important:** This hook CANNOT directly change the model due to OpenClaw architecture.

Instead, use these methods:

1. **Fallback Chain** - Configure fallbacks in openclaw.json
2. **Cron Rotation** - Use token-model-cron to rotate models by time
3. **Manual Override** - Use `/model` command

## Configuration

Edit `config.json` to customize model recommendations.

## Requirements

- OpenClaw with hooks enabled
- Model configured in openclaw.json

## Events

Listens to: `agent:bootstrap`
```

### 4.2 classifier.ts

```typescript
// classifier.ts - Model tier classification

// Communication patterns → Quick
const QUICK_PATTERNS = [
  /^(hi|hey|hello|yo|sup)\b/i,
  /^(thanks|thank you|thx)\b/i,
  /^(ok|okay|sure|got it|understood)\b/i,
  /^(yes|yeah|yep|yup|no|nope)\b/i,
  /^(good|great|nice|cool|awesome)\b/i,
  /^\w{1,15}$/,
];

// Background task patterns → Quick
const BACKGROUND_PATTERNS = [
  /heartbeat/i,
  /^check\s+(email|calendar|weather|monitoring)/i,
  /cron|scheduled/i,
  /^parse\s+(csv|json|log|xml)/i,
  /^extract\s+\w+\s+from/i,
  /^read\s+(log|logs)/i,
  /^scan\s+(file|document|error)/i,
];

// Simple task patterns → Quick
const SIMPLE_TASK_PATTERNS = [
  /^read\s+(file|the\s+\w+)/i,
  /^list\s+(files|dir)/i,
  /^show\s+(me\s+)?(the\s+)?(contents|status)/i,
  /^what'?s?\s+in/i,
  /^get\s+status/i,
  /^check\s+(if|whether|file)/i,
  /^is\s+\w+\s+(running|active|enabled)/i,
];

// Standard task patterns → Standard
const STANDARD_PATTERNS = [
  /^write\s+\w+/i,
  /^create\s+\w+/i,
  /^edit\s+\w+/i,
  /^fix\s+\w+/i,
  /^debug\s+\w+/i,
  /^explain\s+\w+/i,
  /^how\s+(do|can)\s+i/i,
  /^add\s+\w+/i,
  /^update\s+\w+/i,
];

// Complex patterns → Deep
const COMPLEX_PATTERNS = [
  /^design\s+\w+/i,
  /architect/i,
  /^comprehensive\s+\w+/i,
  /^analyze\s+deeply/i,
  /^plan\s+\w+\s+system/i,
  /^create\s+\w+\s+from\s+scratch/i,
  /^refactor\s+\w+\s+completely/i,
  /^implement\s+(full|entire)/i,
];

export type ModelTier = 'quick' | 'standard' | 'deep';

/**
 * Classifies task for model selection
 */
export function classifyForModel(message: string): ModelTier {
  const lower = message.toLowerCase();
  
  // Check Quick patterns first (most common)
  for (const pattern of QUICK_PATTERNS) {
    if (pattern.test(lower)) return 'quick';
  }
  
  for (const pattern of BACKGROUND_PATTERNS) {
    if (pattern.test(lower)) return 'quick';
  }
  
  for (const pattern of SIMPLE_TASK_PATTERNS) {
    if (pattern.test(lower)) return 'quick';
  }
  
  // Check Deep patterns
  for (const pattern of COMPLEX_PATTERNS) {
    if (pattern.test(lower)) return 'deep';
  }
  
  // Check Standard patterns
  for (const pattern of STANDARD_PATTERNS) {
    if (pattern.test(lower)) return 'standard';
  }
  
  // Default to standard
  return 'standard';
}

/**
 * Get model ID for tier
 */
export function getModelForTier(tier: ModelTier, config: Config): string {
  const defaults: Record<ModelTier, string> = {
    quick: 'openrouter/stepfun/step-3.5-flash:free',
    standard: 'anthropic/claude-haiku-4',
    deep: 'openrouter/minimax/minimax-m2.5'
  };
  
  return config?.models?.[tier] || defaults[tier];
}
```

### 4.3 handler.ts

```typescript
// handler.ts - Main hook handler

import type { HookHandler } from "../../src/hooks/hooks.js";
import { classifyForModel, getModelForTier, type ModelTier } from './classifier.js';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';

interface Config {
  models?: {
    quick?: string;
    standard?: string;
    deep?: string;
  };
  enabled?: boolean;
  logLevel?: 'debug' | 'info' | 'warn';
  logToSession?: boolean;
}

function loadConfig(): Config {
  const configPath = join(dirname(__filename), 'config.json');
  if (existsSync(configPath)) {
    try {
      return JSON.parse(readFileSync(configPath, 'utf-8'));
    } catch (e) {
      console.error('[token-model] Failed to load config:', e);
    }
  }
  return { enabled: true, logToSession: false };
}

const handler: HookHandler = async (event) => {
  // Only handle agent:bootstrap events
  if (event.type !== 'agent' || event.action !== 'bootstrap') {
    return;
  }

  const config = loadConfig();
  
  if (config.enabled === false) {
    console.log('[token-model] Hook disabled, skipping');
    return;
  }

  // Extract user message
  const message = extractUserMessage(event.context);
  
  if (!message) {
    console.log('[token-model] No user message found');
    return;
  }

  // Classify for model selection
  const tier = classifyForModel(message);
  const recommendedModel = getModelForTier(tier, config);
  
  // Log the recommendation
  if (config.logLevel !== 'debug') {
    console.log(`[token-model] Task: ${tier} → ${recommendedModel}`);
  } else {
    console.log(`[token-model] Message: "${message.substring(0, 50)}..."`);
    console.log(`[token-model] Tier: ${tier}`);
    console.log(`[token-model] Recommended: ${recommendedModel}`);
  }
  
  // Add note to session messages if enabled
  if (config.logToSession && event.messages) {
    event.messages.push(`[token-model] Using ${tier} model: ${recommendedModel}`);
  }
  
  // Note: We cannot directly change the model here
  // Model selection is done before this hook fires
  // Use config/fallbacks or cron for model rotation
};

function extractUserMessage(context: any): string | null {
  if (context?.sessionEntry?.messages?.length > 0) {
    const messages = context.sessionEntry.messages;
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        return messages[i].content;
      }
    }
  }
  return null;
}

export default handler;
```

### 4.4 config.json

```json
{
  "enabled": true,
  "logLevel": "info",
  "logToSession": false,
  "models": {
    "quick": "openrouter/stepfun/step-3.5-flash:free",
    "standard": "anthropic/claude-haiku-4",
    "deep": "openrouter/minimax/minimax-m2.5"
  }
}
```

---

## 5. Time-Based Model Rotation (Phase 2b - Cron)

Since hooks can't change models, we'll use **cron-based rotation**:

### cron-model-rotation job

```bash
# During work hours (9 AM - 5 PM): Use Standard model
# Outside work hours: Use Quick model

# Add cron job
openclaw cron add \
  --name "model-morning" \
  --cron "0 9 * * 1-5" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Switch to standard model for work hours" \
  --model "anthropic/claude-haiku-4"

# After work: Switch to quick
openclaw cron add \
  --name "model-evening" \
  --cron "0 17 * * 1-5" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Switch to quick model for evening" \
  --model "openrouter/stepfun/step-3.5-flash:free"
```

### rotation-script.ts

```typescript
// rotation-script.ts - Run by cron to rotate models

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';

const CONFIG_PATH = join(process.env.HOME || '', '.openclaw/openclaw.json');

interface OpenClawConfig {
  agents?: {
    defaults?: {
      model?: {
        primary?: string;
        fallbacks?: string[];
      };
    };
  };
}

function rotateModel() {
  const hour = new Date().getHours();
  const isWorkHours = hour >= 9 && hour < 17;
  
  const newModel = isWorkHours 
    ? 'anthropic/claude-haiku-4'  // Standard
    : 'openrouter/stepfun/step-3.5-flash:free';  // Quick
  
  console.log(`[model-rotation] Hour: ${hour}, Work hours: ${isWorkHours}`);
  console.log(`[model-rotation] Setting model to: ${newModel}`);
  
  // Read current config
  if (!existsSync(CONFIG_PATH)) {
    console.error('[model-rotation] Config not found');
    process.exit(1);
  }
  
  const config: OpenClawConfig = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
  
  // Update model
  if (!config.agents) config.agents = {};
  if (!config.agents.defaults) config.agents.defaults = {};
  if (!config.agents.defaults.model) config.agents.defaults.model = {};
  
  config.agents.defaults.model.primary = newModel;
  
  // Write config
  writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  
  console.log('[model-rotation] Model rotated successfully');
}

rotateModel();
```

---

## 6. Fallback Chain Configuration

The most reliable way to use cheaper models is through **fallbacks**:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-5",
        "fallbacks": [
          "anthropic/claude-haiku-4",
          "openrouter/stepfun/step-3.5-flash:free"
        ]
      }
    }
  }
}
```

**How it works:**
1. Primary model (Sonnet) is tried first
2. If it fails or rate-limits, Haiku is tried
3. If Haiku fails, Step 3.5 Flash (free) is tried

---

## 7. Error Handling

| Scenario | Handling |
|----------|----------|
| Config missing | Use defaults |
| Config corrupted | Use defaults, log error |
| No message found | Log, skip classification |
| Model in config invalid | Fall back to default |

---

## 8. Testing Strategy

### Unit Tests

```typescript
describe('classifyForModel', () => {
  it('classifies greetings as quick', () => {
    expect(classifyForModel('hi')).toBe('quick');
    expect(classifyForModel('thanks')).toBe('quick');
  });
  
  it('classifies code tasks as standard', () => {
    expect(classifyForModel('write a function')).toBe('standard');
    expect(classifyForModel('fix the bug')).toBe('standard');
  });
  
  it('classifies design as deep', () => {
    expect(classifyForModel('design a system')).toBe('deep');
    expect(classifyForModel('architect microservices')).toBe('deep');
  });
});
```

### Integration Tests

- Verify hook loads on startup
- Verify classification works with real messages

---

## 9. Dependencies

### Phase Dependencies

| Dependency | Purpose |
|------------|---------|
| Phase 1 (Context Hook) | Provides foundation for hooks |

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| OpenClaw | 2026.2+ | Hook system |
| TypeScript | 5.x | Implementation |

---

## 10. Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| enabled | boolean | true | Enable/disable |
| logLevel | string | "info" | debug, info, warn |
| logToSession | boolean | false | Add note to messages |
| models.quick | string | step-3.5-flash:free | Quick tier model |
| models.standard | string | claude-haiku-4 | Standard tier model |
| models.deep | string | minimax-m2.5 | Deep tier model |

---

## 11. Acceptance Criteria

### Functional Requirements

- [ ] Hook loads on startup
- [ ] Classification works for quick/standard/deep
- [ ] Model recommendations logged
- [ ] Cron rotation script works

### Non-Functional Requirements

- [ ] Hook adds <5ms to bootstrap
- [ ] No crashes on errors

---

## 12. Alternative Approaches Considered

### Approach: Direct Model Change via Config
- **Idea:** Modify openclaw.json in the hook
- **Problem:** Requires restart, race conditions
- **Verdict:** Not used

### Approach: Directive-Based
- **Idea:** Parse `!model:quick` in message
- **Problem:** Requires user action
- **Verdict:** Documented as manual override

### Approach: Session State Detection
- **Idea:** Detect if this is first message or continuation
- **Problem:** Complex to implement reliably
- **Verdict:** Deferred to future phase

---

## 13. References

- OpenClaw Models: `/concepts/models.md`
- OpenClaw Hooks: `/automation/hooks.md`
- OpenClaw Cron: `/automation/cron-jobs.md`

---

*This specification defines Phase 2 implementation. See IMPLEMENTATION_PLAN.md for phase dependencies.*
