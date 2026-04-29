# Operate — redeploy, rotate env, resize, add DB, rollback, triage

Pre-conditions: `auth.md` ran and you have a working `$AUTH` for a dashboard token or account-bound local deploy credential. Local credentials not yet linked to an account can still call most of these (resource caps still apply); the exceptions are flagged below.

Source the operation logger at the top of the first bash block in this chain so every operation is recorded in `~/.opendeploy/logs/<UTC-date>.log`:

```bash
[ -f "$HOME/.opendeploy/lib/log.sh" ] && . "$HOME/.opendeploy/lib/log.sh"
```

Each operation in the matrix below should emit one `od_log info operate.<verb>` line at completion (e.g. `od_log info operate.redeploy deployment_id "$DEPLOYMENT_ID" status "$S"`). For `PUT /env`, log only `var_keys` and `var_count` — never the values.

> **Encryption-at-rest is server-side.** Every value sent in `runtime_variables` / `build_variables` / `variables` is encrypted by the gateway before being written to `service_variables` / `secrets`. The skill always sends **plaintext** over TLS — there is no client-side encryption step, no `is_encrypted` flag, no per-key opt-in. `GET /v1/projects/:id/services/:sid/env` returns the decrypted values, so GET-modify-PUT rotation is straightforward; just don't pipe the GET response into `od_log` or stdout, since at that moment you're holding decrypted secret material.

## Operation matrix

| Intent | Pattern |
|---|---|
| **Redeploy current source** | `POST /v1/deployments/` with the existing `service_id` (deploy.md Step 7). Skip Steps 4 / 4.5 if source hasn't changed. |
| **Redeploy with new source** | deploy.md Steps 4 → 4.5 → 7. Step 4.5 is required — it re-extracts the ZIP and updates `project.source_path`. |
| **Rotate env vars / secrets** | `PUT /v1/projects/$PID/services/$SID/env` (deploy.md Step 5, full replace) → deploy.md Step 7. |
| **Resize a running service** | `PUT /v1/services/$SID` with K8s strings (`cpu_request`, `cpu_limit`, `memory_request`, `memory_limit`). No redeploy needed — the K8s deployment rolls. **Don't** call `PUT /api/v1/projects/:id/resources` (not proxied, 404s). |
| **Add a DB to an existing service** | setup.md 3.2 (create dependency) → merge `env_vars` via deploy.md Step 5 → deploy.md Step 7. |
| **Rename subdomain** | domain.md 8.1 → 8.2 → 8.3 against the existing `ServiceDomain` row. No redeploy. |
| **Cancel a running deployment** | `POST /v1/deployments/$DID/cancel`. Confirm with user first — drops the build. |
| **Roll back** | Find a previous successful `deployment_id` via `GET /v1/projects/$PID/deployments?status=success` → `POST /v1/deployments/$DID/rollback`. |
| **Triage a failed deploy** | `GET /v1/deployments/$DID/logs?tail=300` → ClickHouse build logs `GET /v1/deployments/$DID/build-logs/stream` → map symptom via [`failure-playbook.md`](failure-playbook.md). |

When the request spans two areas ("rotate the DATABASE_URL and redeploy"), do them in one chain — don't ask the user to invoke each step separately.

## Account-binding gates

Local deploy credentials that are not linked to an account will hit `403 bind_required` on:

- billing / subscription routes (`/v1/billing/...`)
- custom production domains (CNAME on a user-owned hostname)

The skill cannot bind on the user's behalf. Surface the error with a clear pointer to the account-binding URL. The URL is **not** stored in `auth.json` — derive it on the fly from the persisted `guest_id` + `bind_sig` + `gateway`:

```bash
GUEST_ID=$(jq -r '.guest_id // .agent_id // empty' "$HOME/.opendeploy/auth.json")
BIND_SIG=$(jq -r '.bind_sig' "$HOME/.opendeploy/auth.json")
GATEWAY=$( jq -r '.gateway'  "$HOME/.opendeploy/auth.json")
BIND_URL="${GATEWAY%/api}/guest/$GUEST_ID?h=$BIND_SIG"
```

## User-only actions (never execute directly)

Show the command, explain the side effect, wait for the user.

| Action | Why user-only |
|---|---|
| Create / rotate a dashboard token via dashboard or `POST /v1/user/api-key` | Requires session login; key shown once. The skill never replaces a dashboard token silently. |
| Project deletion (`DELETE /v1/projects/:id`) | Irreversible; drops services, deployments, DBs |
| `PUT /env` with full secret replacement | Full-replace semantics; easy to wipe a needed var |
| Custom production domain | Out of scope; user binds from dashboard |
| Bind / revoke a guest credential | The user's browser holds the OIDC session. The skill never tries to call `/v1/client-guests/:guest_id/bind` itself. |
