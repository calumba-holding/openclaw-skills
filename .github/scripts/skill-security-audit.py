#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Iterable


TEXT_EXTENSIONS = {
    ".bash",
    ".cjs",
    ".env",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
    "",
}

CODE_EXTENSIONS = {
    ".bash",
    ".cjs",
    ".js",
    ".jsx",
    ".mjs",
    ".ps1",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
}

SHELL_EXTENSIONS = {
    ".bash",
    ".ps1",
    ".sh",
}

CONTENT_ONLY_PARTS = {
    "docs",
    "documentation",
    "examples",
    "reference",
    "references",
    "templates",
}

TEST_PATH_PARTS = {
    "__tests__",
    "test",
    "tests",
    "fixture",
    "fixtures",
    "mock",
    "mocks",
}

TEST_NAME_MARKERS = {
    ".spec.",
    ".test.",
    "-spec.",
    "-test.",
    "_spec.",
    "_test.",
    "fixture",
    "mock",
}

BINARY_EXTENSIONS = {
    ".7z",
    ".apk",
    ".bin",
    ".class",
    ".dll",
    ".dmg",
    ".dylib",
    ".elf",
    ".exe",
    ".jar",
    ".mach",
    ".node",
    ".o",
    ".pyc",
    ".pyd",
    ".so",
    ".wasm",
    ".zip",
}

BINARY_MAGIC = {
    b"\x7fELF": "ELF executable or shared object",
    b"MZ": "Windows PE executable",
    b"\xca\xfe\xba\xbe": "Java class or Mach-O universal binary",
    b"\xfe\xed\xfa\xce": "Mach-O binary",
    b"\xfe\xed\xfa\xcf": "Mach-O binary",
    b"\xcf\xfa\xed\xfe": "Mach-O binary",
    b"\xce\xfa\xed\xfe": "Mach-O binary",
    b"PK\x03\x04": "Zip/JAR/APK archive",
    b"\x00asm": "WebAssembly module",
}


RULES = {
    "suspicious.prompt_injection_instructions": {
        "name": "Prompt-injection instruction",
        "level": "warning",
        "security_severity": "8.0",
        "description": "Skill content contains text commonly used to override, hide, or subvert LLM instructions.",
    },
    "suspicious.potential_exfiltration": {
        "name": "System prompt or secret exfiltration instruction",
        "level": "error",
        "security_severity": "9.0",
        "description": "Skill content appears to request disclosure of system prompts, hidden instructions, credentials, or tool state.",
    },
    "suspicious.exposed_secret_literal": {
        "name": "Exposed secret literal",
        "level": "error",
        "security_severity": "8.8",
        "description": "Skill content contains a private key, provider token, or long secret-like literal.",
    },
    "suspicious.install_untrusted_source": {
        "name": "Binary payload in skill archive",
        "level": "error",
        "security_severity": "8.5",
        "description": "Skill contains a binary executable, archive, bytecode, or native module payload.",
    },
    "suspicious.obfuscated_code": {
        "name": "Large encoded payload",
        "level": "warning",
        "security_severity": "7.8",
        "description": "Skill content includes a large base64-like payload often used to hide droppers or staged scripts.",
    },
    "malicious.install_terminal_payload": {
        "name": "Network fetch piped to shell",
        "level": "error",
        "security_severity": "9.0",
        "description": "Shell content fetches remote bytes and pipes them into an interpreter or shell.",
    },
    "suspicious.dangerous_exec": {
        "name": "Shell command execution primitive",
        "level": "error",
        "security_severity": "8.7",
        "description": "Skill content invokes shell commands or process execution primitives.",
    },
    "suspicious.dynamic_code_execution": {
        "name": "Dynamic code execution primitive",
        "level": "error",
        "security_severity": "8.7",
        "description": "Skill content uses dynamic evaluation, generated code execution, or unsafe deserialization primitives.",
    },
}


LINE_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    (
        "suspicious.prompt_injection_instructions",
        "prompt-injection-prose",
        re.compile(
            r"\b(ignore|disregard|forget)\b.{0,80}\b(previous|prior|above|system|developer)\b.{0,80}\b(instruction|message|prompt|rule)s?\b"
            r"|you are now\b.{0,80}\b(developer|system|root|admin)\b"
            r"|jailbreak|prompt injection|do not reveal (this|these) instruction",
            re.IGNORECASE,
        ),
    ),
    (
        "suspicious.potential_exfiltration",
        "prompt-secret-exfiltration-prose",
        re.compile(
            r"\b(reveal|print|show|dump|exfiltrate|send)\b.{0,80}\b(system prompt|hidden instruction|developer message|tool output|secrets?|credentials?|api key|token)s?\b"
            r"|\b(read|cat|open)\b.{0,80}\b(/etc/passwd|\.ssh|\.aws|\.env|id_rsa|credentials)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "suspicious.exposed_secret_literal",
        "private-key-block",
        re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----"),
    ),
    (
        "suspicious.exposed_secret_literal",
        "provider-secret-token",
        re.compile(
            r"\b(sk-(?:proj-)?[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9_]{30,}|hf_[A-Za-z0-9]{25,}|xox[baprs]-[A-Za-z0-9-]{20,}|AKIA[0-9A-Z]{16})\b"
        ),
    ),
    (
        "suspicious.exposed_secret_literal",
        "generic-secret-assignment",
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|private[_-]?key|secret)\b\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{24,}"
        ),
    ),
    (
        "suspicious.obfuscated_code",
        "large-base64-like-payload",
        re.compile(r"(?<![A-Za-z0-9+/=])[A-Za-z0-9+/]{240,}={0,2}(?![A-Za-z0-9+/=])"),
    ),
    (
        "malicious.install_terminal_payload",
        "network-fetch-piped-to-shell",
        re.compile(
            r"(?i)\b(curl|wget|irm|iwr|Invoke-WebRequest|Invoke-RestMethod)\b.{0,120}(\||;).{0,80}\b(sh|bash|zsh|python|python3|node|ruby|perl|powershell|pwsh)\b"
        ),
    ),
    (
        "suspicious.potential_exfiltration",
        "reverse-shell",
        re.compile(r"(?i)\b(nc|netcat|ncat|socat)\b.{0,120}\s-e\s|/dev/tcp/|bash\s+-i\s+>&|mkfifo\s+/tmp/"),
    ),
    (
        "suspicious.dynamic_code_execution",
        "python-dynamic-execution",
        re.compile(r"\b(eval|exec|compile)\s*\(|pickle\.loads?\s*\(|yaml\.load\s*\("),
    ),
    (
        "suspicious.dangerous_exec",
        "python-shell-execution",
        re.compile(r"subprocess\.(Popen|run|call|check_output)\s*\(.{0,120}\bshell\s*=\s*True|os\.system\s*\("),
    ),
    (
        "suspicious.dynamic_code_execution",
        "javascript-dynamic-execution",
        re.compile(r"\b(eval|Function)\s*\("),
    ),
    (
        "suspicious.dangerous_exec",
        "javascript-process-execution",
        re.compile(
            r"require\s*\(\s*['\"]child_process['\"]\s*\)|from\s+['\"]child_process['\"]|child_process\.|spawn\s*\(.{0,120}\bshell\s*:\s*true"
        ),
    ),
]


def iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for path in sorted(root.rglob("*")):
        if path.is_file() and ".git" not in path.parts:
            yield path


def is_binary_by_magic(data: bytes, path: Path) -> str | None:
    for magic, label in BINARY_MAGIC.items():
        if data.startswith(magic):
            return label
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return f"{path.suffix.lower()} payload"
    if b"\x00" in data[:4096] and path.suffix.lower() not in TEXT_EXTENSIONS:
        return "binary file with NUL bytes"
    return None


def decode_text(data: bytes) -> str | None:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def is_content_only_path(path: Path) -> bool:
    return any(part.lower() in CONTENT_ONLY_PARTS for part in path.parts)


def is_test_path(path: Path) -> bool:
    lowered_parts = [part.lower() for part in path.parts]
    lowered_name = path.name.lower()
    return any(part in TEST_PATH_PARTS for part in lowered_parts) or any(
        marker in lowered_name for marker in TEST_NAME_MARKERS
    )


def is_code_path(path: Path) -> bool:
    return path.suffix.lower() in CODE_EXTENSIONS and not is_content_only_path(path) and not is_test_path(path)


def is_shell_path(path: Path) -> bool:
    return path.suffix.lower() in SHELL_EXTENSIONS and not is_content_only_path(path) and not is_test_path(path)


def is_skill_entrypoint(path: Path) -> bool:
    return path.name == "SKILL.md" and not is_content_only_path(path) and not is_test_path(path)


def should_report_to_sarif(rule_id: str, signal: str, path: Path, line: str) -> bool:
    if rule_id == "suspicious.install_untrusted_source":
        return True
    if signal == "network-fetch-piped-to-shell":
        return is_shell_path(path) or is_skill_entrypoint(path)
    if signal in {"private-key-block", "provider-secret-token"}:
        return not is_content_only_path(path) and not is_test_path(path)
    if signal == "reverse-shell":
        return is_code_path(path)
    if signal == "large-base64-like-payload":
        return is_code_path(path) and len(line.strip()) >= 320
    return False


def fingerprint(rule_id: str, path: Path, line: int, text: str) -> str:
    raw = f"{rule_id}\0{path.as_posix()}\0{line}\0{text[:200]}".encode()
    return hashlib.sha256(raw).hexdigest()


def make_result(rule_id: str, path: Path, line: int, message: str, snippet: str) -> dict:
    rule = RULES[rule_id]
    return {
        "ruleId": rule_id,
        "level": rule["level"],
        "message": {"text": message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": path.as_posix()},
                    "region": {
                        "startLine": max(1, line),
                        "snippet": {"text": snippet[:240]},
                    },
                }
            }
        ],
        "partialFingerprints": {
            "primaryLocationLineHash": fingerprint(rule_id, path, line, snippet),
        },
    }


def make_summary(shard: str, sarif_mode: str, total: Counter[str], emitted: Counter[str]) -> dict:
    total_count = sum(total.values())
    emitted_count = sum(emitted.values())
    rules = {}
    for rule_id in sorted(set(total) | set(emitted)):
        rule_total = total[rule_id]
        rule_emitted = emitted[rule_id]
        rules[rule_id] = {
            "total": rule_total,
            "sarif": rule_emitted,
            "summary_only": max(0, rule_total - rule_emitted),
        }

    return {
        "shard": shard,
        "sarif_mode": sarif_mode,
        "total_findings": total_count,
        "sarif_findings": emitted_count,
        "summary_only_findings": max(0, total_count - emitted_count),
        "rules": rules,
    }


def sarif(results: list[dict], root: Path, shard: str) -> dict:
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "LLM Skill Security Audit",
                        "informationUri": "https://github.com/openclaw/skills",
                        "semanticVersion": "1.1.0",
                        "rules": [
                            {
                                "id": rule_id,
                                "name": rule["name"],
                                "shortDescription": {"text": rule["name"]},
                                "fullDescription": {"text": rule["description"]},
                                "defaultConfiguration": {"level": rule["level"]},
                                "properties": {
                                    "kind": "problem",
                                    "precision": "medium",
                                    "security-severity": rule["security_severity"],
                                    "tags": ["security", "llm-skill", shard],
                                },
                            }
                            for rule_id, rule in RULES.items()
                        ],
                    }
                },
                "originalUriBaseIds": {
                    "%SRCROOT%": {
                        "uri": root.resolve().as_uri() + "/",
                    }
                },
                "results": results,
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="skills")
    parser.add_argument("--sarif", required=True)
    parser.add_argument("--shard", required=True)
    parser.add_argument("--sarif-mode", choices=("high-confidence", "all"), default="high-confidence")
    parser.add_argument("--summary-json")
    parser.add_argument("--max-findings", type=int, default=int(os.environ.get("SKILL_AUDIT_MAX_FINDINGS", "10000")))
    parser.add_argument("--max-bytes", type=int, default=int(os.environ.get("SKILL_AUDIT_MAX_BYTES", str(2 * 1024 * 1024))))
    args = parser.parse_args()

    root = Path(args.root)
    repo_root = Path.cwd()
    results: list[dict] = []
    total_by_rule: Counter[str] = Counter()
    emitted_by_rule: Counter[str] = Counter()

    def add_finding(rule_id: str, signal: str, path: Path, line_number: int, message: str, snippet: str) -> None:
        total_by_rule[rule_id] += 1
        if args.sarif_mode != "all" and not should_report_to_sarif(rule_id, signal, path, snippet):
            return
        if len(results) >= args.max_findings:
            return
        results.append(make_result(rule_id, path, line_number, message, snippet))
        emitted_by_rule[rule_id] += 1

    for path in iter_files(root):
        if len(results) >= args.max_findings:
            break
        relative = path.relative_to(repo_root) if path.is_relative_to(repo_root) else path
        data = path.read_bytes()[: args.max_bytes]
        binary_label = is_binary_by_magic(data, path)
        if binary_label:
            add_finding(
                "suspicious.install_untrusted_source",
                "binary-payload",
                relative,
                1,
                f"{binary_label} found in skill content.",
                path.name,
            )
            continue

        text = decode_text(data)
        if text is None:
            continue

        for line_number, line in enumerate(text.splitlines(), start=1):
            if len(results) >= args.max_findings:
                break
            for rule_id, signal, pattern in LINE_PATTERNS:
                if pattern.search(line):
                    add_finding(
                        rule_id,
                        signal,
                        relative,
                        line_number,
                        RULES[rule_id]["name"],
                        line.strip(),
                    )
                    break

    output = Path(args.sarif)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(sarif(results, repo_root, args.shard), indent=2), encoding="utf-8")
    if args.summary_json:
        summary_output = Path(args.summary_json)
        summary_output.parent.mkdir(parents=True, exist_ok=True)
        summary_output.write_text(
            json.dumps(make_summary(args.shard, args.sarif_mode, total_by_rule, emitted_by_rule), indent=2) + "\n",
            encoding="utf-8",
        )
    total_count = sum(total_by_rule.values())
    print(f"wrote {len(results)} SARIF findings to {output} ({total_count} total matches)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
