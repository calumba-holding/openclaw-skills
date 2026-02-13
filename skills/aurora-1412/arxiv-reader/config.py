"""
Global configuration module.
Loads all settings from .env file at project root.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Project Root ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
load_dotenv(PROJECT_ROOT / ".env")

# ── LLM ──────────────────────────────────────────────────────
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "16000"))

# ── ArXiv ────────────────────────────────────────────────────
ARXIV_CATEGORIES = [
    c.strip()
    for c in os.getenv("ARXIV_CATEGORIES", "cs.AI,cs.LG,cs.CL,cs.CV").split(",")
]
ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "500"))

# ── Fetch Stop Condition ─────────────────────────────────────
FETCH_LOOKBACK_DAYS = int(os.getenv("FETCH_LOOKBACK_DAYS", "1"))

# ── Skills ───────────────────────────────────────────────────
SKILLS_DIR = PROJECT_ROOT / "skills"
