# Service Management API Reference

Base path: `/services`

This reference covers the three service-management operations supported by this skill:

1. Register or update a service
2. Query service detail
3. Disable a service

## Platform Access

All three operations require `AICADE_API_KEY`, sent as the `X-API-Key` request header.

Register/update also requires `AICADE_WALLET_ADDRESS`, sent as the `X-Address` request header.

Before using these APIs, apply for app access on:

- `https://www.aicadegalaxy.com/`

If access has not been granted yet, use the application guide:

- `https://docs.aicadegalaxy.com/white-paper/application-document`

Only after app access is granted can the user obtain the environment values required by this skill:

- `AICADE_API_KEY`
- `AICADE_WALLET_ADDRESS`

## 1. Register Or Update Service

| Field | Value |
| --- | --- |
| Method | `POST` |
| Path | `/services` |
| Content-Type | `application/json` |
| Behavior | Registers a new service or updates an existing service idempotently |

### Required Headers

| Header | Required | Description |
| --- | --- | --- |
| `X-Address` | Yes | Use the value of `AICADE_WALLET_ADDRESS` |
| `Content-Type` | Yes | Fixed value: `application/json` |
| `X-API-Key` | Yes | Use the value of `AICADE_API_KEY` obtained after platform app access is granted |

### Request Body Fields

| Field | Type | Required | Rules / Notes |
| --- | --- | --- | --- |
| `service_id` | string | Yes | Lowercase letters, digits, hyphens only; length 3-64 |
| `service_name` | string | Yes | Max length 128 |
| `endpoint_url` | string | Yes | Max length 512 |
| `auth_type` | enum | Yes | Outbound auth type |
| `auth_location` | enum | No | Defaults to `HEADER`; alias: `authLocation` |
| `outbound_auth` | object | No | May be null when `auth_type = NONE`; otherwise recommended |
| `route_path` | string | Yes | Must start with `/`, example: `/api/my-service` |
| `strip_prefix` | integer | No | `0-10`, default `0` |
| `route_order` | integer | No | Minimum `0`, default `0`; lower value has higher priority |
| `timeout_ms` | integer | No | `1000-300000`, default `30000` |
| `description` | string | No | Service description |
| `tags` | array<string> | No | Classification and search tags |
| `input_schema` | object | Yes | JSON Schema Draft 2020-12 compatible; alias: `inputSchema` |
| `output_schema` | object | Yes | JSON Schema Draft 2020-12 compatible; alias: `outputSchema` |
| `billing` | object | Yes | See BillingDTO |
| `rate_limits` | array<object> | No | See RateLimitDTO |

### AuthConfigDTO

`outbound_auth` config:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `type` | string | Yes | Auth type identifier, matching `auth_type` |
| `api_key` | object | No | API key config |
| `bearer_token` | object | No | Bearer token config |
| `basic_auth` | object | No | Basic auth config |
| `oauth2` | object | No | OAuth2 config |

#### ApiKeyConfig

| Field | Type | Description |
| --- | --- | --- |
| `location` | string | `header` or `query` |
| `query_param` | string | Required when `location=query` |
| `value` | string | API key value |

#### BearerTokenConfig

| Field | Type | Description |
| --- | --- | --- |
| `header_name` | string | Usually `Authorization` |
| `prefix` | string | Usually `Bearer` |
| `token` | string | Token value |

#### BasicAuthConfig

| Field | Type | Description |
| --- | --- | --- |
| `header_name` | string | Header name |
| `username` | string | Username |
| `password` | string | Password |

#### OAuth2Config

| Field | Type | Description |
| --- | --- | --- |
| `header_name` | string | Header name |
| `token_type` | string | Token type |
| `access_token` | string | Access token |
| `refresh_token` | string | Refresh token |
| `client_id` | string | Client ID |
| `client_secret` | string | Client secret |

### BillingDTO

| Field | Type | Required | Rules / Notes |
| --- | --- | --- | --- |
| `billing_type` | enum | Yes | `FREE`, `PER_REQUEST`, `PER_TOKEN`, `SUBSCRIPTION`, etc. |
| `flow_type` | enum | No | Defaults to `INCOME`; values include `INCOME`, `EXPENSE` |
| `currency` | string | Yes | Currency unit, such as `POINTS`; may be empty for `FREE` |
| `price_per_request` | decimal | Yes | Valid for `PER_REQUEST` |
| `prompt_price_per_1k` | decimal | No | Valid for `PER_TOKEN` |
| `completion_price_per_1k` | decimal | No | Valid for `PER_TOKEN` |
| `subscription_period` | string | No | `MONTHLY` or `YEARLY`; valid for `SUBSCRIPTION` |
| `subscription_price` | decimal | No | Valid for `SUBSCRIPTION` |
| `included_requests` | integer | No | Valid for `SUBSCRIPTION`; null means unlimited |
| `included_tokens` | long | No | Valid for `SUBSCRIPTION`; null means unlimited |
| `max_input_tokens_per_req` | integer | No | null means unlimited |
| `max_output_tokens_per_req` | integer | No | null means unlimited |
| `monthly_token_limit` | long | No | null means unlimited |
| `daily_request_limit` | integer | No | null means unlimited |
| `monthly_request_limit` | integer | No | null means unlimited |
| `concurrent_limit` | integer | No | null means unlimited |
| `fallback_strategy` | enum | Yes | Quota-exhaustion fallback strategy |
| `fallback_config` | string | No | JSON string with fallback details |

Fallback examples:

```json
{"max_overdraft": 100, "notify_threshold": 10}
```

```json
{"degrade_service_id": "free-gpt3"}
```

### RateLimitDTO

| Field | Type | Required | Rules / Notes |
| --- | --- | --- | --- |
| `limit_dimension` | enum | No | Defaults to `SERVICE`; examples: `SERVICE`, `USER`, `IP` |
| `qps` | integer | No | Minimum `1`; null means unlimited |
| `rpm` | integer | No | Minimum `1`; null means unlimited |
| `rpd` | integer | No | Minimum `1`; null means unlimited |
| `max_tokens_per_req` | integer | No | Minimum `1`; null means unlimited |
| `ip_whitelist` | string | No | JSON array string, example: `["192.168.1.0/24","10.0.0.1"]` |
| `ip_blacklist` | string | No | JSON array string |

### Register Example

```json
{
  "service_id": "my-llm-service",
  "service_name": "My LLM Service",
  "endpoint_url": "https://api.example.com/v1/chat",
  "auth_type": "API_KEY",
  "auth_location": "HEADER",
  "outbound_auth": {
    "type": "API_KEY",
    "api_key": {
      "location": "header",
      "query_param": null,
      "value": "sk-xxxx"
    }
  },
  "route_path": "/api/my-llm-service",
  "strip_prefix": 1,
  "route_order": 10,
  "timeout_ms": 60000,
  "description": "A public LLM service",
  "tags": ["llm", "chat"],
  "input_schema": {
    "type": "object",
    "required": ["messages"],
    "properties": {
      "messages": {
        "type": "array",
        "items": {"type": "object"}
      }
    }
  },
  "output_schema": {
    "type": "object",
    "properties": {
      "content": {"type": "string"}
    }
  },
  "billing": {
    "billing_type": "PER_TOKEN",
    "flow_type": "INCOME",
    "currency": "POINTS",
    "prompt_price_per_1k": 0.01,
    "completion_price_per_1k": 0.03,
    "monthly_token_limit": 1000000,
    "fallback_strategy": "REJECT"
  },
  "rate_limits": [
    {
      "limit_dimension": "SERVICE",
      "qps": 100,
      "rpm": 1000
    }
  ]
}
```

Response:

```json
{
  "code": 200,
  "data": {
    "//": "ServiceDetailResponse object"
  }
}
```

## 2. Query Service Detail

| Field | Value |
| --- | --- |
| Method | `GET` |
| Path | `/services/{serviceId}` |
| Behavior | Queries service detail by registered service id |

### Required Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `serviceId` | string | Yes | The registered `service_id` |
| `X-API-Key` | string | Yes | Use the value of `AICADE_API_KEY` |

Example:

```http
GET /services/my-llm-service
X-API-Key: YOUR_AICADE_API_KEY
```

Response:

```json
{
  "code": 200,
  "data": {
    "//": "ServiceDetailResponse object"
  }
}
```

## 3. Disable Service

| Field | Value |
| --- | --- |
| Method | `POST` |
| Path | `/services/disable` |
| Behavior | Disables a service |

### Required Inputs

| Name | Type | Required | Description |
| --- | --- | --- | --- |
| `serviceId` | string | Yes | Service id to disable; query parameter |
| `X-API-Key` | string | Yes | Use the value of `AICADE_API_KEY` |

Example:

```http
POST /services/disable?serviceId=my-llm-service
X-API-Key: YOUR_AICADE_API_KEY
```

Response:

```json
{
  "code": 200,
  "data": null
}
```

## Common Behavior

Registration/update validation follows:

```text
@Valid field validation -> business validator -> idempotent service check
```

All APIs are reactive and use Project Reactor with a `boundedElastic` thread pool for blocking operations.

Request body fields should use `snake_case`. Some fields support camelCase aliases through `@JsonAlias`.
