---
name: migration-safety-checker
description: Database migration safety reviewer — detect locks, data loss risks, missing rollback plans, and performance issues in SQL and ORM migrations before they hit production.
---

# Migration Safety Checker

Review database migrations for safety issues before they run in production. Catches table locks, data loss, missing rollbacks, and performance problems that would otherwise cause outages.

Use when: "review this migration", "is this migration safe", "check before we deploy", or when reviewing a PR that contains migration files.

## Step 1 — Find Migrations

```bash
# Common migration locations
find . -type f \( \
  -path "*/migrations/*.sql" -o \
  -path "*/migrations/*.py" -o \
  -path "*/migrate/*.sql" -o \
  -path "*/db/migrate/*.rb" -o \
  -path "*/alembic/versions/*.py" -o \
  -path "*/prisma/migrations/*" -o \
  -path "*/drizzle/*.sql" -o \
  -path "*/knex/migrations/*" -o \
  -path "*/flyway/*.sql" -o \
  -path "*/liquibase/*.xml" -o \
  -path "*/sequelize/migrations/*" \
\) -not -path '*/node_modules/*' 2>/dev/null | sort | tail -10

# Latest migration (the one being reviewed)
git diff --name-only HEAD~1 | grep -i migrat
```

## Step 2 — Check for Dangerous Operations

Read the migration file and check for each of these issues:

### Locking Risks (HIGH)

| Operation | Risk | Fix |
|-----------|------|-----|
| `ALTER TABLE ... ADD COLUMN ... NOT NULL` | Full table lock on large tables (PostgreSQL <11, MySQL) | Add column as nullable first, backfill, then add constraint |
| `ALTER TABLE ... ADD COLUMN ... DEFAULT` | Rewrites entire table (PostgreSQL <11) | Add without default, backfill in batches, then set default |
| `CREATE INDEX` | Blocks writes for duration of index build | Use `CREATE INDEX CONCURRENTLY` (Postgres) or `ALGORITHM=INPLACE` (MySQL) |
| `ALTER TABLE ... ALTER COLUMN TYPE` | Full table rewrite + exclusive lock | Create new column, backfill, swap — never alter type on large tables |
| `ALTER TABLE ... ADD CONSTRAINT` | Validates all rows (lock) | Use `NOT VALID` then `VALIDATE CONSTRAINT` separately (Postgres) |
| `LOCK TABLE` | Explicit lock — why? | Almost never needed; remove or justify |

### Data Loss Risks (CRITICAL)

| Operation | Risk | Check |
|-----------|------|-------|
| `DROP TABLE` | Permanent data deletion | Is there a backup? Is the table truly unused? |
| `DROP COLUMN` | Column data lost | Is the column read anywhere? Check app code |
| `TRUNCATE` | All data deleted | Should this be in a migration at all? |
| `DELETE FROM` without WHERE | Deletes everything | Missing WHERE clause? |
| `ALTER COLUMN ... TYPE` with cast | Possible data truncation | Do current values fit the new type? |
| `DROP INDEX` | Query performance regression | Was this index used? Check query plans |

### Rollback Issues (MEDIUM)

| Issue | Check |
|-------|-------|
| No down/rollback migration | Every `up` must have a `down` |
| Irreversible `down` | `DROP TABLE` can't be rolled back with data |
| Data migration without reverse | If you transformed data, can you reverse it? |
| Schema + data in one migration | Split them — data migrations should be separately rollbackable |

### Performance Issues (MEDIUM)

| Pattern | Issue | Fix |
|---------|-------|-----|
| Backfill in migration | Blocks deployment, holds transaction | Use background jobs for large backfills |
| No batching | One giant UPDATE/INSERT | Batch in chunks of 1000-5000 |
| Multiple ALTERs on same table | Each one locks separately | Combine into one ALTER when possible |
| Large DEFAULT values | Rewrites table | Add column, then set default separately |

## Step 3 — ORM-Specific Checks

### Django / Alembic (Python)
```python
# Watch for these in migration files:
# - RunPython without reverse_code → no rollback
# - AddField with default on large table → lock
# - AlterField changing type → rewrite
# - RemoveField → data loss
# - RunSQL without reverse_sql → no rollback
```

### Rails (Ruby)
```ruby
# Watch for:
# - add_column with null: false without default → fails on existing rows
# - add_index without algorithm: :concurrently → table lock
# - change_column → type change, possible lock
# - remove_column → data loss
# - No reversible block or no down method
```

### Prisma / Drizzle / Knex (Node.js)
```
# Watch for:
# - Column made required (@required/NOT NULL) without default
# - Type changes on existing columns
# - Dropped columns or tables
# - No migration squashing on 50+ migration files
```

## Step 4 — Production Readiness

Check these before approving:

- [ ] Migration runs in a transaction (or explicitly opted out with reason)
- [ ] Estimated row count for affected tables (< 1M rows = usually safe, > 10M = needs careful planning)
- [ ] Tested on staging with production-size data
- [ ] Rollback tested (run down migration, verify data intact)
- [ ] Application code is backward-compatible with both old and new schema
- [ ] Deploy order: schema first (additive), then code, then cleanup migration

## Output Template

```markdown
# Migration Review: [filename]

## Safety Rating: 🟢 Safe / 🟡 Caution / 🔴 Dangerous

## Operations
| # | Operation | Table | Risk | Issue |
|---|-----------|-------|------|-------|
| 1 | ADD COLUMN | users | 🟡 | NOT NULL without default — will lock on 2M rows |
| 2 | CREATE INDEX | orders | 🔴 | Not CONCURRENTLY — will block writes on 5M rows |

## Recommendations
1. [specific fix for each issue]

## Rollback Plan
- [does a rollback migration exist?]
- [is it tested?]
- [any data loss on rollback?]

## Estimated Impact
- Tables affected: X
- Estimated lock time: ~Xs on [table] ([row count] rows)
- Downtime required: yes/no
```

## Notes

- PostgreSQL 11+ handles `ADD COLUMN ... DEFAULT` without a table rewrite (but NOT NULL still needs `NOT VALID` trick)
- MySQL 8.0+ supports instant `ADD COLUMN` at the end of the table
- Always check the actual row count: `SELECT reltuples FROM pg_class WHERE relname = 'table_name'`
- For zero-downtime deploys, follow the expand/contract pattern: add new → backfill → migrate code → drop old
