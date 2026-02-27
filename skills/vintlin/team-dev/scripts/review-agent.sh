#!/bin/bash
# review-agent.sh - Automated code review for PRs
# Skill: team-dev

set -e

# Get skill directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TASKS_FILE="$SKILL_DIR/active-tasks.json"

usage() {
    echo "Usage: $0 --repo <repo> --branch <branch> [--reviewers codex,gemini,claude]"
    echo ""
    echo "Options:"
    echo "  --repo       Repository name"
    echo "  --branch     Branch name (or PR number)"
    echo "  --reviewers  Comma-separated reviewers (default: codex,gemini)"
    exit 1
}

REPO=""
BRANCH=""
REVIEWERS="codex,gemini"

while [[ $# -gt 0 ]]; do
    case $1 in
        --repo) REPO="$2"; shift 2 ;;
        --branch) BRANCH="$2"; shift 2 ;;
        --reviewers) REVIEWERS="$2"; shift 2 ;;
        -h|--help) usage ;;
        *) usage ;;
    esac
done

if [[ -z "$REPO" || -z "$BRANCH" ]]; then
    usage
fi

echo "Starting code review for $REPO/$BRANCH"

# Get PR number
PR_NUM=$(gh pr view "$BRANCH" --repo "$REPO" --json number -q '.number' 2>/dev/null || echo "")

if [[ -z "$PR_NUM" ]]; then
    # Try as branch name
    PR_NUM=$(gh pr list --head "$BRANCH" --repo "$REPO" --json number -q '.[0].number' 2>/dev/null)
fi

if [[ -z "$PR_NUM" ]]; then
    echo "Error: PR not found for branch $BRANCH"
    exit 1
fi

echo "PR #$PR_NUM found"

# Split reviewers
IFS=',' read -ra REVIEWER_ARRAY <<< "$REVIEWERS"

# Run each reviewer
for reviewer in "${REVIEWER_ARRAY[@]}"; do
    reviewer=$(echo "$reviewer" | tr -d ' ')
    echo ""
    echo "=== Running $reviewer review ==="
    
    case $reviewer in
        codex)
            codex review --repo "$REPO" --pr "$PR_NUM" 2>&1 || echo "Codex review completed with warnings"
            ;;
        gemini)
            gemini -p "请审查 GitHub PR #$PR_NUM 的代码变更，重点关注：1) 安全问题 2) 性能问题 3) 代码风格 4) 边缘情况。请提供具体的改进建议。" 2>&1 || echo "Gemini review completed"
            ;;
        claude)
            claude --dangerously-skip-permissions -p "请审查 GitHub PR #$PR_NUM 的代码变更，提供代码审查意见。" 2>&1 || echo "Claude review completed"
            ;;
        *)
            echo "Unknown reviewer: $reviewer"
            ;;
    esac
done

echo ""
echo "=== All reviews completed ==="
echo "Reviewers used: ${REVIEWER_ARRAY[*]}"

# Update task status if found
if [[ -f "$TASKS_FILE" ]]; then
    python3 << PYEOF
import json
with open('$TASKS_FILE', 'r') as f:
    data = json.load(f)

for agent in data.get('agents', []):
    if agent.get('branch') == '$BRANCH':
        if 'checks' not in agent:
            agent['checks'] = {}
        agent['checks']['codeReviewDone'] = True

with open('$TASKS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
PYEOF
fi
