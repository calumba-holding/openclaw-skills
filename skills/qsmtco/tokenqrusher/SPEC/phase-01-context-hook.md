# Phase 1: Context Hook Specification

**Phase:** 1 of 8  
**Title:** Context Filtering Hook  
**Objective:** Create an OpenClaw hook that filters which context files load based on message complexity  
**Status:** Draft  
**Dependencies:** None (Foundation Phase)

---

## 1. Overview

### Purpose

This phase creates the foundational **Context Filtering Hook** - an OpenClaw hook that intercepts the bootstrap process and filters which workspace files are loaded into context based on the complexity of the incoming message.

### Why This Phase First

Context loading is the **biggest source of waste** in OpenClaw:
- Default: 50,000+ tokens loaded for every conversation
- Even "hi" messages load all files (AGENTS.md, TOOLS.md, MEMORY.md, etc.)
- This costs money even when not needed

Solving context filtering delivers the **highest ROI** with relatively low risk.

### Expected Impact

| Message Type | Before | After | Savings |
|--------------|--------|-------|---------|
| Simple (hi, thanks) | 50,000 tokens | 500 tokens | **99%** |
| Standard (write code) | 50,000 tokens | 5,000 tokens | **90%** |
| Complex (architect) | 50,000 tokens | 50,000 tokens | 0% (full context needed) |

---

## 2. Technical Analysis

### OpenClaw Hook System

From research of `/automation/hooks.md`:

**Hook Discovery:**
- Workspace hooks: `<workspace>/hooks/` (per-agent, highest precedence)
- Managed hooks: `~/.openclaw/hooks/` (user-installed, shared)
- Bundled hooks: `<openclaw>/dist/hooks/bundled/` (shipped with OpenClaw)

**Hook Structure:**
```
hook-name/
├── HOOK.md          # Metadata + documentation
└── handler.ts       # Handler implementation
```

**Relevant Events:**
- `agent:bootstrap` - Before workspace bootstrap files are injected
- Can mutate `context.bootstrapFiles` array

### Key API (From Documentation)

```typescript
interface HookEvent {
  type: 'command' | 'session' | 'agent' | 'gateway';
  action: string;
  sessionKey: string;
  timestamp: Date;
  messages: string[];
  context: {
    sessionEntry?: SessionEntry;
    sessionId?: string;
    workspaceDir?: string;
    bootstrapFiles?: WorkspaceBootstrapFile[];  // ← WE CAN MUTATE THIS
    cfg?: OpenClawConfig;
  };
}

interface WorkspaceBootstrapFile {
  name: string;      // e.g., "SOUL.md"
  path: string;      // Full path
  raw?: string;      // Raw content
  injected?: string; // Injected content
}
```

### Implementation Strategy

We need to:
1. Create a hook that listens to `agent:bootstrap`
2. Extract the user's message from the session
3. Classify the message complexity
4. Filter `bootstrapFiles` to only include appropriate files

---

## 3. Architecture

### File Structure

```
~/.openclaw/hooks/
└── token-context/
    ├── HOOK.md              # Hook metadata
    ├── handler.ts           # Main handler
    ├── classifier.ts        # Message classification logic
    └── tests/
        ├── classifier.test.ts
        ├── handler.test.ts
        └── integration.test.ts
```

### Component Design

```
┌─────────────────────────────────────────────────────────────┐
│                  token-context Hook                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  agent:bootstrap event                                       │
│         │                                                   │
│         ▼                                                   │
│  ┌─────────────────┐                                        │
│  │ Get User Message│  From session entry                    │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Classify        │  simple | standard | complex            │
│  │ Complexity      │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Get Allowed     │  From config                           │
│  │ Files List     │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Filter          │  Remove non-allowed files              │
│  │ bootstrapFiles  │                                        │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  Log result & exit                                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Details

### 4.1 HOOK.md

```markdown
---
name: token-context
description: "Filters context files based on message complexity to reduce token usage"
homepage: https://github.com/qsmtco/tokenQrusher
metadata: 
  openclaw: 
    emoji: "🎯"
    events: ["agent:bootstrap"]
    requires: 
      config: ["workspace.dir"]
---

# Token Context Hook

Filters which workspace files are loaded into context based on the complexity of the incoming message.

## What It Does

1. Listens for `agent:bootstrap` event
2. Extracts the user's message from the session
3. Classifies complexity (simple/standard/complex)
4. Filters `bootstrapFiles` to only include necessary files

## Complexity Levels

### Simple (99% token reduction)
Used for: greetings, acknowledgments, simple questions

Files loaded:
- SOUL.md (identity)
- IDENTITY.md (who I am)

### Standard (90% token reduction)
Used for: code writing, file operations, regular work

Files loaded:
- SOUL.md
- IDENTITY.md  
- USER.md (about the user)

### Complex (0% reduction)
Used for: architecture, design, deep analysis

Files loaded:
- ALL files (current behavior preserved)

## Configuration

Edit `config.json` in the hook directory to customize file lists.

## Requirements

- OpenClaw with hooks enabled
- Workspace directory configured

## Events

Listens to: `agent:bootstrap`
```

### 4.2 classifier.ts

```typescript
// classifier.ts - Message complexity classification

// Communication patterns that indicate simple messages
const SIMPLE_PATTERNS = [
  /^(hi|hey|hello|yo|sup)\b/i,
  /^(thanks|thank you|thx)\b/i,
  /^(ok|okay|sure|got it|understood)\b/i,
  /^(yes|yeah|yep|yup|no|nope)\b/i,
  /^(good|great|nice|cool|awesome)\b/i,
  /^(what|how)'s\s+(up|it\s+going)/i,
  /^\w{1,15}$/,  // Single short word
  /^(lol|haha|lmao)\b/i,
];

// Background task patterns
const BACKGROUND_PATTERNS = [
  /heartbeat/i,
  /check\s+(email|calendar|weather|monitoring)/i,
  /cron|scheduled/i,
  /parse\s+(csv|json|log)/i,
];

// Complex task indicators
const COMPLEX_PATTERNS = [
  /design\s+\w+/i,
  /architect/i,
  /comprehensive/i,
  /analyze\s+deeply/i,
  /plan\s+\w+\s+system/i,
  /create\s+\w+\s+from\s+scratch/i,
];

export type ComplexityLevel = 'simple' | 'standard' | 'complex';

/**
 * Classifies message complexity for context filtering
 */
export function classifyComplexity(message: string): ComplexityLevel {
  const lower = message.toLowerCase();
  
  // Check for simple patterns first
  for (const pattern of SIMPLE_PATTERNS) {
    if (pattern.test(lower)) {
      return 'simple';
    }
  }
  
  // Check for background tasks (treated as simple)
  for (const pattern of BACKGROUND_PATTERNS) {
    if (pattern.test(lower)) {
      return 'simple';
    }
  }
  
  // Check for complex patterns
  for (const pattern of COMPLEX_PATTERNS) {
    if (pattern.test(lower)) {
      return 'complex';
    }
  }
  
  // Default to standard
  return 'standard';
}

/**
 * Get list of allowed files for a complexity level
 */
export function getAllowedFiles(complexity: ComplexityLevel, config: Config): string[] {
  const defaults = {
    simple: ['SOUL.md', 'IDENTITY.md'],
    standard: ['SOUL.md', 'IDENTITY.md', 'USER.md'],
    complex: ['SOUL.md', 'IDENTITY.md', 'USER.md', 'TOOLS.md', 'AGENTS.md', 'MEMORY.md', 'HEARTBEAT.md']
  };
  
  return config?.files?.[complexity] || defaults[complexity];
}
```

### 4.3 handler.ts

```typescript
// handler.ts - Main hook handler

import type { HookHandler } from "../../src/hooks/hooks.js";
import { classifyComplexity, getAllowedFiles, type ComplexityLevel } from './classifier.js';
import { readFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';

interface Config {
  files?: {
    simple?: string[];
    standard?: string[];
    complex?: string[];
  };
  enabled?: boolean;
  logLevel?: 'debug' | 'info' | 'warn';
}

function loadConfig(): Config {
  const configPath = join(dirname(__filename), 'config.json');
  if (existsSync(configPath)) {
    try {
      return JSON.parse(readFileSync(configPath, 'utf-8'));
    } catch (e) {
      console.error('[token-context] Failed to load config:', e);
    }
  }
  return { enabled: true };
}

const handler: HookHandler = async (event) => {
  // Only handle agent:bootstrap events
  if (event.type !== 'agent' || event.action !== 'bootstrap') {
    return;
  }

  const config = loadConfig();
  
  if (config.enabled === false) {
    console.log('[token-context] Hook disabled, skipping');
    return;
  }

  // Extract user message from context
  const message = extractUserMessage(event.context);
  
  if (!message) {
    console.log('[token-context] No user message found, using full context');
    return;
  }

  // Classify complexity
  const complexity = classifyComplexity(message);
  const allowedFiles = getAllowedFiles(complexity, config);
  
  // Get current bootstrap files
  const currentFiles = event.context.bootstrapFiles || [];
  const currentFileNames = currentFiles.map(f => f.name);
  
  if (config.logLevel === 'debug') {
    console.log(`[token-context] Message: "${message.substring(0, 50)}..."`);
    console.log(`[token-context] Complexity: ${complexity}`);
    console.log(`[token-context] Allowed files: ${allowedFiles.join(', ')}`);
    console.log(`[token-context] Current files: ${currentFileNames.join(', ')}`);
  }

  // Filter bootstrap files
  const filteredFiles = currentFiles.filter(f => 
    allowedFiles.includes(f.name)
  );

  // Log the filtering
  const removed = currentFileNames.filter(f => !allowedFiles.includes(f));
  if (removed.length > 0) {
    console.log(`[token-context] Removed ${removed.length} files: ${removed.join(', ')}`);
  }
  console.log(`[token-context] Context reduced: ${currentFileNames.length} → ${filteredFiles.length} files`);

  // Apply filtered list
  event.context.bootstrapFiles = filteredFiles;
};

function extractUserMessage(context: any): string | null {
  // Try to get message from session entry
  if (context?.sessionEntry?.messages?.length > 0) {
    const messages = context.sessionEntry.messages;
    // Get the last user message
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role === 'user') {
        return messages[i].content;
      }
    }
  }
  
  // Try alternative path
  if (context?.sessionEntry?.lastMessage) {
    return context.sessionEntry.lastMessage;
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
  "files": {
    "simple": ["SOUL.md", "IDENTITY.md"],
    "standard": ["SOUL.md", "IDENTITY.md", "USER.md"],
    "complex": ["SOUL.md", "IDENTITY.md", "USER.md", "TOOLS.md", "AGENTS.md", "MEMORY.md", "HEARTBEAT.md"]
  }
}
```

---

## 5. Error Handling

### Error Scenarios

| Scenario | Handling | Impact |
|----------|----------|--------|
| Config file missing | Use defaults | Minimal - uses built-in defaults |
| Config file corrupted | Log error, use defaults | Minimal - continues with defaults |
| No user message found | Skip filtering | Minimal - full context loaded |
| bootstrapFiles undefined | Initialize empty array | Graceful - no crash |
| Hook throws exception | Catch, log, re-throw | Could break bootstrap |

### Error Recovery

```typescript
try {
  // Main logic
} catch (error) {
  console.error('[token-context] Error:', error);
  // Don't modify bootstrapFiles on error - preserve full context
  // This is safer than filtering incorrectly
  throw error; // Re-throw to let OpenClaw handle
}
```

---

## 6. Testing Strategy

### Unit Tests (classifier.ts)

```typescript
// tests/classifier.test.ts

import { describe, it } from 'vitest';
import { classifyComplexity } from '../classifier';

describe('classifyComplexity', () => {
  it('classifies greetings as simple', () => {
    expect(classifyComplexity('hi')).toBe('simple');
    expect(classifyComplexity('hello')).toBe('simple');
    expect(classifyComplexity('hey there')).toBe('simple');
  });

  it('classifies acknowledgments as simple', () => {
    expect(classifyComplexity('thanks')).toBe('simple');
    expect(classifyComplexity('ok got it')).toBe('simple');
    expect(classifyComplexity('yes')).toBe('simple');
  });

  it('classifies code tasks as standard', () => {
    expect(classifyComplexity('write a function')).toBe('standard');
    expect(classifyComplexity('fix this bug')).toBe('standard');
  });

  it('classifies design tasks as complex', () => {
    expect(classifyComplexity('design a system')).toBe('complex');
    expect(classifyComplexity('architect a microservices')).toBe('complex');
  });
});
```

### Integration Tests

- Test hook with actual OpenClaw
- Verify bootstrapFiles is modified correctly
- Verify logging works

---

## 7. Dependencies

### Phase Dependencies

This phase has **no dependencies** - it's the foundation.

### External Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| OpenClaw | 2026.2+ | Hook system |
| TypeScript | 5.x | Hook implementation |
| Node.js | 18+ | Runtime |

---

## 8. Configuration Options

### User-Configurable Settings

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| enabled | boolean | true | Enable/disable hook |
| logLevel | string | "info" | debug, info, warn |
| files.simple | string[] | [SOUL.md, IDENTITY.md] | Files for simple messages |
| files.standard | string[] | [SOUL.md, IDENTITY.md, USER.md] | Files for standard messages |
| files.complex | string[] | [ALL] | Files for complex messages |

---

## 9. Logging

### Log Levels

| Level | When | Example |
|-------|------|---------|
| debug | Detailed filtering info | "Current files: SOUL.md, IDENTITY.md, TOOLS.md..." |
| info | Summary | "Context reduced: 7 → 2 files" |
| warn | Issues (non-critical) | "No user message found" |

### Log Output Format

```
[token-context] Message: "hi there how are you?"
[token-context] Complexity: simple
[token-context] Allowed files: SOUL.md, IDENTITY.md
[token-context] Current files: SOUL.md, IDENTITY.md, TOOLS.md, AGENTS.md, MEMORY.md
[token-context] Removed 3 files: TOOLS.md, AGENTS.md, MEMORY.md
[token-context] Context reduced: 7 → 2 files
```

---

## 10. Installation

### Steps

```bash
# 1. Copy hook to managed hooks directory
cp -r token-context ~/.openclaw/hooks/

# 2. Enable hooks in config (if not already)
openclaw configure --set "hooks.internal.enabled=true"

# 3. Enable the hook
openclaw hooks enable token-context

# 4. Restart gateway
openclaw gateway restart

# 5. Verify hook is loaded
openclaw hooks list
# Should show: 🎯 token-context ✓
```

---

## 11. Acceptance Criteria

### Functional Requirements

- [ ] Hook loads on OpenClaw startup
- [ ] Hook listens to `agent:bootstrap` event
- [ ] Message classification works for simple/standard/complex
- [ ] bootstrapFiles is correctly filtered
- [ ] Logging works at configured level

### Non-Functional Requirements

- [ ] Hook adds <10ms to bootstrap time
- [ ] No crashes on error conditions
- [ ] Memory usage <1MB

### Test Coverage

- [ ] Unit tests for classifier (10+ cases)
- [ ] Integration test with OpenClaw
- [ ] Error handling test

---

## 12. Future Enhancements (Post-v2.0)

| Enhancement | Description | Priority |
|-------------|-------------|----------|
| Learning | Remember user's preferences over time | Low |
| Multi-workspace | Different rules per workspace | Low |
| Plugin system | Allow custom classification rules | Medium |

---

## 13. References

- OpenClaw Hooks: `/automation/hooks.md`
- OpenClaw Context: `/concepts/context.md`
- Bootstrap Files: Workspace file injection

---

*This specification defines Phase 1 implementation. See IMPLEMENTATION_PLAN.md for phase dependencies.*
