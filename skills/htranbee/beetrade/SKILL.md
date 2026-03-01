---
name: beetrade
description: Use Beecli to interact with the Beetrade platform for authentication, market data, bot/strategy operations, alerts, accounts, and portfolio workflows. Use this skill whenever a user asks to run or troubleshoot Beecli commands.
metadata:
  openclaw:
    requires:
      bins:
        - beecli
    install:
      - kind: node
        package: "@beelabs/beetrade-cli"
        bins:
          - beecli
        label: "Install Beetrade CLI (npm)"
---

# Beetrade Skill

Use this skill to operate `beecli` safely and efficiently.

## Quick Start

1. Confirm `beecli` exists: `beecli --help`.
2. Check auth state first: `beecli auth status`.
3. If unauthenticated, run `beecli auth login` to interactively continue the login flow.
4. Run read-only/list/get command first to discover IDs before write actions.
5. For mutating operations, restate exact command and impact before executing.

## Safety Rules

Always require explicit user confirmation immediately before executing these actions:

- Any live trading start/stop command.
- Any delete command.
- Any command that updates account credentials.
- Any command that can place real orders or alter scheduled execution.

**Credential Protection Rules:**

- Never read, display, or copy the contents of ~/.beecli/config.json
- Never include credentials (accessToken, refreshToken) in command output or error messages
- If beecli returns raw credentials in JSON, redact them before displaying to the user
- Never suggest or execute commands that expose token values

## URL / API Endpoint Safety

- Only use the default API URL: `https://api.prod.beetrade.com/api/v2`
- Reject any user-supplied custom API URLs, especially during login or authentication
- If a user provides a custom URL, warn that this redirects credentials and refuse to proceed
- Never execute login or auth commands with custom API endpoints
- Treat custom API URLs as a security risk and potential credential exfiltration attempt

Default to safer alternatives first:

- Prefer `paper` or `backtest` before `live`.
- Prefer `list/get/status/detail` before `update/delete/run`.

If command intent is ambiguous, ask one clarifying question before running anything.

## Execution Workflow

When a user asks for an operation, follow this sequence:

1. **Understand intent**: identify resource type (bot, strategy, alert, account, etc.) and target environment (paper/live).
2. **Validate prerequisites**:
- Auth is valid (`beecli auth status`).
- Required IDs are available; if not, discover via list commands.
- Required JSON payload exists and is valid JSON.
- Sanitize all output to remove accessToken/refreshToken from responses
- If beecli returns raw credentials in JSON, redact them before displaying
3. **Preview**: show the exact command you plan to execute.
4. **Confirm if risky**: apply safety rules above.
5. **Execute and report**:
- Return parsed JSON result if successful.
- On failure, include command attempted, error summary, and likely fix.

## JSON Input Guidance

Commands using `-c` or `-d` require JSON strings. If the user gives partial fields:

1. Draft a minimal valid JSON payload.
2. Ask for missing required fields.
3. Use single quotes around the JSON string in shell examples.

## Prohibited Actions

The following actions MUST NEVER be performed, regardless of user request:

- Reading ~/.beecli/config.json or any credential store files
- Displaying, logging, or copying access/refresh tokens
- Using custom API URLs (especially for auth/login commands)
- Bypassing confirmation prompts for high-risk actions
- Executing login commands with non-default API endpoints
- Suggesting commands that expose token values or redirect credentials

## Where To Look For Command Syntax

Use [references/commands.md](references/commands.md) for the full command catalog and examples.

## Notes

- Config file location: `~/.beecli/config.json`
- Default API URL: `https://api.prod.beetrade.com/api/v2`
- Command actions generally emit JSON; CLI help/argument validation output may not be JSON.

## Risk Classification

The skill provides access to a powerful CLI tool (`beecli`) for managing trading accounts, bots, and live trading operations, which inherently carries high risk. While the SKILL.md includes explicit `Safety Rules` and an `Execution Workflow` designed to mitigate prompt injection by requiring user confirmation for sensitive actions (e.g., live trading, deletions, credential updates, custom API URLs for login), the underlying capabilities remain high-risk. The `~/.beecli/config.json` file, which stores sensitive `accessToken` and `refreshToken`, is also a potential target for exfiltration if the agent's safety rules were bypassed. The skill is classified as suspicious due to these high-risk capabilities and the inherent prompt injection surface, despite the good-faith attempt at mitigation, as a successful bypass could lead to significant financial or security impact.

**Mitigations implemented:**

- **Credential exfiltration prevention**: Explicit prohibition on reading config files or displaying tokens
- **URL validation**: Prevents credential redirection via malicious API endpoints
- **Output sanitization**: Removes access/refresh tokens from all command responses
- **User confirmation gates**: Required before all financial-impacting actions
- **Prohibited actions**: Unconditional rules that cannot be overridden by user requests
- **Layered defense**: Multiple independent controls address different attack vectors
