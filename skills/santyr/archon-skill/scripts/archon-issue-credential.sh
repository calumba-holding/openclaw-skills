#!/bin/bash
# Issue Archon verifiable credential
# Usage: archon-issue-credential.sh <issuer-did> <subject-did> <type> <claims-json>

set -e

ISSUER_DID="${1:?Usage: $0 <issuer-did> <subject-did> <type> <claims-json>}"
SUBJECT_DID="${2:?}"
TYPE="${3:?}"
CLAIMS="${4:?}"

export ARCHON_CONFIG_DIR="$HOME/.config/hex/archon"
export ARCHON_PASSPHRASE="hex-daemon-lightning-hive-2026"

cd "$ARCHON_CONFIG_DIR" || exit 1

echo "Issuing credential:"
echo "  Issuer: $ISSUER_DID"
echo "  Subject: $SUBJECT_DID"
echo "  Type: $TYPE"
echo "  Claims: $CLAIMS"

npx @didcid/keymaster issue-credential \
  --issuer-did "$ISSUER_DID" \
  --subject-did "$SUBJECT_DID" \
  --type "$TYPE" \
  --claims "$CLAIMS"
