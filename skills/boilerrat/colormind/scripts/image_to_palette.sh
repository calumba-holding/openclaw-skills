#!/usr/bin/env bash
set -euo pipefail

# Sample a small palette from an image using ImageMagick, choose a base color,
# then generate a Colormind palette from that base color.
#
# Usage:
#   image_to_palette.sh <imagePath> [--model ui|default]
#
# Output:
#   JSON:
#   {
#     sampled: { colors: [{hex,rgb,count}...], base: {..} },
#     colormind: { result: [[r,g,b]...]} 
#   }

IMG="${1:-}"
if [[ -z "$IMG" || "$IMG" == "-h" || "$IMG" == "--help" ]]; then
  echo "Usage: $(basename "$0") <imagePath> [--model ui|default]" >&2
  exit 2
fi
shift || true

MODEL="ui"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model)
      MODEL="${2:-ui}"; shift 2;;
    *)
      echo "Unknown arg: $1" >&2; exit 2;;
  esac
done

# Build histogram (count + rgb + hex)
HIST=$(convert "$IMG" -alpha off -strip -resize 256x256\> -colors 8 -unique-colors -format "%c\n" histogram:info:- \
  | sed -E 's/^[[:space:]]+//')

# Parse histogram to JSON (sorted by count)
SAMPLED_JSON=$(python3 -c 'import json,re,sys; text=sys.stdin.read().splitlines(); pat=re.compile(r"^(\d+):\s+\((\d+),(\d+),(\d+)\)\s+(#[0-9A-Fa-f]{6})"); colors=[]
for ln in text:
    m=pat.search(ln.strip())
    if not m: continue
    count=int(m.group(1)); r,g,b=map(int,[m.group(2),m.group(3),m.group(4)]); hexv=m.group(5).upper();
    colors.append({"count":count,"rgb":[r,g,b],"hex":hexv})
colors.sort(key=lambda x:x["count"], reverse=True); print(json.dumps(colors))' <<< "$HIST")

BASE_RGB=$(python3 -c 'import json,sys; colors=json.loads(sys.stdin.read() or "[]"); base=(colors[0]["rgb"] if colors else [0,0,0]); print(",".join(map(str,base)))' <<< "$SAMPLED_JSON")

GEN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COLORMIND_JSON=$(node "$GEN_DIR/generate_palette.mjs" --model "$MODEL" --input "$BASE_RGB" N N N N)

python3 - <<PY
import json, sys
sampled=json.loads('''$SAMPLED_JSON''' or '[]')
col=json.loads('''$COLORMIND_JSON''')
out={
  "sampled": {
    "colors": sampled,
    "base": sampled[0] if sampled else None,
  },
  "colormind": col,
}
print(json.dumps(out, indent=2))
PY
