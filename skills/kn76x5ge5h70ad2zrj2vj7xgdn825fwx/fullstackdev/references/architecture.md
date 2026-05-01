# Architecture Standards

- Keep modular monolith boundaries clear: router -> service -> data access.
- Keep side effects isolated behind service functions.
- Prefer explicit interfaces and predictable contracts.
- Keep background-heavy jobs isolated from request thread where possible.
- Avoid hidden coupling between UI templates and backend internals.
