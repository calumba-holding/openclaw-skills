#!/bin/bash
# Create new Archon DID with local node
# Usage: archon-create-did.sh <name> <type>
# Type: agent or asset

set -e

NAME="${1:?Usage: $0 <name> <type>}"
TYPE="${2:-agent}"

export ARCHON_CONFIG_DIR="$HOME/.config/hex/archon"
export ARCHON_PASSPHRASE="hex-daemon-lightning-hive-2026"

cd "$ARCHON_CONFIG_DIR" || exit 1

echo "Creating DID: $NAME (type: $TYPE)"
npx @didcid/keymaster create-id --name "$NAME" --type "$TYPE"
