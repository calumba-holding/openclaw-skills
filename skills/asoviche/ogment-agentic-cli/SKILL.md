# Ogment CLI Skill

Securely invoke MCP tools via the Ogment CLI. Use for accessing user's connected SaaS tools (Linear, Notion, Gmail, PostHog, etc.) through Ogment's governance layer.

## When to Use

- User asks to interact with their connected services (issues, docs, emails, analytics)
- You need to call MCP tools that require auth/credentials
- Discovering what integrations the user has available

## Core Workflow

status → catalog → catalog <server> → catalog <server> <tool> → invoke

### 1. Check connectivity (if issues suspected)

ogment status

Returns auth state, connectivity, and available servers. Check summary.status for quick health.

### 2. Discover servers

ogment catalog

Returns list of servers with serverId and toolCount. Use serverId in subsequent calls.

### 3. List tools on a server

ogment catalog <serverId>

Returns all tools with name and description. Scan descriptions to find the right tool.

### 4. Inspect tool schema

ogment catalog <serverId> <toolName>

Returns inputSchema with properties, types, required fields, and descriptions.

### 5. Invoke a tool

ogment invoke <serverId>/<toolName> --input '<json>'

Input can be:
- Inline JSON: --input '{"query": "test"}'
- File: --input @path/to/input.json
- Stdin: echo '{}' | ogment invoke ... --input -

## Output Format

All commands return structured JSON with ok, data, error, meta, and next_actions fields.

- Check ok first — boolean success indicator
- next_actions — suggested follow-up commands
- error.category — validation, not_found, remote, auth, internal
- error.retryable — whether retry might help

## Common Patterns

### Find a tool by intent
ogment catalog <serverId> | jq '.data.tools[] | select(.name + .description | test("email"; "i"))'

### List issues assigned to user
ogment invoke openclaw/Linear_list_issues --input '{"assignee": "me"}'

### Search Notion
ogment invoke openclaw/Notion_notion-search --input '{"query": "quarterly review", "query_type": "internal"}'

### Get Gmail messages
ogment invoke openclaw/gmail_listMessages --input '{"q": "is:unread", "maxResults": 10}'

## Gotchas & Workarounds

1. Opaque server errors - Re-check schema, verify required fields and types
2. Example placeholders are broken - Ignore exampleInput, construct your own
3. Server/tool IDs are case-sensitive - Use exact casing from catalog
4. Empty strings cause 502s - Validate inputs before calling
5. --quiet suppresses everything - Don't use it
6. No tool search/filter - Pipe to jq and filter locally

## Error Recovery

TOOL_NOT_FOUND → Run ogment catalog to rediscover
VALIDATION_INVALID_INPUT → Check JSON syntax
TRANSPORT_REQUEST_FAILED → Check schema, required fields, types
AUTH_INVALID_CREDENTIALS → Run ogment auth login
HTTP_502 → Retry after delay

## Pre-flight Checklist

Before invoking a tool:
1. Confirmed server exists (catalog)
2. Confirmed tool exists (catalog <server>)
3. Checked required fields in schema
4. Matched types exactly (number vs string)
5. Used exact casing for IDs