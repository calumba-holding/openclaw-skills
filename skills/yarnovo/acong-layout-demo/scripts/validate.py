#!/usr/bin/env python3
"""scripts/validate.py — deterministic validation helper.

Demo of a Level 3 script: Claude runs it via bash and only reads the output.
Usage:
    python3 validate.py <file>
Exit codes:
    0 = file exists and is non-empty
    1 = missing argument
    2 = file not found
    3 = file is empty
"""

import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate.py <file>", file=sys.stderr)
        return 1
    p = Path(sys.argv[1])
    if not p.exists():
        print(f"✗ not found: {p}", file=sys.stderr)
        return 2
    if p.stat().st_size == 0:
        print(f"✗ empty: {p}", file=sys.stderr)
        return 3
    print(f"✓ {p} ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
