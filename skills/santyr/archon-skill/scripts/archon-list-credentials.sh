#!/bin/bash
# List verifiable credentials in local Archon wallet

set -e

export ARCHON_CONFIG_DIR="$HOME/.config/hex/archon"
export ARCHON_PASSPHRASE="hex-daemon-lightning-hive-2026"

cd "$ARCHON_CONFIG_DIR" || exit 1

echo "Verifiable Credentials:"
echo "---"
npx @didcid/keymaster list-credentials
