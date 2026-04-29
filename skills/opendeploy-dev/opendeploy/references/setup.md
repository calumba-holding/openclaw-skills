# Setup — create project, DB dependencies, services

Order is fixed: project first, then DB deps (so `env_vars` are ready), then services (pre-merged env baked in). Every curl carries `-H "$AUTH"` — there is no other auth shape. Pre-conditions: `auth.md` has run (so `$AUTH`, `$OD_GATEWAY`, `$OD_REGION_ID` are set) and `analyze-local.md` has produced `$WORKDIR/.opendeploy/analysis.json`.

Source the operation logger at the top of the first bash block in this chain so every `od_log info setup.<step>` call below has somewhere to write:

```bash
[ -f "$HOME/.opendeploy/lib/log.sh" ] && . "$HOME/.opendeploy/lib/log.sh"
```

## DB decision (no API)

Flag a DB if **any**:

- `analysis.database_type` in `{postgres, mysql, mongodb, redis}`
- Any `runtime_vars[].name` ~ `DATABASE_URL | MYSQL_* | POSTGRES_* | PG_* | REDIS_URL | MONGO* | CLICKHOUSE_*`
- A compose DB image was found during local analysis

No DB flagged → skip 3.2:

```bash
DEPENDENCY_IDS_JSON='[]'; echo '{}' > db_env.json
```

Unlinked local deploy credentials may provision a DB (D6 contract). The 1-service-per-project cap still applies, so the DB lives alongside the single web service in the same project.

## 3.1 Create project → `POST /projects/`

```bash
PROJ=$(curl -fsSL -X POST "$OD_GATEWAY/v1/projects/" \
  -H "$AUTH" -H "$JSON" \
  -d "$(jq -n --arg name "$PROJECT_NAME" \
                --arg repo "${GIT_URL:-file://upload}" \
                --arg branch "${GIT_BRANCH:-main}" \
                --arg token "${GIT_TOKEN:-}" \
                --arg region "$OD_REGION_ID" \
     '{name:$name, repo_url:$repo, branch:$branch, token:$token, region_id:$region,
       skip_validation: ($repo|startswith("file://"))}')")
PROJECT_ID=$(echo "$PROJ" | jq -r .id)
od_log info setup.project_create project_id "$PROJECT_ID" name "$PROJECT_NAME" region_id "$OD_REGION_ID"
```

The gateway automatically links the new project to the local deploy credential (writes the internal `projects.agent_id` audit field) when the credential is not yet linked to an account. No additional client-side work needed.

For unlinked local deploy credentials: a second `POST /projects/` from the same credential while a prior project still exists returns **409** with the existing `project_id` — guest credentials are capped at one live project at a time. If you need a second project, wait for the first to be GC'd (6 h) or have the user bind and use a dashboard token.

Schema: [`api-schemas.md`](api-schemas.md) → Step 3.1. Handles 400 Git validation errors with `error_code` / `available_branches` — see [`failure-playbook.md`](failure-playbook.md).

## 3.2 Create DB dependencies (skip if DB decision didn't flag)

```bash
DEP=$(curl -fsSL -X POST "$OD_GATEWAY/v1/dependencies/create" \
  -H "$AUTH" -H "$JSON" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg did "$DEPENDENCY_ID" --arg env "$OD_ENVIRONMENT" \
     '{project_id:$pid, dependency_id:$did, environment:$env}')")
DEP_ID=$(echo "$DEP"  | jq -r .id)
DEP_ENV=$(echo "$DEP" | jq -c .env_vars)
od_log info setup.dependency_create project_id "$PROJECT_ID" dependency_id "$DEPENDENCY_ID" dep_id "$DEP_ID" environment "$OD_ENVIRONMENT"
```

`$OD_ENVIRONMENT` is set by `auth.md` and defaults to `production` ("push to live"). Pass `OD_ENVIRONMENT=staging` from the shell to keep the preview-style flow.

Collect all `DEP_ID`s into `DEPENDENCY_IDS_JSON`. Merge every `DEP_ENV` into `db_env.json`. Optionally poll `GET /dependencies/status/:project_id` until `running` before deploy. Schema: [`api-schemas.md`](api-schemas.md) → Step 3.2.

## 3.3 Create each service → `POST /projects/:id/services/`

Extract the analyzer's per-service var arrays out of `analysis.json` into the
two scratch files the merge step expects. Do this even if either array is
empty — `jq` outputs `[]` and the merge below handles that. Skipping this
step (or skipping the build half) is what caused skill-deployed services to
land with empty `build_variables` and break `NEXT_PUBLIC_*` / `VITE_*` builds.

Real `.env` values, when present, are collected by `analyze-local.md` section
3.5 into `user_overrides.json` and `user_build_overrides.json`. Those files are
local deployment transport only: mode `0600`, never committed, never logged,
and deleted after the deploy attempt. Their key/value pairs are submitted to
the opendeploy API in the `runtime_variables` / `build_variables` fields below.

```bash
SVC_JSON=$(jq -c --arg name "$SVC_NAME" \
  '(.services // [.]) | map(select(.name==$name or .service_name==$name)) | .[0] // (.services[0] // .)' \
  "$WORKDIR/.opendeploy/analysis.json")
echo "$SVC_JSON" | jq '.runtime_vars      // []' > analyzer_runtime.json
echo "$SVC_JSON" | jq '.build_time_vars   // []' > analyzer_build.json
[ -f db_env.json ]            || echo '{}' > db_env.json
[ -f user_overrides.json ]    || echo '{}' > user_overrides.json
[ -f user_build_overrides.json ] || echo '{}' > user_build_overrides.json
chmod 600 user_overrides.json user_build_overrides.json 2>/dev/null || true
```

Pre-merge **both** runtime and build-time vars (later sources override earlier).
`BUILD_VARS` is parallel to `RUNTIME_VARS` — analyzer defaults overlaid with
user overrides. There are no DB-injected build-time vars, so `db_env.json`
participates only in the runtime merge:

```bash
RUNTIME_VARS=$(jq -s '
  (.[0] | map({(.name): (.default // "")}) | add // {}) * (.[1] // {}) * (.[2] // {})
' analyzer_runtime.json db_env.json user_overrides.json)

BUILD_VARS=$(jq -s '
  (.[0] | map({(.name): (.default // "")}) | add // {}) * (.[1] // {})
' analyzer_build.json user_build_overrides.json)
```

### Env upload consent gate (required before the POST below)

Real `.env` values cross the wire as part of `runtime_variables` /
`build_variables` in the request body below. Before that POST, surface an
`AskUserQuestion` listing the keys the agent merged from `user_overrides.json`
and `user_build_overrides.json` (i.e. the keys whose **values came from the
user's .env files**, not analyzer defaults or DB-injected vars). Show **keys
only — never values, never first/last characters of values, never lengths**.

Compute the keyset and a stable hash so subsequent redeploys of the same
project don't re-prompt unless the keyset changes:

```bash
ENV_KEYS=$(jq -s '(.[0] // {}) * (.[1] // {}) | keys | sort' \
  user_overrides.json user_build_overrides.json)
ENV_KEYS_HASH=$(printf '%s' "$ENV_KEYS" | shasum -a 256 | awk '{print $1}')

# If user_overrides + user_build_overrides are both empty objects, there is
# nothing user-supplied to upload (analyzer defaults + DB env are already
# non-secret). Skip the gate entirely in that case.
if [ "$(echo "$ENV_KEYS" | jq 'length')" -gt 0 ]; then
  PRIOR=$(jq -r --arg pid "$PROJECT_ID" --arg h "$ENV_KEYS_HASH" \
    '(.env_consent // {})[$pid] | select(.keys_hash == $h) | .approved_at // empty' \
    "$AUTH_FILE" 2>/dev/null)

  if [ -z "$PRIOR" ]; then
    # Surface AskUserQuestion to the agent. The agent renders ENV_KEYS in the
    # body (one per line) and exposes three options:
    #   - "Approve and upload" → continue.
    #   - "Redact specific keys" → user names keys to drop; agent re-runs
    #     this block with those keys removed from user_overrides.json and
    #     user_build_overrides.json before recomputing ENV_KEYS / ENV_KEYS_HASH.
    #   - "Cancel" → exit 0 without sending any env values.
    #
    # Do NOT echo any value from user_overrides.json into the prompt body.
    # The body must contain only key names and the gateway destination.
    od_log info setup.env_consent_prompt project_id "$PROJECT_ID" \
      keys_hash "$ENV_KEYS_HASH" key_count "$(echo "$ENV_KEYS" | jq 'length')"

    # Once the user picks "Approve and upload", record consent. Use a
    # tempfile + mv to keep the write atomic; never widen the file mode.
    TMP_AUTH=$(mktemp)
    jq --arg pid "$PROJECT_ID" --arg h "$ENV_KEYS_HASH" \
       --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
       '.env_consent = (.env_consent // {}) | .env_consent[$pid] = {keys_hash:$h, approved_at:$ts}' \
       "$AUTH_FILE" > "$TMP_AUTH" && mv "$TMP_AUTH" "$AUTH_FILE"
    chmod 600 "$AUTH_FILE"
    od_log info setup.env_consent_record project_id "$PROJECT_ID" keys_hash "$ENV_KEYS_HASH"
  fi
fi
```

The cache key is `(project_id, keys_hash)` — adding a new env key invalidates
the cached consent and re-prompts. Removing a key does not (the prior superset
already covered it). Pasting a token into `auth.json` manually does not grant
env consent; the prompt is per-project, not per-credential.

**Guest credential caps** (gateway middleware enforces these BEFORE the proxy reaches project-service, returns `403 guest_quota_exceeded` with offending `field` / `requested` / `limit` keys):

- `cpu_limit` ≤ `1` vCPU (1000 millicores)
- `memory_limit` ≤ `1Gi` (1 GiB)
- `replicas` ≤ 1
- 1 service per project

For unlinked local deploy credentials, send these explicitly:

```bash
SVC=$(curl -fsSL -X POST "$OD_GATEWAY/v1/projects/$PROJECT_ID/services/" \
  -H "$AUTH" -H "$JSON" \
  -d "$(jq -n --arg name "$SVC_NAME" --arg type "web" --arg env "$OD_ENVIRONMENT" \
                --arg lang "$SVC_LANG" --arg fw "$SVC_FW" \
                --argjson port "$SVC_PORT" \
                --argjson build_vars "$BUILD_VARS" \
                --argjson runtime_vars "$RUNTIME_VARS" \
     '{name:$name, type:$type, environment:$env, language:$lang, framework:$fw, port:$port,
       build_variables:$build_vars, runtime_variables:$runtime_vars,
       cpu_request:"500m", cpu_limit:"1", memory_request:"512Mi", memory_limit:"1Gi", replicas:1}')")
SERVICE_ID=$(echo "$SVC" | jq -r '.service_id // .id')
# Log only the *names* of variables that landed on the service row — values
# are never logged. The runtime_vars / build_vars maps are local to setup.md
# so we serialise their keysets with `keys` here.
od_log info setup.service_create project_id "$PROJECT_ID" service_id "$SERVICE_ID" \
  name "$SVC_NAME" type web language "$SVC_LANG" framework "$SVC_FW" port "$SVC_PORT" \
  runtime_var_keys "$(echo "$RUNTIME_VARS" | jq -c 'keys')" \
  build_var_keys "$(echo "$BUILD_VARS"   | jq -c 'keys')"
```

For dashboard tokens and account-bound local credentials, use the same shape but raise the limits to whatever the user's subscription allows (typical default is `cpu_limit:"2"`, `memory_limit:"4Gi"`).

Prompt user **before** the POST for any `required:true` var with empty default (LLM/API keys, third-party secrets). Never auto-generate secrets. Schema: [`api-schemas.md`](api-schemas.md) → Step 3.3.

> **Encryption-at-rest is server-side and transparent.** The backend encrypts every value in `runtime_variables` and `build_variables` with the platform AEAD key before persisting (`service_variables` and `secrets` rows store ciphertext; `is_encrypted=true` on each row). Send **plaintext** in the POST body — do not pre-encrypt, do not flag fields as secret, do not omit required values "to keep them out of the wire" (TLS already covers transit, and the server cannot run the deploy without the value). The K8s router still gets the plaintext at deploy time so build-arg substitution and runtime env injection both work; only at-rest persistence is encrypted.
