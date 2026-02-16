# API Reference

## CLI API

The `tokenqrusher` command provides unified access to all tokenQrusher functionality.

### Exit Codes

| Code | Meaning | When |
|------|---------|------|
| 0 | Success | Command completed successfully |
| 1 | General Error | Unexpected error occurred |
| 2 | Invalid Arguments | Command usage error |
| 3 | Config Error | Configuration invalid or missing |
| 4 | Not Found | Required component unavailable |
| 5 | Budget Exceeded | Budget threshold exceeded (budget check) |

### Commands

#### `tokenqrusher context <prompt>`

Recommends context files for a given user prompt.

**Arguments:**

| Name | Required | Type | Description |
|------|----------|------|-------------|
| prompt | No | string | User prompt to analyze. Default: "hello" |

**Options:**

| Flag | Type | Description |
|------|------|-------------|
| `--files` | flag | Show files only, one per line |
| `--json` | flag | Output as JSON |

**Returns:** Stdout with complexity, file list, savings percentage.

**Exit Codes:** 0 on success, 2 on error.

**Example:**

```bash
$ tokenqrusher context "design a microservices architecture" --json
{
  "prompt": "design a microservices architecture",
  "complexity": "complex",
  "confidence": 0.9,
  "files": ["SOUL.md", "IDENTITY.md", "USER.md", "TOOLS.md", "AGENTS.md", "MEMORY.md", "HEARTBEAT.md"],
  "files_count": 7,
  "savings_percent": 0.0
}
```

---

#### `tokenqrusher model <prompt>`

Recommends AI model tier for a given user prompt.

**Arguments:**

| Name | Required | Type | Description |
|------|----------|------|-------------|
| prompt | No | string | User prompt to analyze. Default: "hello" |

**Options:**

| Flag | Type | Description |
|------|------|-------------|
| `--tier` | flag | Show tier only |
| `--json` | flag | Output as JSON |

**Returns:** Stdout with tier, model, cost info.

**Exit Codes:** 0 on success, 2 on error.

**Example:**

```bash
$ tokenqrusher model "fix this bug" --tier
quick

$ tokenqrusher model "fix this bug" --json
{
  "prompt": "fix this bug",
  "tier": "quick",
  "confidence": 0.85,
  "model": "openrouter/stepfun/step-3.5-flash:free",
  "cost": "$0.00/MT"
}
```

---

#### `tokenqrusher budget [--period daily|weekly|monthly]`

Checks current budget status.

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--period` | string | "daily" | Budget period to check |
| `--json` | flag | false | Output as JSON |
| `--warn` | float | env | Warning threshold (0-1) |
| `--quiet` | flag | false | Only non-zero exit on exceeded |

**Environment:** `TOKENQRUSHER_WARNING_THRESHOLD`

**Returns:** Budget status with emoji and numbers.

**Exit Codes:**
- 0: Healthy or warning (with `--quiet`, always returns 0)
- 1: Critical
- 2: Exceeded

**Example:**

```bash
$ tokenqrusher budget --period weekly
🟡 Budget: WARNING
   Period: weekly
   Spent: $22.50 / $30.00 (75%)
   Remaining: $7.50

# Exit code 1 for CRITICAL
```

---

#### `tokenqrusher usage [--days N]`

Shows usage statistics.

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--days` | int | 7 | Number of days to look back |
| `--json` | flag | false | Output as JSON |

**Returns:** Usage summary with cost and token counts.

**Exit Codes:** 0 on success, 3 on data error.

**Example:**

```bash
$ tokenqrusher usage --days 30
=== Usage (30 days) ===
Records: 142
Cost: $87.65
Input: 1,254,320 tokens
Output: 987,450 tokens
```

---

#### `tokenqrusher optimize [--dry-run]`

Runs optimization analysis.

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--dry-run` | flag | false | Show actions without applying |
| `--json` | flag | false | Output as JSON |

**Implementation:** `scripts/cron-optimizer/optimizer.py`

**Returns:** Optimization result with actions taken.

**Exit Codes:** 0 on success or skipped, 1 on failure.

**Example:**

```bash
$ tokenqrusher optimize --json
{
  "result": "SUCCESS",
  "actions_taken": [
    {
      "action_type": "recommend_quick_tier",
      "priority": 80,
      "reason": "Critical budget warning (daily, 96%)",
      "expected_savings": 1.23,
      "parameters": {
        "period": "daily",
        "velocity_daily": 12.5
      }
    }
  ],
  "duration_ms": 145.2,
  "timestamp": "2024-01-15T14:30:45.123456"
}
```

---

#### `tokenqrusher status [--verbose]`

Shows full system status.

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `-v, --verbose` | flag | false | Show detailed info |
| `--json` | flag | false | Output as JSON |

**Returns:** Comprehensive status of all components.

**Exit Codes:** 0 on success.

**Example:**

```bash
$ tokenqrusher status -v
=== tokenQrusher Status ===

Hooks:
  ✓ token-context   (Filters context)
  ✓ token-model     (Routes models)
  ✓ token-usage     (Tracks budgets)
  ✓ token-cron      (Runs optimization)
  ✓ token-heartbeat (Optimizes heartbeat)

Optimizer:
  State: IDLE
  Enabled: True
  Quiet hours: False
  Last run: 2024-01-15T13:00:00
  Consecutive failures: 0
  Config hash: abc123def456

Heartbeat:
  Checks due: 2/4
  Quiet hours active: False
  Intervals:
    email: 7200s
    calendar: 14400s
    weather: 14400s
    monitoring: 7200s

Budgets:
  daily: $5.0
  weekly: $30.0
  monthly: $100.0
```

---

#### `tokenqrusher install [--hooks] [--cron] [--all]`

Installs hooks and cron jobs.

**Options:**

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--hooks` | flag | false | Enable all hooks |
| `--cron` | flag | false | Install cron jobs |
| `--all` | flag | false | Enable hooks AND cron |
| `--dry-run` | flag | false | Show what would be done |

**Returns:** Installation status.

**Exit Codes:** 0 on success, 1 on partial failure.

**Example:**

```bash
$ tokenqrusher install --all --dry-run
Would do:
  - Enable: token-context
  - Enable: token-model
  - Enable: token-usage
  - Enable: token-cron
  - Enable: token-heartbeat
```

---

## Python API

For advanced usage, the modules can be imported:

### `scripts.usage.tracker.UsageTracker`

```python
from pathlib import Path
from tokenqrusher.scripts.usage.tracker import UsageTracker, UsageRecord

tracker = UsageTracker(state_dir=Path.home() / '.openclaw/workspace/memory')

# Add record
record = UsageRecord(
    timestamp=datetime.now().isoformat(),
    cost=0.45,
    input_tokens=1200,
    output_tokens=800,
    model='anthropic/claude-haiku-4'
)
result = tracker.add_record(record)

# Get daily cost
daily = tracker.get_daily_usage(1)
print(f"Today: ${daily.total_cost:.2f}")

# Prune old data
pruned = tracker.prune_old_records(keep_days=30)
```

### `scripts.cron_optimizer.optimizer.CronOptimizer`

```python
from tokenqrusher.scripts.cron_optimizer import CronOptimizer, TriggerReason

optimizer = CronOptimizer()

# Run optimization
result = optimizer.optimize(trigger=TriggerReason.MANUAL)

print(f"Result: {result.result.name}")
print(f"Actions: {len(result.actions_taken)}")
print(f"Duration: {result.duration_ms}ms")

# Get status
status = optimizer.get_status()
print(f"State: {status['state']}")
```

### `scripts.heartbeat_optimizer.optimizer.HeartbeatOptimizer`

```python
from tokenqrusher.scripts.heartbeat_optimizer import HeartbeatOptimizer, CheckType

hb = HeartbeatOptimizer()

# Check which checks should run
for check_type in CheckType:
    should_run, reason = hb.should_check(check_type)
    print(f"{check_type.value}: {should_run} ({reason})")

# Record check result
hb.record_check(CheckType.EMAIL, had_alerts=False)

# Get status
status = hb.get_status()
print(f"Checks due: {status['total_checks_due']}/4")
```

---

## JavaScript API

### `hooks/token-shared/shared.js`

```javascript
const shared = require('../token-shared/shared');

// Pure functions (no side effects)
const complexity = shared.classifyComplexity("hi");
// → { level: 'simple', confidence: 0.95, reasoning: '...' }

const files = shared.getAllowedFiles('standard');
// → ['SOUL.md', 'IDENTITY.md', 'USER.md']

const isValid = shared.isValidFileName('../../../etc/passwd');
// → false (path traversal blocked)

const msgResult = shared.extractUserMessage(context);
if (msgResult.isJust) {
    const message = msgResult.value;
}

// Maybe pattern
const nothing = shared.Nothing();
const just = shared.Just('hello');

if (nothing.isJust) { /* unreachable */ }

// Either pattern
const right = shared.Right(42);
const left = shared.Left('error');

const doubled = shared.mapRight(x => x * 2, right);
// → Right(84)
```

---

## Configuration Schema

### Hook Config (`config.json`)

All hooks accept:

```json
{
  "enabled": true,
  "logLevel": "info"  // "debug" | "info" | "warn"
}
```

### Hook-Specific Configs

**token-context:**
```json
{
  "files": {
    "simple": ["SOUL.md", "IDENTITY.md"],
    "standard": ["SOUL.md", "IDENTITY.md", "USER.md"],
    "complex": ["SOUL.md", ...]
  },
  "dryRun": false
}
```

**token-model:**
```json
{
  "models": {
    "quick": "openrouter/stepfun/step-3.5-flash:free",
    "standard": "anthropic/claude-haiku-4",
    "deep": "openrouter/minimax/minimax-m2.5"
  },
  "logToSession": false
}
```

**token-usage:**
```json
{
  "budgets": {
    "daily": 5.0,
    "weekly": 30.0,
    "monthly": 100.0
  },
  "warningThreshold": 0.8,
  "criticalThreshold": 0.95
}
```

**token-cron:**
```json
{
  "runOnStartup": true,
  "optimizeOnStartup": true,
  "checkBudgetOnStartup": true,
  "quietHours": { "start": 23, "end": 8 }
}
```

**token-heartbeat:**
```json
{
  "intervals": {
    "email": 7200,
    "calendar": 14400,
    "weather": 14400,
    "monitoring": 7200
  },
  "quietHours": { "start": 23, "end": 8 }
}
```

---

## Constants Reference

### Compile-Time Constants (JavaScript)

```javascript
shared.MAX_FILE_NAME_LENGTH      // 255
shared.CONFIG_CACHE_TTL_MS       // 60000 (60s)
shared.MAX_LOG_MESSAGE_LENGTH    // 500
shared.VALID_FILE_NAME_PATTERN   // /^[a-zA-Z0-9._-]+$/
shared.ALLOWED_EXTENSIONS        // ['.md', '.json', '.txt', ...]
```

### Python Constants

```python
from tokenqrusher.scripts.cron_optimizer import ModelTier

ModelTier.QUICK.cost_per_million      # 0.0
ModelTier.STANDARD.cost_per_million  # 0.25
ModelTier.DEEP.cost_per_million      # 0.60
```

---

## Error Handling

### Python Result Type

All Python modules use `Result` type instead of exceptions:

```python
from tokenqrusher.scripts.usage.tracker import Result

result = tracker.add_record(record)

if result.is_success:
    print("Added")
elif result.is_error:
    print(f"Error: {result.error}")
```

### JavaScript Maybe/Either

```javascript
const result = shared.extractUserMessage(context);

if (result.isJust) {
    const message = result.value;
    // use message
} else {
    // no message found
}
```

---

## Type Signatures

### Python Type Hints

```python
def classifyComplexity(message: str) -> ClassificationResult:
    """
    Args:
        message: User message to classify
    
    Returns:
        ClassificationResult: { level, confidence, reasoning }
    
    Postcondition:
        0.0 <= result.confidence <= 1.0
        result.level in {'simple', 'standard', 'complex'}
    """
```

### JavaScript JSDoc

```javascript
/**
 * Validates file name is safe
 * @param {string} name
 * @returns {boolean}
 * @post returns === true iff name matches pattern and length <= 255
 */
function isValidFileName(name) { ... }
```

---

## Logging Format

All log lines follow format:

```
[<module>] <LEVEL>: <message>
```

Examples:

```
[token-context] Entry: handler
[token-context] ✓ 2 files (simple)
[token-context] Exit: success
[usage-tracker] INFO: Loaded 127 records
[budget-checker] WARNING: Budget at 87%
```

## Performance Contract

| Operation | Max Latency | Max Memory | Thread-Safe |
|-----------|-------------|------------|-------------|
| context classify | 1ms | 1MB | ✅ |
| model classify | 1ms | 1MB | ✅ |
| budget check | 10ms | 2MB | ✅ |
| optimization run | 500ms | 10MB | ✅ |
| heartbeat check | 0.5ms | 0.5MB | ✅ |

---

## Versioning

Follows Semantic Versioning:

- **MAJOR**: Breaking changes to API
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, documentation

Current: **2.0.0**
