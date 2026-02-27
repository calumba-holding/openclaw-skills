#!/bin/bash
# spawn-agent.sh - Spawn a coding agent for a task
# Skill: team-dev

set -e

# Get skill directory dynamically (works for any installation path)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TASKS_FILE="$SKILL_DIR/active-tasks.json"
LOGS_DIR="$SKILL_DIR/logs"
MAX_AGENTS=5

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    echo "Usage: $0 --agent <codex|claude|gemini|cursor> --repo <repo> --branch <branch> --description <desc> --prompt <prompt>"
    exit 1
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --agent) AGENT="$2"; shift 2 ;;
        --repo) REPO="$2"; shift 2 ;;
        --branch) BRANCH="$2"; shift 2 ;;
        --description) DESCRIPTION="$2"; shift 2 ;;
        --prompt) PROMPT="$2"; shift 2 ;;
        *) usage ;;
    esac
done

# Validate required arguments
if [[ -z "$AGENT" || -z "$REPO" || -z "$BRANCH" || -z "$DESCRIPTION" || -z "$PROMPT" ]]; then
    usage
fi

# Validate agent type
case $AGENT in
    codex|claude|gemini|cursor) ;;
    *) echo -e "${RED}Error: Invalid agent type: $AGENT${NC}"; usage ;;
esac

echo -e "${GREEN}Spawning $AGENT agent for: $DESCRIPTION${NC}"

# Check current agent count
if [[ -f "$TASKS_FILE" ]]; then
    ACTIVE_COUNT=$(grep -o '"status": "running"' "$TASKS_FILE" | wc -l || echo 0)
else
    ACTIVE_COUNT=0
fi

if [[ $ACTIVE_COUNT -ge $MAX_AGENTS ]]; then
    echo -e "${RED}Error: Maximum agents ($MAX_AGENTS) already running${NC}"
    exit 1
fi

# Create worktree directory
WORKTREE_DIR="../${REPO}-${BRANCH//\//-}"
SESSION_NAME="${AGENT}-${BRANCH//\//-}"

echo "Creating worktree: $WORKTREE_DIR"

# Check if repo exists
if [[ ! -d "$REPO" ]]; then
    echo -e "${YELLOW}Warning: Repo $REPO not found locally${NC}"
    echo "Creating minimal repo structure..."
    mkdir -p "$REPO"
    cd "$REPO"
    git init
    git commit --allow-empty -m "Initial commit"
    cd ..
fi

# Create worktree
cd "$REPO"
if [[ ! -d "../$WORKTREE_DIR" ]]; then
    git worktree add "../$WORKTREE_DIR" -b "$BRANCH" 2>/dev/null || git checkout -b "$BRANCH"
else
    echo "Worktree already exists"
fi
cd "../$WORKTREE_DIR"

# Install dependencies if package.json exists
if [[ -f "package.json" ]]; then
    pnpm install 2>/dev/null || npm install 2>/dev/null || echo "No dependencies to install"
fi
cd "$SCRIPT_DIR"

# Build command based on agent type
case $AGENT in
    codex)
        CMD="codex exec --dangerously-bypass-approvals-and-sandbox -C '$WORKTREE_DIR' '$PROMPT'"
        ;;
    claude)
        CMD="claude --dangerously-skip-permissions -p '$PROMPT'"
        ;;
    gemini)
        CMD="gemini -p '$PROMPT'"
        ;;
    cursor)
        CMD="cursor agent -f -p --workspace '$WORKTREE_DIR' '$PROMPT'"
        ;;
esac

# Create tmux session
tmux new-session -d -s "$SESSION_NAME" -c "$LOGS_DIR" "$CMD" 2>/dev/null || \
    tmux send-keys -t "$SESSION_NAME" "cd $WORKTREE_DIR && $CMD" Enter

# Update tasks file
TIMESTAMP=$(date +%s)000
TEMP_FILE=$(mktemp)

if [[ -f "$TASKS_FILE" ]]; then
    # Add new agent to existing file
    python3 -c "
import json
with open('$TASKS_FILE', 'r') as f:
    data = json.load(f)
data['agents'].append({
    'id': '$BRANCH',
    'tmuxSession': '$SESSION_NAME',
    'agent': '$AGENT',
    'description': '$DESCRIPTION',
    'repo': '$REPO',
    'worktree': '$WORKTREE_DIR',
    'branch': '$BRANCH',
    'startedAt': $TIMESTAMP,
    'status': 'running',
    'notifyOnComplete': True
})
data['activeCount'] = len([a for a in data['agents'] if a.get('status') == 'running'])
with open('$TEMP_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
else
    # Create new file
    python3 -c "
import json
data = {
    'agents': [{
        'id': '$BRANCH',
        'tmuxSession': '$SESSION_NAME',
        'agent': '$AGENT',
        'description': '$DESCRIPTION',
        'repo': '$REPO',
        'worktree': '$WORKTREE_DIR',
        'branch': '$BRANCH',
        'startedAt': $TIMESTAMP,
        'status': 'running',
        'notifyOnComplete': True
    }],
    'maxAgents': $MAX_AGENTS,
    'activeCount': 1
}
with open('$TEMP_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
fi

mv "$TEMP_FILE" "$TASKS_FILE"

echo -e "${GREEN}Agent spawned successfully!${NC}"
echo "Session: $SESSION_NAME"
echo "Worktree: $WORKTREE_DIR"
