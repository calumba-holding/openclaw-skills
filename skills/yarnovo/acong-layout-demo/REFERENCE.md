# REFERENCE.md — API quick reference

Flat-style reference file (Anthropic docs example: pdf-skill has `REFERENCE.md` at root).

## Functions (demo signatures)

```python
def load(path: str) -> Document: ...
def save(doc: Document, path: str) -> None: ...
def merge(a: Document, b: Document) -> Document: ...
```

See `references/api-guide.md` for long-form explanation.
