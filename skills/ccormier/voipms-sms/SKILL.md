---
name: voipms-sms
description: OpenClaw skill for sending and retrieving SMS messages via the VoIP.ms API.
---

# VoIP.ms SMS Skill

Use this skill to send and retrieve SMS messages through the VoIP.ms API.

## Available Scripts

### `scripts/send_sms.py`

Send an SMS from one of your VoIP.ms DIDs to a destination number.

Required arguments:
- `--did`: source VoIP.ms number
- `--dst`: destination phone number
- `--message`: SMS message text

Example:

```bash
python3 scripts/send_sms.py \
  --did "15551234567" \
  --dst "15557654321" \
  --message "Hello from OpenClaw"
```

### `scripts/get_sms.py`

Retrieve SMS messages from the VoIP.ms API for a recent date range.

Arguments:
- `--did` (optional): filter by a specific source number
- `--days` (optional, default `1`): number of days back to fetch

Example (all numbers, last day):

```bash
python3 scripts/get_sms.py --days 1
```

Example (specific DID, last 7 days):

```bash
python3 scripts/get_sms.py --did "15551234567" --days 7
```

## Required Credentials

Set these environment variables before running either script. Since passwords should not be hardcoded or passed in raw chat commands, use the Bitwarden vault to retrieve them on the fly. 

Ensure the vault contains two entries: `api-voipms-username` and `api-voipms-password`.

Example:

```bash
export VOIPMS_API_USERNAME=$(rbw get api-voipms-username)
export VOIPMS_API_PASSWORD=$(rbw get api-voipms-password)
```
