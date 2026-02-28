#!/usr/bin/env bash
set -euo pipefail

# Install rr shortcut command to ~/.local/bin/rr
# so users can run: rr use gpt-5.3-codex

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RR_SRC="$SCRIPT_DIR/rr"
TARGET_DIR="${HOME}/.local/bin"
TARGET="$TARGET_DIR/rr"

mkdir -p "$TARGET_DIR"
cp "$RR_SRC" "$TARGET"
chmod +x "$TARGET"

echo "✅ Installed rr to: $TARGET"

case ":${PATH:-}:" in
  *":$TARGET_DIR:"*)
    echo "✅ PATH already contains $TARGET_DIR"
    ;;
  *)
    echo "⚠️  Add this to your shell profile (~/.zshrc or ~/.bashrc):"
    echo "export PATH=\"$TARGET_DIR:\$PATH\""
    ;;
esac

echo "\nTry:"
echo "  rr show"
echo "  rr use gpt-5.3-codex"
