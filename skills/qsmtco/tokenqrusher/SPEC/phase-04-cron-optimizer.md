# Phase 4: Cron Optimizer Specification

**Phase:** 4 of 8  
**Title:** Periodic Optimization Engine  
**Objective:** Create cron-based automation that periodically analyzes usage and auto-tunes settings  
**Status:** Draft  
**Dependencies:** Phase 1, Phase 2, Phase 3

---

## 1. Overview

### Purpose

This phase creates a **Periodic Optimization Engine** - a system of cron jobs that runs in the background to continuously analyze usage patterns and automatically tune OpenClaw settings for better cost efficiency.

### Why This Phase After 1, 2, & 3

- Phase 1: Reduces context (static filtering)
- Phase 2: Reduces model cost (static routing)
- Phase 3: **Tracks** savings (measurement)
- Phase 4: **Optimizes continuously** (automation)

The optimizer learns from Phase 3's tracking data and adjusts settings automatically.

### Expected Capabilities

| Capability | Description |
|------------|-------------|
| Auto-tuning | Adjust configs based on usage patterns |
| Scheduling | Run optimization on schedule |
| Alerts | Notify when issues detected |
| Reporting | Periodic cost reports |

---

## 2. Technical Analysis

### OpenClaw Cron System

From research of `/automation/cron-jobs.md`:

**Cron Job Types:**
- **Main session**: System event, runs on next heartbeat
- **Isolated**: Dedicated agent turn, own session

**Schedule Types:**
- `at`: One-shot at specific time
- `every`: Recurring interval
- `cron`: Standard cron expression

**Job Storage:**
- `~/.openclaw/cron/jobs.json`

### Optimization Triggers

| Trigger | Action |
|---------|--------|
| High cost today | Switch to cheaper model |
| Many simple tasks | Increase quick model usage |
| Low usage | Reduce heartbeat frequency |
| High context | Enable stricter filtering |

---

## 3. Architecture

### File Structure

```
tokenQrusher/
├── scripts/
│   ├── optimizer/
│   │   ├── __init__.py
│   │   ├── analyzer.py         # Usage pattern analysis
│   │   ├── tuner.py            # Auto-tuning logic
│   │   ├── scheduler.py        # Cron job management
│   │   └── reporter.py         # Report generation
│   └── run_optimizer.py        # Main entry point
├── cron/
│   └── optimizer.yaml          # Cron job definitions
└── templates/
    └── optimizer-report.md     # Report template
```

### Component Design

```
┌─────────────────────────────────────────────────────────────┐
│                  Periodic Optimization Engine                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Cron Scheduler                       │   │
│  │   Runs: hourly, daily, weekly                         │   │
│  └───────────────────────┬─────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Analyzer                           │   │
│  │   - Usage patterns                                   │   │
│  │   - Cost trends                                      │   │
│  │   - Optimization opportunities                        │   │
│  └───────────────────────┬─────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                     Tuner                             │   │
│  │   - Model rotation                                   │   │
│  │   - Context filtering                                │   │
│  │   - Heartbeat intervals                              │   │
│  └───────────────────────┬─────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Reporter                          │   │
│  │   - Generate reports                                 │   │
│  │   - Send notifications                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Implementation Details

### 4.1 analyzer.py

```python
#!/usr/bin/env python3
"""
Usage Pattern Analyzer - Analyzes usage data to find optimization opportunities
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

STATE_FILE = Path.home() / ".openclaw/workspace/memory/usage-history.json"

class UsageAnalyzer:
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
    
    def analyze_task_distribution(self, days: int = 7) -> dict:
        """
        Analyze distribution of task types
        Returns: {simple: %, standard: %, complex: %}
        """
        # This would need to track task types from context/model hooks
        # Placeholder implementation
        return {
            "simple": 60,    # 60% simple
            "standard": 30,  # 30% standard
            "complex": 10    # 10% complex
        }
    
    def analyze_cost_trend(self, days: int = 7) -> dict:
        """Analyze cost trend over time"""
        cutoff = datetime.now() - timedelta(days=days)
        daily_costs = defaultdict(float)
        
        for entry in self.state["history"]:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if entry_time > cutoff:
                date = entry_time.date().isoformat()
                daily_costs[date] += entry.get("total_cost", 0)
        
        if not daily_costs:
            return {"trend": "unknown", "change_percent": 0}
        
        dates = sorted(daily_costs.keys())
        if len(dates) < 2:
            return {"trend": "insufficient_data", "daily_avg": sum(daily_costs.values()) / len(daily_costs)}
        
        # Compare first half to second half
        mid = len(dates) // 2
        first_half = sum(daily_costs[d] for d in dates[:mid]) / mid if mid > 0 else 0
        second_half = sum(daily_costs[d] for d in dates[mid:]) / (len(dates) - mid) if len(dates) - mid > 0 else 0
        
        if first_half == 0:
            change = 100 if second_half > 0 else 0
        else:
            change = ((second_half - first_half) / first_half) * 100
        
        trend = "increasing" if change > 10 else "decreasing" if change < -10 else "stable"
        
        return {
            "trend": trend,
            "change_percent": change,
            "daily_avg": sum(daily_costs.values()) / len(daily_costs),
            "daily_costs": dict(daily_costs)
        }
    
    def analyze_model_usage(self, days: int = 7) -> dict:
        """Analyze which models are being used"""
        # This would come from Phase 2 tracking
        # Placeholder
        return {
            "quick": {"requests": 100, "cost": 0},
            "standard": {"requests": 50, "cost": 0.5},
            "deep": {"requests": 10, "cost": 2.0}
        }
    
    def find_optimization_opportunities(self) -> List[dict]:
        """Find specific optimization opportunities"""
        opportunities = []
        
        # Analyze cost trend
        cost_trend = self.analyze_cost_trend(7)
        if cost_trend.get("trend") == "increasing":
            opportunities.append({
                "type": "cost_increasing",
                "severity": "high",
                "message": "Costs are trending upward",
                "recommendation": "Review model usage and enable stricter optimization"
            })
        
        # Analyze task distribution
        task_dist = self.analyze_task_distribution(7)
        if task_dist.get("simple", 0) > 70:
            opportunities.append({
                "type": "too_much_standard",
                "severity": "medium",
                "message": f"{task_dist['simple']}% of tasks are simple but using standard model",
                "recommendation": "Increase quick model usage for simple tasks"
            })
        
        # Check daily budget
        today = datetime.now().date().isoformat()
        today_cost = 0
        for entry in self.state["history"]:
            if entry["timestamp"].startswith(today):
                today_cost += entry.get("total_cost", 0)
        
        daily_budget = self.state.get("budgets", {}).get("daily", 5.0)
        if today_cost > daily_budget * 0.8:
            opportunities.append({
                "type": "budget_warning",
                "severity": "high" if today_cost > daily_budget else "medium",
                "message": f"${today_cost:.2f} spent today (${daily_budget} budget)",
                "recommendation": "Consider downgrading to free model"
            })
        
        return opportunities
    
    def get_summary(self) -> dict:
        """Get complete analysis summary"""
        return {
            "task_distribution": self.analyze_task_distribution(7),
            "cost_trend": self.analyze_cost_trend(7),
            "model_usage": self.analyze_model_usage(7),
            "opportunities": self.find_optimization_opportunities()
        }


def main():
    import sys
    
    analyzer = UsageAnalyzer()
    
    if len(sys.argv) < 2:
        # Default: full summary
        result = analyzer.get_summary()
        print(json.dumps(result, indent=2))
        return
    
    command = sys.argv[1]
    
    if command == "tasks":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print(json.dumps(analyzer.analyze_task_distribution(days), indent=2))
    
    elif command == "trend":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print(json.dumps(analyzer.analyze_cost_trend(days), indent=2))
    
    elif command == "models":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print(json.dumps(analyzer.analyze_model_usage(days), indent=2))
    
    elif command == "opportunities":
        print(json.dumps(analyzer.find_optimization_opportunities(), indent=2))
    
    elif command == "summary":
        print(json.dumps(analyzer.get_summary(), indent=2))


if __name__ == "__main__":
    main()
```

### 4.2 tuner.py

```python
#!/usr/bin/env python3
"""
Auto-Tuner - Automatically adjusts OpenClaw settings based on analysis
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

CONFIG_PATH = Path.home() / ".openclaw/openclaw.json"
HOOK_CONFIG_DIR = Path.home() / ".openclaw/hooks"

class ConfigTuner:
    def __init__(self):
        self.config = self._load_config()
        self.changes = []
    
    def _load_config(self) -> dict:
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass
        return {}
    
    def _save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def tune_model(self, tier: str) -> dict:
        """
        Switch to a specific model tier
        tier: 'quick', 'standard', 'deep'
        """
        models = {
            "quick": "openrouter/stepfun/step-3.5-flash:free",
            "standard": "anthropic/claude-haiku-4",
            "deep": "openrouter/minimax/minimax-m2.5"
        }
        
        if tier not in models:
            return {"error": f"Unknown tier: {tier}"}
        
        new_model = models[tier]
        
        # Get current
        current = self.config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "unknown")
        
        if current == new_model:
            return {"action": "none", "reason": "already_set", "current": current}
        
        # Set new
        if "agents" not in self.config:
            self.config["agents"] = {}
        if "defaults" not in self.config["agents"]:
            self.config["agents"]["defaults"] = {}
        if "model" not in self.config["agents"]["defaults"]:
            self.config["agents"]["defaults"]["model"] = {}
        
        self.config["agents"]["defaults"]["model"]["primary"] = new_model
        self._save_config()
        
        self.changes.append({
            "timestamp": datetime.now().isoformat(),
            "type": "model",
            "from": current,
            "to": new_model
        })
        
        return {
            "action": "model_changed",
            "from": current,
            "to": new_model,
            "reason": f"Auto-tuned to {tier}"
        }
    
    def tune_context_filtering(self, level: str) -> dict:
        """
        Adjust context filtering level
        level: 'minimal', 'standard', 'aggressive'
        """
        # Update hook config if exists
        hook_config_path = HOOK_CONFIG_DIR / "token-context" / "config.json"
        
        levels = {
            "minimal": {
                "simple": ["SOUL.md", "IDENTITY.md"],
                "standard": ["SOUL.md", "IDENTITY.md", "USER.md"],
                "complex": ["SOUL.md", "IDENTITY.md", "USER.md"]
            },
            "standard": {
                "simple": ["SOUL.md", "IDENTITY.md"],
                "standard": ["SOUL.md", "IDENTITY.md", "USER.md", "TOOLS.md"],
                "complex": ["SOUL.md", "IDENTITY.md", "USER.md", "TOOLS.md", "AGENTS.md", "MEMORY.md"]
            },
            "aggressive": {
                "simple": ["SOUL.md"],
                "standard": ["SOUL.md", "IDENTITY.md"],
                "complex": ["SOUL.md", "IDENTITY.md", "USER.md"]
            }
        }
        
        if level not in levels:
            return {"error": f"Unknown level: {level}"}
        
        if hook_config_path.exists():
            try:
                with open(hook_config_path, 'r') as f:
                    hook_config = json.load(f)
            except json.JSONDecodeError:
                hook_config = {}
        else:
            hook_config = {}
        
        hook_config["files"] = levels[level]
        
        hook_config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(hook_config_path, 'w') as f:
            json.dump(hook_config, f, indent=2)
        
        return {
            "action": "context_filter_changed",
            "level": level,
            "files": levels[level]
        }
    
    def tune_heartbeat(self, frequency: str) -> dict:
        """
        Adjust heartbeat frequency
        frequency: 'aggressive' (1hr), 'normal' (30min), 'passive' (4hr)
        """
        frequencies = {
            "aggressive": {"email": 3600, "calendar": 7200, "monitoring": 1800},
            "normal": {"email": 3600, "calendar": 7200, "monitoring": 1800},
            "passive": {"email": 7200, "calendar": 14400, "monitoring": 14400}
        }
        
        if frequency not in frequencies:
            return {"error": f"Unknown frequency: {frequency}"}
        
        # This would update heartbeat optimizer config
        # Placeholder
        return {
            "action": "heartbeat_changed",
            "frequency": frequency,
            "intervals": frequencies[frequency]
        }
    
    def apply_recommendations(self, opportunities: list) -> dict:
        """Apply auto-tuning based on opportunities"""
        results = []
        
        for opp in opportunities:
            if opp.get("type") == "cost_increasing":
                # Try to reduce costs
                results.append(self.tune_model("quick"))
            
            elif opp.get("type") == "budget_warning":
                # Switch to free model
                results.append(self.tune_model("quick"))
            
            elif opp.get("type") == "too_much_standard":
                # Enable aggressive filtering
                results.append(self.tune_context_filtering("aggressive"))
        
        return {
            "changes_made": len(results),
            "details": results
        }


def main():
    import sys
    
    tuner = ConfigTuner()
    
    if len(sys.argv) < 2:
        print("Usage: tuner.py [model|context|heartbeat|apply] [value]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "model":
        if len(sys.argv) < 3:
            print("Usage: tuner.py model [quick|standard|deep]")
            sys.exit(1)
        result = tuner.tune_model(sys.argv[2])
    
    elif command == "context":
        if len(sys.argv) < 3:
            print("Usage: tuner.py context [minimal|standard|aggressive]")
            sys.exit(1)
        result = tuner.tune_context_filtering(sys.argv[2])
    
    elif command == "heartbeat":
        if len(sys.argv) < 3:
            print("Usage: tuner.py heartbeat [aggressive|normal|passive]")
            sys.exit(1)
        result = tuner.tune_heartbeat(sys.argv[2])
    
    elif command == "apply":
        # Get opportunities and apply
        from analyzer import UsageAnalyzer
        analyzer = UsageAnalyzer()
        opportunities = analyzer.find_optimization_opportunities()
        result = tuner.apply_recommendations(opportunities)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

### 4.3 scheduler.py

```python
#!/usr/bin/env python3
"""
Cron Scheduler - Manages optimization cron jobs
"""
import json
import subprocess
from pathlib import Path
from typing import List, Dict

class CronScheduler:
    def __init__(self):
        self.jobs = []
    
    def add_hourly_optimization(self) -> dict:
        """Add hourly optimization job"""
        return self._add_job({
            "name": "token-optimizer-hourly",
            "schedule": {"kind": "every", "everyMs": 3600000},  # 1 hour
            "payload": {
                "kind": "agentTurn",
                "message": "Run hourly optimization check",
                "model": "openrouter/stepfun/step-3.5-flash:free"
            },
            "sessionTarget": "isolated"
        })
    
    def add_daily_report(self) -> dict:
        """Add daily report job"""
        return self._add_job({
            "name": "token-optimizer-daily-report",
            "schedule": {"kind": "cron", "expr": "0 8 * * *"},  # 8 AM daily
            "payload": {
                "kind": "agentTurn",
                "message": "Generate and send daily cost report",
                "model": "openrouter/stepfun/step-3.5-flash:free"
            },
            "sessionTarget": "isolated",
            "delivery": {"mode": "announce"}
        })
    
    def add_weekly_review(self) -> dict:
        """Add weekly review job"""
        return self._add_job({
            "name": "token-optimizer-weekly",
            "schedule": {"kind": "cron", "expr": "0 9 * * 1"},  # 9 AM Monday
            "payload": {
                "kind": "agentTurn",
                "message": "Run weekly optimization review and tuning",
                "model": "openrouter/minimax/minimax-m2.5"
            },
            "sessionTarget": "isolated"
        })
    
    def _add_job(self, job: dict) -> dict:
        """Add a cron job via OpenClaw CLI"""
        try:
            result = subprocess.run(
                ["openclaw", "cron", "add", "--json"],
                input=json.dumps(job),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {"status": "success", "job": job.get("name")}
            else:
                return {"status": "error", "message": result.stderr}
        
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def list_jobs(self) -> List[dict]:
        """List existing optimization jobs"""
        try:
            result = subprocess.run(
                ["openclaw", "cron", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            return []
        except:
            return []
    
    def remove_job(self, job_name: str) -> dict:
        """Remove a cron job"""
        try:
            result = subprocess.run(
                ["openclaw", "cron", "remove", job_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {"status": "success" if result.returncode == 0 else "error"}
        except Exception as e:
            return {"status": "error", "message": str(e)}


def main():
    import sys
    
    scheduler = CronScheduler()
    
    if len(sys.argv) < 2:
        # List jobs
        jobs = scheduler.list_jobs()
        print(json.dumps(jobs, indent=2))
        return
    
    command = sys.argv[1]
    
    if command == "add-hourly":
        print(json.dumps(scheduler.add_hourly_optimization(), indent=2))
    
    elif command == "add-daily":
        print(json.dumps(scheduler.add_daily_report(), indent=2))
    
    elif command == "add-weekly":
        print(json.dumps(scheduler.add_weekly_review(), indent=2))
    
    elif command == "list":
        print(json.dumps(scheduler.list_jobs(), indent=2))
    
    elif command == "remove":
        if len(sys.argv) < 3:
            print("Usage: scheduler.py remove <job-name>")
            sys.exit(1)
        print(json.dumps(scheduler.remove_job(sys.argv[2]), indent=2))
    
    elif command == "setup":
        # Setup all optimization jobs
        print("Setting up optimization cron jobs...")
        print(json.dumps(scheduler.add_hourly_optimization(), indent=2))
        print(json.dumps(scheduler.add_daily_report(), indent=2))
        print(json.dumps(scheduler.add_weekly_review(), indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### 4.4 reporter.py

```python
#!/usr/bin/env python3
"""
Reporter - Generates and sends optimization reports
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

class Reporter:
    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "templates"
    
    def generate_daily_report(self, usage_data: dict, analysis: dict) -> str:
        """Generate daily optimization report"""
        
        cost = usage_data.get("cost", 0)
        budget = usage_data.get("budget", 5.0)
        percent = (cost / budget * 100) if budget > 0 else 0
        
        opportunities = analysis.get("opportunities", [])
        
        report = f"""
📊 Daily Optimization Report - {datetime.now().date().isoformat()}
{'=' * 50}

💰 Cost Summary
   Today: ${cost:.2f} / ${budget:.2f} ({percent:.0f}%)

📈 Trend
   {analysis.get("cost_trend", {}).get("trend", "unknown")}
   Daily average: ${analysis.get("cost_trend", {}).get("daily_avg", 0):.2f}

🔧 Optimization Opportunities
"""
        
        if opportunities:
            for i, opp in enumerate(opportunities, 1):
                report += f"   {i}. [{opp.get('severity', 'unknown').upper()}] {opp.get('message', '')}\n"
                report += f"      → {opp.get('recommendation', '')}\n"
        else:
            report += "   ✓ No issues found\n"
        
        report += f"""
---
Generated by tokenQrusher v2.0
"""
        
        return report
    
    def generate_weekly_report(self, analysis: dict) -> str:
        """Generate weekly review report"""
        
        task_dist = analysis.get("task_distribution", {})
        model_usage = analysis.get("model_usage", {})
        
        report = f"""
📊 Weekly Optimization Review - Week of {datetime.now().date().isoformat()}
{'=' * 60}

📊 Task Distribution
   Simple: {task_dist.get('simple', 0)}%
   Standard: {task_dist.get('standard', 0)}%
   Complex: {task_dist.get('complex', 0)}%

💰 Model Usage
"""
        
        for model, data in model_usage.items():
            report += f"   {model}: {data.get('requests', 0)} requests (${data.get('cost', 0):.2f})\n"
        
        opportunities = analysis.get("opportunities", [])
        if opportunities:
            report += "\n⚠️ Recommended Actions\n"
            for i, opp in enumerate(opportunities, 1):
                report += f"   {i}. {opp.get('recommendation', '')}\n"
        
        return report
    
    def send_report(self, report: str, channel: str = "telegram") -> dict:
        """Send report to specified channel"""
        # This would use OpenClaw's message system
        # Placeholder
        return {
            "status": "sent",
            "channel": channel,
            "preview": report[:100] + "..."
        }


def main():
    import sys
    
    reporter = Reporter()
    
    if len(sys.argv) < 2:
        print("Usage: reporter.py [daily|weekly|send]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "daily":
        # Get usage and analysis
        from usage_monitor import UsageMonitor
        from analyzer import UsageAnalyzer
        
        monitor = UsageMonitor()
        analyzer = UsageAnalyzer()
        
        usage = monitor.get_daily_usage()
        analysis = analyzer.get_summary()
        
        print(reporter.generate_daily_report(usage, analysis))
    
    elif command == "weekly":
        from analyzer import UsageAnalyzer
        analyzer = UsageAnalyzer()
        analysis = analyzer.get_summary()
        
        print(reporter.generate_weekly_report(analysis))
    
    elif command == "send":
        if len(sys.argv) < 3:
            print("Usage: reporter.py send <channel>")
            sys.exit(1)
        
        report = "Sample report"  # Would generate actual report
        print(json.dumps(reporter.send_report(report, sys.argv[2]), indent=2))


if __name__ == "__main__":
    main()
```

---

## 5. Cron Job Definitions

### 5.1 optimizer.yaml

```yaml
# Cron job definitions for tokenQrusher optimization

jobs:
  - name: "token-optimizer-hourly"
    description: "Hourly optimization check"
    schedule: "0 * * * *"  # Every hour
    command: "python3 scripts/optimizer/run_optimizer.py hourly"
    model: "openrouter/stepfun/step-3.5-flash:free"
    enabled: true

  - name: "token-optimizer-daily-report"
    description: "Daily cost report"
    schedule: "0 8 * * *"  # 8 AM daily
    command: "python3 scripts/optimizer/reporter.py daily"
    model: "openrouter/stepfun/step-3.5-flash:free"
    notify: true

  - name: "token-optimizer-weekly"
    description: "Weekly optimization review"
    schedule: "0 9 * * 1"  # 9 AM Monday
    command: "python3 scripts/optimizer/run_optimizer.py weekly"
    model: "openrouter/minimax/minimax-m2.5"  # Use better model for analysis
    notify: true
```

---

## 6. Integration Points

### With Phase 1 (Context Hook)

- Analyzer reads filtering settings
- Tuner adjusts filtering level

### With Phase 2 (Model Hook)

- Analyzer reads model usage
- Tuner rotates models

### With Phase 3 (Usage Tracking)

- Analyzer reads usage history
- Reporter generates reports

---

## 7. Error Handling

| Scenario | Handling |
|----------|----------|
| No usage data | Skip optimization, log warning |
| Config write fails | Rollback, alert |
| Cron job fails | Retry next schedule |
| Invalid settings | Validate before apply |

---

## 8. Testing Strategy

### Unit Tests

- Test analyzer logic
- Test tuner configuration
- Test reporter generation

### Integration Tests

- Test cron job creation
- Test auto-tuning

---

## 9. Dependencies

### Phase Dependencies

| Dependency | Purpose |
|------------|---------|
| Phase 1 | Context filtering data |
| Phase 2 | Model usage data |
| Phase 3 | Usage history data |

### External Dependencies

| Dependency | Purpose |
|------------|---------|
| OpenClaw Cron | Job scheduling |
| Python 3.7+ | Runtime |

---

## 10. Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| optimizer.enabled | bool | true | Enable auto-optimization |
| optimizer.hourly | bool | true | Run hourly checks |
| optimizer.daily_report | bool | true | Send daily reports |
| optimizer.weekly_review | bool | true | Weekly deep review |
| optimizer.auto_tune | bool | false | Auto-apply changes |

---

## 11. Acceptance Criteria

### Functional Requirements

- [ ] Hourly optimization runs
- [ ] Daily reports generated
- [ ] Weekly reviews generated
- [ ] Auto-tuning applies changes

### Non-Functional Requirements

- [ ] Runs reliably on schedule
- [ ] No config corruption
- [ ] Graceful error handling

---

## 12. References

- OpenClaw Cron: `/automation/cron-jobs.md`
- OpenClaw Hooks: `/automation/hooks.md`

---

*This specification defines Phase 4 implementation. See IMPLEMENTATION_PLAN.md for phase dependencies.*
