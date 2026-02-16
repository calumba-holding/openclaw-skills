# Phase 6: CLI Unification Specification

**Phase:** 6 of 8  
**Title:** Unified CLI  
**Objective:** Create single `tokenqrusher` command that wraps all functionality  
**Status:** Draft  
**Dependencies:** Phase 1-5

---

## 1. Overview

### Purpose

This phase creates a **unified CLI** that provides a single entry point for all tokenQrusher functionality.

### Why This Phase After 1-5

All the underlying components exist. This phase makes them accessible through one CLI.

### Expected Features

| Command | Description |
|---------|-------------|
| `tokenqrusher context <prompt>` | Recommend context files |
| `tokenqrusher model <prompt>` | Recommend model tier |
| `tokenqrusher budget` | Check budget status |
| `tokenqrusher usage` | Show usage summary |
| `tokenqrusher optimize` | Run optimization |
| `tokenqrusher status` | Full system status |

---

## 2. Architecture

### File Structure

```
tokenQrusher/
├── bin/
│   └── tokenqrusher           # Main CLI entry point
├── scripts/
│   └── commands/              # Command modules
│       ├── __init__.py
│       ├── context.py
│       ├── model.py
│       ├── budget.py
│       ├── usage.py
│       └── optimize.py
└── config/
    └── tokenqrusher.json      # CLI configuration
```

---

## 3. Implementation

### 3.1 Main CLI

```python
#!/usr/bin/env python3
"""
tokenQrusher - Unified CLI for token optimization
"""
import argparse
import sys
from pathlib import Path

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

def main():
    parser = argparse.ArgumentParser(
        prog="tokenqrusher",
        description="Token optimization tools for OpenClaw"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Context command
    context_parser = subparsers.add_parser("context", help="Recommend context files")
    context_parser.add_argument("prompt", nargs="?", help="User prompt to analyze")
    context_parser.add_argument("--files", action="store_true", help="Show files only")
    
    # Model command
    model_parser = subparsers.add_parser("model", help="Recommend model tier")
    model_parser.add_argument("prompt", nargs="?", help="User prompt to analyze")
    model_parser.add_argument("--tier", action="store_true", help="Show tier only")
    
    # Budget command
    budget_parser = subparsers.add_parser("budget", help="Check budget status")
    budget_parser.add_argument("--json", action="store_true", help="JSON output")
    budget_parser.add_argument("--warn", type=float, help="Warning threshold")
    
    # Usage command
    usage_parser = subparsers.add_parser("usage", help="Show usage summary")
    usage_parser.add_argument("--days", type=int, default=7, help="Days to show")
    usage_parser.add_argument("--report", action="store_true", help="Generate report")
    
    # Optimize command
    optimize_parser = subparsers.add_parser("optimize", help="Run optimization")
    optimize_parser.add_argument("--dry-run", action="store_true", help="Don't apply changes")
    optimize_parser.add_argument("--auto", action="store_true", help="Auto-apply safe changes")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Full system status")
    status_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install hooks and cron jobs")
    install_parser.add_argument("--hooks", action="store_true", help="Install hooks")
    install_parser.add_argument("--cron", action="store_true", help="Install cron jobs")
    install_parser.add_argument("--all", action="store_true", help="Install everything")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to command
    if args.command == "context":
        from commands.context import run
        return run(args)
    
    elif args.command == "model":
        from commands.model import run
        return run(args)
    
    elif args.command == "budget":
        from commands.budget import run
        return run(args)
    
    elif args.command == "usage":
        from commands.usage import run
        return run(args)
    
    elif args.command == "optimize":
        from commands.optimize import run
        return run(args)
    
    elif args.command == "status":
        from commands.status import run
        return run(args)
    
    elif args.command == "install":
        from commands.install import run
        return run(args)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### 3.2 Example Command Module

```python
# scripts/commands/context.py
"""Context recommendation command"""

import json
import sys
from pathlib import Path

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

def run(args):
    prompt = args.prompt or "hello"
    
    # Use context optimizer
    import context_optimizer
    result = context_optimizer.recommend_context_bundle(prompt)
    
    if args.files:
        for f in result["recommended_files"]:
            print(f)
    else:
        print(json.dumps(result, indent=2))
    
    return 0
```

---

## 4. Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `context` | Recommend context | `tokenqrusher context "write code"` |
| `model` | Recommend model | `tokenqrusher model "hi"` |
| `budget` | Check budget | `tokenqrusher budget` |
| `usage` | Show usage | `tokenqrusher usage --days 30` |
| `optimize` | Run optimizer | `tokenqrusher optimize --auto` |
| `status` | Full status | `tokenqrusher status -v` |
| `install` | Setup | `tokenqrusher install --all` |

---

## 5. Installation

### As npm package

```bash
# Make executable
chmod +x bin/tokenqrusher

# Link to PATH
ln -s $(pwd)/bin/tokenqrusher /usr/local/bin/
```

### With OpenClaw

```bash
# Install as skill
clawhub install tokenQrusher

# CLI available as skill command
```

---

## 6. Acceptance Criteria

- [ ] All subcommands work
- [ ] Help text complete
- [ ] JSON output valid
- [ ] Installation works
- [ ] Integration with Phases 1-5

---

## 7. References

- Python argparse documentation
- OpenClaw CLI patterns

---

*This specification defines Phase 6 implementation. See IMPLEMENTATION_PLAN.md for phase dependencies.*
