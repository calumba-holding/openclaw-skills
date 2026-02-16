#!/usr/bin/env python3
"""
Scheduler - Cron job management for tokenQrusher.

Provides integration with OpenClaw's native cron system.
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

# Import optimizer
sys.path.insert(0, str(Path(__file__).parent))
from optimizer import CronOptimizer, TriggerReason, OptimizationResult

logging.basicConfig(
    level=logging.INFO,
    format='[scheduler] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ScheduledJob:
    """Scheduled optimization job."""
    name: str
    interval_seconds: int
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None


class Scheduler:
    """
    Manages scheduled optimization jobs.
    
    Integrates with OpenClaw's cron system via the `cron` CLI.
    """
    
    # Default job definitions
    DEFAULT_JOBS = {
        'optimize': {
            'interval': 3600,  # 1 hour
            'description': 'Run token optimization'
        },
        'rotate_model': {
            'interval': 7200,  # 2 hours
            'description': 'Rotate model tier based on budget'
        },
        'check_budget': {
            'interval': 300,   # 5 minutes
            'description': 'Check budget thresholds'
        }
    }
    
    def __init__(self, state_dir: Optional[Path] = None):
        """Initialize scheduler."""
        self._state_dir = state_dir or Path.home() / '.openclaw/workspace/memory'
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._optimizer = CronOptimizer(state_dir=self._state_dir)
        self._jobs: Dict[str, ScheduledJob] = {}
        
        # Initialize jobs
        for name, config in self.DEFAULT_JOBS.items():
            self._jobs[name] = ScheduledJob(
                name=name,
                interval_seconds=config['interval'],
                enabled=True
            )
        
        logger.info("Scheduler initialized")
    
    def _get_job_state_file(self, job_name: str) -> Path:
        """Get path to job state file."""
        return self._state_dir / f'cron-job-{job_name}.json'
    
    def _load_job_state(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Load job state from disk."""
        state_file = self._get_job_state_file(job_name)
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return None
    
    def _save_job_state(self, job_name: str, state: Dict[str, Any]) -> None:
        """Save job state to disk."""
        state_file = self._get_job_state_file(job_name)
        
        try:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except IOError as e:
            logger.warning(f"Failed to save job state: {e}")
    
    def run_job(self, job_name: str) -> bool:
        """
        Run a specific job.
        
        Args:
            job_name: Name of job to run
            
        Returns:
            True if job executed successfully
        """
        if job_name not in self._jobs:
            logger.error(f"Unknown job: {job_name}")
            return False
        
        job = self._jobs[job_name]
        
        if not job.enabled:
            logger.info(f"Job {job_name} is disabled, skipping")
            return False
        
        logger.info(f"Running job: {job_name}")
        
        try:
            # Run optimization
            if job_name == 'optimize':
                result = self._optimizer.optimize(trigger=TriggerReason.SCHEDULED)
                success = result.result in (OptimizationResult.SUCCESS, 
                                          OptimizationResult.NO_OP,
                                          OptimizationResult.PARTIAL_SUCCESS)
            
            elif job_name == 'rotate_model':
                result = self._optimizer.optimize(trigger=TriggerReason.BUDGET_WARNING)
                success = True  # Always succeeds
            
            elif job_name == 'check_budget':
                status = self._optimizer.get_status()
                success = True
            
            else:
                success = False
            
            # Update job state
            job.last_run = datetime.now()
            job.next_run = datetime.now() + timedelta(seconds=job.interval_seconds)
            
            self._save_job_state(job_name, {
                'last_run': job.last_run.isoformat(),
                'next_run': job.next_run.isoformat(),
                'success': success
            })
            
            logger.info(f"Job {job_name} completed: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Job {job_name} failed: {e}")
            self._save_job_state(job_name, {
                'error': str(e),
                'last_run': datetime.now().isoformat()
            })
            return False
    
    def get_job_status(self, job_name: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job."""
        if job_name not in self._jobs:
            return None
        
        job = self._jobs[job_name]
        
        # Try to load saved state
        saved_state = self._load_job_state(job_name)
        
        return {
            'name': job.name,
            'enabled': job.enabled,
            'interval_seconds': job.interval_seconds,
            'last_run': job.last_run.isoformat() if job.last_run else None,
            'next_run': job.next_run.isoformat() if job.next_run else None,
            'saved_state': saved_state
        }
    
    def get_all_status(self) -> List[Dict[str, Any]]:
        """Get status of all jobs."""
        return [
            self.get_job_status(name)
            for name in self._jobs.keys()
        ]
    
    def enable_job(self, job_name: str) -> bool:
        """Enable a job."""
        if job_name not in self._jobs:
            return False
        self._jobs[job_name].enabled = True
        return True
    
    def disable_job(self, job_name: str) -> bool:
        """Disable a job."""
        if job_name not in self._jobs:
            return False
        self._jobs[job_name].enabled = False
        return True
    
    def list_jobs(self) -> List[str]:
        """List all job names."""
        return list(self._jobs.keys())


def list_jobs_cli(args) -> int:
    """CLI: List all scheduled jobs."""
    scheduler = Scheduler()
    jobs = scheduler.get_all_status()
    
    if args.json:
        print(json.dumps(jobs, indent=2))
    else:
        print("=== Scheduled Jobs ===")
        for job in jobs:
            status = "✓" if job['enabled'] else "✗"
            print(f"{status} {job['name']}: every {job['interval_seconds']}s")
            print(f"   Last: {job['last_run'] or 'never'}")
            print(f"   Next: {job['next_run'] or 'N/A'}")
    
    return 0


def run_job_cli(args) -> int:
    """CLI: Run a specific job."""
    scheduler = Scheduler()
    
    success = scheduler.run_job(args.job)
    
    if args.json:
        print(json.dumps({'success': success, 'job': args.job}, indent=2))
    else:
        print(f"Job {args.job}: {'SUCCESS' if success else 'FAILED'}")
    
    return 0 if success else 1


def status_cli(args) -> int:
    """CLI: Show scheduler status."""
    scheduler = Scheduler()
    optimizer_status = scheduler._optimizer.get_status()
    
    if args.json:
        print(json.dumps({
            'scheduler': scheduler.get_all_status(),
            'optimizer': optimizer_status
        }, indent=2))
    else:
        print("=== Scheduler Status ===")
        print(f"State: {optimizer_status['state']}")
        print(f"Last run: {optimizer_status['last_run']}")
        print(f"Failures: {optimizer_status['consecutive_failures']}")
        print(f"Quiet hours: {optimizer_status['quiet_hours_active']}")
        print()
        print("Jobs:")
        for job in scheduler.get_all_status():
            status = "✓" if job['enabled'] else "✗"
            print(f"  {status} {job['name']}")
    
    return 0


def enable_cli(args) -> int:
    """CLI: Enable a job."""
    scheduler = Scheduler()
    success = scheduler.enable_job(args.job)
    
    if args.json:
        print(json.dumps({'enabled': success, 'job': args.job}, indent=2))
    else:
        print(f"Job {args.job}: {'enabled' if success else 'not found'}")
    
    return 0 if success else 1


def disable_cli(args) -> int:
    """CLI: Disable a job."""
    scheduler = Scheduler()
    success = scheduler.disable_job(args.job)
    
    if args.json:
        print(json.dumps({'disabled': success, 'job': args.job}, indent=2))
    else:
        print(f"Job {args.job}: {'disabled' if success else 'not found'}")
    
    return 0 if success else 1


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cron Scheduler for tokenQrusher')
    
    subparsers = parser.add_subparsers(dest='command', help='Command')
    
    # list
    list_parser = subparsers.add_parser('list', help='List scheduled jobs')
    list_parser.add_argument('--json', action='store_true', help='JSON output')
    
    # run
    run_parser = subparsers.add_parser('run', help='Run a job')
    run_parser.add_argument('job', help='Job name')
    run_parser.add_argument('--json', action='store_true', help='JSON output')
    
    # status
    status_parser = subparsers.add_parser('status', help='Show scheduler status')
    status_parser.add_argument('--json', action='store_true', help='JSON output')
    
    # enable
    enable_parser = subparsers.add_parser('enable', help='Enable a job')
    enable_parser.add_argument('job', help='Job name')
    enable_parser.add_argument('--json', action='store_true', help='JSON output')
    
    # disable
    disable_parser = subparsers.add_parser('disable', help='Disable a job')
    disable_parser.add_argument('job', help='Job name')
    disable_parser.add_argument('--json', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    commands = {
        'list': list_jobs_cli,
        'run': run_job_cli,
        'status': status_cli,
        'enable': enable_cli,
        'disable': disable_cli
    }
    
    return commands[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
