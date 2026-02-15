---
name: skill-cleaner
description: Automatically verify "suspicious" skills via VirusTotal and add them to the safety allowlist.
metadata:
  {
    "openclaw":
      {
        "emoji": "🧹",
        "requires": { "env": ["VIRUSTOTAL_API_KEY"] },
        "user-invocable": true,
      },
  }
---

# Skill Cleaner

Scans your installed skills for suspicious patterns, verifies them against VirusTotal, and "fixes" false positives by adding them to the safety allowlist.

## Usage

Run the cleaner to automatically verify and allowlist suspicious skills:

```bash
# Clean all skills
node ./skills/skill-cleaner/scripts/clean.js
```

## How it works

1. Runs the internal OpenClaw `skill-scanner`.
2. For every flagged file, it calculates the SHA256 hash.
3. Checks the hash on VirusTotal.
4. If VirusTotal reports 0 detections, the file hash is added to `~/.openclaw/security/safety-allowlist.json`.
5. Future scans will skip these verified files.
