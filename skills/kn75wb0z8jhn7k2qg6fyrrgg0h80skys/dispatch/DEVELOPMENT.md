# Build Plan — Dispatch

## Quick Reference

### Components
- `ProjectManager` — Project lifecycle, phases
- `CostEstimator` — Pre-execution cost prediction
- `ChangeDetector` — New model detection
- `TrustManager` — Privacy-aware selection
- `Setup` — First-time configuration wizard

### Storage
- Data: `~/.openclaw/workspace/.dispatch/`
- Config: `~/.openclaw/skills/dispatch/config/`

### Features
- ✓ Natural language interaction
- ✓ Phase preview before creation
- ✓ Cost estimates upfront
- ✓ Trusted/untrusted model lists
- ✓ Rate limiting for time-based providers
- ✓ Auto-detect new OpenClaw models

## Installation

```bash
# Clone
git clone https://github.com/neidraidd/dispatch.git

# Install to OpenClaw
cd dispatch && ./install.sh

# Or via OpenClaw skills
openclaw skills add dispatch
```
