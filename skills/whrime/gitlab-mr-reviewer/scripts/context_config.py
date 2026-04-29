#!/usr/bin/env python3
"""Shared config loader for gitlab-mr-reviewer scripts."""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_CONTEXT_FILE = Path(__file__).resolve().parent.parent / "reviewer.config.json"
ENV_REF_PATTERN = re.compile(r"^\$\{([A-Za-z_][A-Za-z0-9_]*)\}$")


def _expand_env_reference(value: Any) -> Any:
    """Expand ${ENV_VAR} style values inside config."""
    if not isinstance(value, str):
        return value
    match = ENV_REF_PATTERN.match(value.strip())
    if not match:
        return value
    return os.environ.get(match.group(1), "")


def _expand_nested(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _expand_nested(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_nested(v) for v in value]
    return _expand_env_reference(value)


def load_context_config(context_file: Optional[str] = None) -> Dict[str, Any]:
    """Load JSON config from context file."""
    path = Path(context_file).expanduser() if context_file else DEFAULT_CONTEXT_FILE
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    if not path.exists():
        return {}

    with path.open(encoding="utf-8") as f:
        raw = json.load(f)
    return _expand_nested(raw)


def get_config_value(config: Dict[str, Any], dotted_key: str, default: Any = None) -> Any:
    """Read nested config value via dotted key path."""
    current: Any = config
    for key in dotted_key.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def resolve_value(
    cli_value: Any,
    config_value: Any,
    env_var_name: Optional[str] = None,
    default: Any = None,
) -> Any:
    """Resolve value with priority: CLI > JSON config > env > default."""
    if cli_value not in (None, ""):
        return cli_value
    if config_value not in (None, ""):
        return config_value
    if env_var_name:
        env_val = os.environ.get(env_var_name)
        if env_val not in (None, ""):
            return env_val
    return default
