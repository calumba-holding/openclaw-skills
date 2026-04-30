#!/bin/bash
# Dispatch Installation Script
# Runs interactive setup FIRST, then installs files

set -e

echo "🚀 Dispatch Installation"
echo ""

# Determine paths
if [ -z "$OPENCLAW_WORKSPACE" ]; then
    OPENCLAW_WORKSPACE="$HOME/.openclaw/workspace"
fi

SKILL_DIR="$HOME/.openclaw/skills/dispatch"
DATA_DIR="$OPENCLAW_WORKSPACE/.dispatch"
AGENTS_FILE="$OPENCLAW_WORKSPACE/AGENTS.md"
TOOLS_FILE="$OPENCLAW_WORKSPACE/TOOLS.md"
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ============================================
# STEP 1: Detect configuration BEFORE installing anything
# ============================================

echo "📋 Detecting your OpenClaw configuration..."
echo ""

# Detect providers from openclaw.json
DETECTED_PROVIDERS=""
if [ -f "$OPENCLAW_CONFIG" ]; then
    # Extract provider names from model IDs (format: provider/model or just model name)
    DETECTED_PROVIDERS=$(cat "$OPENCLAW_CONFIG" 2>/dev/null | grep -oE '"[^"]+"' | tr -d '"' | grep -E '^(google|openrouter|anthropic|kimi|openai)/' | cut -d'/' -f1 | sort -u | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')
    
    # Also check for pattern matches in model names
    if [ -z "$DETECTED_PROVIDERS" ]; then
        MODELS=$(cat "$OPENCLAW_CONFIG" 2>/dev/null | grep -oE '"[^"]+"' | tr -d '"')
        [ -n "$MODELS" ] && echo "$MODELS" | grep -qi "gemini" && DETECTED_PROVIDERS="google"
        [ -n "$MODELS" ] && echo "$MODELS" | grep -qi "claude" && DETECTED_PROVIDERS="${DETECTED_PROVIDERS:+$DETECTED_PROVIDERS, }anthropic"
        [ -n "$MODELS" ] && echo "$MODELS" | grep -qi "kimi" && DETECTED_PROVIDERS="${DETECTED_PROVIDERS:+$DETECTED_PROVIDERS, }kimi"
        [ -n "$MODELS" ] && echo "$MODELS" | grep -qi "gpt" && DETECTED_PROVIDERS="${DETECTED_PROVIDERS:+$DETECTED_PROVIDERS, }openai"
    fi
fi

# Detect agents
DETECTED_AGENTS=""
DETECTED_CAPTAIN=""
if [ -f "$OPENCLAW_CONFIG" ]; then
    # Try to extract agent IDs
    DETECTED_AGENTS=$(cat "$OPENCLAW_CONFIG" 2>/dev/null | grep -oE '"id":\s*"[^"]+"' | cut -d'"' -f4 | tr '\n' ', ' | sed 's/, $//')
    
    # Look for 'echo' agent as default captain
    if echo "$DETECTED_AGENTS" | grep -qw "echo"; then
        DETECTED_CAPTAIN="echo"
    else
        DETECTED_CAPTAIN=$(echo "$DETECTED_AGENTS" | cut -d',' -f1 | tr -d ' ')
    fi
fi

# Default values if detection failed
[ -z "$DETECTED_PROVIDERS" ] && DETECTED_PROVIDERS="(none detected - will need manual setup)"
[ -z "$DETECTED_AGENTS" ] && DETECTED_AGENTS="(none detected)"
[ -z "$DETECTED_CAPTAIN" ] && DETECTED_CAPTAIN="(none detected - will need manual selection)"

# ============================================
# STEP 2: Show summary and ask for confirmation
# ============================================

echo "═══════════════════════════════════════════════════════════════"
echo "                 Detected Configuration"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "  1. Providers:     $DETECTED_PROVIDERS"
echo "  2. Agents:        $DETECTED_AGENTS"
echo "  3. Captain:       $DETECTED_CAPTAIN"
echo "  4. Data directory: $DATA_DIR"
echo "  5. Output dir:    $OPENCLAW_WORKSPACE/dispatch"
echo "  6. Auto-check:    weekly"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Ask if happy with defaults
read -p "Are you happy with these settings? [Y/n]: " HAPPY
HAPPY=${HAPPY:-Y}

if [[ ! "$HAPPY" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running interactive setup wizard..."
    echo ""
    
    # Run the interactive Node.js setup
    if [ -f "$SCRIPT_DIR/lib/setup.js" ]; then
        node "$SCRIPT_DIR/lib/setup.js"
    else
        echo "❌ Error: setup.js not found at $SCRIPT_DIR/lib/setup.js"
        exit 1
    fi
    
    # After interactive setup, continue with file installation
    echo ""
    echo "Continuing with file installation..."
fi

echo ""
echo "📦 Installing Dispatch files..."
echo ""

# ============================================
# STEP 3: NOW install files (after confirmation)
# ============================================

# Create directories
echo "Creating directories..."
mkdir -p "$SKILL_DIR"
mkdir -p "$DATA_DIR/projects"
mkdir -p "$DATA_DIR/templates"
mkdir -p "$DATA_DIR/logs"

# Copy skill files
echo "Installing skill files..."
cp -r "$SCRIPT_DIR/lib" "$SKILL_DIR/"
cp -r "$SCRIPT_DIR/config" "$SKILL_DIR/"
[ -d "$SCRIPT_DIR/bin" ] && cp -r "$SCRIPT_DIR/bin" "$SKILL_DIR/" 2>/dev/null || true
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/"
cp "$SCRIPT_DIR/README.md" "$SKILL_DIR/"
cp "$SCRIPT_DIR/package.json" "$SKILL_DIR/"
cp "$SCRIPT_DIR/USER_GUIDE.md" "$SKILL_DIR/"

# Run npm install if package.json exists
if [ -f "$SCRIPT_DIR/package.json" ]; then
    echo "Installing dependencies..."
    cd "$SKILL_DIR" && npm install 2>/dev/null || echo "   (no dependencies to install)"
fi

# ============================================
# STEP 4: Run setup if user accepted defaults
# ============================================

if [[ "$HAPPY" =~ ^[Yy]$ ]]; then
    echo ""
    echo "⚙️  Running setup with detected defaults..."
    node "$SKILL_DIR/lib/setup.js" --auto
fi

# ============================================
# STEP 5: Update workspace documentation
# ============================================

# Add to AGENTS.md if not already present
if [ -f "$AGENTS_FILE" ]; then
    if ! grep -q "## Dispatch" "$AGENTS_FILE" 2>/dev/null; then
        echo "" >> "$AGENTS_FILE"
        echo "---" >> "$AGENTS_FILE"
        echo "" >> "$AGENTS_FILE"
        echo "## Dispatch" >> "$AGENTS_FILE"
        echo "" >> "$AGENTS_FILE"
        echo "Natural language project management. No CLI needed." >> "$AGENTS_FILE"
        echo "" >> "$AGENTS_FILE"
        echo '**Projects:** "Start project [name]" → review phases → approve' >> "$AGENTS_FILE"
        echo '**Phases:** "Estimate [phase]" → "Run [phase]" → track costs' >> "$AGENTS_FILE"
        echo '**Status:** "What'\''s the cost?" | "Show project status"' >> "$AGENTS_FILE"
        echo '**Models:** "Check for new models" | "Update pricing"' >> "$AGENTS_FILE"
        echo '**Trust:** "This is sensitive" → uses trusted models only' >> "$AGENTS_FILE"
        echo "   ✓ Added Dispatch section to AGENTS.md"
    else
        echo "   ℹ Dispatch already in AGENTS.md"
    fi
else
    # Create minimal AGENTS.md
    echo "## Dispatch" > "$AGENTS_FILE"
    echo "" >> "$AGENTS_FILE"
    echo "Natural language project management. No CLI needed." >> "$AGENTS_FILE"
    echo "" >> "$AGENTS_FILE"
    echo '**Projects:** "Start project [name]" → review phases → approve' >> "$AGENTS_FILE"
    echo '**Phases:** "Estimate [phase]" → "Run [phase]" → track costs' >> "$AGENTS_FILE"
    echo '**Status:** "What'\''s the cost?" | "Show project status"' >> "$AGENTS_FILE"
    echo '**Models:** "Check for new models" | "Update pricing"' >> "$AGENTS_FILE"
    echo '**Trust:** "This is sensitive" → uses trusted models only' >> "$AGENTS_FILE"
    echo "   ✓ Created AGENTS.md with Dispatch guide"
fi

# Add to TOOLS.md if not already present
if [ -f "$TOOLS_FILE" ]; then
    if ! grep -q "### Dispatch" "$TOOLS_FILE" 2>/dev/null; then
        echo "" >> "$TOOLS_FILE"
        echo "### Dispatch Skill" >> "$TOOLS_FILE"
        echo "- Location: \`$SKILL_DIR\`" >> "$TOOLS_FILE"
        echo "- Data: \`$DATA_DIR\`" >> "$TOOLS_FILE"
        echo "- Config: \`$SKILL_DIR/config/\`" >> "$TOOLS_FILE"
        echo "   ✓ Added Dispatch to TOOLS.md"
    else
        echo "   ℹ Dispatch already in TOOLS.md"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                 ✓ Dispatch installed!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Try: \"Start project My Project\""
echo ""
