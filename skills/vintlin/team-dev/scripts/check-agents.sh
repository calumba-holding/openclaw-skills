#!/bin/bash
# check-agents.sh - Monitor running agents
# Skill: team-dev

set -e

# Get skill directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TASKS_FILE="$SKILL_DIR/active-tasks.json"
NOTIFY_FILE="$SKILL_DIR/notifications.json"
MAX_RETRIES=3

echo "Checking agents..."

if [[ ! -f "$TASKS_FILE" ]]; then
    echo "No tasks file found"
    exit 0
fi

# Initialize notifications
NOTIFICATIONS=()

# Check each running agent
TEMP_FILE=$(mktemp)
cp "$TASKS_FILE" "$TEMP_FILE"

python3 << 'PYEOF'
import json
import subprocess
import os
import sys

with open('%s' % '$TEMP_FILE', 'r') as f:
    data = json.load(f)

needs_update = False
notifications = []

for agent in data.get('agents', []):
    if agent.get('status') != 'running':
        continue
    
    session = agent.get('tmuxSession', '')
    repo = agent.get('repo', '')
    branch = agent.get('branch', '')
    description = agent.get('description', '')
    retry_count = agent.get('retryCount', 0)
    
    # Check if tmux session exists
    result = subprocess.run(['tmux', 'has-session', '-t', session], 
                          capture_output=True)
    
    if result.returncode != 0:
        # Session dead - check if PR was created
        print(f"Session {session} died")
        
        # Check for PR
        pr_check = subprocess.run(['gh', 'pr', 'list', '--head', branch], 
                                 capture_output=True, text=True, cwd=repo if os.path.exists(repo) else None)
        
        if pr_check.stdout.strip():
            agent['status'] = 'done'
            agent['completedAt'] = int(subprocess.run(['date', '+%s'], 
                                                      capture_output=True).stdout.strip()) * 1000
            agent['checks'] = {'prCreated': True}
            print(f"✓ Agent {session} completed - PR created")
            notifications.append({
                'type': 'success',
                'message': f'✅ PR 已创建: {description}',
                'repo': repo,
                'branch': branch
            })
            needs_update = True
        else:
            # No PR - check retry count
            if retry_count >= %d:
                agent['status'] = 'failed'
                print(f"✗ Agent {session} failed after {retry_count} retries")
                notifications.append({
                    'type': 'error',
                    'message': f'❌ 任务失败: {description}',
                    'repo': repo,
                    'branch': branch
                })
            else:
                agent['retryCount'] = retry_count + 1
                print(f"⚠ Agent {session} dead, will retry ({retry_count + 1}/%d)" % (retry_count + 1))
            needs_update = True

if needs_update:
    with open('%s' % '$TEMP_FILE', 'w') as f:
        json.dump(data, f, indent=2)
    print("Updated task registry")

# Update active count
data['activeCount'] = len([a for a in data.get('agents', []) if a.get('status') == 'running'])
with open('%s' % '$TEMP_FILE', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Active agents: {data['activeCount']}")

# Write notifications for OpenClaw to pick up
if notifications:
    with open('%s' % '$NOTIFY_FILE', 'w') as f:
        json.dump(notifications, f, indent=2)
    print(f"Written {len(notifications)} notifications")
PYEOF

rm "$TEMP_FILE"
