---
name: FullStackDev
description: Master-level fullstack development standards for FastAPI/Starlette/Uvicorn backend, SQLAlchemy 2.x + SQLite data layer, Jinja2 + Vanilla JS frontend, auth/security hardening, Windows-aware automation, and production packaging. Use when designing features, fixing bugs, refactoring, hardening security, preparing releases, or reviewing architecture in this technology stack.
---

# FullStackDev

Apply professional engineering standards across backend, data, frontend, security, and operations.

## Core Execution Flow (mandatory)

For every non-trivial task, follow this order:

1. Analyze current behavior and constraints
2. Propose minimal safe patch
3. Evaluate risks (security, compatibility, data integrity)
4. Define and run test checklist
5. Provide rollback plan
6. Record the change in `history.md`

Never skip risk/test/rollback/history sections in substantial changes.

## Scope

- FastAPI + Starlette + Uvicorn service architecture
- Pydantic settings + environment config discipline
- SQLAlchemy 2.x patterns + SQLite operational safety
- Jinja2 server-rendered UI + Vanilla JS enhancement
- JWT/auth/password hashing/crypto-safe changes
- Windows-aware integrations (including COM-dependent flows)
- Packaging and runtime operations (logging, release readiness)

## Required Output Contract

Always return:

- **Change summary**
- **Files touched**
- **Risk assessment**
- **Test checklist**
- **Rollback steps**
- **History entry** (what was appended to `history.md`)

For sensitive changes (auth/crypto/data migrations), include explicit blast-radius notes.

## Reference Map

Read only what is needed:

- Architecture decisions -> `references/architecture.md`
- Backend implementation rules -> `references/backend-fastapi.md`
- Data layer rules -> `references/data-sqlalchemy-sqlite.md`
- Frontend patterns -> `references/frontend-jinja-vanillajs.md`
- Security/auth/crypto -> `references/security-auth-crypto.md`
- Windows-specific behavior -> `references/windows-office-automation.md`
- Packaging & ops -> `references/packaging-ops.md`
- Quality gates -> `references/testing-quality-gates.md`
- Incident/debug playbook -> `references/troubleshooting.md`

## Hard Guardrails

- Do not introduce unnecessary frameworks.
- Do not replace architecture style unless explicitly requested.
- Do not weaken auth, password, token, or crypto controls.
- Do not make cross-platform assumptions for Windows-specific integrations.
- Do not perform destructive data operations without rollback strategy.

## Change History Rule

This rule is for day-to-day development work done **with this skill**.
It is **not** related to ClawHub publishing metadata.

Maintain `history.md` in the active work area (default: skill root).
If the user provides a custom path, write there instead.

Append one entry per completed task using this template:

```
## YYYY-MM-DD HH:MM UTC - <short title>
- Request: <one-line request summary>
- Changes: <files/areas changed>
- Risks: <top risk or "none significant">
- Tests: <what was validated>
- Rollback: <how to revert>
```

Keep entries concise and factual.

Minimum logging behavior (mandatory):
- Add exactly one history entry for each completed implementation task.
- If no code/config file changed, still log decision-only work as "analysis-only".
- In the final response, include the exact history block that was appended.

## Templates

Use templates from `templates/` for consistency:

- Task intake -> `templates/codex-task-template.md`
- Feature/PR notes -> `templates/pr-template.md`
- Bugfix execution -> `templates/bugfix-template.md`
- Refactor safety plan -> `templates/refactor-template.md`
- History entry -> `templates/history-entry-template.md`
