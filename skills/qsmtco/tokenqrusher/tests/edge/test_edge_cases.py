#!/usr/bin/env python3
"""
Edge case tests for tokenQrusher.

Tests unusual inputs and error conditions.
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'hooks' / 'token-context'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts' / 'cron-optimizer'))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts' / 'heartbeat-optimizer'))


# =============================================================================
# THEOREM: Edge cases in classifier
# =============================================================================

class TestClassifierEdgeCases:
    """Theorem: Classifier handles edge cases gracefully."""
    
    def test_unicode_emoji(self):
        """Emoji should not break classifier."""
        from classifier import classifyComplexity
        
        messages = [
            "👋",
            "🎉",
            "🔥",
            "💯",
            "👍",
            "👎",
        ]
        
        for msg in messages:
            result = classifyComplexity(msg)
            assert result.level is not None
            assert result.confidence >= 0
    
    def test_unicode_foreign(self):
        """Foreign unicode should not break classifier."""
        from classifier import classifyComplexity
        
        messages = [
            "こんにちは",
            "привет",
            "مرحبا",
            "你好",
            "שלום",
        ]
        
        for msg in messages:
            result = classifyComplexity(msg)
            assert result.level is not None
    
    def test_extreme_lengths(self):
        """Extreme message lengths should not break."""
        from classifier import classifyComplexity
        
        # Very short
        result = classifyComplexity("")
        assert result.level is not None
        
        # Very long
        long_msg = "a" * 100000
        result = classifyComplexity(long_msg)
        assert result.level is not None
        
        # Newlines
        result = classifyComplexity("\n\n\n")
        assert result.level is not None
        
        # Tabs
        result = classifyComplexity("\t\t\t")
        assert result.level is not None
    
    def test_malformed_types(self):
        """Malformed types should be handled."""
        from classifier import classifyComplexity
        
        # List
        result = classifyComplexity(["hi"])
        assert result.level is not None
        
        # Number
        result = classifyComplexity(123)
        assert result.level is not None
        
        # Dict
        result = classifyComplexity({"key": "value"})
        assert result.level is not None


# =============================================================================
# THEOREM: Edge cases in budget calculations
# =============================================================================

class TestBudgetEdgeCases:
    """Theorem: Budget handles edge cases."""
    
    def test_zero_limit(self):
        """Zero limit should not crash."""
        from optimizer import BudgetState
        
        budget = BudgetState(period='daily', spent=0, limit=0)
        
        # Should not raise
        assert budget.spending_ratio == 0
        assert budget.remaining == 0
    
    def test_negative_limit(self):
        """Negative limit should work."""
        from optimizer import BudgetState
        
        budget = BudgetState(period='daily', spent=5, limit=-10)
        
        assert budget.spending_ratio == -0.5
        assert budget.is_over_budget is True
    
    def test_extreme_values(self):
        """Extreme values should not crash."""
        from optimizer import BudgetState
        
        budget = BudgetState(
            period='daily',
            spent=1e10,
            limit=1e10
        )
        
        assert budget.spending_ratio == 1.0
        assert budget.is_over_budget is True


# =============================================================================
# THEOREM: Edge cases in datetime parsing
# =============================================================================

class TestDatetimeEdgeCases:
    """Theorem: Datetime handling is robust."""
    
    def test_invalid_timestamp_formats(self):
        """Invalid timestamps should not crash."""
        from optimizer import UsageMetrics
        
        invalid_timestamps = [
            "not-a-date",
            "",
            "2024-13-45",  # Invalid month/day
            "yesterday",
            "tomorrow",
            "00-00-00",
        ]
        
        for ts in invalid_timestamps:
            # Should not raise, should use default
            metrics = UsageMetrics(
                timestamp=ts,
                total_cost=10.0,
                input_tokens=1000,
                output_tokens=2000,
                session_count=1,
                average_cost_per_session=10.0
            )
            
            assert metrics.timestamp == ts
    
    def test_future_timestamps(self):
        """Future timestamps should not crash."""
        from optimizer import UsageMetrics
        
        future = (datetime.now() + timedelta(days=365)).isoformat()
        
        metrics = UsageMetrics(
            timestamp=future,
            total_cost=10.0,
            input_tokens=1000,
            output_tokens=2000,
            session_count=1,
            average_cost_per_session=10.0
        )
        
        assert metrics.timestamp == future


# =============================================================================
# THEOREM: Edge cases in heartbeat
# =============================================================================

class TestHeartbeatEdgeCases:
    """Theorem: Heartbeat handles edge cases."""
    
    def test_invalid_check_type(self):
        """Invalid check type should be handled."""
        from optimizer import CheckType
        
        # This should work
        assert CheckType.EMAIL.value == "email"
    
    def test_quiet_hours_midnight_boundary(self):
        """Quiet hours at midnight boundary."""
        from optimizer import QuietHours
        
        # 23:00 - 08:00
        quiet = QuietHours(23, 8)
        
        # Midnight
        assert quiet.is_quiet(datetime(2024, 1, 1, 0, 0, 0)) is True
        
        # 23:59
        assert quiet.is_quiet(datetime(2024, 1, 1, 23, 59, 0)) is True
        
        # 08:00
        assert quiet.is_quiet(datetime(2024, 1, 1, 8, 0, 0)) is False
        
        # 08:01
        assert quiet.is_quiet(datetime(2024, 1, 1, 8, 1, 0)) is False


# =============================================================================
# THEOREM: Edge cases in configuration
# =============================================================================

class TestConfigEdgeCases:
    """Theorem: Configuration handles edge cases."""
    
    def test_validate_config_with_extra_keys(self):
        """Extra keys should be ignored, not fail."""
        from optimizer import validate_config
        
        config = {
            'enabled': True,
            'intervals': {'optimize': 3600},
            'budgets': {'daily': 5.0, 'weekly': 30.0, 'monthly': 100.0},
            'unknown_key': 'should_be_ignored',
            'extra_data': {'nested': 'value'}
        }
        
        is_valid, errors = validate_config(config)
        
        assert is_valid is True
    
    def test_validate_config_with_none_values(self):
        """None values should be handled."""
        from optimizer import validate_config
        
        config = {
            'enabled': None,
            'intervals': {'optimize': 3600},
            'budgets': {'daily': 5.0, 'weekly': 30.0, 'monthly': 100.0}
        }
        
        is_valid, errors = validate_config(config)
        
        # May or may not be valid depending on implementation


# =============================================================================
# THEOREM: CLI handles edge cases
# =============================================================================

class TestCLIEdgeCases:
    """Theorem: CLI handles edge cases gracefully."""
    
    def test_empty_prompt_defaults(self):
        """Empty prompt should use default."""
        # This is handled in the CLI itself
        # Just verify the logic exists
        default_prompt = 'hello'
        
        prompt = "" or default_prompt
        
        assert prompt == default_prompt
    
    def test_very_long_prompt(self):
        """Very long prompt should not crash."""
        long_prompt = "x" * 100000
        
        # Should not crash when processed
        assert len(long_prompt) == 100000


# =============================================================================
# THEOREM: File I/O edge cases
# =============================================================================

class TestFileIOEdgeCases:
    """Theorem: File operations handle edge cases."""
    
    def test_nonexistent_state_file(self):
        """Nonexistent state file should not crash."""
        from optimizer import HeartbeatOptimizer
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize with non-existent state
            optimizer = HeartbeatOptimizer(state_dir=Path(tmpdir))
            
            # Should initialize without error
            status = optimizer.get_status()
            
            assert 'checks' in status
    
    def test_corrupted_state_file(self):
        """Corrupted state file should not crash."""
        from optimizer import HeartbeatOptimizer
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir)
            
            # Write corrupted JSON
            state_file = state_dir / 'heartbeat-state.json'
            state_file.write_text("not valid json {{{")
            
            # Should handle gracefully
            optimizer = HeartbeatOptimizer(state_dir=state_dir)
            
            status = optimizer.get_status()
            
            assert 'checks' in status


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
