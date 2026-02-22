# bitclawden

An [OpenClaw](https://openclaw.ai/) skill for managing credentials in a [Bitwarden](https://bitwarden.com/) vault via the `bw` CLI.

## What it does

- Look up usernames, passwords, and TOTP codes
- Create new vault items (logins, secure notes, cards, identities)
- Edit existing items
- Generate strong passwords and passphrases
- Sync vault changes

## Requirements

- [`bw` CLI](https://bitwarden.com/help/cli/) installed and in PATH
- An active Bitwarden session (`BW_SESSION` environment variable)

## Installation

Copy or symlink the `bitclawden` folder into your OpenClaw skills directory:

```bash
# Local install
cp -r bitclawden ~/.openclaw/skills/bitclawden

# Or via ClawHub
clawhub install bitclawden
```

## Security

This skill is **owner-only**. It will refuse to execute in group chats or for non-owner users. Passwords are never shown unless explicitly requested in a private context.

## License

MIT
