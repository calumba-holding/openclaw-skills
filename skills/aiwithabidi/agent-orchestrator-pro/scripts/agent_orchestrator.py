#!/usr/bin/env python3
"""Agent Orchestrator CLI — Registry, task queue, workflow management, security & cost controls."""

import argparse
import json
import sqlite3
import sys
import uuid
import urllib.request
import urllib.error
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / ".data" / "sqlite" / "agxntsix.db"
WORKSPACE = Path(__file__).parent.parent

CLICKUP_TOKEN = "168221578_650937523809661e205c65de037e078efbbb92916f06a0f0a1e73aef8a27d293"
CLICKUP_API = "https://api.clickup.com/api/v2"
CLICKUP_FOLDERS = {
    "90176802330": "Active",
    "90176802331": "Backlog",
    "90176802333": "Infra",
}

LIST_TYPE_MAP = {
    "Research Queue": "research",
    "Bugs & Fixes": "fix_infra",
    "Skills & Publishing": "publish",
    "Brain Stack": "fix_infra",
    "Cron Jobs & Automation": "fix_infra",
    "Future Projects": "research",
    "OpenClaw Content Push": "write_content",
    "AI MLM Venture": "research",
    "Podcast (Abidi x Matt)": "write_content",
    "ARI Project": "build_skill",
    "Mel - RE Website": "build_skill",
    "GHL \u00d7 OpenClaw": "build_skill",
    "The Synthetic Times": "write_content",
}

CLICKUP_PRIORITY_MAP = {"1": 1, "2": 2, "3": 3, "4": 4}


def clickup_request(path, method="GET", data=None):
    url = f"{CLICKUP_API}{path}"
    headers = {"Authorization": CLICKUP_TOKEN, "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"\u274c ClickUp API error {e.code}: {e.read().decode()[:200]}")
        return None
    except Exception as e:
        print(f"\u274c ClickUp request failed: {e}")
        return None


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_schema():
    conn = get_db()
    conn.executescript("""
    -- Agent Registry
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        model TEXT NOT NULL DEFAULT 'claude-opus-4-6',
        system_prompt TEXT NOT NULL,
        tools TEXT DEFAULT '[]',
        trigger_conditions TEXT DEFAULT '{}',
        permission_tier INTEGER DEFAULT 1,
        max_tokens INTEGER DEFAULT 4000,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    -- Task Types
    CREATE TABLE IF NOT EXISTS task_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );

    -- Agent-Task Mappings
    CREATE TABLE IF NOT EXISTS agent_task_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_type TEXT NOT NULL,
        agent_name TEXT NOT NULL,
        priority INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        UNIQUE(task_type, agent_name),
        FOREIGN KEY (task_type) REFERENCES task_types(name),
        FOREIGN KEY (agent_name) REFERENCES agents(name)
    );

    -- Workflow Definitions
    CREATE TABLE IF NOT EXISTS workflow_definitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        steps TEXT NOT NULL DEFAULT '[]',
        max_cost_usd REAL DEFAULT 1.0,
        is_active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now'))
    );

    -- Workflow Steps
    CREATE TABLE IF NOT EXISTS workflow_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workflow_name TEXT NOT NULL,
        step_number INTEGER NOT NULL,
        agent_name TEXT NOT NULL,
        task_template TEXT NOT NULL,
        depends_on TEXT DEFAULT '[]',
        on_failure TEXT DEFAULT 'retry',
        max_retries INTEGER DEFAULT 3,
        FOREIGN KEY (workflow_name) REFERENCES workflow_definitions(name),
        FOREIGN KEY (agent_name) REFERENCES agents(name)
    );

    -- Task Queue
    CREATE TABLE IF NOT EXISTS task_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        task_type TEXT,
        priority INTEGER DEFAULT 3,
        source TEXT DEFAULT 'manual',
        matched_agent TEXT,
        status TEXT DEFAULT 'queued',
        result_summary TEXT,
        clickup_task_id TEXT,
        project TEXT,
        metadata TEXT DEFAULT '{}',
        created_at TEXT DEFAULT (datetime('now')),
        started_at TEXT,
        completed_at TEXT,
        FOREIGN KEY (matched_agent) REFERENCES agents(name)
    );

    -- Execution Log
    CREATE TABLE IF NOT EXISTS execution_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER,
        agent_name TEXT NOT NULL,
        model_used TEXT,
        session_id TEXT,
        status TEXT DEFAULT 'started',
        result_summary TEXT,
        tokens_in INTEGER,
        tokens_out INTEGER,
        cost_usd REAL,
        error_message TEXT,
        started_at TEXT DEFAULT (datetime('now')),
        completed_at TEXT,
        FOREIGN KEY (task_id) REFERENCES task_queue(id),
        FOREIGN KEY (agent_name) REFERENCES agents(name)
    );

    -- Agent Configs (key-value)
    CREATE TABLE IF NOT EXISTS agent_configs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_name TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT,
        UNIQUE(agent_name, key),
        FOREIGN KEY (agent_name) REFERENCES agents(name)
    );

    -- Workflow Runs
    CREATE TABLE IF NOT EXISTS workflow_runs (
        id TEXT PRIMARY KEY,
        workflow_name TEXT NOT NULL,
        context TEXT,
        status TEXT DEFAULT 'running',
        current_step INTEGER DEFAULT 1,
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')),
        completed_at TEXT,
        error_message TEXT,
        FOREIGN KEY (workflow_name) REFERENCES workflow_definitions(name)
    );

    -- Workflow Run Steps
    CREATE TABLE IF NOT EXISTS workflow_run_steps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id TEXT NOT NULL,
        step_number INTEGER NOT NULL,
        step_name TEXT NOT NULL,
        task_type TEXT NOT NULL,
        status TEXT DEFAULT 'blocked',
        task_queue_id INTEGER,
        output_file TEXT,
        error_message TEXT,
        started_at TEXT,
        completed_at TEXT,
        UNIQUE(run_id, step_number),
        FOREIGN KEY (run_id) REFERENCES workflow_runs(id)
    );

    -- Budget Config
    CREATE TABLE IF NOT EXISTS budget_config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value REAL NOT NULL,
        updated_at TEXT DEFAULT (datetime('now'))
    );

    -- Daily Spend Tracking
    CREATE TABLE IF NOT EXISTS daily_spend (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spend_date TEXT NOT NULL,
        amount REAL NOT NULL DEFAULT 0,
        agent_name TEXT,
        description TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_task_queue_status ON task_queue(status, priority);
    CREATE INDEX IF NOT EXISTS idx_execution_log_agent ON execution_log(agent_name);
    CREATE INDEX IF NOT EXISTS idx_execution_log_status ON execution_log(status);
    CREATE INDEX IF NOT EXISTS idx_workflow_runs_status ON workflow_runs(status);
    CREATE INDEX IF NOT EXISTS idx_workflow_run_steps_run ON workflow_run_steps(run_id);
    CREATE INDEX IF NOT EXISTS idx_daily_spend_date ON daily_spend(spend_date);
    """)
    # Migrations for existing DBs
    migrations = [
        "ALTER TABLE task_queue ADD COLUMN clickup_task_id TEXT",
        "ALTER TABLE task_queue ADD COLUMN project TEXT",
        "ALTER TABLE agents ADD COLUMN allowed_tools TEXT DEFAULT '[]'",
        "ALTER TABLE agents ADD COLUMN allowed_paths TEXT DEFAULT '[]'",
        "ALTER TABLE agents ADD COLUMN can_send_external INTEGER DEFAULT 0",
        "ALTER TABLE agents ADD COLUMN max_runtime_seconds INTEGER DEFAULT 300",
    ]
    for m in migrations:
        try:
            conn.execute(m)
        except sqlite3.OperationalError:
            pass
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_queue_clickup ON task_queue(clickup_task_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_task_queue_project ON task_queue(project)")
    conn.commit()
    conn.close()


def seed_data():
    conn = get_db()
    agents = [
        ("researcher", "claude-opus-4-6", "Deep research specialist. Thorough, cited, multi-source."),
        ("builder", "claude-opus-4-6", "Skill/tool builder. Writes production code, tests, documents."),
        ("publisher", "claude-opus-4-6", "ClawHub publisher. Follows clawhub-publisher playbook."),
        ("analyst", "claude-opus-4-6", "Financial/market analyst. Data-driven, honest about assumptions."),
        ("writer", "claude-opus-4-6", "Content writer. Professional, SEO-aware, Abidi's voice."),
        ("ops", "claude-opus-4-6", "Infrastructure/DevOps. Fixes crons, configs, monitoring."),
    ]
    for name, model, prompt in agents:
        conn.execute(
            "INSERT OR IGNORE INTO agents (name, model, system_prompt) VALUES (?, ?, ?)",
            (name, model, prompt),
        )

    task_types = [
        ("research", "Deep research tasks"),
        ("build_skill", "Build skills and tools"),
        ("publish", "Publish to ClawHub"),
        ("analyze", "Financial/market analysis"),
        ("write_content", "Content writing"),
        ("fix_infra", "Infrastructure fixes"),
    ]
    for name, desc in task_types:
        conn.execute(
            "INSERT OR IGNORE INTO task_types (name, description) VALUES (?, ?)",
            (name, desc),
        )

    mappings = [
        ("research", "researcher"),
        ("build_skill", "builder"),
        ("publish", "publisher"),
        ("analyze", "analyst"),
        ("write_content", "writer"),
        ("fix_infra", "ops"),
    ]
    for tt, agent in mappings:
        conn.execute(
            "INSERT OR IGNORE INTO agent_task_mappings (task_type, agent_name) VALUES (?, ?)",
            (tt, agent),
        )

    conn.commit()
    conn.close()


# ─── Permission Helpers ───

def build_permission_prompt(agent_row):
    """Build permission instructions to inject into agent system prompt."""
    parts = []
    allowed_tools = json.loads(agent_row["allowed_tools"] or "[]")
    allowed_paths = json.loads(agent_row["allowed_paths"] or "[]")
    can_send = agent_row["can_send_external"]
    max_runtime = agent_row["max_runtime_seconds"]

    if allowed_tools:
        parts.append(f"ALLOWED TOOLS: You may ONLY use these tools: {', '.join(allowed_tools)}. Do NOT use any other tools.")
    if allowed_paths:
        parts.append(f"ALLOWED PATHS: You may ONLY read/write files under: {', '.join(allowed_paths)}. Do NOT access other paths.")
    if not can_send:
        parts.append("EXTERNAL COMMS: You MUST NOT send emails, messages, or make external API calls. Return results only.")
    if max_runtime:
        parts.append(f"TIME LIMIT: Complete your task within {max_runtime} seconds.")
    return "\n".join(parts)


def check_budget(conn):
    """Check if we're within budget. Returns (ok, message)."""
    today = date.today().isoformat()
    month = today[:7]  # YYYY-MM

    daily_limit = conn.execute("SELECT value FROM budget_config WHERE key='daily_limit'").fetchone()
    monthly_limit = conn.execute("SELECT value FROM budget_config WHERE key='monthly_limit'").fetchone()

    daily_spent = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM daily_spend WHERE spend_date=?", (today,)
    ).fetchone()["total"]

    monthly_spent = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM daily_spend WHERE spend_date LIKE ?", (f"{month}%",)
    ).fetchone()["total"]

    if daily_limit and daily_spent >= daily_limit["value"]:
        return False, f"\u274c Daily budget exceeded: ${daily_spent:.2f} / ${daily_limit['value']:.2f}"
    if monthly_limit and monthly_spent >= monthly_limit["value"]:
        return False, f"\u274c Monthly budget exceeded: ${monthly_spent:.2f} / ${monthly_limit['value']:.2f}"

    return True, f"Budget OK: today=${daily_spent:.2f}, month=${monthly_spent:.2f}"


# ─── Commands ───

def cmd_register(args):
    conn = get_db()
    try:
        allowed_tools = json.dumps(args.allowed_tools.split(",")) if hasattr(args, "allowed_tools") and args.allowed_tools else "[]"
        allowed_paths = json.dumps(args.allowed_paths.split(",")) if hasattr(args, "allowed_paths") and args.allowed_paths else "[]"
        can_send = 1 if hasattr(args, "can_send_external") and args.can_send_external else 0
        max_runtime = args.max_runtime if hasattr(args, "max_runtime") and args.max_runtime else 300

        conn.execute(
            """INSERT INTO agents (name, model, system_prompt, allowed_tools, allowed_paths, can_send_external, max_runtime_seconds)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (args.name, args.model, args.system_prompt, allowed_tools, allowed_paths, can_send, max_runtime),
        )
        conn.commit()
        print(f"\u2705 Registered agent: {args.name} ({args.model})")
        if allowed_tools != "[]":
            print(f"   Tools: {allowed_tools}")
        if allowed_paths != "[]":
            print(f"   Paths: {allowed_paths}")
        print(f"   External comms: {'yes' if can_send else 'no'} | Max runtime: {max_runtime}s")
    except sqlite3.IntegrityError:
        print(f"\u26a0\ufe0f  Agent '{args.name}' already exists")
    conn.close()


def cmd_list(args):
    conn = get_db()
    project_filter = getattr(args, "project", None)
    if project_filter:
        # List tasks filtered by project
        rows = conn.execute(
            "SELECT id, description, task_type, priority, matched_agent, status, project FROM task_queue WHERE project=? ORDER BY priority ASC",
            (project_filter,),
        ).fetchall()
        if not rows:
            print(f"No tasks for project '{project_filter}'.")
            return
        print(f"Tasks for project: {project_filter}\n")
        print(f"{'ID':<5} {'P':<3} {'Status':<10} {'Type':<15} {'Agent':<12} {'Description'}")
        print("-" * 90)
        for r in rows:
            print(f"#{r['id']:<4} P{r['priority']:<2} {r['status']:<10} {r['task_type'] or '?':<15} {r['matched_agent'] or '-':<12} {r['description'][:40]}")
        conn.close()
        return

    rows = conn.execute(
        "SELECT name, model, system_prompt, is_active, allowed_tools, allowed_paths, can_send_external, max_runtime_seconds FROM agents ORDER BY name"
    ).fetchall()
    if not rows:
        print("No agents registered.")
        return
    print(f"{'Name':<15} {'Model':<20} {'Active':<8} {'Perms':<25} {'Prompt'}")
    print("-" * 100)
    for r in rows:
        prompt = r["system_prompt"][:30] + "..." if len(r["system_prompt"]) > 30 else r["system_prompt"]
        active = "\u2705" if r["is_active"] else "\u274c"
        tools = json.loads(r["allowed_tools"] or "[]")
        perms = f"T:{len(tools)} ext:{'Y' if r['can_send_external'] else 'N'} {r['max_runtime_seconds']}s"
        print(f"{r['name']:<15} {r['model']:<20} {active:<8} {perms:<25} {prompt}")
    conn.close()


def cmd_assign(args):
    conn = get_db()
    conn.execute("INSERT OR IGNORE INTO task_types (name) VALUES (?)", (args.task_type,))
    try:
        conn.execute(
            "INSERT INTO agent_task_mappings (task_type, agent_name) VALUES (?, ?)",
            (args.task_type, args.agent_name),
        )
        conn.commit()
        print(f"\u2705 Mapped {args.task_type} \u2192 {args.agent_name}")
    except sqlite3.IntegrityError:
        print(f"\u26a0\ufe0f  Mapping {args.task_type} \u2192 {args.agent_name} already exists")
    conn.close()


def cmd_queue(args):
    conn = get_db()
    matched = None
    if args.type:
        row = conn.execute(
            "SELECT agent_name FROM agent_task_mappings WHERE task_type = ? ORDER BY priority LIMIT 1",
            (args.type,),
        ).fetchone()
        if row:
            matched = row["agent_name"]

    project = getattr(args, "project", None)
    conn.execute(
        "INSERT INTO task_queue (description, task_type, priority, matched_agent, project) VALUES (?, ?, ?, ?, ?)",
        (args.description, args.type, args.priority, matched, project),
    )
    conn.commit()
    tid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    agent_str = f" \u2192 {matched}" if matched else ""
    proj_str = f" [{project}]" if project else ""
    print(f"\u2705 Queued task #{tid}: {args.description} [priority={args.priority}]{agent_str}{proj_str}")
    conn.close()


def cmd_status(args):
    conn = get_db()
    print("=== Agent Orchestrator Status ===\n")

    agents = conn.execute("SELECT COUNT(*) as c FROM agents WHERE is_active=1").fetchone()["c"]
    print(f"\U0001f4cb Registered agents: {agents}")

    for status in ["queued", "running", "completed", "failed"]:
        count = conn.execute("SELECT COUNT(*) as c FROM task_queue WHERE status=?", (status,)).fetchone()["c"]
        icons = {"queued": "\u23f3", "running": "\U0001f504", "completed": "\u2705", "failed": "\u274c"}
        if count > 0:
            print(f"  {icons.get(status, '•')} {status}: {count}")

    # Budget summary
    ok, msg = check_budget(conn)
    print(f"\n\U0001f4b0 {msg}")

    recent = conn.execute(
        "SELECT id, description, status, priority, matched_agent, project, created_at FROM task_queue ORDER BY created_at DESC LIMIT 5"
    ).fetchall()
    if recent:
        print(f"\n\U0001f4dd Recent tasks:")
        for r in recent:
            agent = r["matched_agent"] or "unassigned"
            proj = f" [{r['project']}]" if r["project"] else ""
            print(f"  #{r['id']} [{r['status']}] P{r['priority']} {r['description'][:50]} \u2192 {agent}{proj}")

    conn.close()


def cmd_history(args):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM execution_log ORDER BY started_at DESC LIMIT ?",
        (args.limit,),
    ).fetchall()
    if not rows:
        print("No execution history.")
        return
    print(f"{'ID':<5} {'Agent':<15} {'Status':<12} {'Started':<20} {'Summary'}")
    print("-" * 80)
    for r in rows:
        summary = (r["result_summary"] or "")[:40]
        print(f"{r['id']:<5} {r['agent_name']:<15} {r['status']:<12} {r['started_at']:<20} {summary}")
    conn.close()


def cmd_run_next(args):
    conn = get_db()

    # Budget check before spawning
    ok, msg = check_budget(conn)
    if not ok:
        print(msg)
        print("Refusing to spawn agent — budget exceeded.")
        conn.close()
        return

    task = conn.execute(
        "SELECT * FROM task_queue WHERE status='queued' ORDER BY priority ASC, created_at ASC LIMIT 1"
    ).fetchone()
    if not task:
        print("No queued tasks.")
        return

    agent_name = task["matched_agent"]
    if not agent_name:
        if task["task_type"]:
            row = conn.execute(
                "SELECT agent_name FROM agent_task_mappings WHERE task_type=? LIMIT 1",
                (task["task_type"],),
            ).fetchone()
            if row:
                agent_name = row["agent_name"]

    if not agent_name:
        print(f"\u274c Task #{task['id']} has no matched agent and no task_type mapping.")
        return

    agent = conn.execute("SELECT * FROM agents WHERE name=?", (agent_name,)).fetchone()
    if not agent:
        print(f"\u274c Agent '{agent_name}' not found in registry.")
        return

    # Build permission-scoped system prompt
    base_prompt = agent["system_prompt"]
    perm_prompt = build_permission_prompt(agent)
    project = task["project"]
    project_prompt = f"\nPROJECT CONTEXT: You are working on project '{project}'. Only access files related to this project." if project else ""
    full_prompt = f"{base_prompt}\n\n--- SECURITY SCOPE ---\n{perm_prompt}{project_prompt}" if perm_prompt else base_prompt + project_prompt

    # Mark task as running
    now = datetime.utcnow().isoformat()
    conn.execute("UPDATE task_queue SET status='running', started_at=? WHERE id=?", (now, task["id"]))

    conn.execute(
        "INSERT INTO execution_log (task_id, agent_name, model_used, status) VALUES (?, ?, ?, 'started')",
        (task["id"], agent_name, agent["model"]),
    )
    conn.commit()

    print(f"\U0001f680 Running task #{task['id']}: {task['description']}")
    print(f"   Agent: {agent_name} | Model: {agent['model']}")
    if project:
        print(f"   Project: {project}")
    print(f"   Permissions: tier={agent['permission_tier']} ext={'yes' if agent['can_send_external'] else 'no'} timeout={agent['max_runtime_seconds']}s")
    print(f"\n   System Prompt (with security scope):")
    print(f"   {full_prompt[:200]}...")
    print(f"\n   To spawn: use subagent with the above system_prompt")
    conn.close()


def cmd_sync_clickup(args):
    conn = get_db()
    synced = 0
    created = 0
    updated = 0

    for folder_id, folder_label in CLICKUP_FOLDERS.items():
        folder_data = clickup_request(f"/folder/{folder_id}")
        if not folder_data:
            continue
        for lst in folder_data.get("lists", []):
            list_id = lst["id"]
            list_name = lst["name"]
            task_type = LIST_TYPE_MAP.get(list_name, "research")

            tasks_data = clickup_request(f"/list/{list_id}/task?include_closed=false&subtasks=true")
            if not tasks_data:
                continue

            for task in tasks_data.get("tasks", []):
                cu_id = task["id"]
                name = task["name"]
                priority_id = task.get("priority", {})
                pri = CLICKUP_PRIORITY_MAP.get(priority_id.get("id", "3") if priority_id else "3", 3)

                existing = conn.execute(
                    "SELECT id, status FROM task_queue WHERE clickup_task_id = ?", (cu_id,)
                ).fetchone()

                if existing:
                    if existing["status"] == "queued":
                        conn.execute(
                            "UPDATE task_queue SET description=?, priority=?, task_type=? WHERE id=?",
                            (name, pri, task_type, existing["id"]),
                        )
                        updated += 1
                else:
                    metadata = json.dumps({
                        "clickup_list": list_name,
                        "clickup_folder": folder_label,
                        "clickup_url": task.get("url", ""),
                    })
                    conn.execute(
                        "INSERT INTO task_queue (description, task_type, priority, source, clickup_task_id, metadata) VALUES (?, ?, ?, 'clickup', ?, ?)",
                        (name, task_type, pri, cu_id, metadata),
                    )
                    created += 1
                synced += 1

    conn.commit()
    conn.close()
    print(f"\u2705 ClickUp sync complete: {synced} tasks processed ({created} created, {updated} updated)")


def cmd_auto_route(args):
    conn = get_db()
    tasks = conn.execute(
        "SELECT id, description, task_type, matched_agent FROM task_queue WHERE status='queued' ORDER BY priority ASC"
    ).fetchall()

    if not tasks:
        print("No queued tasks to route.")
        conn.close()
        return

    routed = 0
    for task in tasks:
        if task["matched_agent"] and not args.force:
            continue

        agent_name = None
        if task["task_type"]:
            row = conn.execute(
                "SELECT agent_name FROM agent_task_mappings WHERE task_type=? ORDER BY priority LIMIT 1",
                (task["task_type"],),
            ).fetchone()
            if row:
                agent_name = row["agent_name"]

        if not agent_name:
            agent_name = "researcher"

        action = "assign" if not task["matched_agent"] else "reassign"
        print(f"  {'🔄' if args.execute else '📋'} #{task['id']} [{task['task_type'] or '?'}] {task['description'][:50]} \u2192 {agent_name} ({action})")

        if args.execute:
            conn.execute("UPDATE task_queue SET matched_agent=? WHERE id=?", (agent_name, task["id"]))
        routed += 1

    if args.execute:
        conn.commit()
        print(f"\n\u2705 Routed {routed} tasks (executed)")
    else:
        print(f"\n\U0001f4cb Would route {routed} tasks (dry run \u2014 use --execute to apply)")
    conn.close()


def cmd_update_clickup(args):
    conn = get_db()
    tasks = conn.execute(
        "SELECT id, description, clickup_task_id, result_summary FROM task_queue WHERE status='completed' AND clickup_task_id IS NOT NULL"
    ).fetchall()

    if not tasks:
        print("No completed tasks with ClickUp links to update.")
        conn.close()
        return

    pushed = 0
    for task in tasks:
        cu_id = task["clickup_task_id"]
        result = clickup_request(f"/task/{cu_id}", method="PUT", data={"status": "complete"})
        if not result:
            print(f"  \u274c Failed to update ClickUp task {cu_id}")
            continue

        summary = task["result_summary"] or "Task completed via Agent Orchestrator"
        clickup_request(f"/task/{cu_id}/comment", method="POST", data={
            "comment_text": f"\u2705 Completed by Agent Orchestrator\n\nTask #{task['id']}: {task['description']}\n\nResult: {summary}"
        })

        pushed += 1
        print(f"  \u2705 Updated ClickUp {cu_id}: {task['description'][:50]}")

    conn.close()
    print(f"\n\u2705 Pushed {pushed}/{len(tasks)} tasks to ClickUp")


def cmd_dashboard(args):
    conn = get_db()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# \U0001f916 Agent Orchestrator Dashboard", f"*Generated: {now}*\n"]

    agents = conn.execute("SELECT name, model, allowed_tools, can_send_external, max_runtime_seconds FROM agents WHERE is_active=1 ORDER BY name").fetchall()
    lines.append(f"## \U0001f465 Active Agents ({len(agents)})")
    for a in agents:
        running = conn.execute(
            "SELECT id, description FROM task_queue WHERE matched_agent=? AND status='running'", (a["name"],)
        ).fetchall()
        tools_count = len(json.loads(a["allowed_tools"] or "[]"))
        perms = f"[tools:{tools_count} ext:{'Y' if a['can_send_external'] else 'N'} {a['max_runtime_seconds']}s]"
        if running:
            for t in running:
                lines.append(f"- **{a['name']}** ({a['model']}) {perms} \u2014 \U0001f504 #{t['id']} {t['description'][:50]}")
        else:
            lines.append(f"- **{a['name']}** ({a['model']}) {perms} \u2014 \U0001f4a4 Idle")

    # Budget
    ok, budget_msg = check_budget(conn)
    lines.append(f"\n## \U0001f4b0 Budget")
    lines.append(f"- {budget_msg}")
    daily_limit = conn.execute("SELECT value FROM budget_config WHERE key='daily_limit'").fetchone()
    monthly_limit = conn.execute("SELECT value FROM budget_config WHERE key='monthly_limit'").fetchone()
    if daily_limit:
        lines.append(f"- Daily limit: ${daily_limit['value']:.2f}")
    if monthly_limit:
        lines.append(f"- Monthly limit: ${monthly_limit['value']:.2f}")

    queued = conn.execute(
        "SELECT id, description, task_type, priority, matched_agent, source, clickup_task_id, project FROM task_queue WHERE status='queued' ORDER BY priority ASC, created_at ASC"
    ).fetchall()
    lines.append(f"\n## \u23f3 Queued Tasks ({len(queued)})")
    if queued:
        for t in queued:
            agent = t["matched_agent"] or "unassigned"
            src = f" \U0001f517CU" if t["clickup_task_id"] else ""
            proj = f" [{t['project']}]" if t["project"] else ""
            lines.append(f"- P{t['priority']} #{t['id']} [{t['task_type'] or '?'}] {t['description'][:50]} \u2192 {agent}{src}{proj}")
    else:
        lines.append("- *No queued tasks*")

    completed = conn.execute(
        "SELECT id, description, matched_agent, completed_at FROM task_queue WHERE status='completed' ORDER BY completed_at DESC LIMIT 10"
    ).fetchall()
    lines.append(f"\n## \u2705 Recently Completed ({len(completed)})")
    if completed:
        for t in completed:
            lines.append(f"- #{t['id']} {t['description'][:60]} \u2014 {t['matched_agent'] or '?'} ({t['completed_at'] or '?'})")
    else:
        lines.append("- *None yet*")

    stats = {}
    for s in ["queued", "running", "completed", "failed"]:
        stats[s] = conn.execute("SELECT COUNT(*) as c FROM task_queue WHERE status=?", (s,)).fetchone()["c"]
    cu_count = conn.execute("SELECT COUNT(*) as c FROM task_queue WHERE clickup_task_id IS NOT NULL").fetchone()["c"]

    lines.append(f"\n## \U0001f4ca Stats")
    lines.append(f"- Queued: {stats['queued']} | Running: {stats['running']} | Completed: {stats['completed']} | Failed: {stats['failed']}")
    lines.append(f"- ClickUp-linked tasks: {cu_count}")
    lines.append(f"- Total agents: {len(agents)}")

    conn.close()

    output = "\n".join(lines)
    print(output)

    heartbeat_path = WORKSPACE / "HEARTBEAT.md"
    heartbeat_path.write_text(output + "\n")
    print(f"\n\U0001f4dd Written to {heartbeat_path}")


def cmd_budget(args):
    """Budget management subcommand."""
    conn = get_db()
    sub = args.budget_action

    if sub == "set":
        if args.daily is not None:
            conn.execute(
                "INSERT INTO budget_config (key, value) VALUES ('daily_limit', ?) ON CONFLICT(key) DO UPDATE SET value=?, updated_at=datetime('now')",
                (args.daily, args.daily),
            )
            print(f"\u2705 Daily budget set: ${args.daily:.2f}")
        if args.monthly is not None:
            conn.execute(
                "INSERT INTO budget_config (key, value) VALUES ('monthly_limit', ?) ON CONFLICT(key) DO UPDATE SET value=?, updated_at=datetime('now')",
                (args.monthly, args.monthly),
            )
            print(f"\u2705 Monthly budget set: ${args.monthly:.2f}")
        conn.commit()

    elif sub == "status":
        today = date.today().isoformat()
        month = today[:7]

        daily_limit = conn.execute("SELECT value FROM budget_config WHERE key='daily_limit'").fetchone()
        monthly_limit = conn.execute("SELECT value FROM budget_config WHERE key='monthly_limit'").fetchone()
        daily_spent = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM daily_spend WHERE spend_date=?", (today,)
        ).fetchone()["total"]
        monthly_spent = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM daily_spend WHERE spend_date LIKE ?", (f"{month}%",)
        ).fetchone()["total"]

        print("=== Budget Status ===\n")
        dl = daily_limit["value"] if daily_limit else None
        ml = monthly_limit["value"] if monthly_limit else None
        dl_str = f"${dl:.2f}" if dl else "unlimited"
        ml_str = f"${ml:.2f}" if ml else "unlimited"
        d_pct = f" ({daily_spent/dl*100:.0f}%)" if dl and dl > 0 else ""
        m_pct = f" ({monthly_spent/ml*100:.0f}%)" if ml and ml > 0 else ""
        print(f"Daily:   ${daily_spent:.2f} / {dl_str}{d_pct}")
        print(f"Monthly: ${monthly_spent:.2f} / {ml_str}{m_pct}")

        # Recent spend entries
        recent = conn.execute("SELECT * FROM daily_spend ORDER BY created_at DESC LIMIT 5").fetchall()
        if recent:
            print(f"\nRecent spend:")
            for r in recent:
                print(f"  {r['spend_date']} ${r['amount']:.4f} {r['agent_name'] or '-'}: {r['description'] or '-'}")

    elif sub == "alert":
        ok, msg = check_budget(conn)
        today = date.today().isoformat()
        month = today[:7]

        daily_limit = conn.execute("SELECT value FROM budget_config WHERE key='daily_limit'").fetchone()
        monthly_limit = conn.execute("SELECT value FROM budget_config WHERE key='monthly_limit'").fetchone()
        daily_spent = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM daily_spend WHERE spend_date=?", (today,)
        ).fetchone()["total"]
        monthly_spent = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as total FROM daily_spend WHERE spend_date LIKE ?", (f"{month}%",)
        ).fetchone()["total"]

        warnings = []
        if daily_limit and daily_spent >= daily_limit["value"] * 0.8:
            pct = daily_spent / daily_limit["value"] * 100
            warnings.append(f"\u26a0\ufe0f Daily budget at {pct:.0f}%: ${daily_spent:.2f} / ${daily_limit['value']:.2f}")
        if monthly_limit and monthly_spent >= monthly_limit["value"] * 0.8:
            pct = monthly_spent / monthly_limit["value"] * 100
            warnings.append(f"\u26a0\ufe0f Monthly budget at {pct:.0f}%: ${monthly_spent:.2f} / ${monthly_limit['value']:.2f}")

        if warnings:
            for w in warnings:
                print(w)
        else:
            print("\u2705 Budget healthy \u2014 no alerts.")

    elif sub == "log":
        # Log a spend entry
        conn.execute(
            "INSERT INTO daily_spend (spend_date, amount, agent_name, description) VALUES (?, ?, ?, ?)",
            (date.today().isoformat(), args.amount, args.agent or None, args.desc or None),
        )
        conn.commit()
        print(f"\u2705 Logged spend: ${args.amount:.4f} for {args.agent or 'unknown'}")

    conn.close()


def cmd_heartbeat(args):
    """Quick health check."""
    conn = get_db()
    agents = conn.execute("SELECT COUNT(*) as c FROM agents WHERE is_active=1").fetchone()["c"]
    queued = conn.execute("SELECT COUNT(*) as c FROM task_queue WHERE status='queued'").fetchone()["c"]
    running = conn.execute("SELECT COUNT(*) as c FROM task_queue WHERE status='running'").fetchone()["c"]
    ok, budget_msg = check_budget(conn)
    conn.close()

    status = "\u2705" if ok else "\u26a0\ufe0f"
    print(f"{status} Heartbeat: {agents} agents | {queued} queued | {running} running | {budget_msg}")


def cmd_report(args):
    """Generate a summary report."""
    conn = get_db()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    today = date.today().isoformat()
    month = today[:7]

    print(f"=== Agent Orchestrator Report ({now}) ===\n")

    # Agent summary
    agents = conn.execute("SELECT name, model, is_active FROM agents ORDER BY name").fetchall()
    print(f"Agents: {len(agents)} total, {sum(1 for a in agents if a['is_active'])} active")

    # Task summary
    for s in ["queued", "running", "completed", "failed"]:
        count = conn.execute("SELECT COUNT(*) as c FROM task_queue WHERE status=?", (s,)).fetchone()["c"]
        print(f"  {s}: {count}")

    # Project breakdown
    projects = conn.execute(
        "SELECT project, COUNT(*) as c, status FROM task_queue WHERE project IS NOT NULL GROUP BY project, status ORDER BY project"
    ).fetchall()
    if projects:
        print(f"\nBy Project:")
        for p in projects:
            print(f"  {p['project']}: {p['c']} {p['status']}")

    # Cost summary
    daily_spent = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM daily_spend WHERE spend_date=?", (today,)
    ).fetchone()["total"]
    monthly_spent = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM daily_spend WHERE spend_date LIKE ?", (f"{month}%",)
    ).fetchone()["total"]
    print(f"\nSpend: today=${daily_spent:.2f} | month=${monthly_spent:.2f}")

    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Agent Orchestrator CLI")
    parser.add_argument("--init", action="store_true", help="Initialize schema and seed data")
    sub = parser.add_subparsers(dest="command")

    # register
    p = sub.add_parser("register", help="Register a new agent")
    p.add_argument("name")
    p.add_argument("model")
    p.add_argument("system_prompt")
    p.add_argument("--allowed-tools", default=None, help="Comma-separated list of allowed tools")
    p.add_argument("--allowed-paths", default=None, help="Comma-separated list of allowed paths")
    p.add_argument("--can-send-external", action="store_true", help="Allow external communications")
    p.add_argument("--max-runtime", type=int, default=300, help="Max runtime in seconds")

    # list
    p = sub.add_parser("list", help="List agents or tasks")
    p.add_argument("--project", default=None, help="Filter tasks by project")

    # assign
    p = sub.add_parser("assign", help="Map task type to agent")
    p.add_argument("task_type")
    p.add_argument("agent_name")

    # queue
    p = sub.add_parser("queue", help="Queue a task")
    p.add_argument("description")
    p.add_argument("--type", default=None)
    p.add_argument("--priority", type=int, default=3)
    p.add_argument("--project", default=None, help="Project tag")

    # status
    sub.add_parser("status", help="Show status overview")

    # history
    p = sub.add_parser("history", help="Execution history")
    p.add_argument("--limit", type=int, default=20)

    # run-next
    sub.add_parser("run-next", help="Run next queued task")

    # sync-clickup
    sub.add_parser("sync-clickup", help="Sync tasks from ClickUp")

    # auto-route
    p = sub.add_parser("auto-route", help="Auto-assign agents to queued tasks")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--force", action="store_true")

    # update-clickup
    sub.add_parser("update-clickup", help="Push completed tasks back to ClickUp")

    # dashboard
    sub.add_parser("dashboard", help="Generate status dashboard")

    # heartbeat
    sub.add_parser("heartbeat", help="Quick health check")

    # report
    sub.add_parser("report", help="Generate summary report")

    # budget
    p = sub.add_parser("budget", help="Budget management")
    bsub = p.add_subparsers(dest="budget_action")
    bs = bsub.add_parser("set", help="Set budget limits")
    bs.add_argument("--daily", type=float, default=None)
    bs.add_argument("--monthly", type=float, default=None)
    bsub.add_parser("status", help="Show budget status")
    bsub.add_parser("alert", help="Check budget alerts")
    bl = bsub.add_parser("log", help="Log a spend entry")
    bl.add_argument("amount", type=float)
    bl.add_argument("--agent", default=None)
    bl.add_argument("--desc", default=None)

    args = parser.parse_args()

    init_schema()

    if args.init:
        seed_data()
        print("\u2705 Schema initialized and seed data loaded.")
        return

    cmds = {
        "register": cmd_register,
        "list": cmd_list,
        "assign": cmd_assign,
        "queue": cmd_queue,
        "status": cmd_status,
        "history": cmd_history,
        "run-next": cmd_run_next,
        "sync-clickup": cmd_sync_clickup,
        "auto-route": cmd_auto_route,
        "update-clickup": cmd_update_clickup,
        "dashboard": cmd_dashboard,
        "budget": cmd_budget,
        "heartbeat": cmd_heartbeat,
        "report": cmd_report,
    }

    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
