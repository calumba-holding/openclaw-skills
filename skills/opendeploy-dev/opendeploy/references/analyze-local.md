# Local source analysis - opendeploy Step 2

Reference for Step 2: materialize the source, detect services, emit a fixed-schema `analysis.json`. **All client-side.** Do not hit `/upload/analyze-only`, `/upload/analyze-from-upload`, or `/analyze*`.

JSON-mode discipline (Backend CLAUDE.md section 3): emit **exactly** the fields listed in section 3 below. If a field is not confidently knowable, use empty string / empty array - never fabricate.

---

## 1. Materialize source to a local workdir

```bash
WORKDIR=$(mktemp -d)
case "$SOURCE_KIND" in
  git)    git clone --depth=1 ${GIT_BRANCH:+-b "$GIT_BRANCH"} "$GIT_URL" "$WORKDIR" ;;
  zip)    unzip -q "$ZIP_PATH" -d "$WORKDIR" ;;
  folder) WORKDIR="$SOURCE_PATH" ;;
esac
```

### Files to enumerate

One pass, do **not** recurse into `node_modules`, `.git`, `dist`, `target`, `vendor`, `__pycache__`, `.venv`.

```
package.json, pnpm-workspace.yaml, turbo.json, lerna.json, nx.json
requirements.txt, pyproject.toml, Pipfile, setup.py
go.mod, Cargo.toml, pom.xml, build.gradle(.kts), composer.json, Gemfile
Dockerfile, */Dockerfile, docker-compose.y?(a)ml, Procfile
.env.example, .env.sample, .env.template
next.config.{js,mjs,ts}, vite.config.*, nuxt.config.*, svelte.config.*,
  astro.config.*, remix.config.*, angular.json
README* (first 200 lines only)
```

Real deploy env files (`.env`, `.env.local`, `.env.production`,
`.env.development`, `.env.$OD_ENVIRONMENT`, `.env.*.local`) are not source
analysis inputs. They may be read later only by **Deploy env collection** below
so their values can be submitted to the opendeploy API as service configuration.
Never copy real env values into `analysis.json`.

---

## 2. Multi-service detection

Pick the first matching rule:

1. **`docker-compose.y?ml` present** -> each top-level `services:` entry is a candidate service. Extract `image`, `build.context`, `ports`, `environment`, `depends_on`. Entries whose image matches `postgres | mysql | mariadb | mongo | redis | valkey | rabbitmq | clickhouse | elasticsearch | meilisearch | minio` are **dependencies**, not build services.
2. **Monorepo markers** (`pnpm-workspace.yaml`, `turbo.json`, `lerna.json`, `nx.json`) OR multiple top-level `Dockerfile`s -> each workspace package that has its own `Dockerfile` or `scripts.start` is a service.
3. Otherwise -> single service named `$PROJECT_NAME`.

---

## 3. Per-service schema

Emit one object per service. For multi-service, wrap as `{"services":[...]}`. Save to `$WORKDIR/.opendeploy/analysis.json`.

```json
{
  "name": "api",
  "source_path": "./services/api",
  "language": "typescript",
  "language_version": "20",
  "framework": "nextjs",
  "build_tool": "pnpm",
  "package_manager": "pnpm",
  "project_type": "web",
  "port": 3000,
  "entry_point": "src/server.ts",
  "output_directory": ".next",
  "scripts_build": "pnpm build",
  "scripts_start": "pnpm start",
  "database_type": "postgres",
  "dependencies": ["postgres", "redis"],
  "runtime_vars":  [{"name":"DATABASE_URL","required":true,"default":""}],
  "build_time_vars":[{"name":"NEXT_PUBLIC_API_URL","required":false,"default":""}]
}
```

### Field-by-field rules

**`port`** - in priority order:
1. Dockerfile `EXPOSE <N>` -> `N`.
2. compose `ports: ["host:container"]` -> `container`.
3. Framework default:
   - Next.js / Nuxt / Rails -> `3000`
   - Vite `preview` -> `4173`
   - Django -> `8000`
   - Flask -> `5000`
   - Spring Boot / Go `net/http` / Rust Actix -> `8080`
4. Ambiguous -> ask the user; do not guess.

**`language` / `framework`** - derive from manifest, never from file extensions alone:
- `package.json.dependencies.next` -> `framework: nextjs`, `language: typescript` (if `tsconfig.json`) else `javascript`.
- `pyproject.toml.project.dependencies` containing `django` / `fastapi` / `flask` -> corresponding framework.
- `go.mod` present -> `language: go`; framework from imports (e.g. `gin-gonic/gin` -> `gin`).
- `Cargo.toml` -> `language: rust`; framework from deps.
- `pom.xml` / `build.gradle*` -> `language: java`; framework from deps.

**`runtime_vars`** - union of:
- All keys in `.env.example` / `.env.sample` / `.env.template`.
- Grep hits for these patterns in source (just grep, do not parse AST):
  - JS/TS: `process.env.VAR_NAME`
  - Python: `os.getenv("NAME")`, `os.environ["NAME"]`, `os.environ.get("NAME")`
  - Go: `os.Getenv("NAME")`
  - Rust: `std::env::var("NAME")`, `env!("NAME")`
  - Ruby: `ENV["NAME"]`
  - PHP: `getenv("NAME")`, `$_ENV["NAME"]`
  - Shell: `$NAME` / `${NAME}` in `entrypoint.sh` / `docker-entrypoint.sh`
- `environment:` keys from each compose service.

Mark `required: true` only when:
- No default value in `.env.example` / `.env.sample` / `.env.template`, AND
- No fallback in code (e.g. `process.env.FOO || "bar"` -> `required: false`).

When unsure, `required: false` with `default: ""`.

**`database_type`** - pick first match:
1. Compose DB-image (`postgres` / `mysql` / `mariadb` -> `mysql` / `mongo` -> `mongodb` / `redis` / `valkey` -> `redis`).
2. Manifest deps:
   - Postgres: `pg`, `psycopg2`, `sqlalchemy` with `postgres://`, `gorm.io/driver/postgres`, `lib/pq`, `tokio-postgres`, `sequelize` with `dialect:'postgres'`.
   - MySQL: `mysql2`, `pymysql`, `mysql-connector-python`, `gorm.io/driver/mysql`, `go-sql-driver/mysql`.
   - MongoDB: `mongoose`, `mongodb`, `pymongo`, `motor`, `mongo-driver`.
   - Redis: `redis` (npm/py), `ioredis`, `go-redis/redis`, `redis-rs`.
3. Empty string if none.

**`build_time_vars`** - anything matching:
- Prefix `NEXT_PUBLIC_`, `VITE_`, `REACT_APP_`, `PUBLIC_`, `NUXT_PUBLIC_`, `EXPO_PUBLIC_`.
- Any var referenced in `scripts.build` / Dockerfile `ARG` / CI build command.

**`dependencies`** - list of DB types this service needs. Populated if:
- `database_type` is non-empty, include it.
- Multi-service compose has `depends_on` pointing at a DB service - include that DB type too.

---

## 3.5 Deploy env collection - submit values to the platform API

This step is separate from source analysis. It exists so automatic deploys can
pick up local runtime/build configuration without uploading secret files.

Allowed behavior:

- Read real env files only to build deployment override maps.
- Submit the resulting key/value pairs to the opendeploy API as
  `runtime_variables` / `build_variables` during service create, or via
  `PUT /projects/:id/services/:sid/env` for an env rotation.
- Keep local override files mode `0600`.
- Log and report only key names and counts, never values.

Forbidden behavior:

- Do not write real env values to `$WORKDIR/.opendeploy/analysis.json`.
- Do not include real env files in the source ZIP.
- Do not write real env values to `~/.opendeploy/logs/*`.

Collect from these files when present, later files overriding earlier files:

```text
.env
.env.local
.env.$OD_ENVIRONMENT
.env.$OD_ENVIRONMENT.local
```

If the project has its own dotenv parser in its toolchain, prefer that parser.
Otherwise parse standard `KEY=VALUE` dotenv lines, ignoring blank lines,
comments, and malformed keys. Split variables with public build prefixes into
`user_build_overrides.json`; all others go to `user_overrides.json`.

```bash
umask 0077
: > user_overrides.json
: > user_build_overrides.json
chmod 600 user_overrides.json user_build_overrides.json

# The agent should materialize these JSON files as flat objects:
#   user_overrides.json        -> runtime env values submitted to the platform
#   user_build_overrides.json  -> build-time env values submitted to the platform
#
# Public build prefixes:
#   NEXT_PUBLIC_, VITE_, REACT_APP_, PUBLIC_, NUXT_PUBLIC_, EXPO_PUBLIC_
#
# Example shape only; never print values:
#   {"DATABASE_URL":"postgres://...", "SESSION_SECRET":"..."}
```

Delete the two override files after the deploy attempt completes, success or
failure. They are local transport files only.

---

## 4. Decision: does the project need a DB? (Step 2.5)

Create a DB dependency in Step 3.2 if **any** of these hold:

- `analysis.database_type` in {`postgres`, `mysql`, `mongodb`, `redis`}.
- Any `runtime_vars[].name` matches `DATABASE_URL | MYSQL_* | POSTGRES_* | PG_* | REDIS_URL | MONGO* | CLICKHOUSE_*`.
- Section 2's compose parse found a DB-image service (`postgres|mysql|mariadb|mongo|redis|valkey|...`).

Mapping to `dependency_id` values for `POST /dependencies/create`:

| detected | `dependency_id` |
|---|---|
| postgres, postgresql | `postgres` |
| mysql, mariadb | `mysql` |
| mongodb | `mongodb` |
| redis, valkey | `redis` |

If multiple services share a DB -> create **one** dependency in Step 3.2 (no `service_id`), reuse its `env_vars` in every service's Step 3.3 body.

If no signal triggers -> this is a no-op. Do NOT provision "just in case" - it burns region quota.

---

## 5. Package the source for upload (Step 4)

**Format: ZIP only.** The backend (`project-service/internal/handlers/upload.go`) uses `archive/zip` exclusively; tar / tar.gz is rejected at extraction. Keep `source_path` per service so Step 4 can zip the right subfolder for monorepos.

```bash
SRC_ZIP="$WORKDIR/.opendeploy/$SVC_NAME.zip"
mkdir -p "$(dirname "$SRC_ZIP")"

# zip from inside the service subfolder so archive paths are flat.
# Real env/credential files are deployment inputs, not source artifacts.
(cd "$WORKDIR/$SVC_SOURCE_PATH" && \
  zip -qr "$SRC_ZIP" . \
    -x '*.git/*' 'node_modules/*' 'dist/*' 'build/*' \
       'target/*' '.venv/*' '__pycache__/*' '*.pyc' \
       '.opendeploy/*' \
       '.env' '.env.*' '.npmrc' '.pypirc' '.netrc' \
       '*.pem' '*.key' 'id_rsa' 'id_rsa.pub' 'id_ed25519' 'id_ed25519.pub' \
       'credentials.json' 'service-account*.json' '*kubeconfig*')
```

If the user supplied a ZIP directly, inspect it before upload. If it contains
real env or credential files matching the exclusion list above, stop and ask
for a sanitized ZIP or explicit confirmation to continue. The default is to
reject unsafe ZIPs.
