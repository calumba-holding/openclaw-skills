# Phase 3: Usage Integration Specification

**Phase:** 3 of 8  
**Title:** Usage Tracking Integration  
**Objective:** Connect to OpenClaw's built-in usage tracking and implement budget alerts  
**Status:** Draft  
**Dependencies:** Phase 1, Phase 2

---

## 1. Overview

### Purpose

This phase integrates with OpenClaw's **built-in usage tracking** to provide real cost monitoring and budget alerts. Instead of the stub function in v1, we'll leverage what OpenClaw already provides.

### Why This Phase After 1 & 2

- Phase 1: Reduces tokens by filtering context
- Phase 2: Reduces cost by selecting cheaper models
- Phase 3: **Tracks** the savings to prove it works

You can't optimize what you don't measure. This phase provides the measurement.

### Expected Capabilities

| Capability | Description |
|------------|-------------|
| Real-time cost tracking | Show cost per day/week/month |
| Budget alerts | Warn when approaching limit |
| Historical analysis | Compare before/after optimization |
| Model breakdown | Cost per model |

---

## 2. Technical Analysis

### OpenClaw Usage Tracking

From research of `/concepts/usage-tracking.md`:

**Usage Sources:**
- `/status` in chat: Session tokens + estimated cost
- `/usage cost` in chat: Local cost summary
- CLI: `openclaw status --usage`

**Provider Support:**
- Anthropic (Claude): OAuth tokens
- OpenAI: API key
- MiniMax: API key
- OpenRouter: API key

**What It Tracks:**
- Input tokens
- Output tokens
- Total tokens
- Cost (provider-reported)

### Integration Methods

| Method | Pros | Cons |
|--------|------|------|
| CLI `openclaw status --usage` | Easy, reliable | Requires shell |
| Chat command `/usage cost` | Integrated | Requires session |
| Direct file read | Fast | May miss updates |
| Webhook | Real-time | Complex setup |

**Chosen Approach:** CLI-based for reliability, with file-based caching.

---

## 3. Architecture

### File Structure

```
tokenQrusher/
├── scripts/
│   ├── usage_monitor.py     # Main usage tracking
│   ├── budget_checker.py    # Budget monitoring
│   └── cost_analyzer.py     # Historical analysis
├── hooks/
│   └── token-usage/         # Optional hook for session end
│       ├── HOOK.md
│       └── handler.ts
└── config/
    └── budgets.json         # Budget configurations
```

### Component Design

```
┌─────────────────────────────────────────────────────────────┐
│                  Usage Monitoring System                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐                                        │
│  │ Usage Monitor   │  Polls openclaw status                 │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐     ┌─────────────────┐               │
│  │ Cost Calculator │────▶│ Budget Checker   │               │
│  └────────┬────────┘     └────────┬────────┘               │
│           │                        │                        │
│           ▼                        ▼                        │
│  ┌─────────────────┐     ┌─────────────────┐               │
│  │ History Store    │     │ Alert Manager   │               │
│  │ (JSON file)     │     │ (notify user)   │               │
│  └─────────────────┘     └─────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Details

### 4.1 usage_monitor.py

```python
#!/usr/bin/env python3
"""
Usage Monitor - Tracks OpenClaw token usage and costs
"""
import json
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Paths
STATE_DIR = Path.home() / ".openclaw/workspace/memory"
STATE_FILE = STATE_DIR / "usage-history.json"

# Default budgets
DEFAULT_BUDGETS = {
    "daily": 5.0,      # $5/day
    "weekly": 30.0,    # $30/week
    "monthly": 100.0   # $100/month
}

class UsageMonitor:
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load usage history from file"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        
        return {
            "history": [],
            "budgets": DEFAULT_BUDGETS.copy(),
            "last_updated": None,
            "alerts_sent": []
        }
    
    def _save_state(self):
        """Save usage history to file"""
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        self.state["last_updated"] = datetime.now().isoformat()
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def get_current_usage(self) -> dict:
        """Get current usage from OpenClaw"""
        try:
            result = subprocess.run(
                ["openclaw", "status", "--usage"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {"error": result.stderr, "providers": {}}
            
            # Parse output
            # Format: provider -> {input, output, total, cost}
            return self._parse_usage_output(result.stdout)
            
        except subprocess.TimeoutExpired:
            return {"error": "Timeout", "providers": {}}
        except FileNotFoundError:
            return {"error": "OpenClaw not found", "providers": {}}
    
    def _parse_usage_output(self, output: str) -> dict:
        """Parse openclaw status --usage output"""
        providers = {}
        current_provider = None
        total_cost = 0.0
        total_tokens = 0
        
        for line in output.split('\n'):
            line = line.strip()
            
            # Look for provider sections
            if ':' in line and not line.startswith(' '):
                provider_name = line.rstrip(':')
                current_provider = provider_name
                providers[provider_name] = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "cost": 0.0
                }
            
            # Parse metrics
            if current_provider:
                if 'input' in line.lower() and 'tokens' in line.lower():
                    # Extract number
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'tokens' in part.lower() and i > 0:
                            try:
                                providers[current_provider]["input_tokens"] = int(parts[i-1].replace(',', ''))
                            except (ValueError, IndexError):
                                pass
                
                elif 'output' in line.lower() and 'tokens' in line.lower():
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if 'tokens' in part.lower() and i > 0:
                            try:
                                providers[current_provider]["output_tokens"] = int(parts[i-1].replace(',', ''))
                            except (ValueError, IndexError):
                                pass
                
                elif 'cost' in line.lower() or '$' in line:
                    # Extract cost
                    import re
                    match = re.search(r'\$?([\d,]+\.?\d*)', line)
                    if match:
                        try:
                            cost = float(match.group(1).replace(',', ''))
                            providers[current_provider]["cost"] = cost
                            total_cost += cost
                        except ValueError:
                            pass
        
        return {
            "providers": providers,
            "total_cost": total_cost,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_usage(self):
        """Record current usage to history"""
        usage = self.get_current_usage()
        
        if "error" in usage:
            print(f"Error getting usage: {usage['error']}")
            return
        
        # Add to history
        self.state["history"].append({
            "timestamp": usage["timestamp"],
            "total_cost": usage["total_cost"],
            "providers": usage["providers"]
        })
        
        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        self.state["history"] = [
            h for h in self.state["history"]
            if datetime.fromisoformat(h["timestamp"]) > cutoff
        ]
        
        self._save_state()
        return usage
    
    def get_daily_usage(self) -> dict:
        """Get today's usage"""
        today = datetime.now().date()
        today_total = 0.0
        today_providers = {}
        
        for entry in self.state["history"]:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            if entry_date == today:
                today_total += entry["total_cost"]
                for provider, data in entry.get("providers", {}).items():
                    if provider not in today_providers:
                        today_providers[provider] = {"cost": 0.0, "tokens": 0}
                    today_providers[provider]["cost"] += data.get("cost", 0)
        
        return {
            "date": today.isoformat(),
            "cost": today_total,
            "providers": today_providers
        }
    
    def get_weekly_usage(self) -> dict:
        """Get this week's usage"""
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_total = 0.0
        
        for entry in self.state["history"]:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            if entry_date >= week_start:
                week_total += entry["total_cost"]
        
        return {
            "week_start": week_start.isoformat(),
            "cost": week_total,
            "budget": self.state["budgets"].get("weekly", 30.0),
            "percent_used": (week_total / self.state["budgets"].get("weekly", 30.0)) * 100
        }


def main():
    import sys
    
    monitor = UsageMonitor()
    
    if len(sys.argv) < 2:
        print("Usage: usage_monitor.py [record|daily|weekly|budget]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "record":
        result = monitor.record_usage()
        if result:
            print(json.dumps(result, indent=2))
    
    elif command == "daily":
        result = monitor.get_daily_usage()
        print(json.dumps(result, indent=2))
    
    elif command == "weekly":
        result = monitor.get_weekly_usage()
        print(json.dumps(result, indent=2))
    
    elif command == "budget":
        budgets = monitor.state["budgets"]
        print(json.dumps(budgets, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 4.2 budget_checker.py

```python
#!/usr/bin/env python3
"""
Budget Checker - Monitors budgets and sends alerts
"""
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

STATE_FILE = Path.home() / ".openclaw/workspace/memory/usage-history.json"

# Thresholds
WARNING_THRESHOLD = 0.8  # 80% of budget
CRITICAL_THRESHOLD = 0.95  # 95% of budget

class BudgetChecker:
    def __init__(self, budgets: Dict[str, float] = None):
        self.budgets = budgets or {
            "daily": 5.0,
            "weekly": 30.0,
            "monthly": 100.0
        }
    
    def check_budget(self) -> dict:
        """Check current budget status"""
        # Get today's usage
        result = subprocess.run(
            ["python3", "-c", """
import json
import sys
sys.path.append('~/.openclaw/workspace/skills/tokenQrusher/scripts')
from usage_monitor import UsageMonitor
m = UsageMonitor()
print(json.dumps(m.get_daily_usage()))
"""],
            capture_output=True,
            text=True,
            cwd=str(Path.home() / ".openclaw/workspace/skills/tokenQrusher")
        )
        
        try:
            daily = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"error": "Failed to get usage"}
        
        daily_cost = daily.get("cost", 0)
        daily_limit = self.budgets.get("daily", 5.0)
        daily_percent = (daily_cost / daily_limit) * 100 if daily_limit > 0 else 0
        
        status = "ok"
        alert = None
        
        if daily_percent >= CRITICAL_THRESHOLD * 100:
            status = "critical"
            alert = f"🚨 Daily budget EXCEEDED: ${daily_cost:.2f}/${daily_limit:.2f}"
        elif daily_percent >= WARNING_THRESHOLD * 100:
            status = "warning"
            alert = f"⚠️ Daily budget warning: ${daily_cost:.2f}/${daily_limit:.2f} ({daily_percent:.0f}%)"
        
        return {
            "status": status,
            "alert": alert,
            "cost": daily_cost,
            "limit": daily_limit,
            "percent": daily_percent,
            "timestamp": datetime.now().isoformat()
        }
    
    def auto_downgrade(self) -> dict:
        """
        Automatically downgrade model when budget exceeded.
        Returns the action taken.
        """
        budget = self.check_budget()
        
        if budget.get("status") != "critical":
            return {"action": "none", "reason": "budget_ok"}
        
        # Switch to cheapest model
        config_path = Path.home() / ".openclaw/openclaw.json"
        
        if not config_path.exists():
            return {"action": "error", "reason": "config_not_found"}
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError:
            return {"action": "error", "reason": "config_corrupted"}
        
        # Change to free model
        if "agents" not in config:
            config["agents"] = {}
        if "defaults" not in config["agents"]:
            config["agents"]["defaults"] = {}
        if "model" not in config["agents"]["defaults"]:
            config["agents"]["defaults"]["model"] = {}
        
        old_model = config["agents"]["defaults"].get("model", {}).get("primary", "unknown")
        config["agents"]["defaults"]["model"]["primary"] = "openrouter/stepfun/step-3.5-flash:free"
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        return {
            "action": "model_downgraded",
            "old_model": old_model,
            "new_model": "openrouter/stepfun/step-3.5-flash:free",
            "reason": "budget_exceeded"
        }


def main():
    import sys
    
    checker = BudgetChecker()
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        result = checker.auto_downgrade()
        print(json.dumps(result, indent=2))
    else:
        result = checker.check_budget()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

### 4.3 cost_analyzer.py

```python
#!/usr/bin/env python3
"""
Cost Analyzer - Historical analysis and reporting
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

STATE_FILE = Path.home() / ".openclaw/workspace/memory/usage-history.json"

class CostAnalyzer:
    def __init__(self):
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {"history": [], "budgets": {}}
    
    def get_daily_breakdown(self, days: int = 7) -> dict:
        """Get daily cost breakdown for last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        daily = {}
        
        for entry in self.state["history"]:
            entry_date = datetime.fromisoformat(entry["timestamp"]).date()
            if entry_date >= cutoff.date():
                date_str = entry_date.isoformat()
                if date_str not in daily:
                    daily[date_str] = {"cost": 0.0, "providers": {}}
                
                daily[date_str]["cost"] += entry.get("total_cost", 0)
                
                for provider, data in entry.get("providers", {}).items():
                    if provider not in daily[date_str]["providers"]:
                        daily[date_str]["providers"][provider] = 0.0
                    daily[date_str]["providers"][provider] += data.get("cost", 0)
        
        return daily
    
    def get_provider_breakdown(self, days: int = 30) -> dict:
        """Get cost breakdown by provider"""
        cutoff = datetime.now() - timedelta(days=days)
        providers = {}
        
        for entry in self.state["history"]:
            if datetime.fromisoformat(entry["timestamp"]) > cutoff:
                for provider, data in entry.get("providers", {}).items():
                    if provider not in providers:
                        providers[provider] = {"cost": 0.0, "input": 0, "output": 0}
                    
                    providers[provider]["cost"] += data.get("cost", 0)
                    providers[provider]["input"] += data.get("input_tokens", 0)
                    providers[provider]["output"] += data.get("output_tokens", 0)
        
        return providers
    
    def compare_periods(self, days1: int = 7, days2: int = 7) -> dict:
        """Compare two periods for optimization tracking"""
        now = datetime.now()
        
        # Period 1 (most recent)
        cutoff1 = now - timedelta(days=days1)
        period1_cost = 0.0
        for entry in self.state["history"]:
            if datetime.fromisoformat(entry["timestamp"]) > cutoff1:
                period1_cost += entry.get("total_cost", 0)
        
        # Period 2 (previous)
        cutoff2 = cutoff1 - timedelta(days=days2)
        period2_cost = 0.0
        for entry in self.state["history"]:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if cutoff2 < entry_time <= cutoff1:
                period2_cost += entry.get("total_cost", 0)
        
        savings = period2_cost - period1_cost
        savings_percent = (savings / period2_cost * 100) if period2_cost > 0 else 0
        
        return {
            "period1": {"days": days1, "cost": period1_cost},
            "period2": {"days": days2, "cost": period2_cost},
            "savings": savings,
            "savings_percent": savings_percent
        }
    
    def generate_report(self) -> str:
        """Generate human-readable report"""
        daily = self.get_daily_breakdown(7)
        providers = self.get_provider_breakdown(30)
        
        total_7day = sum(d["cost"] for d in daily.values())
        total_30day = sum(p["cost"] for p in providers.values())
        
        report = f"""
📊 Token Usage Report
=====================

Last 7 Days: ${total_7day:.2f}
Last 30 Days: ${total_30day:.2f}

Daily Breakdown:
"""
        for date, data in sorted(daily.items()):
            report += f"  {date}: ${data['cost']:.2f}\n"
        
        report += "\nProvider Breakdown (30 days):\n"
        for provider, data in sorted(providers.items(), key=lambda x: x[1]["cost"], reverse=True):
            report += f"  {provider}: ${data['cost']:.2f}\n"
        
        return report


def main():
    import sys
    
    analyzer = CostAnalyzer()
    
    if len(sys.argv) < 2:
        print(analyzer.generate_report())
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "daily":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print(json.dumps(analyzer.get_daily_breakdown(days), indent=2))
    
    elif command == "providers":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        print(json.dumps(analyzer.get_provider_breakdown(days), indent=2))
    
    elif command == "compare":
        print(json.dumps(analyzer.compare_periods(), indent=2))
    
    elif command == "report":
        print(analyzer.generate_report())
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## 5. Hook: Session End Tracker

Optionally track usage after each session:

```typescript
// hooks/token-usage/handler.ts
import type { HookHandler } from "../../src/hooks/hooks.js";

const handler: HookHandler = async (event) => {
  // This would require session:end event which may not exist yet
  // Placeholder for future implementation
  console.log('[token-usage] Session ended, usage tracked');
};

export default handler;
```

---

## 6. Integration with Phases 1 & 2

### Context Hook Integration

After Phase 1 runs, record the context reduction:

```python
# Add to usage_monitor.py
context_reduction = {
    "simple": {"before": 50000, "after": 500, "saved": 49500},
    "standard": {"before": 50000, "after": 5000, "saved": 45000},
}
```

### Model Hook Integration

Track which models were used:

```python
# Add to usage_monitor.py
model_usage = {
    "quick": 0,
    "standard": 0,
    "deep": 0
}
```

---

## 7. Error Handling

| Scenario | Handling |
|----------|----------|
| OpenClaw not installed | Show error, continue with $0 |
| `openclaw status` fails | Log error, use cached data |
| State file corrupted | Reset state, start fresh |
| Budget exceeded | Send alert, optionally downgrade |

---

## 8. Testing Strategy

### Unit Tests

- Test parsing of usage output
- Test budget calculation
- Test alert thresholds

### Integration Tests

- Test CLI integration
- Test with real OpenClaw

---

## 9. Dependencies

### Phase Dependencies

| Dependency | Purpose |
|------------|---------|
| Phase 1 | Context hook provides reduction metrics |
| Phase 2 | Model hook provides tier info |

### External Dependencies

| Dependency | Purpose |
|------------|---------|
| OpenClaw CLI | Get usage data |
| Python 3.7+ | Script runtime |

---

## 10. Configuration Options

### Environment Variables (Primary)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| TOKENQRUSHER_BUDGET_DAILY | float | 5.0 | Daily budget ($) |
| TOKENQRUSHER_BUDGET_WEEKLY | float | 30.0 | Weekly budget ($) |
| TOKENQRUSHER_BUDGET_MONTHLY | float | 100.0 | Monthly budget ($) |
| TOKENQRUSHER_WARNING_THRESHOLD | float | 0.8 | Alert at 80% |
| TOKENQRUSHER_CRITICAL_THRESHOLD | float | 0.95 | Critical at 95% |
| TOKENQRUSHER_AUTO_DOWNGRADE | bool | true | Auto-switch to cheap model |

### Usage

```bash
# Set custom budgets
export TOKENQRUSHER_BUDGET_DAILY=10.0
export TOKENQRUSHER_BUDGET_WEEKLY=50.0
export TOKENQRUSHER_BUDGET_MONTHLY=200.0

# Disable auto-downgrade
export TOKENQRUSHER_AUTO_DOWNGRADE=false

# In Docker
# docker run -e TOKENQRUSHER_BUDGET_DAILY=10.0 ...
```

### Configuration Code

```python
import os
from typing import Optional

class BudgetConfig:
    """Budget configuration with env var support"""
    
    def __init__(self):
        self.daily = self._get_budget('daily', 5.0)
        self.weekly = self._get_budget('weekly', 30.0)
        self.monthly = self._get_budget('monthly', 100.0)
        self.warning_threshold = self._get_float(
            'WARNING_THRESHOLD', 0.8
        )
        self.critical_threshold = self._get_float(
            'CRITICAL_THRESHOLD', 0.95
        )
        self.auto_downgrade = self._get_bool(
            'AUTO_DOWNGRADE', True
        )
    
    def _get_budget(self, key: str, default: float) -> float:
        """Get budget from env var"""
        env_key = f"TOKENQRUSHER_BUDGET_{key.upper()}"
        return self._get_float(env_key, default)
    
    def _get_float(self, key: str, default: float) -> float:
        """Get float from env var"""
        value = os.environ.get(f"TOKENQRUSHER_{key}")
        if value:
            try:
                return float(value)
            except ValueError:
                pass
        return default
    
    def _get_bool(self, key: str, default: bool) -> bool:
        """Get bool from env var"""
        value = os.environ.get(f"TOKENQRUSHER_{key}")
        if value:
            return value.lower() in ('true', '1', 'yes')
        return default

# Usage
config = BudgetConfig()
print(config.daily)   # 5.0 (or env value)
```

---

## 11. Acceptance Criteria

### Functional Requirements

- [ ] Get current usage from OpenClaw
- [ ] Calculate daily/weekly/monthly costs
- [ ] Check budgets and generate alerts
- [ ] Auto-downgrade on budget exceeded
- [ ] Generate historical reports

### Non-Functional Requirements

- [ ] Works offline (cached data)
- [ ] Fast (<1s to check budget)
- [ ] Reliable (handles errors gracefully)

---

## 12. References

- OpenClaw Usage: `/concepts/usage-tracking.md`
- OpenClaw Status: CLI reference

---

*This specification defines Phase 3 implementation. See IMPLEMENTATION_PLAN.md for phase dependencies.*
