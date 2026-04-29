# references/api-guide.md — long-form API guide

Community convention: group extended references under `references/`.

This demonstrates that Claude (or any loader) can walk into a subdirectory and read `.md` files on demand.

## Concepts

### Document

An abstract representation of something the agent can operate on.

### Operations

- `load` — parse from filesystem
- `save` — persist to filesystem
- `merge` — combine two documents into one

## See also

- `REFERENCE.md` (flat quick reference)
- `references/examples.md` (usage examples)
