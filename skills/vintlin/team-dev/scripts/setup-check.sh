#!/bin/bash
# setup-check.sh - First-time setup verification
# Skill: team-dev

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Team Dev Skill Setup Check ==="
echo ""

ISSUES=0

# Check 1: Script permissions
echo "Checking script permissions..."
for script in "$SCRIPT_DIR"/*.sh; do
    if [[ -x "$script" ]]; then
        echo -e "  ✓ $(basename $script) is executable"
    else
        echo -e "  ✗ $(basename $script) is NOT executable"
        ISSUES=$((ISSUES + 1))
    fi
done
echo ""

# Check 2: tmux
echo "Checking tmux..."
if command -v tmux &> /dev/null; then
    VERSION=$(tmux -V)
    echo -e "  ✓ tmux installed: $VERSION"
else
    echo -e "  ✗ tmux NOT installed"
    echo "    Install with: brew install tmux"
    ISSUES=$((ISSUES + 1))
fi
echo ""

# Check 3: Required CLIs
echo "Checking required CLIs..."
for cli in gh codex claude gemini cursor; do
    if command -v $cli &> /dev/null; then
        echo -e "  ✓ $cli available"
    else
        echo -e "  ✗ $cli NOT found"
        ISSUES=$((ISSUES + 1))
    fi
done
echo ""

# Check 4: Directories
echo "Checking directories..."
for dir in logs references; do
    if [[ -d "$SKILL_DIR/$dir" ]]; then
        echo -e "  ✓ $dir/ exists"
    else
        echo -e "  ✗ $dir/ missing, creating..."
        mkdir -p "$SKILL_DIR/$dir"
    fi
done
echo ""

# Check 5: Active tasks file
echo "Checking task registry..."
if [[ -f "$SKILL_DIR/active-tasks.json" ]]; then
    echo -e "  ✓ active-tasks.json exists"
else
    echo -e "  ⚠ active-tasks.json not found, will be created on first use"
    echo '{}' > "$SKILL_DIR/active-tasks.json"
fi
echo ""

# Summary
echo "=== Summary ==="
if [[ $ISSUES -eq 0 ]]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Configure cron (see references/initialization.md)"
    echo "  2. Spawn your first agent:"
    echo "     ./scripts/spawn-agent.sh --agent codex --repo my-repo --branch fix/test --description 'test' --prompt 'hello'"
else
    echo -e "${RED}✗ $ISSUES issue(s) found${NC}"
    echo ""
    echo "Please fix the issues above before continuing."
fi
