# Data Layer (SQLAlchemy 2.x + SQLite)

- Use SQLAlchemy 2.x style consistently.
- Keep transaction boundaries explicit.
- For SQLite, preserve durability/performance pragmas (including WAL-oriented operation where configured).
- Never apply schema/data changes without rollback notes.
- Validate query performance impact for frequent paths.
