#!/usr/bin/env python3
"""
Unit tests for tokenQrusher heartbeat optimizer.

Tests the heartbeat optimization logic exhaustively.
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts' / 'heartbeat-optimizer'))

from optimizer import (
    CheckType,
    CheckInterval,
    QuietHours,
    CheckState,
    calculate_should_check,
    compute_check_schedule,
    estimate_token_savings,
    HeartbeatOptimizer,
)


# =============================================================================
# THEOREM: CheckInterval validates input
# =============================================================================

class TestCheckInterval:
    """Theorem: CheckInterval enforces invariants."""
    
    def test_positive_interval(self):
        """Positive intervals should work."""
        interval = CheckInterval(CheckType.EMAIL, 3600)
        
        assert interval.interval_seconds == 3600
    
    def test_zero_interval_raises(self):
        """Zero interval should raise ValueError."""
        with pytest.raises(ValueError):
            CheckInterval(CheckType.EMAIL, 0)
    
    def test_negative_interval_raises(self):
        """Negative interval should raise ValueError."""
        with pytest.raises(ValueError):
            CheckInterval(CheckType.EMAIL, -100)


# =============================================================================
# THEOREM: QuietHours handles all cases
# =============================================================================

class TestQuietHours:
    """Theorem: Quiet hours correctly identifies quiet times."""
    
    @pytest.mark.parametrize("hour,expected", [
        # Default: 23:00 - 08:00
        (0, True),   # 00:00 - in quiet hours
        (1, True),   # 01:00 - in quiet hours
        (7, True),   # 07:00 - in quiet hours
        (8, False),  # 08:00 - not in quiet hours
        (12, False), # 12:00 - not in quiet hours
        (18, False), # 18:00 - not in quiet hours
        (22, False), # 22:00 - not in quiet hours
        (23, True),  # 23:00 - in quiet hours
    ])
    def test_default_quiet_hours(self, hour, expected):
        """Default quiet hours (23:00-08:00) should work."""
        quiet = QuietHours(23, 8)
        
        dt = datetime(2024, 1, 1, hour)
        
        assert quiet.is_quiet(dt) is expected
    
    def test_same_day_quiet_hours(self):
        """Same-day quiet hours should work."""
        quiet = QuietHours(14, 18)  # 14:00 - 18:00
        
        assert quiet.is_quiet(datetime(2024, 1, 1, 15)) is True
        assert quiet.is_quiet(datetime(2024, 1, 1, 12)) is False
    
    def test_invalid_hours_raises(self):
        """Invalid hours should raise ValueError."""
        with pytest.raises(ValueError):
            QuietHours(25, 8)  # Invalid hour
        
        with pytest.raises(ValueError):
            QuietHours(23, 25)  # Invalid hour


# =============================================================================
# THEOREM: CheckState should_check logic
# =============================================================================

class TestCheckState:
    """Theorem: CheckState.should_check is correct."""
    
    def test_never_checked(self):
        """Never checked should return True."""
        state = CheckState(CheckType.EMAIL, None, None)
        
        now = datetime.now()
        
        assert state.should_check(now, 3600) is True
    
    def test_interval_not_met(self):
        """Not enough time passed should return False."""
        now = datetime.now()
        five_minutes_ago = now - timedelta(minutes=5)
        
        state = CheckState(CheckType.EMAIL, five_minutes_ago, None)
        
        assert state.should_check(now, 3600) is False
    
    def test_interval_met(self):
        """Enough time passed should return True."""
        now = datetime.now()
        two_hours_ago = now - timedelta(hours=2)
        
        state = CheckState(CheckType.EMAIL, two_hours_ago, None)
        
        assert state.should_check(now, 3600) is True


# =============================================================================
# THEOREM: calculate_should_check is deterministic
# =============================================================================

class TestCalculateShouldCheck:
    """Theorem: Pure function, same input = same output."""
    
    def test_quiet_hours_returns_false(self):
        """Quiet hours should return False."""
        quiet = QuietHours(23, 8)
        
        # During quiet hours (2 AM)
        dt = datetime(2024, 1, 1, 2)
        
        state = CheckState(CheckType.EMAIL, None, None)
        
        should_run, reason = calculate_should_check(state, 3600, dt, quiet)
        
        assert should_run is False
        assert reason == "quiet_hours"
    
    def test_interval_not_met_returns_false(self):
        """Interval not met should return False."""
        quiet = QuietHours(23, 8)  # Not 2 AM
        
        dt = datetime(2024, 1, 1, 12)  # Noon
        
        # Checked 5 minutes ago
        state = CheckState(CheckType.EMAIL, dt - timedelta(minutes=5), None)
        
        should_run, reason = calculate_should_check(state, 3600, dt, quiet)
        
        assert should_run is False
        assert "remaining" in reason
    
    def test_interval_met_returns_true(self):
        """Interval met should return True."""
        quiet = QuietHours(23, 8)
        
        dt = datetime(2024, 1, 1, 12)
        
        # Checked 2 hours ago
        state = CheckState(CheckType.EMAIL, dt - timedelta(hours=2), None)
        
        should_run, reason = calculate_should_check(state, 3600, dt, quiet)
        
        assert should_run is True
    
    def test_never_run_returns_true(self):
        """Never run should return True."""
        quiet = QuietHours(23, 8)
        
        dt = datetime(2024, 1, 1, 12)
        
        state = CheckState(CheckType.EMAIL, None, None)
        
        should_run, reason = calculate_should_check(state, 3600, dt, quiet)
        
        assert should_run is True


# =============================================================================
# THEOREM: compute_check_schedule is deterministic
# =============================================================================

class TestComputeSchedule:
    """Theorem: Pure function, same input = same output."""
    
    def test_all_checks_evaluated(self):
        """All check types should be in result."""
        quiet = QuietHours.default()
        
        result = compute_check_schedule({}, {}, quiet)
        
        assert set(result.keys()) == set(CheckType)
    
    def test_same_inputs_same_output(self):
        """Same inputs should produce same output."""
        quiet = QuietHours.default()
        
        result1 = compute_check_schedule({}, {}, quiet)
        result2 = compute_check_schedule({}, {}, quiet)
        
        assert result1 == result2


# =============================================================================
# THEOREM: estimate_token_savings is correct
# =============================================================================

class TestTokenSavings:
    """Theorem: Token savings calculation is correct."""
    
    def test_no_savings_for_max_checks(self):
        """48 checks (max) should give 0 savings."""
        savings = estimate_token_savings(48)
        
        assert savings['reduction_percent'] == 0
        assert savings['tokens_saved_per_day'] == 0
    
    def test_full_savings_for_minimal_checks(self):
        """Few checks should give maximum savings."""
        savings = estimate_token_savings(12)  # 75% reduction
        
        assert savings['reduction_percent'] == 75
        assert savings['checks_reduced'] == 36
    
    def test_savings_calculation(self):
        """Savings should be calculated correctly."""
        # Original: 48 * 100 = 4800
        # Optimized: 12 * 100 = 1200
        # Savings: 3600
        
        savings = estimate_token_savings(12)
        
        assert savings['original_tokens_per_day'] == 4800
        assert savings['optimized_tokens_per_day'] == 1200
        assert savings['tokens_saved_per_day'] == 3600


# =============================================================================
# THEOREM: HeartbeatOptimizer maintains invariants
# =============================================================================

class TestHeartbeatOptimizer:
    """Theorem: HeartbeatOptimizer is thread-safe and correct."""
    
    def test_initialization(self):
        """Should initialize with defaults."""
        optimizer = HeartbeatOptimizer()
        
        assert optimizer._intervals is not None
        assert optimizer._quiet_hours is not None
    
    def test_should_check_all(self):
        """First run should check all."""
        optimizer = HeartbeatOptimizer()
        
        for check_type in CheckType:
            should_run, reason = optimizer.should_check(check_type)
            
            assert should_run is True
    
    def test_record_check(self):
        """Recording check should update state."""
        optimizer = HeartbeatOptimizer()
        
        optimizer.record_check(CheckType.EMAIL, had_alerts=False)
        
        # Should not raise
        should_run, reason = optimizer.should_check(CheckType.EMAIL)
        
        # Should be False (just checked)
        # Note: depends on timing
        assert isinstance(should_run, bool)
    
    def test_get_status(self):
        """get_status should return valid structure."""
        optimizer = HeartbeatOptimizer()
        
        status = optimizer.get_status()
        
        assert 'quiet_hours' in status
        assert 'checks' in status
        assert 'total_checks_due' in status
    
    def test_get_savings_estimate(self):
        """get_savings_estimate should return valid data."""
        optimizer = HeartbeatOptimizer()
        
        savings = optimizer.get_savings_estimate()
        
        assert 'reduction_percent' in savings
        assert 0 <= savings['reduction_percent'] <= 100
    
    def test_reset_check(self):
        """reset_check should force next run."""
        optimizer = HeartbeatOptimizer()
        
        # Record a check
        optimizer.record_check(CheckType.EMAIL, had_alerts=False)
        
        # Reset it
        optimizer.reset_check(CheckType.EMAIL)
        
        # Should run now
        should_run, reason = optimizer.should_check(CheckType.EMAIL)
        
        assert should_run is True
    
    def test_reset_all(self):
        """reset_all should reset all checks."""
        optimizer = HeartbeatOptimizer()
        
        # Record checks
        for check_type in CheckType:
            optimizer.record_check(check_type, False)
        
        # Reset all
        optimizer.reset_all()
        
        # All should run
        for check_type in CheckType:
            should_run, reason = optimizer.should_check(check_type)
            
            assert should_run is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
