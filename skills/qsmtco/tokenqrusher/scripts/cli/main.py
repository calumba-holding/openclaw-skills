#!/usr/bin/env python3
"""
Unified CLI for tokenQrusher - Token optimization for OpenClaw.

This CLI provides a single entry point for all tokenQrusher functionality:
- Context optimization
- Model routing
- Usage tracking
- Budget checking
- Cron scheduling
- Heartbeat optimization

Design Principles:
- Deterministic: Same input always produces same output
- Exhaustive: Every error case handled
- Static typing: Full type hints, mypy compatible
- Pure functions: Easy to test
"""
from __future__ import annotations

import sys
import os
import json
import argparse
import logging
from pathlib import Path
from typing import (
    Optional, List, Dict, Any, Tuple, 
    Callable, TypeVar, Generic
)
from dataclasses import dataclass
from enum import Enum, auto
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[tokenqrusher] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# THEOREMS (Constants)
# =============================================================================

class ExitCode(Enum):
    """CLI exit codes (theorems)."""
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ARGS = 2
    CONFIG_ERROR = 3
    NOT_FOUND = 4
    BUDGET_EXCEEDED = 5


class ComplexityLevel(Enum):
    """Context complexity levels."""
    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLEX = "complex"


class ModelTier(Enum):
    """AI model tiers."""
    QUICK = "quick"
    STANDARD = "standard"
    DEEP = "deep"


# =============================================================================
# RESULT TYPES (Theorems)
# =============================================================================

@dataclass(frozen=True, slots=True)
class CliResult:
    """Immutable CLI result."""
    exit_code: ExitCode
    message: str
    data: Optional[Dict[str, Any]] = None
    
    @property
    def success(self) -> bool:
        """Whether operation succeeded."""
        return self.exit_code == ExitCode.SUCCESS
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'exit_code': self.exit_code.value,
            'message': self.message,
            'data': self.data
        }


# =============================================================================
# SUB-COMMAND INTERFACE (Abstract)
# =============================================================================

class SubCommand(ABC):
    """Abstract base class for subcommands."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name."""
        pass
    
    @property
    @abstractmethod
    def help(self) -> str:
        """Command help text."""
        pass
    
    @abstractmethod
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        """Add command-specific arguments."""
        pass
    
    @abstractmethod
    def execute(self, args: argparse.Namespace) -> CliResult:
        """Execute the command."""
        pass


# =============================================================================
# CONTEXT COMMAND
# =============================================================================

class ContextCommand(SubCommand):
    """Context optimization - recommend context files for a prompt."""
    
    @property
    def name(self) -> str:
        return "context"
    
    @property
    def help(self) -> str:
        return "Recommend context files for a prompt"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('prompt', nargs='?', default='hello', help='User prompt')
        parser.add_argument('--files', action='store_true', help='Show files only')
        parser.add_argument('--json', action='store_true', help='JSON output')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        # Import classifier from token-context hook
        prompt = args.prompt
        
        # Simple pattern matching (same as hook)
        simple_patterns = [
            r'^(hi|hey|hello|yo|sup|howdy)$',
            r'^(thanks|thank you|thx|ty)$',
            r'^(ok|okay|sure|got it|understood)$',
            r'^(yes|yeah|yep|yup|no|nope|nah)$',
            r'^(good|great|nice|cool|awesome)$',
            r'^\?+$',
        ]
        
        complex_patterns = [
            r'^(design|architect)\s+\w+',
            r'\barchitect(?:ure|ing)?\b',
            r'\bcomprehensive\b',
            r'\banalyze\s+deeply\b',
            r'\bplan\s+\w+\s+system\b',
        ]
        
        import re
        
        level = ComplexityLevel.STANDARD
        confidence = 0.6
        
        for pattern in simple_patterns:
            if re.match(pattern, prompt, re.IGNORECASE):
                level = ComplexityLevel.SIMPLE
                confidence = 0.95
                break
        
        if level == ComplexityLevel.STANDARD:
            for pattern in complex_patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    level = ComplexityLevel.COMPLEX
                    confidence = 0.90
                    break
        
        # Get files for level
        files_map = {
            ComplexityLevel.SIMPLE: ['SOUL.md', 'IDENTITY.md'],
            ComplexityLevel.STANDARD: ['SOUL.md', 'IDENTITY.md', 'USER.md'],
            ComplexityLevel.COMPLEX: ['SOUL.md', 'IDENTITY.md', 'USER.md', 'TOOLS.md', 'AGENTS.md', 'MEMORY.md']
        }
        
        files = files_map[level]
        
        # Calculate savings
        total_files = 7  # Max files
        savings = ((total_files - len(files)) / total_files) * 100
        
        data = {
            'prompt': prompt,
            'complexity': level.value,
            'confidence': confidence,
            'files': files,
            'files_count': len(files),
            'savings_percent': savings
        }
        
        if args.json:
            return CliResult(ExitCode.SUCCESS, "OK", data)
        
        if args.files:
            output = '\n'.join(files)
            return CliResult(ExitCode.SUCCESS, output, data)
        
        message = f"Complexity: {level.value} (confidence: {confidence:.0%})\nFiles: {', '.join(files)}\nSavings: {savings:.0f}%"
        return CliResult(ExitCode.SUCCESS, message, data)


# =============================================================================
# MODEL COMMAND
# =============================================================================

class ModelCommand(SubCommand):
    """Model routing - recommend model tier for a prompt."""
    
    @property
    def name(self) -> str:
        return "model"
    
    @property
    def help(self) -> str:
        return "Recommend model tier for a prompt"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('prompt', nargs='?', default='hello', help='User prompt')
        parser.add_argument('--tier', action='store_true', help='Show tier only')
        parser.add_argument('--json', action='store_true', help='JSON output')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        prompt = args.prompt
        
        import re
        
        # Determine tier
        tier = ModelTier.STANDARD
        confidence = 0.6
        
        # Quick patterns
        quick_patterns = [
            r'^(hi|hey|hello|yo|sup|howdy)$',
            r'^(thanks|thank you|thx|ty)$',
            r'^(ok|okay|sure|got it)$',
            r'^(yes|no|yeah|nope)$',
            r'^heartbeat$',
            r'^check\s+(email|calendar|weather|status)',
            r'^read\s+(file|log)',
            r'^list\s+(files|dir)',
        ]
        
        # Deep patterns
        deep_patterns = [
            r'^(design|architect)\s+\w+',
            r'\barchitect(?:ure|ing)?\b',
            r'\bcomprehensive\b',
            r'\banalyze\s+deeply\b',
            r'\boptimize\s+(performance|speed)',
        ]
        
        for pattern in quick_patterns:
            if re.match(pattern, prompt, re.IGNORECASE):
                tier = ModelTier.QUICK
                confidence = 0.90
                break
        
        if tier == ModelTier.STANDARD:
            for pattern in deep_patterns:
                if re.search(pattern, prompt, re.IGNORECASE):
                    tier = ModelTier.DEEP
                    confidence = 0.90
                    break
        
        # Model mappings
        models = {
            ModelTier.QUICK: 'openrouter/stepfun/step-3.5-flash:free',
            ModelTier.STANDARD: 'anthropic/claude-haiku-4',
            ModelTier.DEEP: 'openrouter/minimax/minimax-m2.5'
        }
        
        costs = {
            ModelTier.QUICK: '$0.00/MT',
            ModelTier.STANDARD: '$0.25/MT',
            ModelTier.DEEP: '$0.60+/MT'
        }
        
        model = models[tier]
        cost = costs[tier]
        
        data = {
            'prompt': prompt,
            'tier': tier.value,
            'confidence': confidence,
            'model': model,
            'cost': cost
        }
        
        if args.json:
            return CliResult(ExitCode.SUCCESS, "OK", data)
        
        if args.tier:
            return CliResult(ExitCode.SUCCESS, tier.value, data)
        
        message = f"Tier: {tier.value} (confidence: {confidence:.0%})\nModel: {model}\nCost: {cost}"
        return CliResult(ExitCode.SUCCESS, message, data)


# =============================================================================
# BUDGET COMMAND
# =============================================================================

class BudgetCommand(SubCommand):
    """Budget status - check spending against limits."""
    
    @property
    def name(self) -> str:
        return "budget"
    
    @property
    def help(self) -> str:
        return "Check budget status"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--period', choices=['daily', 'weekly', 'monthly'],
                           default='daily', help='Budget period')
        parser.add_argument('--json', action='store_true', help='JSON output')
        parser.add_argument('--warn', type=float, help='Warning threshold (0-1)')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        # Get budget from environment or defaults
        budgets = {
            'daily': float(os.environ.get('TOKENQRUSHER_BUDGET_DAILY', '5.0')),
            'weekly': float(os.environ.get('TOKENQRUSHER_BUDGET_WEEKLY', '30.0')),
            'monthly': float(os.environ.get('TOKENQRUSHER_BUDGET_MONTHLY', '100.0'))
        }
        
        warning_threshold = args.warn or float(os.environ.get('TOKENQRUSHER_WARNING_THRESHOLD', '0.8'))
        
        # Try to get current usage from state
        state_dir = Path.home() / '.openclaw/workspace/memory'
        state_file = state_dir / 'usage-history.json'
        
        spent = 0.0
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                
                # Sum today's costs
                from datetime import datetime
                today = datetime.now().isoformat().split('T')[0]
                
                if isinstance(data, list):
                    for record in data:
                        if record.get('timestamp', '').startswith(today):
                            spent += record.get('cost', 0)
            except (json.JSONDecodeError, IOError):
                pass
        
        limit = budgets[args.period]
        percent = spent / limit if limit > 0 else 0
        
        # Determine status
        if percent >= 1.0:
            status = 'EXCEEDED'
            emoji = '🚨'
        elif percent >= 0.95:
            status = 'CRITICAL'
            emoji = '🔴'
        elif percent >= warning_threshold:
            status = 'WARNING'
            emoji = '🟡'
        else:
            status = 'HEALTHY'
            emoji = '✅'
        
        remaining = max(0, limit - spent)
        
        data = {
            'period': args.period,
            'spent': spent,
            'limit': limit,
            'remaining': remaining,
            'percent': percent,
            'status': status
        }
        
        if args.json:
            return CliResult(ExitCode.SUCCESS, "OK", data)
        
        message = f"{emoji} Budget: {status}\nPeriod: {args.period}\nSpent: ${spent:.2f} / ${limit:.2f} ({percent:.0%})\nRemaining: ${remaining:.2f}"
        
        if percent >= warning_threshold:
            return_code = ExitCode.GENERAL_ERROR
        else:
            return_code = ExitCode.SUCCESS
        
        return CliResult(return_code, message, data)


# =============================================================================
# USAGE COMMAND
# =============================================================================

class UsageCommand(SubCommand):
    """Usage summary - show token usage statistics."""
    
    @property
    def name(self) -> str:
        return "usage"
    
    @property
    def help(self) -> str:
        return "Show usage summary"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--days', type=int, default=7, help='Days to show')
        parser.add_argument('--json', action='store_true', help='JSON output')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        state_dir = Path.home() / '.openclaw/workspace/memory'
        state_file = state_dir / 'usage-history.json'
        
        if not state_file.exists():
            return CliResult(ExitCode.NOT_FOUND, "No usage data found", {'records': 0})
        
        try:
            with open(state_file, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            return CliResult(ExitCode.CONFIG_ERROR, f"Failed to read: {e}")
        
        if not isinstance(data, list):
            return CliResult(ExitCode.CONFIG_ERROR, "Invalid data format")
        
        # Filter to last N days
        from datetime import datetime, timedelta
        cutoff = datetime.now() - timedelta(days=args.days)
        
        records = []
        total_cost = 0
        total_input = 0
        total_output = 0
        
        for record in data:
            try:
                ts = datetime.fromisoformat(record.get('timestamp', ''))
                if ts >= cutoff:
                    records.append(record)
                    total_cost += record.get('cost', 0)
                    total_input += record.get('input_tokens', 0)
                    total_output += record.get('output_tokens', 0)
            except ValueError:
                pass
        
        data = {
            'period_days': args.days,
            'record_count': len(records),
            'total_cost': total_cost,
            'total_input_tokens': total_input,
            'total_output_tokens': total_output
        }
        
        if args.json:
            return CliResult(ExitCode.SUCCESS, "OK", data)
        
        message = f"=== Usage ({args.days} days) ===\nRecords: {len(records)}\nCost: ${total_cost:.2f}\nInput: {total_input:,} tokens\nOutput: {total_output:,} tokens"
        
        return CliResult(ExitCode.SUCCESS, message, data)


# =============================================================================
# OPTIMIZE COMMAND
# =============================================================================

class OptimizeCommand(SubCommand):
    """Run optimization."""
    
    @property
    def name(self) -> str:
        return "optimize"
    
    @property
    def help(self) -> str:
        return "Run optimization"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
        parser.add_argument('--json', action='store_true', help='JSON output')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        # Import optimizer
        sys.path.insert(0, str(Path(__file__).parent.parent / 'cron-optimizer'))
        try:
            from optimizer import CronOptimizer, TriggerReason, OptimizationResult
            
            optimizer = CronOptimizer()
            result = optimizer.optimize(trigger=TriggerReason.MANUAL)
            
            data = {
                'result': result.result.name,
                'actions': len(result.actions_taken),
                'duration_ms': result.duration_ms
            }
            
            if args.json:
                return CliResult(ExitCode.SUCCESS, "OK", data)
            
            message = f"Optimization: {result.result.name}\nActions: {len(result.actions_taken)}\nDuration: {result.duration_ms:.1f}ms"
            
            return CliResult(ExitCode.SUCCESS, message, data)
            
        except ImportError as e:
            return CliResult(ExitCode.NOT_FOUND, f"Optimizer not available: {e}")


# =============================================================================
# STATUS COMMAND
# =============================================================================

class StatusCommand(SubCommand):
    """Full system status."""
    
    @property
    def name(self) -> str:
        return "status"
    
    @property
    def help(self) -> str:
        return "Show full system status"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
        parser.add_argument('--json', action='store_true', help='JSON output')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        import subprocess
        
        status_data: Dict[str, Any] = {}
        
        # Get hooks status
        try:
            result = subprocess.run(
                ['openclaw', 'hooks', 'list'],
                capture_output=True,
                text=True,
                timeout=10
            )
            status_data['hooks'] = result.stdout if result.returncode == 0 else result.stderr
        except Exception as e:
            status_data['hooks_error'] = str(e)
        
        # Try to get optimizer status
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'cron-optimizer'))
            from optimizer import CronOptimizer
            optimizer = CronOptimizer()
            opt_status = optimizer.get_status()
            status_data['optimizer'] = opt_status
        except ImportError:
            status_data['optimizer'] = 'not available'
        
        # Try to get heartbeat status
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / 'heartbeat-optimizer'))
            from optimizer import HeartbeatOptimizer
            hb = HeartbeatOptimizer()
            status_data['heartbeat'] = hb.get_status()
        except ImportError:
            status_data['heartbeat'] = 'not available'
        
        # Budget status
        budgets = {
            'daily': float(os.environ.get('TOKENQRUSHER_BUDGET_DAILY', '5.0')),
            'weekly': float(os.environ.get('TOKENQRUSHER_BUDGET_WEEKLY', '30.0')),
            'monthly': float(os.environ.get('TOKENQRUSHER_BUDGET_MONTHLY', '100.0'))
        }
        status_data['budgets'] = budgets
        
        if args.json:
            return CliResult(ExitCode.SUCCESS, "OK", status_data)
        
        # Format text output
        lines = ["=== tokenQrusher Status ===", ""]
        
        if 'hooks' in status_data:
            lines.append("Hooks:")
            lines.append(status_data['hooks'])
        
        if 'optimizer' in status_data and isinstance(status_data['optimizer'], dict):
            lines.append("")
            lines.append("Optimizer:")
            opt = status_data['optimizer']
            lines.append(f"  State: {opt.get('state', 'unknown')}")
            lines.append(f"  Enabled: {opt.get('enabled', True)}")
            lines.append(f"  Quiet hours: {opt.get('quiet_hours_active', False)}")
        
        if 'heartbeat' in status_data and isinstance(status_data['heartbeat'], dict):
            lines.append("")
            lines.append("Heartbeat:")
            hb = status_data['heartbeat']
            lines.append(f"  Checks due: {hb.get('total_checks_due', 0)}")
        
        lines.append("")
        lines.append("Budgets:")
        for period, limit in budgets.items():
            lines.append(f"  {period}: ${limit}")
        
        message = "\n".join(lines)
        
        return CliResult(ExitCode.SUCCESS, message, status_data)


# =============================================================================
# INSTALL COMMAND
# =============================================================================

class InstallCommand(SubCommand):
    """Install hooks and cron jobs."""
    
    @property
    def name(self) -> str:
        return "install"
    
    @property
    def help(self) -> str:
        return "Install hooks and cron jobs"
    
    def add_args(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument('--hooks', action='store_true', help='Install hooks')
        parser.add_argument('--cron', action='store_true', help='Install cron jobs')
        parser.add_argument('--all', action='store_true', help='Install everything')
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    
    def execute(self, args: argparse.Namespace) -> CliResult:
        actions: List[str] = []
        
        if args.all or args.hooks:
            actions.append("Enable token-context hook")
            actions.append("Enable token-model hook")
            actions.append("Enable token-usage hook")
            actions.append("Enable token-cron hook")
            actions.append("Enable token-heartbeat hook")
        
        if args.all or args.cron:
            actions.append("Add cron job for optimize (hourly)")
            actions.append("Add cron job for budget-check (5 min)")
        
        if not actions:
            return CliResult(ExitCode.INVALID_ARGS, "No actions specified. Use --hooks, --cron, or --all")
        
        if args.dry_run:
            message = "Would do:\n" + "\n".join(f"  - {a}" for a in actions)
            return CliResult(ExitCode.SUCCESS, message, {'actions': actions})
        
        # Execute actions
        results = []
        
        if args.all or args.hooks:
            import subprocess
            hooks = ['token-context', 'token-model', 'token-usage', 'token-cron', 'token-heartbeat']
            for hook in hooks:
                try:
                    subprocess.run(['openclaw', 'hooks', 'enable', hook],
                                capture_output=True, timeout=10)
                    results.append(f"Enabled: {hook}")
                except Exception as e:
                    results.append(f"Failed: {hook}: {e}")
        
        message = "Installation complete:\n" + "\n".join(f"  - {r}" for r in results)
        
        return CliResult(ExitCode.SUCCESS, message, {'results': results})


# =============================================================================
# MAIN CLI
# =============================================================================

class TokenQrusherCLI:
    """
    Unified CLI for tokenQrusher.
    
    Coordinates all subcommands.
    """
    
    def __init__(self) -> None:
        """Initialize CLI."""
        self.commands: Dict[str, SubCommand] = {
            'context': ContextCommand(),
            'model': ModelCommand(),
            'budget': BudgetCommand(),
            'usage': UsageCommand(),
            'optimize': OptimizeCommand(),
            'status': StatusCommand(),
            'install': InstallCommand(),
        }
        
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog='tokenqrusher',
            description='Token optimization tools for OpenClaw',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Add subcommands
        for cmd in self.commands.values():
            cmd_parser = subparsers.add_parser(cmd.name, help=cmd.help)
            cmd.add_args(cmd_parser)
        
        return parser
    
    def run(self, argv: Optional[List[str]] = None) -> int:
        """
        Run CLI.
        
        Args:
            argv: Command line arguments (default: sys.argv)
            
        Returns:
            Exit code
        """
        args = self.parser.parse_args(argv)
        
        # No command specified
        if not args.command:
            self.parser.print_help()
            return ExitCode.SUCCESS.value
        
        # Get command
        cmd = self.commands.get(args.command)
        
        if cmd is None:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return ExitCode.INVALID_ARGS.value
        
        # Execute
        try:
            result = cmd.execute(args)
            
            # Print output
            if result.message:
                print(result.message)
            
            if result.data and args.__dict__.get('json'):
                print(json.dumps(result.data, indent=2))
            
            return result.exit_code.value
            
        except Exception as e:
            logger.exception("Command failed")
            print(f"Error: {e}", file=sys.stderr)
            return ExitCode.GENERAL_ERROR.value


def main() -> int:
    """Entry point."""
    cli = TokenQrusherCLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())
