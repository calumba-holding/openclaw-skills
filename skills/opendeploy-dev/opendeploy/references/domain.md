# Domain — bind / rename auto-subdomain (`*.opendeploy.run` for production, `*.dev.opendeploy.run` for staging)

Pre-conditions: `auth.md` ran and you have `$SERVICE_ID` and `$OD_ENVIRONMENT`. Allowed for both local credentials not yet linked to an account and account-bound credentials. Server enforces uniqueness across the namespace. Custom production domains (CNAME on a user-owned hostname) are out of scope for this skill — those need an account-bound user and live in the dashboard.

Source the operation logger at the top of the first bash block in this chain:

```bash
[ -f "$HOME/.opendeploy/lib/log.sh" ] && . "$HOME/.opendeploy/lib/log.sh"
```

> Both `staging` and `production` auto-domains support subdomain rename via `PUT /service-domains/:id/subdomain`. (The previous production-only gate in `project-service/internal/handlers/service_domain.go` was removed alongside the `OD_ENVIRONMENT` switch.)

## Step 8 — Subdomain → `PUT /service-domains/:id/subdomain`

```bash
# 8.1 check availability
curl -fsSL -H "$AUTH" "$OD_GATEWAY/v1/service-domains/check-subdomain/$SUBDOMAIN" | jq .

# 8.2 find the auto domain row for the active environment (poll up to 30s after the deploy succeeds)
AUTO_ID=$(curl -fsSL -H "$AUTH" \
  "$OD_GATEWAY/v1/service-domains?service_id=$SERVICE_ID&environment=$OD_ENVIRONMENT&type=auto" \
  | jq -r '.[0].id')

# 8.3 rename
curl -fsSL -X PUT "$OD_GATEWAY/v1/service-domains/$AUTO_ID/subdomain" \
  -H "$AUTH" -H "$JSON" \
  -d "$(jq -n --arg s "$SUBDOMAIN" '{subdomain:$s}')"
od_log info domain.rename service_id "$SERVICE_ID" auto_id "$AUTO_ID" \
  subdomain "$SUBDOMAIN" environment "$OD_ENVIRONMENT"
```

On 409 → append a 4-char suffix and retry 8.1 once. Verify (production lands on `*.opendeploy.run`, staging on `*.dev.opendeploy.run`):

```bash
BASE_DOMAIN=$([ "$OD_ENVIRONMENT" = "production" ] && echo "opendeploy.run" || echo "dev.opendeploy.run")
curl -fsSL -o /dev/null -w "%{http_code}\n" "https://$SUBDOMAIN.$BASE_DOMAIN${HEALTH_PATH:-/}"
```

Schema: [`api-schemas.md`](api-schemas.md) → Step 8. Subdomain reserved list and edge cases in there too.

## Rename an existing subdomain (no redeploy)

Same three calls (8.1 → 8.2 → 8.3) against the existing `ServiceDomain` row. The K8s ingress rolls without a deployment.

## Why this is allowed for guest credentials

Subdomain rename touches only the `service_domains` row + ingress. It does not change billing or the guest resource envelope, so the gateway lets local credentials update auto subdomains. Custom production domains (`type=custom`) are gated and return `403 bind_required` — direct the user to the account-binding URL printed by `deploy.md`.
