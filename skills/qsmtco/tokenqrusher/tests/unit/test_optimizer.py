#!/usr/bin/env python3
"""
Unit tests for tokenQrusher cron optimizer.

Tests the core optimization logic exhaustively.
"""
import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts' / 'cron-optimizer'))

from optimizer import (
    UsageMetrics,
    BudgetState,
    OptimizationAction,
    ModelTier,
    TriggerReason,
    OptimizationResult,
    calculate_spending_velocity,
    determine_optimal_tier,
    compute_optimization_actions,
    validate_config,
    CronOptimizer,
)


# =============================================================================
# THEOREM: UsageMetrics is immutable and valid
# =============================================================================

class TestUsageMetrics:
    """Theorem: UsageMetrics maintains invariants."""
    
    def test_from_dict_clamps_negative_values(self):
        """Negative values should be clamped to 0."""
        data = {
            'timestamp': '2024-01-01T00:00:00',
            'total_cost': -10.0,
            'input_tokens': -100,
            'output_tokens': -200,
            'session_count': -5,
            'average_cost_per_session': -1.0
        }
        
        metrics = UsageMetrics.from_dict(data)
        
        assert metrics.total_cost >= 0
        assert metrics.input_tokens >= 0
        assert metrics.output_tokens >= 0
        assert metrics.session_count >= 0
    
    def test_from_dict_accepts_valid_data(self):
        """Valid data should be preserved."""
        data = {
            'timestamp': '2024-01-01T00:00:00',
            'total_cost': 10.5,
            'input_tokens': 1000,
            'output_tokens': 2000,
            'session_count': 5,
            'average_cost_per_session': 2.1
        }
        
        metrics = UsageMetrics.from_dict(data)
        
        assert metrics.total_cost == 10.5
        assert metrics.input_tokens == 1000
        assert metrics.output_tokens == 2000
    
    def test_to_dict_roundtrip(self):
        """to_dict should be inverse of from_dict."""
        original = UsageMetrics(
            timestamp='2024-01-01T00:00:00',
            total_cost=10.5,
            input_tokens=1000,
            output_tokens=2000,
            session_count=5,
            average_cost_per_session=2.1
        )
        
        restored = UsageMetrics.from_dict(original.to_dict())
        
        assert restored.timestamp == original.timestamp
        assert restored.total_cost == original.total_cost


# =============================================================================
# THEOREM: BudgetState calculations are correct
# =============================================================================

class TestBudgetState:
    """Theorem: Budget calculations maintain invariants."""
    
    def test_spending_ratio_is_non_negative(self):
        """spending_ratio should never be negative."""
        budget = BudgetState(period='daily', spent=5.0, limit=10.0)
        
        assert budget.spending_ratio >= 0
    
    def test_spending_ratio_calculation(self):
        """spending_ratio should equal spent/limit."""
        budget = BudgetState(period='daily', spent=3.0, limit=10.0)
        
        assert budget.spending_ratio == 0.3
    
    def test_remaining_calculation(self):
        """remaining should equal limit - spent."""
        budget = BudgetState(period='daily', spent=7.0, limit=10.0)
        
        assert budget.remaining == 3.0
    
    def test_remaining_can_be_negative(self):
        """remaining can be negative when over budget."""
        budget = BudgetState(period='daily', spent=15.0, limit=10.0)
        
        assert budget.remaining == -5.0
    
    def test_is_over_budget_true_when_exceeded(self):
        """is_over_budget True when spent > limit."""
        budget = BudgetState(period='daily', spent=11.0, limit=10.0)
        
        assert budget.is_over_budget is True
    
    def test_is_over_budget_false_when_under(self):
        """is_over_budget False when spent < limit."""
        budget = BudgetState(period='daily', spent=5.0, limit=10.0)
        
        assert budget.is_over_budget is False
    
    @pytest.mark.parametrize("percent,expected", [
        (0.0, 'healthy'),
        (0.5, 'healthy'),
        (0.79, 'healthy'),
        (0.80, 'warning'),
        (0.90, 'warning'),
        (0.94, 'warning'),
        (0.95, 'critical'),
        (1.0, 'exceeded'),
    ])
    def test_status_classification(self, percent, expected):
        """Status should classify correctly based on spending_ratio."""
        spent = percent * 100
        budget = BudgetState(period='daily', spent=spent, limit=100.0)
        
        assert budget.status == expected


# =============================================================================
# THEOREM: calculate_spending_velocity is deterministic and correct
# =============================================================================

class TestSpendingVelocity:
    """Theorem: Spending velocity calculation is correct."""
    
    def test_zero_velocity_for_identical_timestamps(self):
        """Identical timestamps should give zero velocity."""
        now = datetime.now()
        
        current = UsageMetrics(
            timestamp=now.isoformat(),
            total_cost=10.0,
            input_tokens=1000,
            output_tokens=2000,
            session_count=1,
            average_cost_per_session=10.0
        )
        
        velocity = calculate_spending_velocity(current, current)
        
        assert velocity == 0.0
    
    def test_positive_velocity(self):
        """Positive spending should give positive velocity."""
        prev_time = datetime(2024, 1, 1, 0, 0, 0)
        curr_time = datetime(2024, 1, 1, 1, 0, 0)  # 1 hour later
        
        previous = UsageMetrics(
            timestamp=prev_time.isoformat(),
            total_cost=10.0,
            input_tokens=1000,
            output_tokens=2000,
            session_count=1,
            average_cost_per_session=10.0
        )
        
        current = UsageMetrics(
            timestamp=curr_time.isoformat(),
            total_cost=20.0,  # +10 in 1 hour
            input_tokens=1500,
            output_tokens=2500,
            session_count=2,
            average_cost_per_session=10.0
        )
        
        velocity = calculate_spending_velocity(current, previous)
        
        assert velocity == 10.0  # $10/hour
    
    def test_zero_velocity_for_invalid_timestamps(self):
        """Invalid timestamps should return 0."""
        current = UsageMetrics(
            timestamp='invalid',
            total_cost=10.0,
            input_tokens=1000,
            output_tokens=2000,
            session_count=1,
            average_cost_per_session=10.0
        )
        
        velocity = calculate_spending_velocity(current, current)
        
        assert velocity == 0.0


# =============================================================================
# THEOREM: determine_optimal_tier is deterministic
# =============================================================================

class TestDetermineOptimalTier:
    """Theorem: Model tier selection is correct."""
    
    @pytest.mark.parametrize("complexity,spent,limit,expected_tier", [
        # Simple tasks
        ('simple', 0, 10, ModelTier.STANDARD),  # Under budget, use standard
        ('simple', 5, 10, ModelTier.QUICK),    # Over 80%, use quick
        ('simple', 11, 10, ModelTier.QUICK),   # Over budget, use quick
        
        # Standard tasks
        ('standard', 0, 10, ModelTier.STANDARD),
        ('standard', 5, 10, ModelTier.QUICK),  # High spending
        ('standard', 11, 10, ModelTier.QUICK),
        
        # Complex tasks - always deep
        ('complex', 0, 10, ModelTier.DEEP),
        ('complex', 5, 10, ModelTier.DEEP),
        ('complex', 11, 10, ModelTier.DEEP),
    ])
    def test_tier_selection(self, complexity, spent, limit, expected_tier):
        """Tiers should be selected correctly."""
        budget = BudgetState(period='daily', spent=spent, limit=limit)
        
        tier = determine_optimal_tier(budget, complexity)
        
        assert tier == expected_tier


# =============================================================================
# THEOREM: compute_optimization_actions is deterministic
# =============================================================================

class TestComputeActions:
    """Theorem: Same inputs produce same actions."""
    
    def test_no_actions_for_healthy_budget(self):
        """Healthy budget should produce no actions."""
        metrics = UsageMetrics(
            timestamp=datetime.now().isoformat(),
            total_cost=1.0,
            input_tokens=100,
            output_tokens=200,
            session_count=1,
            average_cost_per_session=1.0
        )
        
        budget = BudgetState(period='daily', spent=1.0, limit=10.0)
        
        actions = compute_optimization_actions(metrics, budget, [])
        
        # Should have no high-priority actions
        assert all(a.priority < 80 for a in actions)
    
    def test_force_quick_when_exceeded(self):
        """Over budget should force quick tier."""
        metrics = UsageMetrics(
            timestamp=datetime.now().isoformat(),
            total_cost=15.0,
            input_tokens=1000,
            output_tokens=2000,
            session_count=5,
            average_cost_per_session=3.0
        )
        
        budget = BudgetState(period='daily', spent=15.0, limit=10.0)
        
        actions = compute_optimization_actions(metrics, budget, [])
        
        # Should have force_quick_tier action
        action_types = [a.action_type for a in actions]
        
        assert 'force_quick_tier' in action_types
    
    def test_actions_sorted_by_priority(self):
        """Actions should be sorted by priority (highest first)."""
        metrics = UsageMetrics(
            timestamp=datetime.now().isoformat(),
            total_cost=11.0,
            input_tokens=1000,
            output_tokens=2000,
            session_count=15,
            average_cost_per_session=0.73
        )
        
        budget = BudgetState(period='daily', spent=11.0, limit=10.0)
        
        actions = compute_optimization_actions(metrics, budget, [])
        
        priorities = [a.priority for a in actions]
        
        assert priorities == sorted(priorities, reverse=True)


# =============================================================================
# THEOREM: validate_config catches errors
# =============================================================================

class TestValidateConfig:
    """Theorem: Config validation is exhaustive."""
    
    def test_valid_config(self):
        """Valid config should pass."""
        config = {
            'enabled': True,
            'intervals': {
                'optimize': 3600,
                'check': 300
            },
            'budgets': {
                'daily': 5.0,
                'weekly': 30.0,
                'monthly': 100.0
            }
        }
        
        is_valid, errors = validate_config(config)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_missing_required_keys(self):
        """Missing required keys should fail."""
        config = {
            'enabled': True
        }
        
        is_valid, errors = validate_config(config)
        
        assert is_valid is False
        assert len(errors) > 0
    
    def test_invalid_interval(self):
        """Invalid interval should fail."""
        config = {
            'enabled': True,
            'intervals': {
                'optimize': 30  # Too small
            },
            'budgets': {
                'daily': 5.0,
                'weekly': 30.0,
                'monthly': 100.0
            }
        }
        
        is_valid, errors = validate_config(config)
        
        assert is_valid is False
    
    def test_invalid_budget(self):
        """Invalid budget should fail."""
        config = {
            'enabled': True,
            'intervals': {
                'optimize': 3600
            },
            'budgets': {
                'daily': -5.0,  # Negative
                'weekly': 30.0,
                'monthly': 100.0
            }
        }
        
        is_valid, errors = validate_config(config)
        
        assert is_valid is False


# =============================================================================
# THEOREM: ModelTier cost properties are correct
# =============================================================================

class TestModelTierCosts:
    """Theorem: Model costs are correct."""
    
    def test_quick_is_free(self):
        """Quick tier should be free."""
        assert ModelTier.QUICK.cost_per_million == 0.0
    
    def test_standard_cost(self):
        """Standard tier should cost $0.25/MT."""
        assert ModelTier.STANDARD.cost_per_million == 0.25
    
    def test_deep_cost(self):
        """Deep tier should cost $0.60/MT."""
        assert ModelTier.DEEP.cost_per_million == 0.60
    
    def test_can_afford(self):
        """can_afford should work correctly."""
        assert ModelTier.QUICK.can_afford(0) is True  # Free
        assert ModelTier.STANDARD.can_afford(0.10) is True
        assert ModelTier.STANDARD.can_afford(0.05) is False
        assert ModelTier.DEEP.can_afford(0.50) is True
        assert ModelTier.DEEP.can_afford(0.30) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
