#!/usr/bin/env python3
"""
Usage Tracker - Fetches and stores OpenClaw usage data.

Provides a robust interface to OpenClaw's /usage command and local caching.

Design Contract:
- All public methods are thread-safe via RLock
- No exceptions for control flow - return Either/Result types
- Logging only at entry, exit, error
- Immutability preferred
"""
import subprocess
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[usage-tracker] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# RESULT TYPE (No exceptions for control flow)
# =============================================================================

class ResultStatus(Enum):
    """Result status codes."""
    SUCCESS = auto()
    ERROR = auto()
    NOT_FOUND = auto()


@dataclass(frozen=True)
class Result:
    """Result type - success or error, no exceptions."""
    status: ResultStatus
    data: Any = None
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        return self.status == ResultStatus.SUCCESS
    
    @property
    def is_error(self) -> bool:
        return self.status == ResultStatus.ERROR


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class UsageRecord:
    """Single usage record."""
    timestamp: str
    cost: float
    input_tokens: int
    output_tokens: int
    session_key: Optional[str] = None
    model: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageRecord':
        return cls(**data)


@dataclass
class UsageSnapshot:
    """Usage snapshot for a time period."""
    period: str  # 'daily', 'weekly', 'monthly'
    start_date: str
    end_date: str
    total_cost: float
    total_input_tokens: int
    total_output_tokens: int
    record_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageSnapshot':
        return cls(**data)


class UsageTracker:
    """
    Tracks OpenClaw usage with local caching.
    
    Provides:
    - Fetch usage from OpenClaw
    - Local storage for historical data
    - Aggregation by time period
    """
    
    def __init__(
        self,
        state_dir: Path,
        state_file: str = 'usage-history.json',
        cache_ttl: int = 60  # Cache TTL in seconds
    ):
        """
        Initialize usage tracker.
        
        Args:
            state_dir: Directory for state files
            state_file: Name of state file
            cache_ttl: Cache time-to-live in seconds
        """
        self.state_dir = Path(state_dir)
        self.state_file = self.state_dir / state_file
        self.cache_ttl = cache_ttl
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: float = 0
        
        # Thread safety - RLock for reentrant locking
        self._lock = threading.RLock()
        
        # Ensure state directory exists
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self._data: List[UsageRecord] = []
        self._load_data()
    
    def _load_data(self) -> None:
        """Load usage data from disk."""
        if not self.state_file.exists():
            logger.info(f"No existing usage data at {self.state_file}")
            return
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                self._data = [UsageRecord.from_dict(r) for r in data]
                logger.info(f"Loaded {len(self._data)} usage records")
            else:
                logger.warning("Invalid usage data format")
                
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted usage data: {e}")
        except IOError as e:
            logger.error(f"Failed to load usage data: {e}")
    
    def _save_data(self) -> Result:
        """
        Save usage data to disk (thread-safe).
        
        Returns:
            Result indicating success or error
        """
        try:
            data = [r.to_dict() for r in self._data]
            
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Saved {len(self._data)} records")
            return Result(status=ResultStatus.SUCCESS)
            
        except IOError as e:
            logger.error(f"Failed to save usage data: {e}")
            return Result(status=ResultStatus.ERROR, error=str(e))
    
    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid."""
        if self._cache is None:
            return False
        return (time.time() - self._cache_time) < self.cache_ttl
    
    def fetch_from_openclaw(self) -> List[UsageRecord]:
        """
        Fetch current usage from OpenClaw.
        
        Returns:
            List of usage records from this session
            
        Note:
            This uses the session_status command which provides
            aggregated usage for the current session.
        """
        records = []
        
        try:
            # Try to get session status - use subprocess for proper resource management
            result = subprocess.run(
                ['openclaw', 'session', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            ).stdout
            
            if result and 'session_status' in result.lower():
                # Parse session status output
                # Format: varies but typically includes cost info
                logger.debug(f"Session status: {result[:200]}")
                
                # Try to parse JSON if present
                try:
                    data = json.loads(result)
                    if 'usage' in data:
                        usage = data['usage']
                        record = UsageRecord(
                            timestamp=datetime.now().isoformat(),
                            cost=usage.get('cost', 0.0),
                            input_tokens=usage.get('input_tokens', 0),
                            output_tokens=usage.get('output_tokens', 0),
                            model=usage.get('model', 'unknown')
                        )
                        records.append(record)
                except json.JSONDecodeError:
                    # Try to extract numbers from text
                    pass
                    
        except Exception as e:
            logger.warning(f"Failed to fetch from OpenClaw: {e}")
        
        return records
    
    def add_record(self, record: UsageRecord) -> Result:
        """
        Add a usage record (thread-safe).
        
        Args:
            record: Usage record to add
            
        Returns:
            Result indicating success or error
        """
        with self._lock:
            # Check for duplicates
            for existing in self._data:
                if existing.timestamp == record.timestamp:
                    return Result(status=ResultStatus.SUCCESS)  # Already exists
            
            self._data.append(record)
            
            save_result = self._save_data()
            if not save_result.is_success:
                return save_result
            
            logger.debug(f"Added record: {record.timestamp}")
            return Result(status=ResultStatus.SUCCESS)
    
    def get_daily_usage(self, days: int = 1) -> UsageSnapshot:
        """
        Get usage for the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Usage snapshot for the period
        """
        now = datetime.now()
        start = now - timedelta(days=days)
        
        records = [
            r for r in self._data
            if start.isoformat() <= r.timestamp <= now.isoformat()
        ]
        
        return UsageSnapshot(
            period='daily',
            start_date=start.isoformat(),
            end_date=now.isoformat(),
            total_cost=sum(r.cost for r in records),
            total_input_tokens=sum(r.input_tokens for r in records),
            total_output_tokens=sum(r.output_tokens for r in records),
            record_count=len(records)
        )
    
    def get_weekly_usage(self, weeks: int = 1) -> UsageSnapshot:
        """Get usage for the last N weeks."""
        return self.get_daily_usage(days=weeks * 7)
    
    def get_monthly_usage(self, months: int = 1) -> UsageSnapshot:
        """Get usage for the last N months."""
        return self.get_daily_usage(days=months * 30)
    
    def get_current_cost(self) -> float:
        """Get total cost for current period (today)."""
        return self.get_daily_usage(1).total_cost
    
    def get_all_records(self) -> List[UsageRecord]:
        """Get all usage records."""
        return sorted(self._data, key=lambda r: r.timestamp, reverse=True)
    
    def prune_old_records(self, keep_days: int = 30) -> Result:
        """
        Remove records older than keep_days (thread-safe).
        
        Args:
            keep_days: Number of days to keep
            
        Returns:
            Result with count of removed records
        """
        with self._lock:
            cutoff = datetime.now() - timedelta(days=keep_days)
            cutoff_str = cutoff.isoformat()
            
            original_count = len(self._data)
            self._data = [
                r for r in self._data
                if r.timestamp >= cutoff_str
            ]
            
            removed = original_count - len(self._data)
            
            if removed > 0:
                save_result = self._save_data()
                if not save_result.is_success:
                    return save_result
                logger.info(f"Pruned {removed} old records")
            
            return Result(status=ResultStatus.SUCCESS, data={'removed': removed})
        
        if removed > 0:
            self._save_data()
            logger.info(f"Pruned {removed} old records")
        
        return removed
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage summary."""
        daily = self.get_daily_usage(1)
        weekly = self.get_weekly_usage(1)
        monthly = self.get_monthly_usage(1)
        
        return {
            'daily': daily.to_dict(),
            'weekly': weekly.to_dict(),
            'monthly': monthly.to_dict(),
            'total_records': len(self._data)
        }


def get_tracker(state_dir: Optional[Path] = None) -> UsageTracker:
    """Get or create usage tracker instance."""
    if state_dir is None:
        state_dir = Path.home() / '.openclaw/workspace/memory'
    
    return UsageTracker(state_dir)


if __name__ == '__main__':
    # Test
    tracker = get_tracker()
    print(json.dumps(tracker.get_usage_summary(), indent=2))
