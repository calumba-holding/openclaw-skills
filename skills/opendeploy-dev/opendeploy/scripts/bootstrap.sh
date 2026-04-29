#!/usr/bin/env bash
# opendeploy skill bootstrap — per-agent prompted installer.
#
# What this script does (read before running):
#   1. Probes a fixed list of known AI-agent config directories under $HOME
#      (no scanning, no fs traversal — only the paths in AGENT_BASES below).
#   2. For each one that EXISTS, asks the user y/N before installing into
#      that specific agent. The default for every prompt is N — you must
#      explicitly type 'y' for each agent you want installed. No "install
#      to all" shortcut.
#   3. For each approved agent, downloads ~12 files (SKILL.md, skill.json,
#      references/*.md, scripts/log.sh) from $BASE and writes them under
#      <agent>/skills/opendeploy/ + <agent>/skills/<alias>/. No files are
#      placed outside of <agent>/skills/. Existing files are overwritten.
#
# It does NOT: execute downloaded files, modify shell rc files, install system
# packages, write outside $HOME, contact any host other than $BASE, or install
# into agents the user did not explicitly approve.
#
# Usage:
#   # Inspect first (recommended):
#   curl -fsSL https://opendeploy.dev/skills/scripts/bootstrap.sh | less
#
#   # Then install (must be a TTY — per-agent prompts cannot be answered
#   # over a curl|bash pipe):
#   bash <(curl -fsSL https://opendeploy.dev/skills/scripts/bootstrap.sh)
#
# Consent / scope controls:
#   OPDEPLOY_AGENTS="claude,codex"   Comma-separated allowlist. Only the
#                                    named agents will be considered for
#                                    install (others are skipped without a
#                                    prompt). The y/N prompt still fires for
#                                    each one in the list. Default: every
#                                    detected agent. Names: claude, codex,
#                                    opencode, cursor, factory, slate, kiro,
#                                    hermes, gbrain.
#   OPDEPLOY_YES=1                   Skip every per-agent confirmation prompt
#                                    and install into all agents that pass
#                                    the OPDEPLOY_AGENTS allowlist. Required
#                                    when stdin is not a TTY (e.g. curl|bash).
#                                    Combine with OPDEPLOY_AGENTS to scope.
#                                    Set this only after reviewing the script.
#   OPDEPLOY_SKILL_BASE=https://...  Override source URL (testing/mirrors).
#                                    Default: https://opendeploy.dev/skills
#
# Agent → skill directory mapping:
#   Claude Code           ~/.claude/skills/opendeploy/
#   OpenAI Codex CLI      ~/.codex/skills/opendeploy/
#   OpenCode              ~/.config/opencode/skills/opendeploy/
#   Cursor                ~/.cursor/skills/opendeploy/
#   Factory Droid         ~/.factory/skills/opendeploy/
#   Slate                 ~/.slate/skills/opendeploy/
#   Kiro                  ~/.kiro/skills/opendeploy/
#   Hermes                ~/.hermes/skills/opendeploy/
#   GBrain                ~/.gbrain/skills/opendeploy/
#   OpenClaw              (inherits Claude — spawns Claude Code sessions)

set -u

BASE="${OPDEPLOY_SKILL_BASE:-https://opendeploy.dev/skills}"

FILES=(
  SKILL.md
  skill.json
  references/auth.md
  references/setup.md
  references/deploy.md
  references/domain.md
  references/operate.md
  references/api-schemas.md
  references/analyze-local.md
  references/failure-playbook.md
  scripts/log.sh
)

# Slash-command aliases — installed as sibling skills so users can type `/deploy`
# instead of having to remember "opendeploy". Each alias is a single SKILL.md
# that delegates to ../opendeploy/SKILL.md at runtime.
ALIAS_NAMES=(deploy)

# Name -> base path. Order is preserved by iterating AGENT_ORDER below.
AGENT_ORDER=(claude codex opencode cursor factory slate kiro hermes gbrain)
agent_base_for() {
  case "$1" in
    claude)   echo "$HOME/.claude" ;;
    codex)    echo "$HOME/.codex" ;;
    opencode) echo "$HOME/.config/opencode" ;;
    cursor)   echo "$HOME/.cursor" ;;
    factory)  echo "$HOME/.factory" ;;
    slate)    echo "$HOME/.slate" ;;
    kiro)     echo "$HOME/.kiro" ;;
    hermes)   echo "$HOME/.hermes" ;;
    gbrain)   echo "$HOME/.gbrain" ;;
    *)        echo "" ;;
  esac
}

# Resolve the active agent set: allowlist (if OPDEPLOY_AGENTS is set) intersected
# with "directory exists on disk".
declare -a TARGETS=()
declare -a SKIPPED_MISSING=()
declare -a SKIPPED_FILTERED=()

if [ -n "${OPDEPLOY_AGENTS:-}" ]; then
  IFS=',' read -r -a ALLOW <<< "$OPDEPLOY_AGENTS"
else
  ALLOW=("${AGENT_ORDER[@]}")
fi

allowed() {
  local needle="$1" a
  for a in "${ALLOW[@]}"; do
    [ "$(echo "$a" | tr -d ' ')" = "$needle" ] && return 0
  done
  return 1
}

for name in "${AGENT_ORDER[@]}"; do
  base="$(agent_base_for "$name")"
  if ! allowed "$name"; then
    SKIPPED_FILTERED+=("$name")
    continue
  fi
  if [ ! -d "$base" ]; then
    SKIPPED_MISSING+=("$name")
    continue
  fi
  TARGETS+=("$name|$base")
done

if [ "${#TARGETS[@]}" -eq 0 ]; then
  echo "opendeploy: no agent directories matched (allowlist=${OPDEPLOY_AGENTS:-<all>})"
  echo "opendeploy: nothing to do"
  exit 0
fi

# Print the plan, then ask the user per-agent whether to install. Default for
# every prompt is N — explicit y per agent. With curl|bash, stdin is the
# script (not a TTY), so per-agent prompts can't be answered; in that case we
# require OPDEPLOY_YES=1 to take the "install into every detected agent that
# passed the allowlist" path.
echo "opendeploy bootstrap"
echo "  source:    $BASE"
echo "  files:     ${#FILES[@]} canonical + ${#ALIAS_NAMES[@]} alias(es) per agent"
echo "  detected:"
for t in "${TARGETS[@]}"; do
  name="${t%%|*}"; base="${t#*|}"
  echo "    - $name  -> $base/skills/opendeploy/  (and $base/skills/${ALIAS_NAMES[*]}/)"
done
if [ "${#SKIPPED_MISSING[@]}" -gt 0 ]; then
  echo "  skip (no dir): ${SKIPPED_MISSING[*]}"
fi
if [ "${#SKIPPED_FILTERED[@]}" -gt 0 ]; then
  echo "  skip (filtered out by OPDEPLOY_AGENTS): ${SKIPPED_FILTERED[*]}"
fi
echo ""

declare -a APPROVED=()

if [ "${OPDEPLOY_YES:-}" = "1" ]; then
  # Non-interactive opt-in: install into every agent that passed the
  # allowlist filter. Equivalent to answering y to every per-agent prompt.
  echo "opendeploy: OPDEPLOY_YES=1 — installing into all detected agents above"
  APPROVED=("${TARGETS[@]}")
elif [ -t 0 ]; then
  # Interactive: prompt per agent. Default N. The user must explicitly type
  # y for each agent they want installed. No "all" shortcut — the whole
  # point of this loop is that approving Claude doesn't sneak files into
  # Codex / Cursor / etc.
  echo "Per-agent confirmation (default is N, type y to install):"
  for t in "${TARGETS[@]}"; do
    name="${t%%|*}"; agent_base="${t#*|}"
    printf "  Install into %s (%s/skills/opendeploy/) ? [y/N] " "$name" "$agent_base"
    read -r REPLY
    case "$REPLY" in
      y|Y|yes|YES) APPROVED+=("$t") ;;
      *) echo "    skipped: $name" ;;
    esac
  done
  if [ "${#APPROVED[@]}" -eq 0 ]; then
    echo "opendeploy: nothing approved, exiting"
    exit 0
  fi
else
  # Non-TTY without OPDEPLOY_YES — we have no way to ask the user per agent.
  # Refuse rather than silently installing into directories the user did not
  # see prompted.
  echo "opendeploy: stdin is not a TTY (you are likely running 'curl ... | bash')."
  echo "            Per-agent confirmation prompts can't run without a TTY."
  echo ""
  echo "            Re-run interactively after reviewing the script:"
  echo ""
  echo "              bash <(curl -fsSL $BASE/scripts/bootstrap.sh)"
  echo ""
  echo "            Or, if you want to install into every detected agent in"
  echo "            one shot, opt in explicitly with OPDEPLOY_YES=1 and scope"
  echo "            with OPDEPLOY_AGENTS:"
  echo ""
  echo "              curl -fsSL $BASE/scripts/bootstrap.sh | OPDEPLOY_AGENTS=claude OPDEPLOY_YES=1 bash"
  echo ""
  exit 1
fi

installed=0

for t in "${APPROVED[@]}"; do
  name="${t%%|*}"
  agent_base="${t#*|}"
  dest="$agent_base/skills/opendeploy"
  mkdir -p "$dest/references" "$dest/scripts"
  for f in "${FILES[@]}"; do
    curl -fsSL "$BASE/$f" -o "$dest/$f" 2>/dev/null || true
  done
  echo "opendeploy: installed -> $dest"
  installed=$((installed + 1))

  for alias in "${ALIAS_NAMES[@]}"; do
    alias_dest="$agent_base/skills/$alias"
    mkdir -p "$alias_dest"
    curl -fsSL "$BASE/$alias/SKILL.md" -o "$alias_dest/SKILL.md" 2>/dev/null || true
    echo "opendeploy: alias /$alias installed -> $alias_dest"
  done
done

echo "opendeploy: $installed agent(s) installed"
