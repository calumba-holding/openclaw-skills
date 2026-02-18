#!/usr/bin/env bash
# SECURITY MANIFEST:
# Environment variables accessed: BW_SERVER, BW_EMAIL, BW_MASTER_PASSWORD, CREDS_FILE (optional)
# External endpoints called: User-configured BW_SERVER (Bitwarden/Vaultwarden API)
# Local files read: $CREDS_FILE (default: secrets/bitwarden.env), /tmp/.bw_session
# Local files written: /tmp/.bw_session (session token cache)

# Bitwarden CLI wrapper for OpenClaw
# Works with both official Bitwarden and Vaultwarden servers
# Usage: bw.sh <command> [args...]
# Commands: login, unlock, lock, list, get, create, edit, delete, generate, sync, status

set -euo pipefail

# Configuration: set via environment or credentials file
# Required env vars: BW_SERVER, BW_EMAIL, BW_MASTER_PASSWORD
CREDS_FILE="${CREDS_FILE:-${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}/secrets/bitwarden.env}"
SESSION_FILE="/tmp/.bw_session"

load_creds() {
  # SECURITY: Safe KEY=VALUE parsing without executing arbitrary shell code
  if [[ -f "$CREDS_FILE" ]]; then
    while IFS='=' read -r key value; do
      # Skip comments and empty lines
      [[ "$key" =~ ^[[:space:]]*# ]] && continue
      [[ -z "$key" ]] && continue
      # Strip quotes and whitespace
      value="${value%\"}"
      value="${value#\"}"
      value="${value%\'}"
      value="${value#\'}"
      key="${key//[[:space:]]/}"
      # Export only expected variables
      case "$key" in
        BW_SERVER|BW_EMAIL|BW_MASTER_PASSWORD)
          export "$key=$value"
          ;;
      esac
    done < "$CREDS_FILE"
  fi
  
  if [[ -z "${BW_SERVER:-}" ]]; then
    echo "ERROR: BW_SERVER not set. Configure via environment or credentials file." >&2
    exit 1
  fi
  if [[ -z "${BW_EMAIL:-}" ]]; then
    echo "ERROR: BW_EMAIL not set. Configure via environment or credentials file." >&2
    exit 1
  fi
  if [[ -z "${BW_MASTER_PASSWORD:-}" ]]; then
    echo "ERROR: BW_MASTER_PASSWORD not set. Configure via environment or credentials file." >&2
    exit 1
  fi
}

get_session() {
  if [[ -f "$SESSION_FILE" ]]; then
    cat "$SESSION_FILE"
  elif [[ -n "${BW_SESSION:-}" ]]; then
    echo "$BW_SESSION"
  fi
}

ensure_session() {
  local session
  session=$(get_session)
  if [[ -z "$session" ]]; then
    do_login
    session=$(get_session)
  fi
  if [[ -z "$session" ]]; then
    echo "ERROR: No active session. Run: bw.sh login" >&2
    exit 1
  fi
  export BW_SESSION="$session"
}

do_login() {
  load_creds

  # Configure server
  bw config server "$BW_SERVER" >/dev/null 2>&1 || true

  local status
  status=$(bw status 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unauthenticated'))" 2>/dev/null || echo "unauthenticated")

  if [[ "$status" == "unauthenticated" ]]; then
    local session
    session=$(bw login "$BW_EMAIL" "$BW_MASTER_PASSWORD" --raw 2>/dev/null)
    echo "$session" > "$SESSION_FILE"
    chmod 600 "$SESSION_FILE"
    echo "Logged in successfully."
  elif [[ "$status" == "locked" ]]; then
    local session
    session=$(bw unlock "$BW_MASTER_PASSWORD" --raw 2>/dev/null)
    echo "$session" > "$SESSION_FILE"
    chmod 600 "$SESSION_FILE"
    echo "Vault unlocked."
  else
    echo "Already logged in and unlocked."
  fi
}

cmd="${1:-help}"
shift || true

case "$cmd" in
  login)
    do_login
    ;;
  status)
    bw status 2>/dev/null
    ;;
  sync)
    ensure_session
    bw sync
    ;;
  list)
    ensure_session
    if [[ $# -gt 0 ]]; then
      bw list items --search "$*"
    else
      bw list items
    fi
    ;;
  get)
    ensure_session
    bw get item "$1"
    ;;
  get-password)
    ensure_session
    bw get password "$1"
    ;;
  get-username)
    ensure_session
    bw get username "$1"
    ;;
  get-notes)
    ensure_session
    bw get notes "$1"
    ;;
  create)
    ensure_session
    local_name="${1:?name required}"
    local_user="${2:?username required}"
    local_pass="${3:?password required}"
    local_uri="${4:-}"
    local_notes="${5:-}"

    uris_json="[]"
    if [[ -n "$local_uri" ]]; then
      uris_json="[{\"uri\":\"$local_uri\"}]"
    fi

    template="{\"type\":1,\"name\":\"$local_name\",\"login\":{\"username\":\"$local_user\",\"password\":\"$local_pass\",\"uris\":$uris_json},\"notes\":\"$local_notes\"}"
    echo "$template" | bw encode | bw create item
    ;;
  create-json)
    ensure_session
    if [[ $# -gt 0 ]]; then
      echo "$1" | bw encode | bw create item
    else
      bw encode | bw create item
    fi
    ;;
  edit)
    ensure_session
    echo "$2" | bw encode | bw edit item "$1"
    ;;
  delete)
    ensure_session
    bw delete item "$1"
    ;;
  generate)
    local_len="${1:-24}"
    bw generate --length "$local_len" --uppercase --lowercase --number --special
    ;;
  lock)
    bw lock
    rm -f "$SESSION_FILE"
    ;;
  logout)
    bw logout
    rm -f "$SESSION_FILE"
    ;;
  help|*)
    cat <<EOF
Bitwarden CLI Wrapper (works with Bitwarden and Vaultwarden)

Usage: bw.sh <command> [args...]

Commands:
  login                          Login/unlock vault
  status                         Show vault status
  sync                           Sync vault
  list [search]                  List items (optional search filter)
  get <name|id>                  Get full item
  get-password <name|id>         Get just the password
  get-username <name|id>         Get just the username
  get-notes <name|id>            Get just the notes
  create <name> <user> <pass> [uri] [notes]  Create login item
  create-json <json>             Create item from JSON
  edit <id> <json>               Edit item
  delete <id>                    Delete item
  generate [length]              Generate secure password
  lock                           Lock vault
  logout                         Logout
EOF
    ;;
esac
