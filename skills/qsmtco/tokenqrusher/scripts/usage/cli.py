#!/usr/bin/env python3
"""
Usage CLI - Main command-line interface for tokenQrusher usage tracking.

Provides unified access to usage stats, budget checks, and optimization.
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

from .config import Config, get_config, reset_config
from .tracker import get_tracker, UsageTracker
from .budget import BudgetChecker, BudgetStatus, check_budget_cli


def usage_summary(args) -> int:
    """Show usage summary."""
    tracker = get_tracker()
    summary = tracker.get_usage_summary()
    
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print("=== Usage Summary ===")
        print(f"Total records: {summary['total_records']}")
        print()
        
        for period in ['daily', 'weekly', 'monthly']:
            data = summary[period]
            print(f"{period.capitalize()}:")
            print(f"  Cost: ${data['total_cost']:.2f}")
            print(f"  Input tokens: {data['total_input_tokens']:,}")
            print(f"  Output tokens: {data['total_output_tokens']:,}")
            print(f"  Records: {data['record_count']}")
            print()
    
    return 0


def budget_status(args) -> int:
    """Show budget status."""
    return check_budget_cli(args)


def usage_records(args) -> int:
    """Show usage records."""
    tracker = get_tracker()
    records = tracker.get_all_records()
    
    if args.json:
        print(json.dumps([r.to_dict() for r in records], indent=2))
    else:
        print(f"=== Usage Records ({len(records)} total) ===")
        for r in records[:args.limit]:
            print(f"{r.timestamp[:19]} | ${r.cost:.4f} | in:{r.input_tokens} out:{r.output_tokens}")
    
    return 0


def prune_records(args) -> int:
    """Prune old usage records."""
    tracker = get_tracker()
    removed = tracker.prune_old_records(args.days)
    print(f"Pruned {removed} records older than {args.days} days")
    return 0


def show_config(args) -> int:
    """Show current configuration."""
    config = get_config()
    
    if args.json:
        print(json.dumps({
            'budget': {
                'daily': config.budget.daily,
                'weekly': config.budget.weekly,
                'monthly': config.budget.monthly,
                'warning_threshold': config.budget.warning_threshold,
                'critical_threshold': config.budget.critical_threshold,
                'auto_downgrade': config.budget.auto_downgrade
            },
            'usage': {
                'state_dir': str(config.usage.state_dir),
                'state_file': config.usage.state_file,
                'retention_days': config.usage.retention_days,
                'poll_interval_seconds': config.usage.poll_interval_seconds
            }
        }, indent=2))
    else:
        print("=== tokenQrusher Configuration ===")
        print()
        print("Budget:")
        print(f"  Daily: ${config.budget.daily}")
        print(f"  Weekly: ${config.budget.weekly}")
        print(f"  Monthly: ${config.budget.monthly}")
        print(f"  Warning: {config.budget.warning_threshold:.0%}")
        print(f"  Critical: {config.budget.critical_threshold:.0%}")
        print(f"  Auto-downgrade: {config.budget.auto_downgrade}")
        print()
        print("Usage:")
        print(f"  State dir: {config.usage.state_dir}")
        print(f"  Retention: {config.usage.retention_days} days")
        print(f"  Poll interval: {config.usage.poll_interval_seconds}s")
    
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='tokenqrusher',
        description='Token optimization tools for OpenClaw'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Usage summary
    summary_parser = subparsers.add_parser('usage', help='Show usage summary')
    summary_parser.add_argument('--json', action='store_true', help='JSON output')
    
    # Budget check
    budget_parser = subparsers.add_parser('budget', help='Check budget status')
    budget_parser.add_argument('--period', choices=['daily', 'weekly', 'monthly'],
                              default='daily', help='Budget period')
    budget_parser.add_argument('--json', action='store_true', help='JSON output')
    budget_parser.add_argument('--quiet', action='store_true', help='Only exit non-zero if exceeded')
    
    # Records
    records_parser = subparsers.add_parser('records', help='Show usage records')
    records_parser.add_argument('--limit', type=int, default=20, help='Limit results')
    records_parser.add_argument('--json', action='store_true', help='JSON output')
    
    # Prune
    prune_parser = subparsers.add_parser('prune', help='Prune old records')
    prune_parser.add_argument('--days', type=int, default=30, help='Keep days')
    
    # Config
    config_parser = subparsers.add_parser('config', help='Show configuration')
    config_parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to command
    if args.command == 'usage':
        return usage_summary(args)
    elif args.command == 'budget':
        return budget_status(args)
    elif args.command == 'records':
        return usage_records(args)
    elif args.command == 'prune':
        return prune_records(args)
    elif args.command == 'config':
        return show_config(args)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
