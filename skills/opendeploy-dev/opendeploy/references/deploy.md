# Deploy — park source, bind to project, build, watch, report

Pre-conditions: `auth.md` ran (so `$AUTH`, `$OD_GATEWAY`, `$OD_REGION_ID`, `$OD_ENVIRONMENT`, `$GUEST_ID`, `$BIND_SIG`, `$BIND_URL`, `$IS_BOUND` are set), and `setup.md` ran (so `$PROJECT_ID`, `$SERVICE_ID`, optionally `$DEPENDENCY_IDS_JSON` are set). For redeploy of an existing service, only Step 4 -> 4.5 -> 7 + 9 fire (everything else is reused).

Source the operation logger at the top of the first bash block in this chain. Re-sourcing is idempotent — needed because the agent may run deploy.md in a separate Bash invocation from auth.md:

```bash
[ -f "$HOME/.opendeploy/lib/log.sh" ] && . "$HOME/.opendeploy/lib/log.sh"
```

## Step 4 — Park source → `POST /upload/upload-only`

Parks the archive in a shared tmpdir and returns a `temp_file_path`. **Does NOT bind the upload to any project, does NOT extract the ZIP, does NOT set `project.source_path`.** Step 4.5 does all of that.

Pick 4.a or 4.b per service.

**4.a ZIP** (local folder / existing ZIP / monorepo subfolder). **Must be ZIP** — the backend only imports `archive/zip`, no `.tar.gz`.

```bash
SRC_ZIP="$WORKDIR/.opendeploy/$SVC_NAME.zip"
mkdir -p "$(dirname "$SRC_ZIP")"

# zip from inside the service subfolder so paths are flat.
# Real env/credential files are deployment inputs, not source artifacts.
(cd "$WORKDIR/$SVC_SOURCE_PATH" && \
  zip -qr "$SRC_ZIP" . \
    -x '*.git/*' 'node_modules/*' 'dist/*' 'build/*' \
       'target/*' '.venv/*' '__pycache__/*' '*.pyc' \
       '.opendeploy/*' \
       '.env' '.env.*' '.npmrc' '.pypirc' '.netrc' \
       '*.pem' '*.key' 'id_rsa' 'id_rsa.pub' 'id_ed25519' 'id_ed25519.pub' \
       'credentials.json' 'service-account*.json' '*kubeconfig*')

UP=$(curl -fsSL -X POST "$OD_GATEWAY/v1/upload/upload-only" \
  -H "$AUTH" \
  -F "project_name=$PROJECT_NAME" -F "region_id=$OD_REGION_ID" \
  -F "project_file=@$SRC_ZIP")
```

If the user supplied an existing ZIP, inspect before upload:

```bash
UNSAFE_ZIP_ENTRIES=$(unzip -l "$SRC_ZIP" | awk '
  { path=$NF }
  path ~ /(^|\/)\.env($|[.\/])/ ||
  path ~ /(^|\/)\.(npmrc|pypirc|netrc)$/ ||
  path ~ /(^|\/)(id_rsa|id_rsa\.pub|id_ed25519|id_ed25519\.pub)$/ ||
  path ~ /\.(pem|key)$/ ||
  path ~ /(^|\/)(credentials\.json|service-account.*\.json)$/ ||
  path ~ /kubeconfig/ { print path }
')
[ -z "$UNSAFE_ZIP_ENTRIES" ] || {
  printf '%s\n' "ZIP contains env or credential files. Provide a sanitized ZIP or explicitly approve uploading these files." >&2
  printf '%s\n' "$UNSAFE_ZIP_ENTRIES" >&2
  exit 1
}
```

Do not upload a ZIP that contains real env or credential files by default.

**4.b Git URL** (whole-repo deploy):

```bash
UP=$(curl -fsSL -X POST "$OD_GATEWAY/v1/upload/upload-only" \
  -H "$AUTH" \
  -F "project_name=$PROJECT_NAME" -F "region_id=$OD_REGION_ID" \
  -F "git_url=$GIT_URL" \
  ${GIT_BRANCH:+-F "branch=$GIT_BRANCH"} \
  ${GIT_TOKEN:+-F "git_token=$GIT_TOKEN"})
```

`GIT_TOKEN` is sent only to the opendeploy gateway for private repository
access. Never print it, log it, or include it in `analysis.json`.

```bash
TEMP_FILE_PATH=$(echo "$UP" | jq -r .temp_file_path)
od_log info deploy.upload_only project_id "$PROJECT_ID" service_id "$SERVICE_ID" \
  source "${GIT_URL:+git}${GIT_URL:-zip}" temp_file_path "$TEMP_FILE_PATH"
```

Schema: [`api-schemas.md`](api-schemas.md) → Step 4.

## Step 4.5 — Bind upload to project → `POST /upload/update-source` (REQUIRED)

`/upload/upload-only` alone only parks the archive in a shared tmpdir. The deployment handler writes `temp_file_path` into the Deployment row, but **the Temporal workflow input uses `SourcePath`, not `TempFilePath`**. Without Step 4.5, `SourcePath == ""` and every build fails inside 1 second with the generic `"Service failed to deploy"` — see [`failure-playbook.md`](failure-playbook.md) → *Deployment fails at progress=10 within seconds*.

`/upload/update-source` copies the temp file into `/var/lib/minions/projects/<PROJECT_ID>/<uuid>/`, extracts the ZIP, sets `project.source_path` to the extracted directory, and (if `analysis` is provided) writes `project.analyze_config` JSON so the build activity can skip its own LLM analysis.

```bash
UPDATE=$(curl -fsSL -X POST "$OD_GATEWAY/v1/upload/update-source" \
  -H "$AUTH" -H "$JSON" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg tmp "$TEMP_FILE_PATH" \
              --slurpfile analysis "$WORKDIR/.opendeploy/analysis.json" \
     '{project_id:$pid, temp_file_path:$tmp, analysis:$analysis[0]}')")

SOURCE_PATH=$(echo "$UPDATE" | jq -r .source_path)
od_log info deploy.update_source project_id "$PROJECT_ID" source_path "$SOURCE_PATH"
```

If your local `analysis.json` doesn't conform to the backend `ProjectAnalysisResult` shape, omit the `analysis` key — Step 4.5 will still bind + extract; the build activity falls back to Railpack auto-detect.

Schema: [`api-schemas.md`](api-schemas.md) → Step 4.5. Not optional.

## Step 5 — Env override (optional) → `PUT /projects/:id/services/:sid/env`

Skip unless user supplied late secrets or is rotating. PUT is a **full replace** — your payload becomes the entire variable set.

### Env upload consent gate (required before the PUT below)

Same shape as `setup.md` Step 3.3. Hash the sorted keyset of `$OVERRIDES`,
look up `auth.json` `.env_consent[$PROJECT_ID].keys_hash`, and re-prompt
via `AskUserQuestion` if the hash changed (or no record exists yet).
Show keys only — never values:

```bash
ENV_KEYS=$(echo "$OVERRIDES" | jq 'keys | sort')
ENV_KEYS_HASH=$(printf '%s' "$ENV_KEYS" | shasum -a 256 | awk '{print $1}')
PRIOR=$(jq -r --arg pid "$PROJECT_ID" --arg h "$ENV_KEYS_HASH" \
  '(.env_consent // {})[$pid] | select(.keys_hash == $h) | .approved_at // empty' \
  "$AUTH_FILE" 2>/dev/null)
if [ -z "$PRIOR" ]; then
  od_log info deploy.env_consent_prompt project_id "$PROJECT_ID" service_id "$SERVICE_ID" \
    keys_hash "$ENV_KEYS_HASH" key_count "$(echo "$ENV_KEYS" | jq 'length')"
  # Agent surfaces AskUserQuestion (Approve / Redact / Cancel). On Redact,
  # drop the named keys from $OVERRIDES, recompute, retry. On Cancel,
  # exit 0 without sending the PUT.
  TMP_AUTH=$(mktemp)
  jq --arg pid "$PROJECT_ID" --arg h "$ENV_KEYS_HASH" \
     --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     '.env_consent = (.env_consent // {}) | .env_consent[$pid] = {keys_hash:$h, approved_at:$ts}' \
     "$AUTH_FILE" > "$TMP_AUTH" && mv "$TMP_AUTH" "$AUTH_FILE"
  chmod 600 "$AUTH_FILE"
fi
```

```bash
curl -fsSL -X PUT "$OD_GATEWAY/v1/projects/$PROJECT_ID/services/$SERVICE_ID/env" \
  -H "$AUTH" -H "$JSON" \
  -d "$(jq -n --argjson vars "$OVERRIDES" '{variables:$vars}')"
# Log only the *names* of variables that were rotated — values never touch the log.
od_log info deploy.env_replace project_id "$PROJECT_ID" service_id "$SERVICE_ID" \
  var_keys "$(echo "$OVERRIDES" | jq -c 'keys')" var_count "$(echo "$OVERRIDES" | jq 'length')"
```

> **Encryption-at-rest:** the gateway encrypts every value in `variables` with the platform AEAD key before writing the `service_variables` rows (the row's `is_encrypted` column flips to `true`). Send **plaintext** in the PUT body — there is no client-side key, no `is_encrypted` flag, no per-key opt-in. The matching `GET /v1/projects/:id/services/:sid/env` decrypts and returns plaintext, which is why the GET-modify-PUT rotation pattern still works. Do **not** dump the GET response body to logs or stdout — it is decrypted secret material.

Schema: [`api-schemas.md`](api-schemas.md) → Step 5.

## Step 6 — Resources (no separate call)

Resources are set **only at service creation** (in `setup.md` Step 3.3, body fields `cpu_request/cpu_limit/memory_request/memory_limit` as K8s strings). The deployment handler reads them off the Service row.

> **Do NOT pass `resources:{...}` in the Step 7 body.** `deployment-service` defines `ResourceLimits.cpu_limit` as `float64`, so sending K8s strings (`"2"`, `"500m"`, `"1Gi"`) returns `400 json: cannot unmarshal string into Go struct field ResourceLimits.resources.cpu_limit of type float64`. The skill previously re-asserted this block and every first deploy 400'd until it was dropped. If you need to override at Step 7, switch to numeric cores/GiB — but the service-row values are already the source of truth.

> The `PUT /api/v1/projects/:id/resources` handler is **not** proxied by the gateway — it 404s. Don't call it. To change resources on a running service without redeploying, use `PUT /v1/services/:id` with the same four K8s-style fields (see [`operate.md`](operate.md)).

## Step 7 — Build + deploy → `POST /deployments/`

One call per service. Requires Step 4.5 to have run.

```bash
SOURCE=${GIT_URL:+git}; SOURCE=${SOURCE:-zip}
DEP=$(curl -fsSL -X POST "$OD_GATEWAY/v1/deployments/" \
  -H "$AUTH" -H "$JSON" \
  -d "$(jq -n --arg pid "$PROJECT_ID" --arg sid "$SERVICE_ID" \
                --arg env "$OD_ENVIRONMENT" --arg src "$SOURCE" \
                --arg tmp "$TEMP_FILE_PATH" --arg branch "${GIT_BRANCH:-main}" \
                --argjson deps "$DEPENDENCY_IDS_JSON" \
     '{project_id:$pid, service_id:$sid, environment:$env,
       source:$src, temp_file_path:$tmp, branch:$branch, dependencies:$deps}')")
DEPLOYMENT_ID=$(echo "$DEP" | jq -r .id)
DEPLOY_T0=$(date +%s)
od_log info deploy.create project_id "$PROJECT_ID" service_id "$SERVICE_ID" \
  deployment_id "$DEPLOYMENT_ID" environment "$OD_ENVIRONMENT" source "$SOURCE" \
  branch "${GIT_BRANCH:-main}" dependencies "$DEPENDENCY_IDS_JSON"
```

`temp_file_path` is stored on the deployment row for dependency-detection hints, but the actual build reads `project.source_path` populated by Step 4.5. Do **not** add a `resources` block here — see Step 6 note.

### Watch until terminal

The `/status` suffix is documented in `Backend/API.md` as an alias but the gateway does **not** register it — calls return 404. Use the resource GET instead:

```bash
while :; do
  S=$(curl -fsSL -H "$AUTH" "$OD_GATEWAY/v1/deployments/$DEPLOYMENT_ID" | jq -r .status)
  case "$S" in success|failed|cancelled|rolled_back) break ;; esac
  sleep 5
done
DEPLOY_DURATION=$(( $(date +%s) - DEPLOY_T0 ))
# Use level=error on failure so triage tooling can `jq 'select(.level=="error")'` cleanly.
case "$S" in
  success)                            LV=info  ;;
  failed|cancelled|rolled_back)       LV=error ;;
  *)                                  LV=warn  ;;
esac
od_log "$LV" deploy.terminal deployment_id "$DEPLOYMENT_ID" status "$S" duration_seconds "$DEPLOY_DURATION"
```

- Build logs (WS, ClickHouse): `GET /deployments/:id/build-logs/stream`
- Deploy logs (SSE): `GET /deployments/:id/logs/stream`
- One-shot: `GET /deployments/:id/logs?tail=N`

On `failed`: dump `logs?tail=300` + last 200 build_log lines; consult [`failure-playbook.md`](failure-playbook.md). **Don't retry silently** — "Task polling timeout" is a frontend 5-min timeout; ClickHouse build_logs is authoritative. If the deployment failed in <2 s at `progress=10` with `error_msg:"Service failed"`, Step 4.5 was skipped or silently errored — re-run it and retry Step 7.

Schema: [`api-schemas.md`](api-schemas.md) → Step 7.

## Step 9 — Final report

Resolve the live URL:

```bash
APP_URL=$(curl -fsSL -H "$AUTH" \
  "$OD_GATEWAY/v1/service-domains?service_id=$SERVICE_ID&environment=$OD_ENVIRONMENT&type=auto" \
  | jq -r '.[0].domain // .[0].url // empty')
[ -n "$APP_URL" ] && case "$APP_URL" in https://*) ;; *) APP_URL="https://$APP_URL" ;; esac
```

The output below is the **canonical post-deploy report**. Print it verbatim with the variable substitutions filled in — same Markdown formatting in both branches so the user gets a stable, predictable layout every time.

**Bolding rules** (apply consistently in both branches):
- `##`/`###` headings — section structure
- `**Field:**` (bold + colon) — every label on the left of a value
- Backticked `code` — every identifier (project name, service name, status, UUIDs)
- `**6 hours**` — bold the time-pressure number
- URLs are **never** bolded — keeps Markdown auto-linking and avoids broken styled links in renderers that don't enter bold spans

Then branch on `$IS_BOUND` (set by `auth.md` from a `/v1/profile` probe):

### Branch A — `IS_BOUND == 0` (local credential needs account binding)

The token is a local deploy credential that has not been linked to a user account yet. The dashboard project page would 401-bounce them to the landing site, so print the account-binding URL instead.

```bash
APP_URL_Q=$(printf '%s' "$APP_URL" | jq -sRr @uri)
SEP="?"; case "$BIND_URL" in *\?*) SEP="&" ;; esac
BIND_URL_WITH_APP="$BIND_URL"
[ -n "$APP_URL_Q" ] && BIND_URL_WITH_APP="${BIND_URL}${SEP}url=${APP_URL_Q}"
od_log info report branch A is_bound 0 deployment_id "$DEPLOYMENT_ID" \
  app_url "$APP_URL" bind_url "$BIND_URL"
```

`$BIND_URL` was derived deterministically in `auth.md` as `${OD_GATEWAY%/api}/guest/$GUEST_ID?h=$BIND_SIG`. Do **not** substitute a server-returned URL here — it has been observed to point at the marketing host `opendeploy.dev` without the dashboard route, which served the landing page instead of the SSO bind flow.

Print exactly (substitute `<OD_LOG_FILE>` with the absolute path in `$OD_LOG_FILE`, e.g. `~/.opendeploy/logs/2026-04-26.log`):

```text
## Deployment successful

**Live URL:** <APP_URL>

### Bind this deployment

Open the link below in your browser and sign in via SSO to bind this
deployment to your opendeploy account. The token in `~/.opendeploy/auth.json`
keeps working afterwards — redeploys from this machine won't prompt again.
The deployment is garbage-collected after **6 hours** if you don't bind it.

**Bind URL:** <BIND_URL_WITH_APP>

---

- **Project:** `<PROJECT_NAME>`
- **Service:** `<SVC_NAME>`
- **Environment:** `<OD_ENVIRONMENT>`
- **Status:** `success`
- **Project ID:** `<PROJECT_ID>`
- **Deployment ID:** `<DEPLOYMENT_ID>`
- **Log file:** `<OD_LOG_FILE>`
```

### Branch B — `IS_BOUND == 1` (dashboard token or account-bound local credential)

`/v1/profile` returned 200, so the token authenticates as a real user. The project belongs to them and the dashboard project page will load. Print the **dashboard project URL**:

```bash
DASHBOARD_HOST="${OD_GATEWAY%/api}"
PROJECT_URL="$DASHBOARD_HOST/projects/$PROJECT_ID"
od_log info report branch B is_bound 1 deployment_id "$DEPLOYMENT_ID" \
  app_url "$APP_URL" project_url "$PROJECT_URL"
```

Print exactly (substitute `<OD_LOG_FILE>` with the absolute path in `$OD_LOG_FILE`):

```text
## Deployment successful

**Live URL:** <APP_URL>
**Dashboard:** <PROJECT_URL>

---

- **Project:** `<PROJECT_NAME>`
- **Service:** `<SVC_NAME>`
- **Environment:** `<OD_ENVIRONMENT>`
- **Status:** `success`
- **Project ID:** `<PROJECT_ID>`
- **Deployment ID:** `<DEPLOYMENT_ID>`
- **Log file:** `<OD_LOG_FILE>`
```

The dashboard host is `OD_GATEWAY` minus the trailing `/api`. The dashboard route `/projects/:id` lives on the same host as the gateway it talks to.

### Cross-branch hygiene

Never echo `BIND_SIG` standalone; it is meaningful only as part of the account-binding URL. Never log `OD_API_KEY`. Do not shorten the account-binding URL through a third-party service — the redemption host must remain the dashboard host derived from `OD_GATEWAY`. Do not insert emoji into the report; the format above is the contract.
