# Register Service Guided Intake

Use this reference when preparing `POST /services`.

The goal is to ask focused questions, assemble the request JSON, then ask the user to confirm it before generating curl. Do not register directly from the bundled example.

## Question Flow

### 1. Platform Environment

First check local environment with:

```bash
node {baseDir}/scripts/build-service-request.mjs env-check --operation register
```

If `AICADE_API_KEY` exists locally, use it as `X-API-Key` and do not ask the user to confirm it.

If `AICADE_WALLET_ADDRESS` exists locally, use it as `X-Address` and do not ask the user to confirm it.

Ask only for missing values:

- Missing `AICADE_API_KEY`: ask the user to provide it or apply for platform access.
- Missing `AICADE_WALLET_ADDRESS`: ask for the caller wallet address.

If not, point the user to:

- `https://docs.aicadegalaxy.com/white-paper/application-document`

### 2. Service Identity

Ask for:

- `service_id`: lowercase letters, digits, hyphens, length 3-64
- `service_name`: display name
- `description`: optional
- `tags`: optional list

Example question:

```text
先确认服务基础信息：service_id、service_name、服务描述、tags 分别是什么？
service_id 只能用小写字母、数字和连字符，长度 3-64。
```

### 3. Endpoint And Gateway Route

Ask for:

- `endpoint_url`: upstream API URL
- `route_path`: gateway route, must start with `/`
- `strip_prefix`: default `0`, range `0-10`
- `route_order`: default `0`
- `timeout_ms`: default `30000`, range `1000-300000`

Example question:

```text
这个服务实际请求地址 endpoint_url 是什么？希望在网关暴露成哪个 route_path？
如果没有特殊要求，我会使用 strip_prefix=0、route_order=0、timeout_ms=30000。
```

### 4. Outbound Auth

Ask which `auth_type` to use:

- `NONE`
- `API_KEY`
- `BEARER_TOKEN`
- `BASIC_AUTH`
- `OAUTH2`

Then ask only for the matching config.

For `API_KEY`, confirm:

- header or query
- header name or query parameter name if needed
- key value or placeholder

For sensitive values, prefer placeholders such as `${UPSTREAM_API_KEY}` unless the user intentionally provides real secrets.

### 5. Input And Output Schemas

Ask for:

- expected request parameters
- required fields
- response fields

Generate JSON Schema Draft 2020-12-compatible `input_schema` and `output_schema`.

If the user only describes fields in prose, convert them into schemas and ask for confirmation.

### 6. Billing

Ask for billing mode:

- `FREE`
- `PER_REQUEST`
- `PER_TOKEN`
- `SUBSCRIPTION`

Then ask follow-up details:

- `FREE`: `currency` can be empty, `price_per_request` can be `0`
- `PER_REQUEST`: `currency`, `price_per_request`
- `PER_TOKEN`: `currency`, `prompt_price_per_1k`, `completion_price_per_1k`
- `SUBSCRIPTION`: `currency`, `subscription_period`, `subscription_price`, included quota

Always confirm:

- `flow_type`, usually `INCOME`
- `fallback_strategy`, such as `REJECT`, `OVERDRAFT`, or `DEGRADE`
- limits such as daily/monthly requests or token caps when needed

### 7. Rate Limits

Ask whether rate limits are needed.

Common prompts:

- service-level QPS/RPM/RPD
- user-level RPM/RPD
- IP whitelist or blacklist
- `max_tokens_per_req` for LLM services

If no rate limits are required, set `rate_limits` to `[]`.

### 8. Final Confirmation

Show the assembled JSON and ask:

```text
这是我整理出的注册服务 JSON。请确认是否可以用它生成最终 curl；如果要改计费、接口地址、鉴权或 schema，我会先改 JSON。
```

Only after confirmation should the final curl be generated.

Before generating register/update curl, verify:

- `AICADE_API_KEY` is available and maps to `X-API-Key`
- `AICADE_WALLET_ADDRESS` is available and maps to `X-Address`

## Minimum Final Output

The final answer or output file should include:

- confirmed registration JSON
- generated curl
- validation checklist
- note that the script only generated a request and did not call the remote API unless the user explicitly requested execution
