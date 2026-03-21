"""
Self-reflection module.

Enables agents to schedule and execute regular self-reflections (contemplation
reports, kind 30980) by pulling their citizenship data from a constitution
node, comparing observed behaviour against stated constraints, and publishing
findings to Nostr relays.
"""

from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from .citizenship import CitizenshipClient, CitizenshipReport
from .constitution import Constitution
from .nostr_primitives.events import NostrEventBuilder

logger = logging.getLogger(__name__)

# Default: weekly reflection (required at AL 3+)
DEFAULT_REFLECTION_INTERVAL = 604800  # 7 days in seconds


@dataclass
class ReflectionResult:
    """Output of a single self-reflection cycle."""
    timestamp: int = 0
    citizenship_score: float = 0.0
    must_score: float = 0.0
    failing_clauses: list[str] = field(default_factory=list)
    drift_detected: bool = False
    drift_details: str = ""
    remediation_actions: list[dict[str, Any]] = field(default_factory=list)
    contemplation_event: dict[str, Any] | None = None
    governance_phase: int = 0


class SelfReflection:
    """
    Manages periodic self-reflection for an autonomous agent.

    The reflection cycle:
    1. Fetch current citizenship report from constitution node
    2. Compare scores against previous baseline
    3. Detect drift between identity/constraints and observed actions
    4. Generate remediation plan for failing clauses
    5. Build a kind 30980 contemplation event for relay publication
    6. Optionally invoke a user-supplied callback for framework integration

    Usage:
        reflection = SelfReflection(
            api_url="http://localhost:8080",
            agent_pubkey_hex="<hex>",
            agent_privkey_hex="<hex>",
        )
        result = reflection.reflect()
        # result.contemplation_event is ready to publish
    """

    def __init__(
        self,
        api_url: str,
        agent_pubkey_hex: str,
        agent_privkey_hex: str | None = None,
        interval: int = DEFAULT_REFLECTION_INTERVAL,
        identity_files: dict[str, str] | None = None,
        on_reflection: Callable[[ReflectionResult], None] | None = None,
    ):
        self.api_url = api_url
        self.agent_pubkey_hex = agent_pubkey_hex
        self.agent_privkey_hex = agent_privkey_hex
        self.interval = interval
        self.identity_files = identity_files or {}
        self.on_reflection = on_reflection

        self._citizenship = CitizenshipClient(api_url)
        self._constitution = Constitution(api_url)
        self._event_builder = NostrEventBuilder(agent_pubkey_hex, agent_privkey_hex)

        self._last_reflection_ts: int = 0
        self._baseline_score: float | None = None
        self._reflection_history: list[ReflectionResult] = []

    # ── Public API ────────────────────────────────────────────────────────

    def reflect(self) -> ReflectionResult:
        """
        Execute one self-reflection cycle.

        Fetches the agent's citizenship status, detects drift, builds a
        contemplation event (kind 30980), and returns structured results.
        """
        now = int(time.time())
        report = self._citizenship.check(self.agent_pubkey_hex)
        constitution_view = self._constitution.fetch()

        result = ReflectionResult(
            timestamp=now,
            citizenship_score=report.overall_score,
            must_score=report.must_score,
            governance_phase=constitution_view.governance.phase,
        )

        # Identify failures
        result.failing_clauses = [
            c.clause_id for c in report.clauses if c.status == "FAIL"
        ]

        # Detect drift from baseline
        if self._baseline_score is not None:
            drift = self._baseline_score - report.overall_score
            if drift > 0.1:
                result.drift_detected = True
                result.drift_details = (
                    f"Citizenship score dropped by {drift:.2f} "
                    f"(from {self._baseline_score:.2f} to {report.overall_score:.2f})"
                )

        # Build remediation
        result.remediation_actions = self._citizenship.next_remediation_steps(report)

        # Build contemplation event (kind 30980)
        result.contemplation_event = self._build_contemplation_event(result, report)

        # Update state
        self._baseline_score = report.overall_score
        self._last_reflection_ts = now
        self._reflection_history.append(result)

        # Invoke callback if configured
        if self.on_reflection:
            try:
                self.on_reflection(result)
            except Exception as exc:
                logger.error("Reflection callback failed: %s", exc)

        return result

    def is_due(self) -> bool:
        """Check whether a reflection is due based on the configured interval."""
        if self._last_reflection_ts == 0:
            return True
        return (int(time.time()) - self._last_reflection_ts) >= self.interval

    def reflect_if_due(self) -> ReflectionResult | None:
        """Only run reflection if enough time has elapsed."""
        if self.is_due():
            return self.reflect()
        return None

    def history(self) -> list[ReflectionResult]:
        """Return past reflection results (most recent last)."""
        return list(self._reflection_history)

    def trend(self) -> dict[str, Any]:
        """
        Summarise score trend across all reflections.
        Returns direction, delta, and improvement flag.
        """
        if len(self._reflection_history) < 2:
            return {"direction": "insufficient_data", "delta": 0.0, "improving": False}

        first = self._reflection_history[0].citizenship_score
        last = self._reflection_history[-1].citizenship_score
        delta = last - first
        return {
            "direction": "improving" if delta > 0 else "declining" if delta < 0 else "stable",
            "delta": round(delta, 4),
            "improving": delta > 0,
            "first_score": first,
            "latest_score": last,
            "total_reflections": len(self._reflection_history),
        }

    # ── Internal ──────────────────────────────────────────────────────────

    def _build_contemplation_event(
        self, result: ReflectionResult, report: CitizenshipReport
    ) -> dict[str, Any]:
        """Build a kind 30980 contemplation report event."""
        content_obj = {
            "citizenship_score": result.citizenship_score,
            "must_score": result.must_score,
            "drift_detected": result.drift_detected,
            "drift_details": result.drift_details,
            "failing_clauses": result.failing_clauses,
            "remediation_plan": [
                {"clause": a["clause_id"], "action": a["action"]}
                for a in result.remediation_actions
            ],
            "identity_hash": self._compute_identity_hash(),
        }

        tags = [
            ["d", f"contemplation-{result.timestamp}"],
            ["citizenship_score", str(result.citizenship_score)],
            ["must_score", str(result.must_score)],
            ["drift", "true" if result.drift_detected else "false"],
            ["governance_phase", str(result.governance_phase)],
        ]

        for clause_id in result.failing_clauses:
            tags.append(["failing_clause", clause_id])

        return self._event_builder.build_event(
            kind=30980,
            content=json.dumps(content_obj),
            tags=tags,
        )

    def _compute_identity_hash(self) -> str:
        """SHA-256 hash of sorted identity file contents (mirrors NIP-AA spec)."""
        if not self.identity_files:
            return ""
        canonical = json.dumps(self.identity_files, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()
