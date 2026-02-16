#!/usr/bin/env python3
"""
Budget Checker - Monitors spending against configured budgets.

Provides budget status checking, threshold alerts, and auto-downgrade logic.
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

# Import local modules
from .config import get_config, BudgetConfig
from .tracker import get_tracker, UsageTracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[budget-checker] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class BudgetStatus(Enum):
    """Budget status levels."""
    OK = 'ok'
    WARNING = 'warning'  # 80-95%
    CRITICAL = 'critical'  # 95%+
    EXCEEDED = 'exceeded'  # Over budget


@dataclass
class BudgetState:
    """Current budget state."""
    status: BudgetStatus
    period: str  # 'daily', 'weekly', 'monthly'
    spent: float
    limit: float
    percent: float
    remaining: float
    recommendations: List[str]


class BudgetChecker:
    """
    Budget monitoring and enforcement.
    
    Features:
    - Check budget status
    - Threshold alerts (warning, critical)
    - Auto-downgrade recommendations
    - Configurable limits
    """
    
    def __init__(self, config: Optional[BudgetConfig] = None):
        """
        Initialize budget checker.
        
        Args:
            config: Budget configuration (uses env vars if not provided)
        """
        self.config = config or get_config().budget
    
    def check_budget(self, period: str = 'daily') -> BudgetState:
        """
        Check budget for a time period.
        
        Args:
            period: 'daily', 'weekly', or 'monthly'
            
        Returns:
            BudgetState with current status
        """
        # Get usage tracker
        tracker = get_tracker()
        
        # Get usage for period
        if period == 'daily':
            usage = tracker.get_daily_usage(1)
        elif period == 'weekly':
            usage = tracker.get_weekly_usage(1)
        else:
            usage = tracker.get_monthly_usage(1)
        
        # Get limit for period
        limit = self._get_limit(period)
        spent = usage.total_cost
        remaining = max(0, limit - spent)
        percent = spent / limit if limit > 0 else 0
        
        # Determine status
        status = self._determine_status(percent)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(status, percent, period)
        
        return BudgetState(
            status=status,
            period=period,
            spent=spent,
            limit=limit,
            percent=percent,
            remaining=remaining,
            recommendations=recommendations
        )
    
    def _get_limit(self, period: str) -> float:
        """Get budget limit for period."""
        if period == 'daily':
            return self.config.daily
        elif period == 'weekly':
            return self.config.weekly
        else:
            return self.config.monthly
    
    def _determine_status(self, percent: float) -> BudgetStatus:
        """Determine budget status from percentage."""
        if percent >= 1.0:
            return BudgetStatus.EXCEEDED
        elif percent >= self.config.critical_threshold:
            return BudgetStatus.CRITICAL
        elif percent >= self.config.warning_threshold:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.OK
    
    def _generate_recommendations(
        self,
        status: BudgetStatus,
        percent: float,
        period: str
    ) -> List[str]:
        """Generate actionable recommendations."""
        recs = []
        
        if status == BudgetStatus.EXCEEDED:
            recs.append("⚠️ BUDGET EXCEEDED - Immediate action required")
            recs.append("Switch to free model tier (Quick)")
            recs.append("Reduce conversation complexity")
            recs.append("Consider upgrading budget or pausing non-essential tasks")
            
        elif status == BudgetStatus.CRITICAL:
            recs.append(f"🔴 Critical: Budget at {percent:.0%}")
            recs.append("Switch to cheaper model tier")
            recs.append("Limit complex queries")
            
        elif status == BudgetStatus.WARNING:
            recs.append(f"🟡 Warning: Budget at {percent:.0%}")
            recs.append("Consider using Quick tier for simple tasks")
            
        else:
            recs.append("✅ Budget healthy")
        
        return recs
    
    def check_all_periods(self) -> Dict[str, BudgetState]:
        """Check budgets for all time periods."""
        return {
            'daily': self.check_budget('daily'),
            'weekly': self.check_budget('weekly'),
            'monthly': self.check_budget('monthly')
        }
    
    def get_worst_status(self) -> BudgetState:
        """Get the worst budget status across all periods."""
        states = self.check_all_periods()
        
        # Priority: exceeded > critical > warning > ok
        priority = {
            BudgetStatus.EXCEEDED: 3,
            BudgetStatus.CRITICAL: 2,
            BudgetStatus.WARNING: 1,
            BudgetStatus.OK: 0
        }
        
        worst = states['daily']
        for period, state in states.items():
            if priority[state.status] > priority[worst.status]:
                worst = state
        
        return worst
    
    def should_auto_downgrade(self) -> bool:
        """
        Check if auto-downgrade should be triggered.
        
        Returns:
            True if auto-downgrade is recommended
        """
        if not self.config.auto_downgrade:
            return False
        
        state = self.get_worst_status()
        
        # Only downgrade on critical or exceeded
        return state.status in (BudgetStatus.CRITICAL, BudgetStatus.EXCEEDED)
    
    def get_downgrade_action(self) -> Optional[Dict[str, Any]]:
        """
        Get recommended action for auto-downgrade.
        
        Returns:
            Dict with action details, or None if no action needed
        """
        if not self.should_auto_downgrade():
            return None
        
        state = self.get_worst_status()
        
        return {
            'action': 'downgrade_model',
            'reason': f'Budget {state.status.value} ({state.period})',
            'current_spent': state.spent,
            'budget_limit': state.limit,
            'percent': state.percent,
            'recommendation': 'Switch to quick tier (free model)'
        }
    
    def format_status_text(self, state: Optional[BudgetState] = None) -> str:
        """
        Format budget status as human-readable text.
        
        Args:
            state: Budget state (gets worst if not provided)
            
        Returns:
            Formatted status string
        """
        if state is None:
            state = self.get_worst_status()
        
        emoji = {
            BudgetStatus.OK: '✅',
            BudgetStatus.WARNING: '🟡',
            BudgetStatus.CRITICAL: '🔴',
            BudgetStatus.EXCEEDED: '🚨'
        }
        
        lines = [
            f"{emoji[state.status]} Budget: {state.status.value.upper()}",
            f"   Period: {state.period}",
            f"   Spent: ${state.spent:.2f} / ${state.limit:.2f} ({state.percent:.0%})",
            f"   Remaining: ${state.remaining:.2f}"
        ]
        
        if state.recommendations:
            lines.append("")
            lines.extend("   " + r for r in state.recommendations)
        
        return "\n".join(lines)


def check_budget_cli(args) -> int:
    """
    CLI entry point for budget checking.
    
    Returns:
        Exit code (0 for success)
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Check token budget status')
    parser.add_argument('--period', choices=['daily', 'weekly', 'monthly'], 
                       default='daily', help='Budget period')
    parser.add_argument('--json', action='store_true', 
                       help='Output as JSON')
    parser.add_argument('--quiet', action='store_true',
                       help='Only exit with non-zero if budget exceeded')
    
    parsed = parser.parse_args(args)
    
    try:
        checker = BudgetChecker()
        state = checker.check_budget(parsed.period)
        
        if parsed.json:
            output = {
                'status': state.status.value,
                'period': state.period,
                'spent': state.spent,
                'limit': state.limit,
                'percent': state.percent,
                'remaining': state.remaining
            }
            print(json.dumps(output, indent=2))
        else:
            print(checker.format_status_text(state))
        
        # Exit code based on status
        if parsed.quiet:
            return 0
        
        if state.status == BudgetStatus.EXCEEDED:
            return 2
        elif state.status == BudgetStatus.CRITICAL:
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(check_budget_cli(sys.argv[1:]))
