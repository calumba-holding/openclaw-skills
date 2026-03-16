---
name: ascii-chord
description: Show ASCII guitar chord diagrams using the ascii_chord CLI tool. Use when asked how to play a guitar chord, or to show chord charts/diagrams for any chord name (e.g. E, B7, Am, C, G, Dm, etc.). Uses a bundled pre-compiled binary — no internet access or build step required.
metadata:
  openclaw:
    requires:
      bins: []
    bundledBinaries:
      note: >
        Pre-compiled binaries are included in bin/ for macOS arm64. Built from
        https://github.com/ascii-music/ascii_chord at commit 197a47033fb45f83936bd1e8b410de41db3b595d
        (MIT license, authored by the same person as this skill). No external fetch or build required.
---

# ascii-chord

Display ASCII guitar chord diagrams using [ascii_chord](https://github.com/ascii-music/ascii_chord) — an open-source Rust CLI (MIT license, authored by the same person as this skill).

Pre-compiled binaries are bundled in `bin/` — no Rust toolchain or internet access needed.

## Bundled Binaries

| File | Platform | Built from commit |
|---|---|---|
| `bin/aschord-darwin-arm64` | macOS Apple Silicon | `197a4703` |

## Setup (first use)

Make the binary executable and symlink it:

```bash
SKILL_DIR="$(dirname "$0")"
# detect arch
ARCH=$(uname -m)
OS=$(uname -s | tr '[:upper:]' '[:lower:]')

if [ "$OS" = "darwin" ] && [ "$ARCH" = "arm64" ]; then
  BINARY="$SKILL_DIR/bin/aschord-darwin-arm64"
else
  echo "No bundled binary for $OS/$ARCH — see fallback below"
  exit 1
fi

chmod +x "$BINARY"
```

For day-to-day use, just call the binary directly (see Usage below).

## Usage

Set `ASCHORD` to the correct binary path for the platform, then:

**Single chord:**
```bash
SKILL_BIN=/Users/yuchen/.openclaw/workspace-mati/skills/ascii-chord/bin/aschord-darwin-arm64
chmod +x $SKILL_BIN && $SKILL_BIN get <CHORD>
```

**Multiple chords side by side:**
```bash
$SKILL_BIN list <CHORD1> <CHORD2> ...
```

**List all supported chords:**
```bash
$SKILL_BIN all
```

## Examples

```bash
SKILL_BIN=/Users/yuchen/.openclaw/workspace-mati/skills/ascii-chord/bin/aschord-darwin-arm64
chmod +x $SKILL_BIN

# Single chord
$SKILL_BIN get Am

# Progression
$SKILL_BIN list C G Am F

# All supported chords
$SKILL_BIN all
```

## Fallback (non-arm64 macOS or Linux)

If no bundled binary matches your platform, build from source:

```bash
[ -d /tmp/ascii_chord ] || git clone https://github.com/ascii-music/ascii_chord /tmp/ascii_chord
git -C /tmp/ascii_chord checkout 197a47033fb45f83936bd1e8b410de41db3b595d
cd /tmp/ascii_chord && cargo build --release
```

Then use `/tmp/ascii_chord/target/release/aschord` as the binary.

## Notes

- Chord names are case-sensitive (`Am` not `am`, `B7` not `b7`)
- Source repo: https://github.com/ascii-music/ascii_chord (MIT licensed)
- Pinned commit: `197a47033fb45f83936bd1e8b410de41db3b595d`
