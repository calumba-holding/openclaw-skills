---
name: toingg-create-campaign
description: Create and launch Toingg voice-calling campaigns by POSTing user-supplied JSON to the toingg/make_campaign API. Use when Codex needs to turn campaign briefs (title, prompt, tone, notifications, autopilot flags, etc.) into live Toingg campaigns via the `create_campaign.py` helper.
---

# Toingg Campaign Creator

This skill turns structured campaign briefs into Toingg campaigns using the
`create_campaign.py` helper, which wraps `https://prepodapi.toingg.com/api/v3/create_campaign`.
All campaign parameters come from the user; the script only handles auth and HTTP.

## Requirements

1. **Auth token**: Export `TOINGG_API_TOKEN` before running the script.
   ```bash
   export TOINGG_API_TOKEN="<bearer token>"
   ```
2. **Payload file**: Build a JSON file that matches Toingg's schema. Use
   [`references/payload-template.md`](references/payload-template.md) as a base and
   keep only the fields needed for the campaign.

## Workflow

1. **Collect campaign inputs** from the user: title, voice, language, script/purpose,
   tone, analysis schema, notifications, autopilot flags, etc.
2. **Draft the payload JSON** in the workspace (e.g., `campaign.json`). Start from the
   template reference and customize each field. Validate that required keys (such as
   `title`, `voice`, `language`, `purpose`, and `script`) are populated.
3. **Review for security**: ensure no secrets besides the bearer token are embedded in
   the payload file.
4. **Create the campaign**:
   ```bash
   cd skills/toingg-create-campaign
   ./scripts/create_campaign.py /path/to/campaign.json > create-response.json
   ```
   The script prints the API's JSON response (success object or error details).
5. **Confirm results** with the user. Share `create-response.json`, noting the new
   campaign ID or any errors returned by the API.

## Troubleshooting

- **401 Unauthorized**: The `TOINGG_API_TOKEN` env var is missing or expired. Refresh it
  in the Toingg dashboard and re-export before re-running the script.
- **422/400 errors**: The payload is missing required fields or contains invalid values.
  Check the response body in `create-response.json` for field-level messages and adjust
  the JSON accordingly.
- **Networking issues**: Re-run after verifying internet connectivity. The script uses a
  60s timeout; transient failures can be retried safely.

## Extending the payload

If Toingg adds new campaign fields, simply include them in the JSON payload—no script
changes are required. Keep the reference template updated so future operators know the
available knobs.
