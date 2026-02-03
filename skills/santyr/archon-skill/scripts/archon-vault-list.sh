#!/bin/bash
# List contents of Archon vault
# Usage: archon-vault-list.sh <vault-name>

set -e

VAULT_NAME="${1:?Usage: $0 <vault-name>}"

export ARCHON_CONFIG_DIR="$HOME/.config/hex/archon"
export ARCHON_PASSPHRASE="hex-daemon-lightning-hive-2026"

cd "$ARCHON_CONFIG_DIR" || exit 1

echo "Vault: $VAULT_NAME"
echo "---"
npx @didcid/keymaster list-vault-items "$VAULT_NAME"
