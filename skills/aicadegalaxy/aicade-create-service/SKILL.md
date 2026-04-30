---
name: aicade-create-service
description: Use when registering, updating, querying, or disabling aicade service-management APIs under /services, especially when preparing service metadata, billing, rate limits, auth config, JSON Schema inputs/outputs, or curl requests.
metadata:
  openclaw:
    emoji: "🧩"
    requires:
      bins: [node]
---
`READ BEFORE INSTALL`
This skill is built from the bundled service-management API reference.
It covers exactly these three operations:
1. Register or update a service: `POST /services`
2. Query service detail: `GET /services/{serviceId}`
3. Disable a service: `POST /services/disable?serviceId=...`
`READ BEFORE INSTALL`

# aicade-create-service

Use this skill when you need to prepare, validate, or generate requests for aicade service registration and management.

## Core Principle

Treat every service-management operation as a guided flow, not a one-shot dynamic call.

For `POST /services`, do not immediately fill the request from a generic example. First ask the user multiple focused questions, confirm the answers, then generate the final registration JSON and curl.

For `GET /services/{serviceId}` and `POST /services/disable`, also ask for the required operation inputs first. Do not infer `serviceId` or `base_url` from previous turns unless the user explicitly confirms reusing them.

Environment variables are different: check the local environment first. If `AICADE_API_KEY` already exists locally, use it without asking the user to confirm it again. For register/update, if `AICADE_WALLET_ADDRESS` already exists locally, use it without asking again.

Before generating a request, make sure the user has confirmed:

- stable `service_id`, `service_name`, `endpoint_url`, and `route_path`
- correct outbound auth settings
- valid `input_schema` and `output_schema`
- explicit billing and fallback rules
- rate limits when the service needs operational protection
- `AICADE_API_KEY` supplied by the platform before calling any endpoint
- `AICADE_WALLET_ADDRESS` supplied by the caller before register/update; it is sent as `X-Address`

## Quick Start

Set the platform API key first:

```bash
export AICADE_API_KEY=YOUR_AICADE_API_KEY
export AICADE_WALLET_ADDRESS=YOUR_AICADE_WALLET_ADDRESS
```

After the user confirms the generated registration JSON, write it to a local spec file and generate the register/update request:

```bash
node {baseDir}/scripts/build-service-request.mjs \
  register \
  --base-url https://api.example.com \
  --spec /path/to/confirmed-register-service.json
```

After the user confirms the query inputs, generate a query request:

```bash
node {baseDir}/scripts/build-service-request.mjs \
  detail \
  --base-url https://api.example.com \
  --service-id my-llm-service
```

After the user confirms the disable inputs, generate a disable request:

```bash
node {baseDir}/scripts/build-service-request.mjs \
  disable \
  --base-url https://api.example.com \
  --service-id my-llm-service
```

## Workflow

### 1. Check Local Environment First

Before asking for platform credentials, check whether the required environment variables are already present:

```bash
node {baseDir}/scripts/build-service-request.mjs env-check --operation register
node {baseDir}/scripts/build-service-request.mjs env-check --operation detail
node {baseDir}/scripts/build-service-request.mjs env-check --operation disable
```

If `AICADE_API_KEY` is already present, do not ask the user to confirm it. Use it as `X-API-Key`.

For register/update, if `AICADE_WALLET_ADDRESS` is already present, do not ask the user to confirm it. Use it as `X-Address`.

Ask only for missing environment values. If the user does not have platform access yet, point them to:

- `https://www.aicadegalaxy.com/`
- `https://docs.aicadegalaxy.com/white-paper/application-document`

Explain briefly that only after obtaining app access can they get the AICADE environment variables required by this skill:

- `AICADE_API_KEY`
- `AICADE_WALLET_ADDRESS`

`AICADE_API_KEY` is sent as `X-API-Key`. `AICADE_WALLET_ADDRESS` is sent as `X-Address` for register/update requests.

### 2. Identify The Operation

- **Register/update**: use when creating a service or replacing the configuration for an existing `service_id`
- **Detail**: use when checking the registered gateway contract
- **Disable**: use when turning off a service

Always run the matching guided intake before generating the final request:

- **Register/update**: collect and confirm the full registration JSON
- **Detail**: collect and confirm `base_url` and `serviceId`; use local `AICADE_API_KEY` when present
- **Disable**: collect and confirm `base_url` and `serviceId`; use local `AICADE_API_KEY` when present

### 3. Load The API Reference When Needed

Read these references when needed:

- `references/register-intake.md` for the required multi-step questions
- `references/service-operations-intake.md` for query/detail and disable question flows
- `references/service-management-api.md` for field rules, enum guidance, auth examples, billing rules, or rate-limit structure

### 4. Ask Register Intake Questions

Collect the registration fields in small groups. Do not ask for every field in one wall of text.

Use this order:

1. Service identity: `service_id`, `service_name`, `description`, `tags`
2. Endpoint and gateway route: `endpoint_url`, `route_path`, `strip_prefix`, `route_order`, `timeout_ms`
3. Outbound auth: `auth_type`, `auth_location`, `outbound_auth`
4. Input/output contract: `input_schema`, `output_schema`
5. Billing: `billing_type`, `currency`, prices, limits, `fallback_strategy`
6. Rate limits: service/user/IP limits and token limits
7. Final review: show the assembled JSON and ask for confirmation before generating curl

When the user has not supplied a value, ask a direct question and offer a reasonable default when the API supports one. For sensitive values such as API keys or tokens, ask for placeholders unless the user explicitly wants to include the real value.

### 5. Prepare Register Input

Start from:

- `{baseDir}/assets/register-service.template.json` for a minimal fill-in template
- `{baseDir}/assets/register-service.example.json` only as a shape reference, not as the user's final registration

Keep request body fields in `snake_case`. The API supports a few camelCase aliases, but generated requests should prefer `snake_case`.

### 6. Validate Critical Fields

Before presenting or sending a register request, check:

- `AICADE_API_KEY` is available as an environment variable or passed explicitly with `--api-key`
- `AICADE_WALLET_ADDRESS` is available as an environment variable or passed explicitly with `--address`
- `service_id` uses lowercase letters, digits, and hyphens only, length 3-64
- `route_path` starts with `/`
- `timeout_ms` is between `1000` and `300000` when set
- `strip_prefix` is between `0` and `10` when set
- `input_schema` and `output_schema` are JSON Schema compatible
- `billing.billing_type`, `billing.currency`, and `billing.fallback_strategy` are present
- `outbound_auth.type` matches `auth_type` unless `auth_type` is `NONE`

### 7. Generate Requests

Use `scripts/build-service-request.mjs` to print a ready-to-run curl command. The script reads `AICADE_API_KEY` and `AICADE_WALLET_ADDRESS` by default, or accepts `--api-key` and `--address` for one-off generation. The script does not call the remote API; it only reads local input and prints the command.

## Endpoint Summary

| Operation | Method | Path | Required headers |
| --- | --- | --- | --- |
| Register/update | `POST` | `/services` | `X-Address`, `X-API-Key`, `Content-Type: application/json` |
| Detail | `GET` | `/services/{serviceId}` | `X-API-Key` |
| Disable | `POST` | `/services/disable?serviceId=...` | `X-API-Key` |

## Common Mistakes

- Do not skip the platform access check; `AICADE_API_KEY` must be obtained before using these APIs.
- Do not ask the user to reconfirm `AICADE_API_KEY` when it already exists in the local environment.
- Do not ask the user to reconfirm `AICADE_WALLET_ADDRESS` for register/update when it already exists in the local environment.
- Do not generate a register/update request without `AICADE_WALLET_ADDRESS`; it is required for `X-Address`.
- Do not use `assets/register-service.example.json` as the user's final service config without asking questions.
- Do not generate the final register curl before the user confirms the assembled JSON.
- Do not generate query/detail curl before asking and confirming `serviceId` and `base_url`.
- Do not silently reuse a previous `serviceId`; ask whether to reuse it.
- Do not omit `X-API-Key`; all three operations require it and the value should come from `AICADE_API_KEY`.
- Do not put registration body fields in random casing; prefer documented `snake_case`.
- Do not register without `input_schema`, `output_schema`, and `billing`.
- Do not put `serviceId` in the disable body; it is a query parameter.
- Do not treat `POST /services` as create-only; it is idempotent and updates existing `service_id`.

## Files Included

- `references/service-management-api.md`
- `references/register-intake.md`
- `references/service-operations-intake.md`
- `scripts/build-service-request.mjs`
- `assets/register-service.template.json`
- `assets/register-service.example.json`
