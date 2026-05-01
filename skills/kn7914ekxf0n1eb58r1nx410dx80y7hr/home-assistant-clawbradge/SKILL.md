---
name: home-assistant
description: Control Home Assistant devices via ClawBridge API. Use when users ask to turn lights on/off, check device states, or interact with any exposed Home Assistant entities. Handles entity discovery, state checks, and service calls with human approval flow.
---

# Home Assistant Skill

Control Home Assistant devices through ClawBridge (air-gapped API proxy with human approval).

## What is ClawBridge?

ClawBridge is an API gateway that sits between AI agents and Home Assistant:
- **Token isolation:** Your HA token never leaves ClawBridge
- **Human approval:** Service calls require explicit approval via web UI
- **Read-only by default:** AI can query sensors/state freely
- **Audit trail:** Logs every request for transparency

## Configuration

- **Base URL:** `http://YOUR_CLAWBRIDGE_IP:PORT` (e.g., `http://192.168.1.100:8100`)
- **API Key:** Generate in ClawBridge web UI
- **Discord Webhook:** (Optional) For real-time notifications

## Installation

1. Install ClawBridge as a Home Assistant add-on or standalone Docker container
2. Generate an API key in the ClawBridge web UI
3. Configure the Discord webhook (optional, for notifications)
4. Edit `scripts/ha-discord.py` to set your entity filters

## Real-Time Notifications

**Python → Discord Direct** — zero AI cost, instant delivery.

### Start Monitoring
```bash
python3 /path/to/skills/home-assistant/scripts/ha-discord.py &
```

### Stop Monitoring
```bash
# Find the process and kill it
pgrep -f ha-discord.py
kill <PID>
```

### Filter Entities

Edit `scripts/ha-discord.py`:
```python
# Watch only these (empty = all)
WATCH_ENTITIES = ["light.office", "binary_sensor.front_door"]

# Ignore these
IGNORE_ENTITIES = ["sensor.cpu_temp"]
```

## Device Control

### Check Exposed Entities
```bash
curl -s "http://YOUR_CLAWBRIDGE_IP:PORT/api/states" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  | grep -o '"entity_id": "[^"]*"' | cut -d'"' -f4
```

### Check Entity State
```bash
curl -s "http://YOUR_CLAWBRIDGE_IP:PORT/api/states/{entity_id}" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Control a Device
```bash
curl -s -X POST "http://YOUR_CLAWBRIDGE_IP:PORT/api/services/{domain}/{service}" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"entity_id": "{entity_id}"}'
```

**Note:** Service calls require human approval via ClawBridge web UI.

### Quick Script
```bash
./skills/home-assistant/scripts/ha-control.sh state light.office
./skills/home-assistant/scripts/ha-control.sh on light.office
./skills/home-assistant/scripts/ha-control.sh off light.office
```

## Notification Formats

| Domain | Message |
|--------|---------|
| light | 💡 **{name}** turned **on/off** |
| switch | 🔌 **{name}** turned **on/off** |
| binary_sensor (door) | 🚪 **{name}** **opened/closed** |
| binary_sensor (motion) | 📡 **{name}** **motion detected** |
| person | 👤 **{name}** is now **{state}** |
| lock | 🔒 **{name}** **locked/unlocked** |
| other | 🔔 **{name}** `old` → `new` |

## Scripts

| Script | Purpose |
|--------|---------|
| `ha-discord.py` | **Primary** — WebSocket → Discord direct (zero cost) |
| `ha-monitor.py` | WebSocket → file (for cron-based delivery) |
| `ha-control.sh` | Quick CLI for on/off/state |

## Why ClawBridge?

### The Problem with Standard HA AI Integration
- Long-lived tokens = full API access
- No approval workflow for destructive actions
- One prompt injection = uncontrolled home access

### The ClawBridge Solution
- AI gets scoped API keys (not your HA token)
- Service calls queue for human approval
- Read operations pass through instantly
- Full audit trail of every request

## API Reference

See [references/clawbridge-api.md](references/clawbridge-api.md)

## License

MIT - Contributions welcome!
