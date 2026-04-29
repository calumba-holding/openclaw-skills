#!/usr/bin/env bash
# scripts/hello.sh — deterministic helper demo
#
# Claude invokes this via bash. Only stdout ends up in context, the script
# body itself never loads — that's the token efficiency of Level 3 scripts.

set -euo pipefail

NAME="${1:-world}"
echo "Hello, ${NAME}! (from acong-layout-demo/scripts/hello.sh)"
