# API schemas - opendeploy

Full field reference for every gateway endpoint the `opendeploy` skill touches. Grouped by pipeline step.

**URL convention**: `OD_GATEWAY` includes the `/api` prefix (e.g. `https://dashboard.dev.opendeploy.dev/api`). Endpoint paths below are written as `/v1/...` - the full request URL is `$OD_GATEWAY/v1/...`. All calls send `Authorization: Bearer $OD_API_KEY`. UUIDs are v4 strings.

Default error envelope (unless a step overrides):
- 401 - bad or expired API key.
- 403 - subscription / quota gate hit.
- 404 - wrong ID.
- 409 - conflict (duplicate name / domain).
- Body shape: `{"error": "..."}`.

---

## Step 0 - POST `/v1/client-guests/register` (gateway, anonymous)

Create a local deploy credential on cold start when `~/.opendeploy/auth.json` is missing or its `api_key` is empty. **No auth required.** The skill writes the response into `~/.opendeploy/auth.json` (mode 0600) only after explicit user approval and uses Bearer mode for everything else.

- **Body** (optional):
  | field | type | required | note |
  |---|---|---|---|
  | `source_hint` | string | optional | free-form tag, e.g. `"claude-code/Darwin"`. Logged for triage; not persisted. |
  | `name` | string | optional | user-facing label, ≤ 64 chars after trim. Becomes the default name on the credential row; user can override on the account-binding page or rename later via PATCH. |
  | `hostname` | string | legacy optional | The skill does not send this by default. Older clients may send it for triage; omit unless the user explicitly wants device labels. |
- **Rate limit**: 5 / hour / source IP. 429 with `Retry-After` on overage. Don't retry inside the skill — surface the wait to the user.
- **Idempotency**: Within 24h the same `(source_ip, user_agent)` calling again returns the same pending row. On replay the `api_key` field is omitted (the plaintext is never re-shown). If the skill's local `auth.json` is missing AND a replay returns no plaintext, surface a friendly error rather than retrying.
- **Response 200**:
  | field | type | note |
  |---|---|---|
  | `guest_id` | uuid | persist into `auth.json.guest_id` |
  | `api_key` | string | `od_a` + 43 base62 chars; persist into `auth.json.api_key`. **Omitted on idempotent replay** — see above. |
  | `gateway` | string | echoes the API base URL the skill should use; persist into `auth.json.gateway` |
  | `bind_sig` | string | hex MAC; persist into `auth.json.bind_sig`. Used by the skill only to construct the account-binding URL — never sent to the user standalone. |
  | `name` | string | echoes the persisted label. On replay this is whatever the user has curated since (e.g. via the account-binding page or PATCH); on first creation it equals the request body or the server-side default. The skill does not persist it — name lives server-side. |
  | `bind_url` | string | **IGNORED by the skill.** Server-built handoff URL with the shape `https://<dashboard_host>/guest/<guest_id>?h=<bind_sig>`. The skill always derives the account-binding URL locally as `${OD_GATEWAY%/api}/guest/<guest_id>?h=<bind_sig>` and ignores this field on read. After deploy the skill appends `url=<APP_URL>` before printing to the user. |
  | `expires_in_seconds` | int | resource GC horizon (6 hours). Token itself is NOT expired by this; only the project resources are. |

### Bind / list / rename / revoke (OIDC-only, dashboard surface)

These exist for completeness; the **skill never calls them**. The user's browser does, after SSO. Listed here so failure-playbook can describe what 401 means when one is hit.

- `GET  /v1/client-guests/:guest_id/status?h=<bind_sig>` — anonymous, sig-authenticated. Returns `{ guest_id, state, name, hostname, created_at, last_deployed_at, expires_at }` so the account-binding page can pre-fill the rename input before the user signs in.
- `POST /v1/client-guests/:guest_id/bind` — body `{ "sig": "<bind_sig>", "name": "<optional override>" }`. Verifies the HMAC, transitions the credential to `state=bound`, atomically updates ownership for every internal project row matching that credential, and (when `name` is non-empty after trim) overrides the persisted label. Returns `{ guest_id, bound_at, name, project_ids }`.
- `GET /v1/client-guests` — list bound guest credentials for the OIDC user. Each item carries `guest_id`, `name`, `hostname`, `prefix`, `bound_at`, `source_ip`, `source_user_agent`, `last_deployed_at`.
- `PATCH /v1/client-guests/:guest_id` — owner rename. Body `{ "name": "..." }`. Trim + ≤ 64 chars; empty rejected with 400 `name_required`.
- `DELETE /v1/client-guests/:guest_id` — soft-delete + Redis pub-sub invalidation.

### What's gone (do NOT call)

Older HMAC request-signing flows are stale. Every request now uses `Authorization: Bearer od_*` and the client-agent register/bind lifecycle above.

---

## Preamble

### GET `/v1/profile`
User-profile read for dashboard tokens and account-bound local deploy credentials only. **Do not use this as the preflight sanity check** because local credentials not yet linked to an account authenticate as guest tenants and are expected to 401 here.

- **Response 200**: `{"id": uuid, "email": string, "plan": string, ...}`
- **401** -> expected for local credentials not yet linked to an account. Only treat as invalid when the caller expected a dashboard token or account-bound credential.

### GET `/v1/regions` (cluster-service passthrough)
Sanity-check the Bearer token and discover an active region; required for `POST /projects` and `POST /upload/upload-only`. This endpoint works for dashboard tokens, account-bound local credentials, and local credentials not yet linked to an account.

- **Response 200**: array of
  | field | type | note |
  |---|---|---|
  | `id` | uuid | pass as `region_id` / `OD_REGION_ID` |
  | `name` | string | |
  | `code` | string | |
  | `status` | string | `active` / `inactive` - pick first `active` |
  | `environment` | string | `staging` / `production` |

---

## Step 3.1 - POST `/v1/projects` (project-service)
Create a project.

- **Body**:
  | field | type | required | note |
  |---|---|---|---|
  | `name` | string | yes | lowercase, DNS-safe |
  | `repo_url` | string | yes | for non-Git sources use any placeholder + `skip_validation:true` |
  | `branch` | string | optional | default: repo HEAD |
  | `token` | string | optional | Git token for private repo |
  | `build_config` | string (JSON) | optional | |
  | `deploy_config` | string (JSON) | optional | |
  | `region_id` | uuid | optional | server uses `DEFAULT_REGION_ID` if omitted |
  | `skip_validation` | bool | optional | set `true` for ZIP / folder sources |
  | `description` | string | optional | |
- **Response 201**: full `Project` object - `id`, `name`, `repo_url`, `branch`, `region_id`, `created_at`.
- **Errors**:
  - 400 on Git validation failure - body includes `error_code`, `error_message`, optional `available_branches`, `default_branch`.
  - 409 duplicate name.

---

## Step 3.2 - POST `/v1/dependencies/create` (build-service)
Provision a database dependency for the project. Only call if Step 2.5 flagged a DB. `service_id` is intentionally omitted - we bind via env_vars on service creation at Step 3.3.

- **Body**:
  | field | type | required | note |
  |---|---|---|---|
  | `project_id` | uuid | yes | from Step 3.1 |
  | `dependency_id` | string | yes | `postgres` / `mysql` / `mongodb` / `redis` (extend as backend supports) |
  | `template_id` | string | optional | picks a non-default template (e.g. `postgres-15`) |
  | `environment` | string | optional | default `staging` |
  | `service_id` | uuid | optional | **leave empty** at this stage - no service exists yet |
  | `display_name` | string | optional | user-visible name |
  | `username` | string | optional | custom DB user |
  | `password` | string | optional | server generates if omitted |
  | `database_name` | string | optional | custom DB name |
- **Response 200**:
  | field | type | note |
  |---|---|---|
  | `id` | uuid | instance id of the provisioned dep - collect into `DEPENDENCY_IDS_JSON` |
  | `dependency_id` | string | echo |
  | `name` / `display_name` | string | |
  | `type` | string | `postgres`/`mysql`/... |
  | `status` | string | `provisioning` -> `running` |
  | `environment` | string | |
  | `env_vars` | map[string]string | **inject into every consumer service's `runtime_variables`** - typically `DATABASE_URL`, and per-DB fields (e.g. `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`) |
  | `message` | string | |

### Related: GET `/v1/dependencies/status/:project_id`
Optional readiness polling before Step 7.

- **Response 200**: `{ "dependencies": [{ "id": uuid, "status": string, ... }] }`.

---

## Step 3.3 - POST `/v1/projects/:id/services` (project-service)
Create a service inside a project. Call once per detected service. `runtime_variables` is pre-merged: analyzer defaults + DB `env_vars` + user overrides.

- **Path params**: `id` = `PROJECT_ID`.
- **Body**:
  | field | type | required | note |
  |---|---|---|---|
  | `name` | string | yes | DNS-safe |
  | `type` | string | yes | `web` (HTTP), `worker` (background), `cron`, `static` |
  | `environment` | string | yes | `staging` or `production`. Skill defaults to `production` via `$OD_ENVIRONMENT`; pass `OD_ENVIRONMENT=staging` for the preview-style flow |
  | `language` | string | optional | from local analysis |
  | `framework` | string | optional | from local analysis |
  | `port` | int | optional | |
  | `source_path` | string | optional | subfolder in a monorepo |
  | `dockerfile` | string | optional | inline Dockerfile content |
  | `dockerfile_path` | string | optional | path within the tarball |
  | `build_context` | string | optional | |
  | `build_command` | string | optional | |
  | `build_variables` | map[string]string | optional | build-time env (for `ARG` / `NEXT_PUBLIC_*` etc.) |
  | `runtime_variables` | map[string]string | optional | **pre-merged analyzer + DB `env_vars` + user overrides** |
  | `health_check_path` | string | optional | |
  | `readiness_path` | string | optional | |
  | `cpu_request` / `cpu_limit` | string | optional | K8s strings - we set `500m` / `2` |
  | `memory_request` / `memory_limit` | string | optional | `1Gi` / `4Gi` |
  | `replicas` | int | optional | default 1 |
  | `auto_scaling` | bool | optional | |
  | `dependencies` | []string | optional | sibling **service names** this one needs (not DB dep IDs) |
  | `internal_only` | bool | optional | blocks external ingress |
- **Response 201**: `{ "message": "Service created successfully", "service_id": "<uuid>" }` - **not** a full Service object. Parse `.service_id` (fall back to `.id` for older builds). If the caller needs resource/env spec back, follow up with `GET /v1/services/<service_id>`.

> **Encryption-at-rest (server-side, transparent to skill):** every value in `runtime_variables` and `build_variables` is encrypted with the platform AEAD key before being persisted (`service_variables.value` and `secrets.value` rows are stored as ciphertext, `is_encrypted=true`). The skill keeps sending **plaintext** over TLS — do not pre-encrypt. `GET /v1/services/<id>` and `GET /v1/projects/:id/services/:sid/env` return the values **decrypted** by the gateway, so a GET-modify-PUT round-trip continues to work without any extra step.

---

## Step 4 - POST `/v1/upload/upload-only` (project-service)
Park the source on the build-service. Does **not** invoke the analyzer. Either `project_file` or `git_url` must be set.

- **Content-Type**: `multipart/form-data`
- **Form fields**:
  | field | type | required | note |
  |---|---|---|---|
  | `project_name` | string | yes | |
  | `description` | string | optional | |
  | `region_id` | uuid | yes | must be an `active` region |
  | `project_file` | file | conditional | required unless `git_url` set. **ZIP only** - backend handler uses `archive/zip`; tar/tar.gz is rejected |
  | `git_url` | string | conditional | required unless `project_file` set |
  | `git_token` | string | optional | Git token for private repo |
  | `branch` | string | optional | default branch auto-detected |
- **Response 200**:
  | field | type | note |
  |---|---|---|
  | `temp_file_path` | string | pass to `POST /deployments` as `temp_file_path` |
  | `filename` | string | original filename (file path) |
  | `git_url` | string | set when git path |
  | `branch` | string | set when git path |
  | `is_git` | bool | |
- **Errors**: 400 missing file/url, invalid region, Git validation failed (body may include `error_code`, `error_message`, `available_branches`, `default_branch`).

> Do not call `/analyze-only`, `/analyze-from-upload`, `/analyze-env-vars`, `/create-from-analysis` - those invoke server-side LLM analysis we already did locally.
>
> **Caveat - this endpoint alone is not enough.** It parks the ZIP in a shared tmpdir; it does **not** attach the archive to any project, extract it, or populate `project.source_path`. The Temporal deployment workflow reads `deployment.SourcePath` (copied from `project.source_path`) - it does **not** read `TempFilePath` from the deployment row (see `shared/temporal/workflows/deployment.go:1774` -> `agent-service/.../activities.go:431`). You must follow up with Step 4.5 (`/upload/update-source`) before `POST /deployments`, or the build activity immediately fails because `filepath.Join("", "Dockerfile") == "/Dockerfile"` doesn't exist.

---

## Step 4.5 - POST `/v1/upload/update-source` (project-service)
Bind the parked archive to an existing project. Copies the temp file into `/var/lib/minions/projects/<project_id>/<upload_uuid>/`, extracts the ZIP, sets `project.source_path` + `project.original_file_path`, and (if `analysis` is passed) serializes it as the project's `analyze_config`. Handler: `project-service/internal/handlers/upload.go:1907` (`UpdateProjectSource`).

This is the step the Dashboard "Update source" button calls and is **required for every ZIP-based deploy**. Not to be confused with `/upload/analyze-from-upload`, which also runs server-side LLM analysis (forbidden by this skill).

- **Body**:
  | field | type | required | note |
  |---|---|---|---|
  | `project_id` | uuid | yes | existing project from Step 3.1 |
  | `temp_file_path` | string | yes | value returned by Step 4 - backend `os.Stat`s this path, so it must still exist |
  | `analysis` | object | optional | the local `ProjectAnalysisResult` from Step 2; if omitted, the build activity falls back to Railpack auto-detect. Unknown fields are ignored - a best-effort match of the skill's analysis schema is fine |
- **Response 200**:
  | field | type | note |
  |---|---|---|
  | `project_id` | uuid | echo |
  | `source_path` | string | absolute path on project-service's filesystem to the extracted directory |
  | `services` | `[]Service` | services currently attached to the project |
  | `message` | string | `"Project source updated successfully"` or `"Project source already up to date"` when the temp file is expired but the project still has a valid `source_path` |
- **Errors**:
  - 400 `{"error":"Uploaded file not found or expired..."}` - temp file cleaned up before this call. Re-upload and retry.
  - 403 ownership - wrong user.
  - 404 - wrong project id.
  - 500 - filesystem write failed.

---

## Step 5 - PUT `/v1/projects/:id/services/:service_id/env` (project-service)
Optional: override / rotate runtime variables after the service is created. **Full replace** - missing keys get removed.

- **Path params**: `id` = `PROJECT_ID`, `service_id` = `SERVICE_ID`.
- **Body**:
  | field | type | required | note |
  |---|---|---|---|
  | `variables` | map[string]string | yes | replaces all runtime vars for this service |
- **Server limits** (400 on violation): key <= 128 chars, value <= 32 KiB.
- **Response 200**: `{ "service_id": uuid, "variables": [...], "count": int }`.

> **Encryption-at-rest:** every value in `variables` is encrypted server-side before the row is written (`service_variables.value` is ciphertext, `is_encrypted=true`). Skill sends **plaintext** — do not pre-encrypt. The matching `GET` decrypts and returns plaintext, so the GET-modify-PUT pattern works unchanged.

> To rotate one value, first `GET /projects/:id/services/:sid/env` (returns the decrypted map) and PUT the merged map. Never log the GET response body wholesale — it contains decrypted secrets.

---

## Step 6 - no-op (resources handled inline)

Resources are set **only at Step 3.3** (`cpu_request / cpu_limit / memory_request / memory_limit` in the `POST /v1/projects/:id/services` body, K8s strings - `500m`, `2`, `1Gi`, `4Gi`). The deployment handler reads them off the Service row for each build.

> **Do NOT pass `resources:{...}` in the Step 7 body.** Earlier versions of this schema suggested re-asserting resources there; that re-assertion 400s with `json: cannot unmarshal string into Go struct field ResourceLimits.resources.cpu_limit of type float64` because the deployment-service `ResourceLimits` struct expects **numeric cores/GiB**, not K8s strings. Either leave the block off entirely (recommended, Service row is authoritative) or, if you must override per-deploy, send numeric values (e.g. `cpu_limit: 2.0`, `memory_limit: 4`).

> **Do not call `PUT /v1/projects/:id/resources`.** The handler (`UpdateProjectResources`) is registered on deployment-service (`deployment-service/internal/routes/routes.go:85`) but **not** proxied by the gateway (`gateway/internal/routes/routes.go` has no matching route). Attempting returns 404.

### Alternative: change resources on an existing running service

If you later need to adjust resources without redeploying:

#### PUT `/v1/services/:id` (project-service, gateway-exposed)
- **Path params**: `id` = `SERVICE_ID`.
- **Body** (partial update; only the fields below relevant here - see `UpdateServiceRequest` for full set):
  | field | type | note |
  |---|---|---|
  | `cpu_request` | string | K8s cpu, e.g. `500m` |
  | `cpu_limit` | string | e.g. `2` |
  | `memory_request` | string | e.g. `1Gi` |
  | `memory_limit` | string | e.g. `4Gi` |
- **Response 200**: updated `Service` object.
- Per-service only - loop over `SERVICE_ID`s if you want to touch them all.

---

## Step 7 - POST `/v1/deployments` (deployment-service)
Trigger build + deploy for one service. Requires subscription + quota (gateway returns 403 otherwise).

- **Body** (skill-relevant fields only - full set in `CreateDeploymentRequest`):
  | field | type | required | note |
  |---|---|---|---|
  | `project_id` | uuid | yes | |
  | `service_id` | uuid | yes | the service to deploy |
  | `environment` | string | yes | `staging` or `production`. Skill default is `production` via `$OD_ENVIRONMENT` ("push to live"); pass `OD_ENVIRONMENT=staging` for preview |
  | `source` | string | yes | `git` (Step 4.b) or `zip` (Step 4.a) |
  | `temp_file_path` | string | yes | from Step 4 - stored on the deployment row for dependency-detection hints. **Does not feed the build.** The build activity reads the directory at `project.source_path` populated by Step 4.5 |
  | `branch` | string | optional | for `source=git` |
  | `resources` | object | **omit** | See Step 6. Sending K8s-string values 400s; Service row is authoritative. Only include if overriding per-deploy with numeric cores/GiB |
  | `strategy` | string | optional | deployment strategy; server default if omitted |
  | `version_type` | string | optional | `major` / `minor` / `patch` |
  | `description` | string | optional | |
  | `env_vars` | object | optional | leave empty - env was baked at Step 3.3 unless you did a Step 5 override |
  | `dependencies` | []string | optional | dependency IDs this version binds to (from Step 3.2) |
  | `is_rollback` | bool | optional | leave false |
  | `use_github_token` | bool | optional | leave false |
- **Response 201/200**:
  | field | type | note |
  |---|---|---|
  | `id` | uuid | `DEPLOYMENT_ID` |
  | `status` | string | initial - usually `pending` or `analyzing` |
  | `project_id` / `service_id` | uuid | |
  | `environment` | string | |
  | `created_at` | RFC3339 | |
- **400** missing `temp_file_path` or invalid strategy. **403** subscription / quota.

### Status + logs

#### GET `/v1/deployments/:id`
The canonical way to poll terminal state. Returns the full deployment record plus a `runtime_logs_query` hint.

- **Response 200** (skill-relevant fields only):
  | field | type | note |
  |---|---|---|
  | `id` | uuid | |
  | `status` | string | `pending`/`analyzing`/`pending_review`/`building`/`deploying`/`success`/`failed`/`cancelled`/`rolled_back` |
  | `progress` | int | 0-100; jumps to `10` right before the Temporal workflow starts |
  | `message` / `error_msg` / `error_context` | string | populated on `failed` |
  | `temp_file_path` | string | echo from create |
  | `completed_at` | RFC3339 | set on terminal status |

> The `GET /v1/deployments/:id/status` alias **is listed in `Backend/API.md:62` as `.../:id/status` and `.../status/:id`** but the gateway does **not** register it - calls return 404 page-not-found. Always poll `GET /v1/deployments/:id` instead. The list form `GET /v1/deployments/?project_id=<pid>` returns the same record wrapped under `.data[]` if you need to correlate siblings.

#### GET `/v1/deployments/:id/logs?tail=N&since=RFC3339`
- **Response 200**: `{"deployment_id": uuid, "logs": [...] | null, "total": int}`. `logs` is `null` when the deployment failed in the pre-build synchronous path (Temporal workflow started but the per-service activity errored before writing any log) - that's the `progress=10` sub-2-second failure signature covered in `failure-playbook.md`.

#### GET `/v1/deployments/:id/logs/stream` (SSE)
Live deploy logs.

#### GET `/v1/deployments/:id/build-logs/stream` (WebSocket)
Live build logs from ClickHouse. Prefer this over SSE for builds > 5 min. "Task polling timeout" surfaced elsewhere is a frontend 5-min timeout - trust ClickHouse build_logs for real state.

---

## Step 8 - Domain binding (project-service)

### 8.1 GET `/v1/service-domains/check-subdomain/:subdomain`
- **Path params**: `subdomain` = the prefix only, not the full FQDN.
- **Response 200**:
  | field | type | note |
  |---|---|---|
  | `available` | bool | |
  | `reason` | string | filled when `available:false` - `"reserved"` or `"taken"` |
- **Reserved list** (hard-blocked server-side): `www, api, admin, dashboard, console, app, apps, mail, ftp, ssh, vpn, cdn, static, assets, media, images, files, docs, blog, shop, store, payment, pay, billing, account, login, auth, oauth, sso, security, secure, test, staging, dev, development, prod, production, demo, preview, beta, minions, system, root, ns1, ns2, mx, status, health, ingress, registry, monitor, grafana, ...`.

### 8.2 GET `/v1/service-domains?service_id=<uuid>`
List domains for a service.

- **Query params**:
  - `service_id` (uuid) - required filter.
  - `environment` (`staging`|`production`) - optional.
  - `type` (`auto`|`custom`) - optional.
- **Response 200**: array of `ServiceDomain`:
  | field | type | note |
  |---|---|---|
  | `id` | uuid | |
  | `service_id` | uuid | |
  | `project_id` | uuid | |
  | `domain` | string | full FQDN |
  | `environment` | string | `staging` / `production` |
  | `type` | string | `auto` / `custom` |
  | `status` | string | `pending` / `active` / `verified` / `failed` |
  | `ssl_enabled` | bool | |
  | `is_primary` | bool | |

### 8.3 PUT `/v1/service-domains/:id/subdomain`
Rename the auto subdomain prefix.

- **Path params**: `id` = the auto domain's id from 8.2.
- **Body**:
  | field | type | required | note |
  |---|---|---|---|
  | `subdomain` | string | yes | 2-32 chars, `[a-z0-9-]`, no leading/trailing hyphen |
- **Response 200**: updated `ServiceDomain` - new `domain` = `<subdomain>.opendeploy.run` (production) or `<subdomain>.dev.opendeploy.run` (staging).
- **Errors**: 400 invalid format; 409 collision; 403 not your service. Works for both `staging` and `production` auto-domains.
- **Caveat**: server-side handler is documented for auto-generated domains. If the auto domain row for `$OD_ENVIRONMENT` hasn't been written yet (can happen right after Step 7 completes), poll 8.2 for up to 30 s before 8.3.

### 8.4 POST `/v1/service-domains/:id/retry`
Optional: kick the domain controller to re-reconcile cert + ingress after a rename. Safe to skip - usually auto-reconciles within 30 s.

- **Body**: none.
- **Response 200**: `{ "status": "reconciling" }` or similar acknowledgement.
