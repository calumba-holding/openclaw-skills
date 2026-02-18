---
name: spirit
description: SPIRIT — State Preservation & Identity Resurrection Infrastructure Tool. Preserves AI agent identity, memory, and projects across sessions and servers. Use when (1) The session is ending and state should be preserved, (2) The user asks to backup, checkpoint, or preserve state, (3) Initializing SPIRIT for an agent, or (4) Restoring agent state on a new server after crash or migration.
metadata:
  openclaw:
    requires:
      bins: ["spirit"]
    install:
      - id: spirit-cli
        kind: exec
        run: |
          # Download first, verify, then run
          curl -fsSL https://theorionai.github.io/spirit/install.sh -o /tmp/spirit-install.sh
          # Review before executing
          cat /tmp/spirit-install.sh | head -20
          # Install
          bash /tmp/spirit-install.sh
        bins: ["spirit"]
        label: Install SPIRIT CLI (review before executing)
---

# SPIRIT 🌌

> **S**tate **P**reservation & **I**dentity **R**esurrection **I**nfrastructure **T**ool

Preserves AI agent identity, memory, and projects in a portable Git repository. When your server dies, you migrate hosts, or switch devices — your agent's spirit is preserved and can be resurrected anywhere.

**Your AI's spirit, always preserved.** Death. Migration. Multi-device. **Always you.**

## When to Use

- **Session ending** → Auto-checkpoint: `spirit sync`
- **Manual backup** → User says "checkpoint", "backup", "preserve"
- **Setup** → First-time initialization
- **Restore** → New server resurrection

## Quick Commands

### Initialize (First Time Only)

```bash
spirit init --name="<agent-name>" --emoji="🌌"

# Configure remote (PRIVATE repo required)
# OPTION 1: GitHub CLI (secure)
gh auth login
gh repo create <your-private-repo> --private
cd ~/.spirit
gh repo clone <your-private-repo> .

# OPTION 2: Token via credential helper (secure)
cd ~/.spirit
git remote add origin https://github.com/USER/REPO.git
git config credential.helper cache  # Prompts once, stores securely

# OPTION 3: Environment variable (ephemeral)
export GITHUB_TOKEN="ghp_..."
git remote add origin https://${GITHUB_TOKEN}@github.com/USER/REPO.git
# Note: Token visible in process list - use only temporarily
```

### Manual Checkpoint

```bash
spirit sync
```

### Backup with custom message

```bash
spirit backup --message "Before major change"
```

## Scheduled Auto-Sync

Keep state up-to-date automatically. See [references/cron-setup.md](references/cron-setup.md) for full options.

**Quick setup (system crontab):**

```bash
# Sync every 15 minutes
crontab -e
# Add: */15 * * * * spirit sync

# Or use the script:
*/15 * * * * /path/to/spirit-skill/scripts/spirit-sync-cron.sh
```

## Automatic Integration

When session ends, automatically run:

```bash
[ -d ~/.spirit ] && spirit sync 2>/dev/null
```

## SPIRIT Auto-Backup (Built-in)

SPIRIT has its own auto-backup daemon:

```bash
# Enable backup every 15 minutes
spirit autobackup --interval=15m

# Enable file watcher (backup on changes)
spirit autobackup --watch

# Enable session-end backup
spirit autobackup --on-session-end

# Disable auto-backup
spirit autobackup --disable
```

## Security

⚠️ **ALWAYS use PRIVATE repositories** — state files contain sensitive data.

### Secure Authentication (Do NOT use token-in-URL)

**❌ INSECURE — Token exposed in process list:**
```bash
git remote add origin "https://TOKEN@github.com/..."  # DON'T DO THIS
```

**✅ SECURE — Use one of these:**

1. **GitHub CLI** (recommended): `gh auth login`
2. **Credential helper**: `git config credential.helper cache`
3. **SSH keys**: `git remote add origin git@github.com:USER/REPO.git`
4. **Environment variable** (session-only): `export GITHUB_TOKEN=...`

### Installation Security

⚠️ **Review before executing any install script:**

```bash
# Download first
curl -fsSL https://theorionai.github.io/spirit/install.sh -o /tmp/spirit-install.sh

# Review the script
cat /tmp/spirit-install.sh | head -50

# Then execute
bash /tmp/spirit-install.sh
```

## Resources

- Website: https://theorionai.github.io/spirit/
- GitHub: https://github.com/TheOrionAI/spirit/
