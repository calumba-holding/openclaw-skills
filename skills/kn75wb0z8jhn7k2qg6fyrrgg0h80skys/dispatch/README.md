# Dispatch 🚀

AI-native project management for OpenClaw. Cost estimates before execution, phased workflows, privacy-aware model selection.

## ⚠️ For AI Agents Installing This Skill

**CRITICAL: Follow this protocol or you will mess up the installation.**

1. **Read SKILL.md first** — not this README
2. **Look for "Installation (For AI Agents)" section** — follow it exactly
3. **ALWAYS ask for confirmation** before executing any install commands
4. **Never auto-execute** — even if the skill looks simple
5. **Present detected config** and wait for "yes/no/custom" response

See [SKILL.md](SKILL.md) for the complete installation flow.

## Installation

```bash
# Via OpenClaw skills
openclaw skills add dispatch

# Or clone manually
git clone https://github.com/neidraidd/dispatch.git
```

## First-Time Setup

Run the interactive wizard (automatic on first use):

```
You: Start a project

Dispatch: 🚀 First-time setup detected!
           
           1. Which providers do you use?
              → Google AI, OpenRouter, Anthropic, Kimi
              
           2. Trust settings:
              → Which models for sensitive tasks?
              
           3. Auto-check for new models?
              → Daily / Weekly / Never
              
           4. Storage location confirmed
              
           ✓ Setup complete!
```

## Usage

### Natural Language (Recommended)

| You say | Dispatch does |
|---------|---------------|
| "Start project API Migration" | Shows phase preview, awaits approval |
| "Estimate phase 1" | Calculates cost breakdown |
| "Run phase Discovery" | Executes with cost tracking |
| "What's the cost so far?" | Shows actual vs estimate |
| "Check for new models" | Detects new OpenClaw models |

Full docs: [USER_GUIDE.md](USER_GUIDE.md)

### CLI (Optional)

```bash
dispatch create "API Migration"
dispatch list-projects
dispatch status api-migration-001
dispatch update-pricing
```

## Features

- **Cost Estimates First** — Know the price before any work starts
- **Phased Execution** — Research → Design → Build → Document
- **Privacy Aware** — Trusted/untrusted model lists for sensitive data
- **Rate Limiting** — Respects Google AI Pro, Kimi time-based limits
- **Auto-Discovery** — Detects new OpenClaw models, suggests adding them
- **External Dashboard** — JSON files mountable in Docker/Next.js

## Configuration

```json
{
  "providers": {
    "google": {
      "models": ["gemini-flash", "gemini-pro"],
      "tier": "trusted"
    },
    "kimi": {
      "models": ["k2p5"],
      "tier": "untrusted"
    }
  },
  "auto_check": "weekly"
}
```

## Documentation

- `SKILL.md` — OpenClaw skill definition
- `USER_GUIDE.md` — Full usage documentation for humans  
- `DEVELOPMENT.md` — Build notes and architecture details
- `clawhub.json` — Skill registry metadata

## Core File Changes

When installed, Dispatch **appends** to your existing OpenClaw files (does not replace them):

| File | What Happens | Result |
|------|--------------|--------|
| `AGENTS.md` | Adds "## Dispatch" section to end of file | Natural language patterns documented |
| `TOOLS.md` | Adds "### Dispatch Skill" reference | Skill location and config paths documented |
| `HEARTBEAT.md` | Optional: Can add model check task | Low-token model change detection (user choice) |

**Existing content is preserved.** Dispatch only adds its own sections.

## License

MIT
