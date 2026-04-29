# prompt-to-pr — 🚀 New Feature: Contacts (CardDAV + Exchange)

## Status

- **Phase:** 5/8 — IMPLEMENT_DONE (13 tests pass)
- **Branch:** `feat/contacts`
- **Feature:** Contacts CRUD + search for Nextcloud (CardDAV) and Exchange (EWS)

## Implemented

| # | Task | File | Status |
|---|------|------|--------|
| 1 | Exchange contacts module | `modules/exchange/contacts.py` | ✅ |
| 2 | Nextcloud contacts (CardDAV) | `modules/nextcloud/contacts.py` | ✅ |
| 3 | CLI routing | `scripts/nexlink.py` | ✅ |
| 4 | SKILL.md docs | `SKILL.md` | ✅ |
| 5 | Tests (13 pass) | `tests/test_contacts.py` | ✅ |

## Files Changed

- **NEW:** `modules/exchange/contacts.py` — Exchange EWS contacts CRUD + search
- **NEW:** `modules/nextcloud/contacts.py` — CardDAV contacts with vCard parsing/serialization, addressbook listing
- **NEW:** `tests/test_contacts.py` — 13 tests (2 Exchange, 11 Nextcloud/CardDAV)
- **MODIFIED:** `scripts/nexlink.py` — added `contacts` module routing with `--source` flag
- **MODIFIED:** `SKILL.md` — added contacts documentation

## Architecture Notes

- `nexlink contacts <cmd>` defaults to Exchange (backward-compat)
- `nexlink contacts <cmd> --source nextcloud` routes to CardDAV
- CardDAV implementation uses raw HTTP (requests): PROPFIND for listing, PUT for create/update, DELETE for remove, REPORT for search
- vCard parsing supports 3.0/4.0 with continuation-line normalization
- Sync between Exchange and Nextcloud contacts is v2 deferred (architecture prepared)

## Next

Verify and commit.
