---
name: acong-layout-demo
description: Kitchen-sink SKILL.md demonstrating the full recommended skill directory layout — multi-file progressive disclosure (FORMS.md + REFERENCE.md), a `references/` subfolder with deep docs, a `scripts/` subfolder with executable helpers, and an `assets/` subfolder with templates. Use when you need a reference implementation for authoring complex Claude Code / ClawHub skills, or when validating a skill loader's ability to handle nested directories.
---

# Acong Layout Demo

A reference skill that exercises **every** structural convention published by Anthropic + the openclaw / vercel-labs community. Use it as a template when bootstrapping non-trivial skills.

## When to use

- Authoring a new complex skill and looking for a layout blueprint
- Validating a skill loader / registry / CLI handles nested folders
- Teaching Progressive Disclosure (Level 1/2/3) by example

## Progressive Disclosure levels demonstrated

| Level | File | Purpose |
|---|---|---|
| 1 — metadata (always loaded) | `SKILL.md` frontmatter | `name` + `description` |
| 2 — instructions (on trigger) | `SKILL.md` body (this text) | Overview + when-to-use |
| 3 — references (on demand) | `FORMS.md`, `REFERENCE.md` (flat) + `references/*.md` (nested) | Deep docs, loaded only when needed |
| 3 — scripts (on demand) | `scripts/*.sh`, `scripts/*.py` | Deterministic helpers executed via bash |
| 3 — assets (on demand) | `assets/*` | Templates, schemas, fixtures |

## Structure map

```
acong-layout-demo/
├── SKILL.md              ← you are here
├── FORMS.md              ← flat-style reference (Anthropic doc example)
├── REFERENCE.md          ← flat-style API ref
├── references/
│   ├── api-guide.md
│   └── examples.md
├── scripts/
│   ├── hello.sh          ← shell helper
│   └── validate.py       ← python helper
└── assets/
    ├── template.md.tpl   ← text template
    └── config.example.yaml
```

## Usage hints for Claude

1. **Need a quick answer?** Stay in this file (Level 2).
2. **Need to fill a form?** Read `FORMS.md`.
3. **Need API spec?** Read `REFERENCE.md` or `references/api-guide.md` for extended version.
4. **Need deterministic validation?** Run `scripts/validate.py <file>`.
5. **Need a template?** Copy `assets/template.md.tpl` and substitute placeholders.

## Not functional

This skill doesn't *do* anything — it's a structural demo. Copy its layout when starting a real skill.
