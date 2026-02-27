---
name: fastmail-suite
description: Secure, safe-by-default Fastmail integration (email, contacts, calendar) via JMAP + CalDAV. Use when you want to read/search email, read/search contacts, view upcoming events, or (only when explicitly enabled) send email and create/reschedule/cancel calendar events. Designed for least-privilege tokens, redacted output by default, and explicit write enable switches.
---

# Fastmail Suite

Use the bundled scripts (stdlib-only) to interact with Fastmail **safely**.

## Quick start (safe / read-only)

### Email (JMAP)

```bash
export FASTMAIL_TOKEN='…'              # read token
python3 skills/fastmail-suite/scripts/fastmail.py mail inbox --limit 20
python3 skills/fastmail-suite/scripts/fastmail.py mail search "invoice" --limit 10
python3 skills/fastmail-suite/scripts/fastmail.py mail read <email-id>
```

### Contacts (JMAP)

```bash
export FASTMAIL_TOKEN='…'
python3 skills/fastmail-suite/scripts/fastmail.py contacts search "alice"
```

### Calendar (CalDAV)

```bash
export FASTMAIL_CALDAV_USER='you@yourdomain'
export FASTMAIL_CALDAV_PASS='app-password'
python3 skills/fastmail-suite/scripts/fastmail.py calendar calendars
python3 skills/fastmail-suite/scripts/fastmail.py calendar upcoming --days 7
```

## Security model (important)

### 1) Redaction is ON by default
- Output is redacted unless you pass `--raw`.
- Control globally with `FASTMAIL_REDACT` (default `1`).

### 2) Writes are OFF by default
Any write operation requires:

```bash
export FASTMAIL_ENABLE_WRITES=1
```

### 3) Use separate tokens/passwords (recommended)
- **Email reading:** `FASTMAIL_TOKEN`
- **Email sending:** `FASTMAIL_TOKEN_SEND` (optional but recommended)
- **Calendar:** `FASTMAIL_CALDAV_USER` + `FASTMAIL_CALDAV_PASS` (Fastmail app password)

## Tasks

### Email
- List inbox: `mail.py inbox [--limit N] [--unread]`
- Unread in inbox: `mail.py unread [--limit N]`
- Search: `mail.py search <query> [--from addr] [--after YYYY-MM-DD] [--before YYYY-MM-DD] [--limit N]`
- Read: `mail.py read <id> [--full] [--raw]`
- Send (writes enabled):

```bash
export FASTMAIL_ENABLE_WRITES=1
export FASTMAIL_TOKEN_SEND='…'         # token with submission scope
# optional identity selection:
export FASTMAIL_IDENTITY_EMAIL='you@yourdomain'
python3 skills/fastmail-suite/scripts/fastmail.py mail send \
  --to recipient@example.com --subject "Hello" --body "Hi there"
```

### Calendar
- Upcoming: `calendar_caldav.py upcoming --days 7 [--debug]`
- Create (writes enabled): `calendar_caldav.py create --calendar-name NAME --summary TEXT --start ISO --end ISO --tz TZID`
- Reschedule/update (writes enabled): `calendar_caldav.py update --href HREF --etag ETAG --summary ... --start ... --end ... --tz ...`
- Cancel (writes enabled): `calendar_caldav.py delete --href HREF --etag ETAG`

Tip: use `upcoming --debug` to get `href` + `etag` for update/delete.

## Notes for publishing later
- Keep tokens/app passwords out of the skill; use env vars only.
- Default to redacted output and write-blocking (already enforced in scripts).
