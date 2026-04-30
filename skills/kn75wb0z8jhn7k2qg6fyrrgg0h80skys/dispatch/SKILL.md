---
name: dispatch
description: AI-native project management with cost estimates, phased execution, multi-agent coordination, and privacy-aware model selection. Use for complex multi-step work requiring cost transparency and agent orchestration.
---

# Dispatch

Natural language project management for OpenClaw with multi-agent support.

## When to Use

- Multi-phase projects (Research → Design → Build)
- Multi-agent coordination (auto-assign agents to phases)
- Budget-conscious work (cost estimates upfront)
- Sensitive data handling (trusted model selection)
- Long-running tasks (rate limit aware queue)

## Installation (For AI Agents)

**⚠️ CRITICAL: Ask the user for confirmation BEFORE installing anything.**

When the user asks you to install Dispatch, follow this exact flow:

### Step 1: Detect Configuration

Run this to detect their OpenClaw setup:
```bash
# Read their config to detect providers and agents
cat ~/.openclaw/openclaw.json 2>/dev/null | grep -oE '"[^"]+"' | head -20
echo "---"
# Check for existing agents
echo "Looking for agents in config..."
```

### Step 2: Present Configuration to User

Show them what you detected and ask for confirmation:

```
🚀 Dispatch Installation

I'm about to install the Dispatch skill. Here's what I detected:

═══════════════════════════════════════════════════════════════
              Detected Configuration
═══════════════════════════════════════════════════════════════

  1. Providers:     [google, kimi, openrouter, etc.]
  2. Agents:        [echo, cipher, rift, etc.]
  3. Captain:       [echo or first available]
  4. Data directory: ~/.openclaw/workspace/.dispatch
  5. Output dir:    ~/.openclaw/workspace/dispatch
  6. Auto-check:    weekly

═══════════════════════════════════════════════════════════════

Proceed with these settings? [yes/no/custom]

• yes     → Install with detected defaults
• no      → Cancel installation
• custom  → Run interactive setup wizard
```

### Step 3: Only Proceed After Confirmation

**DO NOT install anything until the user explicitly responds.**

If they say **yes**:
```bash
git clone https://github.com/Neidraidd/dispatch.git ~/.openclaw/skills/dispatch
cd ~/.openclaw/skills/dispatch
bash install.sh
# When install.sh asks "Are you happy with these settings?", answer "Y"
```

If they say **custom**:
```bash
git clone https://github.com/Neidraidd/dispatch.git ~/.openclaw/skills/dispatch
cd ~/.openclaw/skills/dispatch
bash install.sh
# When install.sh asks "Are you happy with these settings?", answer "N"
# This will run the interactive wizard
```

If they say **no**: Stop and do not install.

## Manual Installation (For Users)

```bash
git clone https://github.com/neidraidd/dispatch.git ~/.openclaw/skills/dispatch
cd ~/.openclaw/skills/dispatch && bash install.sh
```

The install script will:
1. Detect your OpenClaw configuration
2. Show you what was detected
3. Ask for confirmation before making any changes
4. Run setup (auto or interactive based on your choice)
5. Install files and update documentation

## Quick Start

```
You: Start project "API Migration"

Dispatch: 🚀 Project: 20260208-api-migration
           Captain: echo
           Suggested phases:
             1. Discovery (~$1.20) → cipher
             2. Design (~$2.50) → cipher
             3. Implementation (~$5.00) → rift
             4. Documentation (~$0.80) → void
           
           Proceed? (yes/edit/abort)
```

## Commands

| Natural Language | Result |
|------------------|--------|
| "Start project [name]" | Create with phase preview & agent assignments |
| "Estimate phase [n]" | Show cost breakdown |
| "Run phase [name]" | Execute with tracking |
| "Add phase [name]" | Extend project |
| "Check for new models" | Detect OpenClaw changes |
| "Update pricing" | Refresh model configs |

## Configuration Files

- `~/.openclaw/workspace/.dispatch/` — Internal project data (JSON metadata, costs, logs)
- `~/.openclaw/workspace/dispatch/` — Project deliverables (HTML reports, documents) — **configurable**
- `~/.openclaw/skills/dispatch/config/pricing.json` — Model pricing
- `~/.openclaw/skills/dispatch/config/trust.json` — Trust levels

## Directory Structure

```
.dispatch/                    # Internal state (hidden)
├── config.json              # Skill configuration (includes output_dir, captain, agents)
├── projects/
│   └── [YYYYMMDD-name]/     # Date-first project IDs
│       ├── meta.json        # Project metadata
│       ├── costs.json       # Cost tracking
│       └── phases/
│           └── [NN-phase-name]/
│               ├── meta.json
│               └── tasks/
├── templates/
└── logs/

dispatch/                     # Output directory (configurable)
└── [YYYYMMDD-name]/          # Same date-first ID
    └── [NN-phase-name]/
        ├── AGENT_INSTRUCTIONS.md  # Tells agent what to create
        ├── research_report.html
        ├── design_report.html
        └── ... (deliverables)
```

## Multi-Agent Support

### Captain
One agent is designated as the **Captain**:
- Receives project requests from user
- Spawns sub-agents for each phase
- Tells each agent: what to do, what to name files, where to save

### Agent Assignment
Each phase is auto-assigned an agent based on type:
- **Research/Discovery** → cipher (Research & Architecture)
- **Design** → cipher or rift (System Design)
- **Implementation** → rift (Lead Engineer)
- **Testing** → ghost (Security & Monitoring)
- **Documentation** → void (The Scrapper)

Users can override assignments during project creation.

### Task Delegation
For each phase, Captain creates a `TASK_BRIEF.md` that tells the assigned agent:
- What task to complete
- Exact output path
- Exact filenames to use
- Who to report back to

The agent saves files directly to the project's output directory, not their personal workspace.

## Project ID Format

Projects are named with date-first IDs for chronological sorting:
- Format: `YYYYMMDD-sanitized-project-name`
- Example: `20260208-api-migration`
