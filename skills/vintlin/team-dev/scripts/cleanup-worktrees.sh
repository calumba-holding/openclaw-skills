#!/bin/bash
# cleanup-worktrees.sh - Clean up merged worktrees
# Skill: team-dev

set -e

# Get skill directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TASKS_FILE="$SKILL_DIR/active-tasks.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Cleaning up worktrees..."

# Get all worktrees from all repos in tasks
if [[ -f "$TASKS_FILE" ]]; then
    python3 << EOF
import json
import subprocess
import os

with open('$TASKS_FILE', 'r') as f:
    data = json.load(f)

cleaned = []

for agent in data.get('agents', []):
    if agent.get('status') not in ['done', 'failed', 'merged']:
        continue
    
    repo = agent.get('repo', '')
    worktree = agent.get('worktree', '')
    branch = agent.get('branch', '')
    
    # Check if branch was merged
    if repo and os.path.exists(repo):
        result = subprocess.run(
            ['git', 'branch', '--merged', 'main'],
            cwd=repo, capture_output=True, text=True
        )
        
        if branch in result.stdout or 'main' in result.stdout:
            # Remove worktree
            if os.path.exists(worktree):
                subprocess.run(['git', 'worktree', 'remove', '--force', worktree], cwd=repo)
                print(f"Removed worktree: {worktree}")
                cleaned.append(worktree)
            
            # Remove branch
            subprocess.run(['git', 'branch', '-d', branch], cwd=repo, capture_output=True)
            print(f"Removed branch: {branch}")

# Update tasks file - remove cleaned agents
data['agents'] = [a for a in data.get('agents', []) 
                  if a.get('status') not in ['done', 'failed', 'merged'] 
                  or a.get('worktree') not in cleaned]

with open('$TASKS_FILE', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Cleaned {len(cleaned)} worktrees")
EOF
else
    echo "No tasks file found"
fi

echo "Cleanup complete"
