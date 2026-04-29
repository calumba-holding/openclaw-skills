# Auth - write `~/.opendeploy/auth.json`, initialize local deploy credential if needed

Single source of truth for the gateway URL is the SKILL.md frontmatter `metadata.api_base`. The shell here mirrors it; if you change one, change both.

## Auth file shape: `~/.opendeploy/auth.json`

The auth file lives in the **user's home directory**, not the project's. It is a long-lived credential that stays with the user across every project they deploy from this machine. Per-deploy working state (project_id, service_id, deployment_id, source.zip, analysis.json) still lives in `<PWD>/.opendeploy/` because it is deploy-scoped — but the credential is not.

A stray `<PWD>/.opendeploy/auth.json` from a previous skill version is migrated into `~/.opendeploy/auth.json` automatically on first run; see the resolve flow below.

```json
{
  "version": 1,
  "api_key": "od_axxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "gateway": "https://dashboard.dev.opendeploy.dev/api",
  "guest_id": "8f3e2b14-ad7c-4f0c-9b1d-aaaaaaaaaaaa",
  "bind_sig": "0123456789abcdef",
  "env_consent": {
    "<project_id>": {
      "keys_hash": "<sha256 of sorted env keyset>",
      "approved_at": "2026-04-28T12:00:00Z"
    }
  }
}
```

- `version` (int, currently `1`) — schema marker. Unrecognized → abort with a clear message; do not auto-rewrite.
- `api_key` (string, required) — the user's `od_*` token. Treat as a secret. Same field for dashboard tokens and local deploy credentials — kind byte at position 3 tells the gateway which table to look up.
- `gateway` (string, optional) — overrides the default API base URL.
- `guest_id` (string, optional) — present only for local deploy credentials; the skill uses it to construct the account-binding URL on first deploy. Older files with `agent_id` are tolerated and migrated in memory.
- `bind_sig` (string, optional) — HMAC seal the dashboard verifies on bind. Present only for local deploy credentials.
- `env_consent` (object, optional) — per-project record of the user's `.env` upload approvals. Keyed by `project_id`. Each entry is `{keys_hash: <sha256 of the sorted keyset>, approved_at: <UTC ISO 8601>}`. Written by `setup.md` Step 3.3 and `deploy.md` Step 5 only after the user picks "Approve and upload" in the consent prompt. The cache key is `(project_id, keys_hash)` — adding a new env key invalidates the cached consent and re-prompts. No env values are ever stored here, only the keyset hash.

The account-binding URL is **never persisted**. It is always derived at use-time from `${gateway%/api}/guest/<guest_id>?h=<bind_sig>` — the dashboard route lives on the same host as the gateway, period. The server's URL field (when returned from `/v1/client-guests/register`) is **ignored** because mis-set gateway config has historically returned URLs pointing at the wrong host.

File permissions MUST be `0600` (owner read/write only). The skill sets this when it writes the file. If pre-existing perms are looser, the skill warns and tightens — never deletes.

## Operation log

The skill writes a JSONL audit trail to `~/.opendeploy/logs/<UTC-date>.log` (one file per UTC day, appended). Every other reference (`setup.md`, `deploy.md`, `domain.md`, `operate.md`) sources the logger and emits one line per operation boundary. The auth block below installs the logger as `~/.opendeploy/lib/log.sh` once (idempotent, mode 0600) so subsequent steps and subsequent sessions can `. "$HOME/.opendeploy/lib/log.sh"` without re-running auth.

**File layout** under `$HOME/.opendeploy/`:

```
auth.json             # 0600 — credential (see schema above)
lib/log.sh            # 0600 — logger function, written by auth.md
logs/2026-04-26.log   # 0600 — JSONL operation log, daily roll
```

**Log line schema** — one JSON object per line:

```json
{"ts":"2026-04-26T22:50:01Z","level":"info","step":"deploy.create","status":"ok","project_id":"7f3e…","deployment_id":"9a4f…"}
```

`ts` (UTC ISO 8601), `level` (`info` / `warn` / `error`), `step` (dot-separated, e.g. `auth.resolve`, `setup.project_create`, `deploy.upload_only`, `deploy.terminal`, `domain.bind`, `report`), then arbitrary key-value context.

**Secret guard.** The logger silently drops any key matching `api_key`, `bind_sig`, `password`, `token`, `*secret*`, `*Authorization*`. Even if a step accidentally passes one, it is never written to disk. Don't relax this filter.

**Retention.** Not auto-rotated. To prune, run `find ~/.opendeploy/logs -mtime +30 -delete` — the skill never deletes logs on its own.

## Resolve / credential initialization flow

### Consent gate - required before credential initialization, skipped on reuse

Before running the bash block, **peek at the auth file**. If `~/.opendeploy/auth.json` already exists and has a non-empty `api_key`, skip this gate entirely — the resolve path below reuses it without any user prompt. Same `OPDEPLOY_AUTH_FILE` override applies.

If the file is missing or empty, you MUST surface a one-time consent prompt before the bash block runs `POST /v1/client-guests/register`. The block writes a long-lived credential to disk; that needs explicit user approval, not just an automatic call.

Use `AskUserQuestion`:

> Question: `"opendeploy needs a credential to deploy. Create one now?"`
>
> Body (verbatim, so the user knows what they're approving):
> > opendeploy will call `POST https://dashboard.dev.opendeploy.dev/api/v1/client-guests/register` (anonymous, IP rate-limited) and save the returned token to `~/.opendeploy/auth.json` with mode `0600`. The token deploys under guest-tenant resource caps until you sign in via the binding URL printed after deploy. After binding, the same token continues to work with account-level deploy authority.
>
> Options:
> - `Yes, create a guest credential` — proceed.
> - `I'll paste my own dashboard token` — abort credential initialization, tell the user to create a token at the dashboard's API-keys page and write `{"version":1,"api_key":"od_k...","gateway":"https://dashboard.dev.opendeploy.dev/api"}` to `~/.opendeploy/auth.json` (mode 0600), then re-run the deploy.
> - `Cancel` — exit the skill, leave no files behind.

Branch on the answer:

| User picked | Action |
|---|---|
| `Yes, create a guest credential` | Export the internal handoff signal `OPDEPLOY_CONSENT_GRANTED=1` in the same Bash invocation as the block below, then run it. This variable exists solely to carry the AskUserQuestion answer into the bash block — it is **not** a public env var, is **not** documented in the skill's `optional_env_vars`, and must **never** be set ambient in the shell, in CI config, or in `.envrc`. Any value other than `1` set inside the same Bash invocation that just answered the prompt is treated as missing. |
| `I'll paste my own dashboard token` | Print the paste-your-own instructions, then `exit 0`. Do **not** run the bash block. |
| `Cancel` | Print "deploy cancelled.", `exit 0`. Do **not** run the bash block, do **not** create any files. |

Non-interactive contexts (CI, headless runners, agents without an `AskUserQuestion` channel) **cannot** use the guest-registration path. There is no env-var bypass. The supported pattern is: have a human create a dashboard token (`od_k*`) at the dashboard's API-keys page once, then pre-provision `~/.opendeploy/auth.json` (mode `0600`) with `{"version":1,"api_key":"od_k...","gateway":"https://dashboard.dev.opendeploy.dev/api"}` before the CI job runs. The skill's resolve path will reuse it without prompting.

### Bash block

```bash
OD_GATEWAY="${OD_GATEWAY:-https://dashboard.dev.opendeploy.dev/api}"
AUTH_FILE="${OPDEPLOY_AUTH_FILE:-$HOME/.opendeploy/auth.json}"
mkdir -p "$(dirname "$AUTH_FILE")" && chmod 700 "$(dirname "$AUTH_FILE")"

# Install the operation logger. `od_log` is a JSONL writer with a built-in
# secret guard. Idempotent — overwriting log.sh on every run is fine because
# the function body is deterministic and small. Prefer the bundled
# scripts/log.sh so scanners and users can audit the exact logger code.
# Fall back to the embedded copy only when the skill was read from a URL and
# no local scripts/log.sh exists.
OD_LIB_DIR="$HOME/.opendeploy/lib"
OD_LOG_DIR="$HOME/.opendeploy/logs"
mkdir -p "$OD_LIB_DIR" "$OD_LOG_DIR"
chmod 700 "$OD_LIB_DIR" "$OD_LOG_DIR"

LOGGER_SRC=""
for candidate in \
  "${OPDEPLOY_SKILL_DIR:-}/scripts/log.sh" \
  "$HOME/.claude/skills/opendeploy/scripts/log.sh" \
  "$HOME/.codex/skills/opendeploy/scripts/log.sh" \
  "$HOME/.cursor/skills/opendeploy/scripts/log.sh" \
  "$HOME/.config/opencode/skills/opendeploy/scripts/log.sh" \
  "$HOME/.factory/skills/opendeploy/scripts/log.sh"; do
  [ -n "$candidate" ] && [ -f "$candidate" ] && { LOGGER_SRC="$candidate"; break; }
done

if [ -n "$LOGGER_SRC" ]; then
  cp "$LOGGER_SRC" "$OD_LIB_DIR/log.sh"
else
  cat > "$OD_LIB_DIR/log.sh" <<'EOF'
# Operation logger for the opendeploy skill — sourced by every reference's
# first bash block. JSONL, daily-rolled, secret-redacted. Failures swallowed
# so logging never aborts a deploy.

OD_LOG_DIR="${OD_LOG_DIR:-$HOME/.opendeploy/logs}"
OD_LOG_FILE="$OD_LOG_DIR/$(date -u +%Y-%m-%d).log"
[ -d "$OD_LOG_DIR" ] || { mkdir -p "$OD_LOG_DIR" && chmod 700 "$OD_LOG_DIR"; }
[ -e "$OD_LOG_FILE" ] || { : > "$OD_LOG_FILE" 2>/dev/null && chmod 600 "$OD_LOG_FILE"; }

# Usage: od_log <level> <step> [key value]...
#   level: info | warn | error
#   step:  dot-separated identifier, e.g. deploy.upload_only
# Sensitive keys (api_key, bind_sig, password, token, *secret*, *Authorization*)
# are dropped before serialisation — accidental leaks are physically impossible.
od_log() {
  local level=${1:-info} step=${2:-unknown}; shift 2 2>/dev/null || true
  local ts; ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  local args=(--arg ts "$ts" --arg lv "$level" --arg st "$step")
  local merge='{ts:$ts, level:$lv, step:$st}'
  local i=0
  while [ $# -ge 2 ]; do
    case "$1" in
      api_key|bind_sig|password|token|*secret*|*Authorization*|authorization)
        shift 2; continue ;;
    esac
    args+=(--arg "k$i" "$1" --arg "v$i" "$2")
    merge="$merge + {(\$k$i): \$v$i}"
    i=$((i+1))
    shift 2
  done
  jq -nc "${args[@]}" "$merge" >> "$OD_LOG_FILE" 2>/dev/null || true
}
EOF
fi
chmod 600 "$OD_LIB_DIR/log.sh"
. "$OD_LIB_DIR/log.sh"

od_log info skill.start pwd "$PWD" host "$(uname -s)/$(uname -m)" pid "$$"

# Backwards compat: prior skill versions wrote the auth into the project
# directory ($PWD/.opendeploy/auth.json), which leaks an orphan agent every
# time you deploy from a new folder. If we find one and the new home location
# is empty, migrate it. If $OPDEPLOY_AUTH_FILE was set explicitly, skip — the
# user picked their own path on purpose.
LEGACY_AUTH="$PWD/.opendeploy/auth.json"
if [ -z "$OPDEPLOY_AUTH_FILE" ] \
    && [ ! -f "$AUTH_FILE" ] && [ -f "$LEGACY_AUTH" ]; then
  mv "$LEGACY_AUTH" "$AUTH_FILE"
  chmod 600 "$AUTH_FILE"
  echo "opendeploy: migrated auth $LEGACY_AUTH -> $AUTH_FILE"
  # Only remove the legacy dir if it was emptied by the migration. If there
  # are other per-deploy state files (project_id.txt, source.zip, etc.) the
  # rmdir fails silently — that's the right behavior, leave them alone.
  rmdir "$PWD/.opendeploy" 2>/dev/null || true
fi

OD_API_KEY=""
GUEST_ID=""
BIND_SIG=""
IS_BOUND=0

if [ -f "$AUTH_FILE" ] && [ -s "$AUTH_FILE" ]; then
  PERM=$(stat -f '%Lp' "$AUTH_FILE" 2>/dev/null || stat -c '%a' "$AUTH_FILE" 2>/dev/null)
  case "$PERM" in 600|400) ;; *) chmod 600 "$AUTH_FILE" ;; esac

  OD_API_KEY=$(jq -r '.api_key // empty' "$AUTH_FILE")
  GUEST_ID=$(jq -r '.guest_id // .agent_id // empty' "$AUTH_FILE")
  BIND_SIG=$(jq -r '.bind_sig // empty' "$AUTH_FILE")
  GATEWAY_FROM_FILE=$(jq -r '.gateway // empty' "$AUTH_FILE")
  [ -n "$GATEWAY_FROM_FILE" ] && OD_GATEWAY="$GATEWAY_FROM_FILE"
fi

AUTH_MODE=reuse
if [ -z "$OD_API_KEY" ]; then
  AUTH_MODE=init
  # Belt-and-suspenders: the AskUserQuestion consent gate above is the primary
  # control. This in-process handoff catches the case where an agent ran the
  # bash block without surfacing the prompt first. The variable is internal —
  # not advertised in the skill's optional_env_vars — and the agent sets it in
  # the same Bash invocation as a result of the AskUserQuestion answer.
  # CI / non-interactive runners cannot satisfy this check; they must
  # pre-provision an existing dashboard token in $AUTH_FILE before the job
  # runs.
  if [ "${OPDEPLOY_CONSENT_GRANTED:-}" != "1" ]; then
    od_log error auth.register reason consent_missing
    echo "opendeploy: refused to create a credential without explicit user consent." >&2
    echo "Surface the AskUserQuestion gate from auth.md ('Resolve / credential initialization flow')" >&2
    echo "and only run this bash block after the user picks 'Yes, create a guest credential'." >&2
    echo "For CI / non-interactive use, pre-provision $AUTH_FILE with a dashboard token instead." >&2
    exit 1
  fi

  # Privacy-preserving default label. Do not send the local hostname unless the
  # user explicitly chooses to include one in a future named-credential flow.
  AGENT_NAME_DEFAULT="opendeploy local deploy"
  REGISTER_BODY=$(jq -nc \
    --arg sh   "claude-code/$(uname -s)" \
    --arg name "$AGENT_NAME_DEFAULT" \
    '{source_hint:$sh, name:$name}')
  RESP=$(curl -fsSL -X POST "$OD_GATEWAY/v1/client-guests/register" \
    -H "Content-Type: application/json" \
    -d "$REGISTER_BODY")
  OD_API_KEY=$(echo "$RESP" | jq -r '.api_key // empty')
  GUEST_ID=$(echo "$RESP"  | jq -r '.guest_id // .agent_id // empty')
  BIND_SIG=$(echo "$RESP"  | jq -r '.bind_sig // empty')
  GW=$(echo "$RESP"        | jq -r '.gateway // empty')
  [ -n "$GW" ] && OD_GATEWAY="$GW"
  # Server's account-binding URL field is intentionally discarded — see auth-file
  # schema notes above. We always derive locally from OD_GATEWAY + guest_id +
  # bind_sig so a mis-set URL base on the gateway can't surface a
  # marketing-host URL that 404s into the landing page.

  if [ -z "$OD_API_KEY" ]; then
    od_log error auth.register reason api_key_missing http_status replay_or_lost
    echo "opendeploy returned an existing local deploy credential but did not return api_key." >&2
    echo "The plaintext key is only shown once. Restore the previous $AUTH_FILE or wait 24h and retry." >&2
    exit 1
  fi
  if [ -z "$GUEST_ID" ] || [ -z "$BIND_SIG" ]; then
    od_log error auth.register reason missing_guest_or_bindsig
    echo "opendeploy credential registration response was missing guest_id or bind_sig." >&2
    exit 1
  fi

  umask 0077
  jq -n --arg k "$OD_API_KEY" --arg gw "$OD_GATEWAY" \
        --arg gid "$GUEST_ID" --arg sig "$BIND_SIG" \
    '{version:1, api_key:$k, gateway:$gw, guest_id:$gid, bind_sig:$sig}' > "$AUTH_FILE"
  chmod 600 "$AUTH_FILE"
fi

# Always derive the account-binding URL deterministically from the gateway host.
# The dashboard's /guest/:guest_id route lives on the same host as the gateway
# it talks to (OD_GATEWAY minus /api). Never read the server URL field from the
# response or the auth file.
BIND_URL=""
if [ -n "$GUEST_ID" ] && [ -n "$BIND_SIG" ]; then
  BIND_URL="${OD_GATEWAY%/api}/guest/$GUEST_ID?h=$BIND_SIG"
fi

AUTH="Authorization: Bearer ${OD_API_KEY}"
JSON="Content-Type: application/json"

# Sanity check + region discovery. Use /regions/, not /profile: local deploy
# credentials that are not linked to an account are guest tenants and are not
# OIDC users, so /profile is expected to 401 for them.
# Do NOT auto-delete auth.json — the user may be using a key bound to a
# different environment. Tell the user, exit, let them decide.
REGIONS_JSON=$(curl -fsSL -H "$AUTH" "$OD_GATEWAY/v1/regions/" 2>/dev/null) || {
  echo "opendeploy rejected the saved API key in $AUTH_FILE." >&2
  echo "If you intended to start fresh, delete $AUTH_FILE and re-run; otherwise" >&2
  echo "replace the api_key with a valid one from your dashboard." >&2
  exit 1
}

# Auto-pick first active region if unset.
: "${OD_REGION_ID:=$(printf '%s' "$REGIONS_JSON" | jq -r '[.[] | select(.status=="active")][0].id // empty')}"
[ -n "$OD_REGION_ID" ] || { echo "no active region"; exit 1; }

# Account-state probe. /v1/profile returns 200 for dashboard tokens and
# account-bound local credentials, 401 for local credentials that have not been
# linked to an account. This is the canonical signal for the deploy-final
# branch in deploy.md Step 9.
if curl -fsS -o /dev/null -H "$AUTH" "$OD_GATEWAY/v1/profile" 2>/dev/null; then
  IS_BOUND=1
fi

od_log info auth.resolve mode "$AUTH_MODE" is_bound "$IS_BOUND" \
  guest_id "${GUEST_ID:-none}" gateway "$OD_GATEWAY" region_id "$OD_REGION_ID"

# Default deploy environment. `production` lands the workload on
# `*.opendeploy.run` and is the skill default ("push to live").
# Set `OD_ENVIRONMENT=staging` to keep the old preview-style flow on
# `*.dev.opendeploy.run`. Anything else aborts here so we don't pass an
# unsupported value to deployment-service (which only handles
# `staging` / `production`).
OD_ENVIRONMENT="${OD_ENVIRONMENT:-production}"
case "$OD_ENVIRONMENT" in
  staging|production) ;;
  *) echo "OD_ENVIRONMENT must be 'staging' or 'production' (got '$OD_ENVIRONMENT')" >&2; exit 1 ;;
esac
```

After this block:
- `$AUTH` is the Bearer header (every downstream curl uses `-H "$AUTH"`).
- `$OD_GATEWAY` is the gateway base (includes `/api`).
- `$OD_REGION_ID` is set.
- `$OD_ENVIRONMENT` is `production` (default) or `staging` — every downstream step that takes an `environment` field reads from this var.
- `$GUEST_ID` / `$BIND_SIG` are set when the token is a local deploy credential (`od_a*`); empty for dashboard tokens.
- `$BIND_URL` is set deterministically when local credential metadata is available; empty for dashboard tokens.
- `$IS_BOUND` is `1` for dashboard tokens and account-bound local credentials (i.e. `/v1/profile` returned 200), `0` for local credentials not yet linked to an account.
- `$OD_LOG_FILE` points at `~/.opendeploy/logs/<UTC-date>.log`. The `od_log` shell function is in scope; subsequent references re-source `~/.opendeploy/lib/log.sh` at the top of their first bash block to pick it up across separate tool calls.

The deploy-final report (see `deploy.md` Step 9) branches on `$IS_BOUND`:
- `0` -> print the account-binding URL so the user can sign in and attach the deployment to their account. Covers first-time credentials and subsequent runs where the auth file persisted but has not been linked yet.
- `1` -> print the project's dashboard URL instead. Dashboard tokens and account-bound local credentials already authenticate as a real user, so the project page (logs, env vars, resize, etc.) is the right destination.

## Rate limit on register

`POST /v1/client-guests/register` is rate-limited at 5 / hour / source IP. On 429 the response carries `Retry-After`. Don't retry inside the skill — tell the user.

The same (source IP, user-agent) calling within 24h gets the same pending row back (idempotent replay). On replay the response omits the `api_key` field — if you don't already have the plaintext from a prior call, you must surface a friendly error rather than try again.

## Time skew

Sync NTP. The agent register / bind handlers accept up to 5 minutes of clock skew on the server side; far drift will cause unrelated TLS issues before it cares about timestamps.
