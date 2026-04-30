# Service Operations Guided Intake

Use this reference for service detail queries and service disable operations.

These operations are simpler than registration, but they are still question-driven. Do not generate curl until the user confirms the inputs.

## Shared Questions

First check local environment:

```bash
node {baseDir}/scripts/build-service-request.mjs env-check --operation detail
node {baseDir}/scripts/build-service-request.mjs env-check --operation disable
```

If `AICADE_API_KEY` exists locally, use it as `X-API-Key` and do not ask the user to confirm it.

Ask only if missing:

- `AICADE_API_KEY`

Always ask or confirm:

- service-management API `base_url`

If `base_url` was used earlier in the conversation, ask whether to reuse it.

## Query Service Detail

Operation:

- `GET /services/{serviceId}`

Ask:

- Which `serviceId` should be queried?
- Should I reuse the current `base_url`, or should it change?

Confirm:

```text
我将查询服务详情：
- GET {base_url}/services/{serviceId}
- Header: X-API-Key from AICADE_API_KEY
请确认是否生成 curl。
```

Only then generate:

```bash
node {baseDir}/scripts/build-service-request.mjs detail \
  --base-url {base_url} \
  --service-id {serviceId}
```

`AICADE_WALLET_ADDRESS` / `X-Address` is not required for detail queries.

## Disable Service

Operation:

- `POST /services/disable?serviceId=...`

Before asking the user for credentials, run:

```bash
node {baseDir}/scripts/build-service-request.mjs env-check --operation disable
```

If `AICADE_API_KEY` exists locally, use it as `X-API-Key` and do not ask the user to confirm it.

Ask:

- Which `serviceId` should be disabled?
- Should I reuse the current `base_url`, or should it change?

Confirm:

```text
我将禁用服务：
- POST {base_url}/services/disable?serviceId={serviceId}
- Header: X-API-Key from AICADE_API_KEY
请确认是否生成 curl。
```

Only then generate:

```bash
node {baseDir}/scripts/build-service-request.mjs disable \
  --base-url {base_url} \
  --service-id {serviceId}
```

`AICADE_WALLET_ADDRESS` / `X-Address` is not required for disable operations. Do not ask for wallet address when disabling a service.

## Minimum Final Output

The final answer or output file should include:

- operation name
- confirmed inputs
- generated curl
- expected response shape
- note that no remote API call was sent unless explicitly requested
