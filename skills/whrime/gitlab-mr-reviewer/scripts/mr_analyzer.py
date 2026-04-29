#!/usr/bin/env python3
"""
GitLab MR Analyzer

Analyzes a checked-out MR branch against a base branch using git diff.
Detects risk patterns, categorizes files, scores complexity, and produces
a structured review report.

Usage:
    python mr_analyzer.py /path/to/repo
    python mr_analyzer.py . --base origin/main --head HEAD
    python mr_analyzer.py . --base origin/main --mr-id 42
    python mr_analyzer.py . --base origin/main --json --output /tmp/result.json
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from context_config import get_config_value, load_context_config, resolve_value


# ---------------------------------------------------------------------------
# File categorization — used to determine review priority
# ---------------------------------------------------------------------------

FILE_CATEGORIES = {
    "critical": {
        "patterns": [
            r"auth", r"security", r"password", r"token", r"secret",
            r"payment", r"billing", r"crypto", r"encrypt", r"oauth",
            r"jwt", r"permission", r"privilege",
        ],
        "weight": 5,
        "label": "CRITICAL",
        "description": "Security-sensitive files requiring careful review",
    },
    "high": {
        "patterns": [
            r"api", r"database", r"migration", r"schema", r"model",
            r"config", r"env", r"middleware", r"router", r"gateway",
        ],
        "weight": 4,
        "label": "HIGH",
        "description": "Core infrastructure files",
    },
    "medium": {
        "patterns": [
            r"service", r"controller", r"handler", r"util", r"helper",
            r"manager", r"processor", r"resolver",
        ],
        "weight": 3,
        "label": "MEDIUM",
        "description": "Business logic files",
    },
    "low": {
        "patterns": [
            r"test", r"spec", r"mock", r"fixture", r"story",
            r"readme", r"docs", r"\.md$", r"\.txt$",
        ],
        "weight": 1,
        "label": "LOW",
        "description": "Tests and documentation",
    },
}

# ---------------------------------------------------------------------------
# Risk patterns — detected on added lines only (+)
# ---------------------------------------------------------------------------

RISK_PATTERNS = [
    {
        "name": "hardcoded_secret",
        "pattern": r"(password|secret|api[_-]?key|token|access[_-]?key)\s*[=:]\s*['\"][^'\"]{6,}['\"]",
        "severity": "critical",
        "message": "疑似硬编码密钥 — 请改用环境变量或 Vault",
    },
    {
        "name": "sql_injection",
        "pattern": r"(SELECT|INSERT|UPDATE|DELETE|DROP)\s.+\+\s*['\"]",
        "severity": "critical",
        "message": "SQL 字符串拼接 — 存在注入风险，请使用参数化查询",
    },
    {
        "name": "command_injection",
        "pattern": r"(exec|system|popen|subprocess\.call|os\.system)\s*\(.+[\+\%]",
        "severity": "critical",
        "message": "命令注入风险 — 避免在 shell 命令中使用用户输入",
    },
    {
        "name": "debugger_statement",
        "pattern": r"\bdebugger\b",
        "severity": "high",
        "message": "存在 debugger 语句 — 不应提交到生产代码",
    },
    {
        "name": "print_debug",
        "pattern": r"\bprint\s*\(.*debug|console\.(log|debug)\(",
        "severity": "medium",
        "message": "调试输出语句 — 生产代码应使用日志框架",
    },
    {
        "name": "todo_fixme",
        "pattern": r"\b(TODO|FIXME|HACK|XXX)\b",
        "severity": "low",
        "message": "TODO/FIXME 注释 — 确认是否需要在此 MR 内处理",
    },
    {
        "name": "eslint_disable",
        "pattern": r"eslint-disable",
        "severity": "medium",
        "message": "ESLint 规则被禁用 — 需要说明原因",
    },
    {
        "name": "typescript_any",
        "pattern": r":\s*any\b",
        "severity": "medium",
        "message": "TypeScript any 类型 — 请使用具体类型",
    },
    {
        "name": "empty_catch",
        "pattern": r"catch\s*\([^)]*\)\s*\{\s*\}",
        "severity": "high",
        "message": "空 catch 块 — 异常被吞掉，至少添加日志",
    },
    {
        "name": "force_push_hint",
        "pattern": r"--force|--no-verify",
        "severity": "medium",
        "message": "脚本中存在 --force / --no-verify — 确认是否合理",
    },
]


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def run_git(cmd: List[str], cwd: Path) -> Tuple[bool, str]:
    """Run a git command; return (success, stdout)."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, timeout=60
        )
        return result.returncode == 0, result.stdout.strip()
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as exc:
        return False, str(exc)


def get_changed_files(repo: Path, base: str, head: str) -> List[Dict]:
    """Return list of changed files with status."""
    ok, out = run_git(["git", "diff", "--name-status", f"{base}...{head}"], repo)
    if not ok or not out:
        ok, out = run_git(["git", "diff", "--name-status", base, head], repo)
    if not ok or not out:
        ok, out = run_git(["git", "diff", "--name-status", "--cached"], repo)

    status_map = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed", "C": "copied"}
    files = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            status_char = parts[0][0]
            filepath = parts[-1]
            files.append({"path": filepath, "status": status_map.get(status_char, "modified")})
    return files


def get_file_diff(repo: Path, filepath: str, base: str, head: str) -> str:
    """Return diff content for a specific file."""
    ok, out = run_git(["git", "diff", f"{base}...{head}", "--", filepath], repo)
    if not ok:
        ok, out = run_git(["git", "diff", "--cached", "--", filepath], repo)
    return out if ok else ""


def count_diff_lines(diff: str) -> Dict[str, int]:
    """Count added/deleted lines in a diff."""
    additions = sum(1 for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++"))
    deletions = sum(1 for l in diff.splitlines() if l.startswith("-") and not l.startswith("---"))
    return {"additions": additions, "deletions": deletions}


def get_commit_log(repo: Path, base: str, head: str) -> Dict:
    """Analyze commit messages between base and head."""
    ok, out = run_git(["git", "log", "--oneline", f"{base}...{head}"], repo)
    if not ok or not out:
        return {"commits": 0, "issues": []}

    commits = out.splitlines()
    issues = []
    conventional = re.compile(
        r"^(feat|fix|docs|style|refactor|test|chore|perf|ci|build|revert)(\(.+\))?!?:"
    )
    for c in commits:
        msg = c[8:] if len(c) > 8 else c
        if not conventional.match(msg):
            issues.append({"commit": c[:7], "issue": "未遵循 Conventional Commit 格式"})
        if len(msg) > 72:
            issues.append({"commit": c[:7], "issue": "提交信息超过 72 字符"})

    return {"commits": len(commits), "issues": issues}


# ---------------------------------------------------------------------------
# Analysis helpers
# ---------------------------------------------------------------------------

def categorize_file(filepath: str) -> Tuple[str, int, str]:
    """Return (category_key, weight, label) for a file path."""
    lower = filepath.lower()
    for cat, info in FILE_CATEGORIES.items():
        for pat in info["patterns"]:
            if re.search(pat, lower):
                return cat, info["weight"], info["label"]
    return "medium", 2, "MEDIUM"


def scan_risks(diff: str, filepath: str) -> List[Dict]:
    """Scan added lines for risk patterns."""
    added = "\n".join(
        l[1:] for l in diff.splitlines()
        if l.startswith("+") and not l.startswith("+++")
    )
    found = []
    for risk in RISK_PATTERNS:
        matches = re.findall(risk["pattern"], added, re.IGNORECASE)
        if matches:
            found.append({
                "name": risk["name"],
                "severity": risk["severity"],
                "message": risk["message"],
                "file": filepath,
                "count": len(matches),
            })
    return found


def complexity_score(files: List[Dict], risks: List[Dict]) -> int:
    """Score 1-10: higher = more complex / riskier."""
    score = 0
    n = len(files)
    score += 3 if n > 20 else 2 if n > 10 else 1 if n > 5 else 0

    total_changes = sum(f.get("additions", 0) + f.get("deletions", 0) for f in files)
    score += 3 if total_changes > 500 else 2 if total_changes > 200 else 1 if total_changes > 50 else 0

    critical = sum(1 for r in risks if r["severity"] == "critical")
    high = sum(1 for r in risks if r["severity"] == "high")
    score += min(2, critical)
    score += min(2, high)

    return min(10, max(1, score))


def complexity_label(score: int) -> str:
    if score <= 2:
        return "Simple"
    if score <= 4:
        return "Moderate"
    if score <= 6:
        return "Complex"
    if score <= 8:
        return "Very Complex"
    return "Critical"


def review_verdict(score: int, risks: List[Dict]) -> Tuple[str, int]:
    """
    Return (verdict, quality_score 0-100).
    verdict: approve | approve_with_suggestions | request_changes | block
    """
    critical = sum(1 for r in risks if r["severity"] == "critical")
    high = sum(1 for r in risks if r["severity"] == "high")

    # Quality score: start at 100, deduct for complexity and risks
    quality = 100
    quality -= (score - 1) * 4          # complexity penalty
    quality -= critical * 20
    quality -= high * 8
    quality -= sum(1 for r in risks if r["severity"] == "medium") * 3
    quality = max(0, min(100, quality))

    if critical > 0 or quality < 50:
        verdict = "block"
    elif high > 2 or quality < 70:
        verdict = "request_changes"
    elif quality >= 90:
        verdict = "approve"
    else:
        verdict = "approve_with_suggestions"

    return verdict, quality


VERDICT_LABELS = {
    "approve": "✅ APPROVE",
    "approve_with_suggestions": "✅ APPROVE WITH SUGGESTIONS",
    "request_changes": "🟠 REQUEST CHANGES",
    "block": "🚫 BLOCK",
}


# ---------------------------------------------------------------------------
# Branch-aware review policy
# ---------------------------------------------------------------------------

BRANCH_POLICIES = {
    "main":    {"strictness": "strict",   "min_score": 70, "label": "main/master"},
    "master":  {"strictness": "strict",   "min_score": 70, "label": "main/master"},
    "release": {"strictness": "strict",   "min_score": 70, "label": "release/*"},
    "dev":     {"strictness": "standard", "min_score": 60, "label": "dev/develop"},
    "develop": {"strictness": "standard", "min_score": 60, "label": "dev/develop"},
    "hotfix":  {"strictness": "standard", "min_score": 60, "label": "hotfix/* (security-focused)"},
    "feature": {"strictness": "relaxed",  "min_score": 50, "label": "feature/*"},
    "fix":     {"strictness": "standard", "min_score": 60, "label": "fix/*"},
    "chore":   {"strictness": "relaxed",  "min_score": 50, "label": "chore/*"},
}

DEFAULT_POLICY = {"strictness": "standard", "min_score": 60, "label": "unknown"}


def detect_branch_policy(branch: str) -> Dict:
    """Return review policy based on branch name prefix."""
    b = branch.lower().strip()
    for prefix, policy in BRANCH_POLICIES.items():
        if b == prefix or b.startswith(f"{prefix}/") or b.startswith(f"{prefix}-"):
            return {**policy, "branch": branch}
    return {**DEFAULT_POLICY, "branch": branch}


def get_current_branch(repo: Path) -> str:
    ok, out = run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"], repo)
    return out.strip() if ok and out.strip() not in ("HEAD", "") else "unknown"


def apply_branch_policy(verdict: str, quality: int, policy: Dict, risks: List[Dict]) -> Tuple[str, int, List[str]]:
    """
    Adjust verdict based on branch policy strictness.
    Returns (adjusted_verdict, quality, policy_notes).
    """
    notes = []
    min_score = policy["min_score"]
    strictness = policy["strictness"]

    # hotfix branches: escalate security findings
    if "hotfix" in policy.get("branch", "").lower():
        critical_sec = sum(1 for r in risks if r["severity"] == "critical")
        if critical_sec > 0 and verdict not in ("block",):
            verdict = "block"
            notes.append("hotfix 分支发现 critical 安全问题，自动升级为 BLOCK")

    # strict branches: enforce min_score
    if strictness == "strict" and quality < min_score and verdict == "approve_with_suggestions":
        verdict = "request_changes"
        notes.append(f"目标分支 [{policy['label']}] 要求质量分 ≥ {min_score}，当前 {quality}")

    # relaxed branches: downgrade request_changes if only medium/low issues
    if strictness == "relaxed" and verdict == "request_changes":
        has_high_plus = any(r["severity"] in ("critical", "high") for r in risks)
        if not has_high_plus:
            verdict = "approve_with_suggestions"
            notes.append(f"feature 分支无 critical/high 问题，降级为 APPROVE WITH SUGGESTIONS")

    if quality < min_score and verdict == "approve":
        verdict = "approve_with_suggestions"
        notes.append(f"质量分 {quality} 低于 {policy['label']} 最低要求 {min_score}")

    return verdict, quality, notes


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze(repo: Path, base: str = "origin/main", head: str = "HEAD", mr_id: Optional[int] = None, branch: Optional[str] = None) -> Dict:
    changed = get_changed_files(repo, base, head)
    if not changed:
        return {"status": "no_changes", "message": "base と head の間に差分がありません"}

    all_risks: List[Dict] = []
    file_analyses: List[Dict] = []

    for f in changed:
        path = f["path"]
        cat, weight, label = categorize_file(path)
        diff = get_file_diff(repo, path, base, head)
        counts = count_diff_lines(diff)
        risks = scan_risks(diff, path)
        all_risks.extend(risks)
        file_analyses.append({
            "path": path,
            "status": f["status"],
            "category": cat,
            "category_label": label,
            "priority_weight": weight,
            "additions": counts["additions"],
            "deletions": counts["deletions"],
            "risks": risks,
        })

    # Sort highest priority first
    file_analyses.sort(key=lambda x: (-x["priority_weight"], x["path"]))

    commits = get_commit_log(repo, base, head)
    cx_score = complexity_score(file_analyses, all_risks)
    verdict, quality = review_verdict(cx_score, all_risks)

    # Branch-aware policy adjustment
    detected_branch = branch or get_current_branch(repo)
    policy = detect_branch_policy(detected_branch)
    verdict, quality, policy_notes = apply_branch_policy(verdict, quality, policy, all_risks)

    return {
        "status": "analyzed",
        "mr_id": mr_id,
        "branch_policy": {
            "branch": detected_branch,
            "label": policy["label"],
            "strictness": policy["strictness"],
            "min_score": policy["min_score"],
            "notes": policy_notes,
        },
        "summary": {
            "files_changed": len(file_analyses),
            "total_additions": sum(f["additions"] for f in file_analyses),
            "total_deletions": sum(f["deletions"] for f in file_analyses),
            "complexity_score": cx_score,
            "complexity_label": complexity_label(cx_score),
            "quality_score": quality,
            "commits": commits["commits"],
            "verdict": verdict,
            "verdict_label": VERDICT_LABELS[verdict],
        },
        "risks": {
            "critical": [r for r in all_risks if r["severity"] == "critical"],
            "high":     [r for r in all_risks if r["severity"] == "high"],
            "medium":   [r for r in all_risks if r["severity"] == "medium"],
            "low":      [r for r in all_risks if r["severity"] == "low"],
        },
        "files": file_analyses,
        "commit_issues": commits["issues"],
        "review_order": [f["path"] for f in file_analyses[:10]],
    }


# ---------------------------------------------------------------------------
# Report formatting
# ---------------------------------------------------------------------------

def print_report(result: Dict) -> None:
    if result["status"] == "no_changes":
        print(result["message"])
        return

    s = result["summary"]
    r = result["risks"]
    bp = result.get("branch_policy", {})
    mr_tag = f" — MR #{result['mr_id']}" if result.get("mr_id") else ""

    sep = "=" * 60
    print(sep)
    print(f"MR ANALYSIS REPORT{mr_tag}")
    print(sep)

    if bp:
        print(f"\n目标分支 : {bp.get('branch', '?')} [{bp.get('label', '?')}]  严格程度: {bp.get('strictness', '?')}  最低分要求: {bp.get('min_score', '?')}")
        for note in bp.get("notes", []):
            print(f"  ⚠️  {note}")

    print(f"\n复杂度 : {s['complexity_score']}/10 ({s['complexity_label']})")
    print(f"变更文件 : {s['files_changed']}")
    print(f"代码行   : +{s['total_additions']} / -{s['total_deletions']}")
    print(f"提交数   : {s['commits']}")

    print("\n--- 风险摘要 ---")
    print(f"  Critical : {len(r['critical'])}")
    print(f"  High     : {len(r['high'])}")
    print(f"  Medium   : {len(r['medium'])}")
    print(f"  Low      : {len(r['low'])}")

    if r["critical"]:
        print("\n--- Critical 风险 ---")
        for risk in r["critical"]:
            print(f"  [{risk['file']}] {risk['message']} (×{risk['count']})")

    if r["high"]:
        print("\n--- High 风险 ---")
        for risk in r["high"]:
            print(f"  [{risk['file']}] {risk['message']} (×{risk['count']})")

    if result["commit_issues"]:
        print("\n--- 提交信息问题 ---")
        for issue in result["commit_issues"][:5]:
            print(f"  {issue['commit']}: {issue['issue']}")

    print("\n--- 建议审核顺序 ---")
    for i, path in enumerate(result["review_order"], 1):
        info = next(f for f in result["files"] if f["path"] == path)
        print(f"  {i:2d}. [{info['category_label']:8s}] {path}")

    print(f"\n--- 审核结论 ---")
    print(f"  {s['verdict_label']}  (质量评分: {s['quality_score']}/100)")

    print("\n" + sep)


def build_gitlab_comment(result: Dict) -> str:
    """Build a Markdown comment suitable for glab mr note --message."""
    if result["status"] == "no_changes":
        return "暂无变更。"

    s = result["summary"]
    r = result["risks"]
    bp = result.get("branch_policy", {})
    mr_tag = f"MR #{result['mr_id']}" if result.get("mr_id") else "本次 MR"

    lines = [
        f"## {s['verdict_label']} — 代码审核摘要 ({mr_tag})",
        "",
        f"**复杂度:** {s['complexity_score']}/10 ({s['complexity_label']})  "
        f"**质量评分:** {s['quality_score']}/100",
        f"**变更文件:** {s['files_changed']}  "
        f"**新增行:** +{s['total_additions']}  "
        f"**删除行:** -{s['total_deletions']}",
        "",
    ]

    if bp:
        strictness_emoji = {"strict": "🔒", "standard": "📋", "relaxed": "🔓"}.get(bp.get("strictness", ""), "📋")
        lines.append(f"**目标分支:** {bp.get('branch', '?')} — {strictness_emoji} {bp.get('label', '')}  *(最低分: {bp.get('min_score', '?')})*")
        for note in bp.get("notes", []):
            lines.append(f"> ⚠️ {note}")
        lines.append("")

    lines += [
        "### 风险摘要",
        "",
        "| 级别 | 数量 |",
        "|------|------|",
        f"| 🔴 Critical | {len(r['critical'])} |",
        f"| 🟠 High     | {len(r['high'])} |",
        f"| 🟡 Medium   | {len(r['medium'])} |",
        f"| 🟢 Low      | {len(r['low'])} |",
        "",
    ]

    if r["critical"]:
        lines.append("### 🔴 Critical 问题")
        lines.append("")
        for risk in r["critical"]:
            lines.append(f"- **`{risk['file']}`** — {risk['message']} (×{risk['count']})")
        lines.append("")

    if r["high"]:
        lines.append("### 🟠 High 问题")
        lines.append("")
        for risk in r["high"]:
            lines.append(f"- **`{risk['file']}`** — {risk['message']} (×{risk['count']})")
        lines.append("")

    lines.append("### 建议审核顺序")
    lines.append("")
    for i, path in enumerate(result["review_order"], 1):
        info = next(f for f in result["files"] if f["path"] == path)
        lines.append(f"{i}. `{path}` [{info['category_label']}]")

    lines.append("")
    lines.append("> *由 GitLab MR Reviewer 自动生成*")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a GitLab MR branch for review")
    parser.add_argument("repo_path", nargs="?", default=".", help="Path to git repo (default: .)")
    parser.add_argument("--context-file", help="JSON config path (default: ../reviewer.config.json)")
    parser.add_argument("--base", "-b", help="Base ref (default from config/env: origin/<defaultBaseBranch>)")
    parser.add_argument("--head", default="HEAD", help="Head ref (default: HEAD)")
    parser.add_argument("--mr-id", type=int, help="MR ID for display purposes")
    parser.add_argument("--branch", help="MR source branch name for policy detection (auto-detected if omitted)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--gitlab-comment", action="store_true", help="Output GitLab Markdown comment")
    parser.add_argument("--output", "-o", help="Write output to file")
    args = parser.parse_args()
    cfg = load_context_config(args.context_file)

    repo_path = args.repo_path
    cfg_repo = get_config_value(cfg, "review.repoPath")
    if repo_path in (None, "", ".") and cfg_repo:
        repo_path = cfg_repo

    raw_base = resolve_value(
        args.base,
        get_config_value(cfg, "gitlab.defaultBaseBranch"),
        "GITLAB_DEFAULT_BASE_BRANCH",
        "main",
    )
    base_ref = raw_base if "/" in raw_base else f"origin/{raw_base}"

    repo = Path(os.path.expanduser(repo_path)).resolve()
    if not (repo / ".git").exists():
        print(f"Error: {repo} is not a git repository", file=sys.stderr)
        sys.exit(1)

    result = analyze(repo, base_ref, args.head, args.mr_id, args.branch)

    if args.json:
        text = json.dumps(result, indent=2, ensure_ascii=False)
    elif args.gitlab_comment:
        text = build_gitlab_comment(result)
    else:
        print_report(result)
        return

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"结果已写入 {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()
