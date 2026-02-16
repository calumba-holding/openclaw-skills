#!/usr/bin/env python3
"""
Configuration module for tokenQrusher usage tracking.

Handles configuration from environment variables with sensible defaults.
Follows the principle: env vars > config file > defaults
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class BudgetConfig:
    """Budget configuration with environment variable support."""
    
    daily: float = 5.0
    weekly: float = 30.0
    monthly: float = 100.0
    warning_threshold: float = 0.8  # 80%
    critical_threshold: float = 0.95  # 95%
    auto_downgrade: bool = True
    
    @classmethod
    def from_env(cls) -> 'BudgetConfig':
        """Create config from environment variables."""
        return cls(
            daily=cls._get_float('TOKENQRUSHER_BUDGET_DAILY', 5.0),
            weekly=cls._get_float('TOKENQRUSHER_BUDGET_WEEKLY', 30.0),
            monthly=cls._get_float('TOKENQRUSHER_BUDGET_MONTHLY', 100.0),
            warning_threshold=cls._get_float('TOKENQRUSHER_WARNING_THRESHOLD', 0.8),
            critical_threshold=cls._get_float('TOKENQRUSHER_CRITICAL_THRESHOLD', 0.95),
            auto_downgrade=cls._get_bool('TOKENQRUSHER_AUTO_DOWNGRADE', True)
        )
    
    @staticmethod
    def _get_float(key: str, default: float) -> float:
        """Get float from environment variable."""
        value = os.environ.get(key)
        if value:
            try:
                return float(value)
            except ValueError:
                pass
        return default
    
    @staticmethod
    def _get_bool(key: str, default: bool) -> bool:
        """Get bool from environment variable."""
        value = os.environ.get(key)
        if value:
            return value.lower() in ('true', '1', 'yes', 'on')
        return default


@dataclass 
class UsageConfig:
    """General usage tracking configuration."""
    
    state_dir: Path = field(default_factory=lambda: Path.home() / '.openclaw/workspace/memory')
    state_file: str = 'usage-history.json'
    retention_days: int = 30
    poll_interval_seconds: int = 300  # 5 minutes
    
    @classmethod
    def from_env(cls) -> 'UsageConfig':
        """Create config from environment variables."""
        state_dir = os.environ.get('TOKENQRUSHER_STATE_DIR')
        return cls(
            state_dir=Path(state_dir) if state_dir else Path.home() / '.openclaw/workspace/memory',
            state_file=os.environ.get('TOKENQRUSHER_STATE_FILE', 'usage-history.json'),
            retention_days=cls._get_int('TOKENQRUSHER_RETENTION_DAYS', 30),
            poll_interval_seconds=cls._get_int('TOKENQRUSHER_POLL_INTERVAL', 300)
        )
    
    @staticmethod
    def _get_int(key: str, default: int) -> int:
        """Get int from environment variable."""
        value = os.environ.get(key)
        if value:
            try:
                return int(value)
            except ValueError:
                pass
        return default


@dataclass
class Config:
    """Main configuration container."""
    
    budget: BudgetConfig = field(default_factory=BudgetConfig.from_env)
    usage: UsageConfig = field(default_factory=UsageConfig.from_env)
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> 'Config':
        """
        Load configuration.
        
        Priority: environment variables > config file > defaults
        
        Args:
            config_path: Optional path to config file
            
        Returns:
            Config instance
        """
        config = cls()
        
        # Try to load from config file
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                
                # Override with file config
                if 'budget' in file_config:
                    bc = file_config['budget']
                    config.budget.daily = bc.get('daily', config.budget.daily)
                    config.budget.weekly = bc.get('weekly', config.budget.weekly)
                    config.budget.monthly = bc.get('monthly', config.budget.monthly)
                    
                if 'usage' in file_config:
                    uc = file_config['usage']
                    if 'state_dir' in uc:
                        config.usage.state_dir = Path(uc['state_dir'])
                    config.usage.state_file = uc.get('state_file', config.usage.state_file)
                    config.usage.retention_days = uc.get('retention_days', config.usage.retention_days)
                    
            except (json.JSONDecodeError, IOError) as e:
                # Log but continue with defaults
                print(f"[tokenqrusher] Warning: Failed to load config: {e}")
        
        return config
    
    def save(self, config_path: Path) -> None:
        """Save configuration to file."""
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_dict = {
            'budget': {
                'daily': self.budget.daily,
                'weekly': self.budget.weekly,
                'monthly': self.budget.monthly,
                'warning_threshold': self.budget.warning_threshold,
                'critical_threshold': self.budget.critical_threshold,
                'auto_downgrade': self.budget.auto_downgrade
            },
            'usage': {
                'state_dir': str(self.usage.state_dir),
                'state_file': self.usage.state_file,
                'retention_days': self.usage.retention_days,
                'poll_interval_seconds': self.usage.poll_interval_seconds
            }
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_dict, f, indent=2)


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: Optional[Path] = None) -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load(config_path)
    return _config


def reset_config() -> None:
    """Reset global config (mainly for testing)."""
    global _config
    _config = None
