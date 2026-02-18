---
name: discogs-claw
description: Search for vinyl record prices on Discogs using curl. Retrieves Low, Median, and High price suggestions based on condition.
metadata: {"clawdbot":{"emoji":"💿","requires":{"bins":["jq","curl"]}}}
---

# Discogs Claw

Search for vinyl record prices on Discogs using the Discogs API.

## Setup

### Option 1: Environment Variable (Recommended)

```bash
export DISCOGS_TOKEN="your_discogs_token_here"
```

### Option 2: Config file
Located on ~/.openclaw/credentials/discogs.json or /data/.openclaw/credentials/discogs.json

```json
{
  "DISCOGS_TOKEN": "your_discogs_token_here"
}
```

## Usage

### Run the Skill

The skill accepts a JSON input containing the search query.

```bash
# Example search
echo '{"query": "Daft Punk - Random Access Memories"}' | ./scripts/discogs.sh
```

## Example Output

```json
{
  "release_id": 4570366,
  "title": "Daft Punk - Random Access Memories",
  "year": "2013",
  "prices": {
    "low": 25.00,
    "median": 35.00,
    "high": 60.00,
    "currency": "USD"
  }
}
```

## Requirements

- `curl`
- `jq`
- Discogs API Token (`DISCOGS_TOKEN`)

