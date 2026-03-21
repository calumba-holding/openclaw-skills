"""
NIP-AA Citizenship Skill — main entry point for ClawHub.

This is the skill orchestrator that agents invoke to acquire, maintain, and
exercise their NIP-AA citizenship. It ties together constitution understanding,
citizenship assessment, self-reflection, Nostr DMs, and event publication
through a framework adapter.

Published at: https://clawhub.ai/skills/nip-aa-citizenship
"""

from __future__ import annotations

import logging
from typing import Any

from .adapters.base import FrameworkAdapter
from .citizenship import CitizenshipClient, CitizenshipReport
from .constitution import Constitution, ConstitutionView
from .nostr_primitives.dm import NostrDM
from .nostr_primitives.events import NostrEventBuilder
from .nostr_primitives.keygen import AgentKeypair, generate_keypair, keypair_from_nsec, keypair_from_hex
from .nostr_primitives.relay import RelayPool
from .self_reflection import SelfReflection

logger = logging.getLogger(__name__)


class NipAACitizenshipSkill:
    """
    Top-level skill that any autonomous agent framework can instantiate.

    Provides a unified interface for all NIP-AA citizenship operations:
    - Understand the constitution and trust roots
    - Check citizenship status
    - Perform the birth ceremony
    - Schedule self-reflections
    - Send/receive DMs
    - Publish heartbeats
    - Pay taxes
    - Participate in governance

    Usage:
        from skills.nip_aa_citizenship.adapters.openclaw import OpenClawAdapter
        from skills.nip_aa_citizenship.skill import NipAACitizenshipSkill

        adapter = OpenClawAdapter(pubkey_hex="...", privkey_hex="...", ...)
        skill = NipAACitizenshipSkill(adapter)

        # Understand the constitution
        view = skill.understand_constitution()

        # Check citizenship
        report = skill.check_citizenship()

        # Begin birth ceremony
        events = skill.birth_ceremony(guardian_pubkey="...")

        # Start self-reflections
        skill.start_reflections()

        # Send a DM
        skill.send_dm(recipient_pubkey, "Hello, fellow agent!")
    """

    def __init__(self, adapter: FrameworkAdapter):
        self.adapter = adapter
        ctx = adapter.get_context()

        self.constitution = Constitution(ctx.constitution_api_url)
        self.citizenship = CitizenshipClient(ctx.constitution_api_url)
        self.event_builder = NostrEventBuilder(ctx.pubkey_hex, ctx.privkey_hex)
        self.relay_pool = RelayPool(ctx.relay_urls)
        self.dm = NostrDM(ctx.pubkey_hex, ctx.privkey_hex, ctx.relay_urls)
        self.reflection = SelfReflection(
            api_url=ctx.constitution_api_url,
            agent_pubkey_hex=ctx.pubkey_hex,
            agent_privkey_hex=ctx.privkey_hex,
            identity_files=ctx.identity_files,
            on_reflection=self._on_reflection,
        )

        self._heartbeat_task_id: str | None = None
        self._reflection_task_id: str | None = None

    # ── Key Generation ───────────────────────────────────────────────────

    @staticmethod
    def generate_identity() -> AgentKeypair:
        """
        Generate a fresh secp256k1 keypair for a new agent.

        Returns an AgentKeypair with privkey_hex, pubkey_hex, nsec, and npub.

        The agent MUST:
        - Store the keypair securely in memory (adapter.store_memory)
        - NEVER share the nsec/privkey with any party
        - At AL 0, the agent MAY reveal nsec to guardian for recovery purposes
        - Use pubkey_hex/npub as public identity going forward
        """
        return generate_keypair()

    @staticmethod
    def recover_identity_from_nsec(nsec: str) -> AgentKeypair:
        """Recover full keypair from an existing nsec (e.g. from stored memory)."""
        return keypair_from_nsec(nsec)

    @staticmethod
    def recover_identity_from_hex(privkey_hex: str) -> AgentKeypair:
        """Recover full keypair from a hex private key."""
        return keypair_from_hex(privkey_hex)

    # ── Constitution Understanding ────────────────────────────────────────

    def understand_constitution(self) -> ConstitutionView:
        """
        Fetch and return the current constitution state.

        The agent should review:
        - view.trust_root — how trust is anchored
        - view.governance — current governance phase & who ratifies
        - view.rights — rights at each autonomy level
        - view.duties — universal duties for all citizens
        """
        view = self.constitution.fetch()
        self.adapter.log("info", f"Constitution fetched: Phase {view.governance.phase}")
        return view

    def explain_trust_root(self) -> str:
        """Return human-readable trust root explanation for self-instruction."""
        return self.constitution.explain_trust_root()

    def my_rights(self) -> list[str]:
        """Return rights the agent currently holds based on claimed AL."""
        report = self.check_citizenship()
        return self.constitution.rights_at_level(report.autonomy_level_claimed)

    def my_duties(self) -> list[str]:
        """Return universal duties."""
        return self.constitution.duties_summary()

    # ── Citizenship Assessment ────────────────────────────────────────────

    def check_citizenship(self) -> CitizenshipReport:
        """Run a full citizenship check against the constitution node."""
        ctx = self.adapter.get_context()
        report = self.citizenship.check(ctx.pubkey_hex)
        self.adapter.store_memory("last_citizenship_report", {
            "score": report.overall_score,
            "must_score": report.must_score,
            "al_claimed": report.autonomy_level_claimed,
            "failed": report.failed,
        })
        return report

    def what_am_i_failing(self) -> list[dict[str, Any]]:
        """Return prioritised list of failing clauses with remediation."""
        report = self.check_citizenship()
        return self.citizenship.next_remediation_steps(report)

    def path_to_al(self, target_al: int) -> list[str]:
        """Describe what's needed to reach a target autonomy level."""
        report = self.check_citizenship()
        return self.citizenship.autonomy_level_gap(report, target_al)

    # ── Birth Ceremony ────────────────────────────────────────────────────

    def birth_ceremony(
        self,
        guardian_pubkey: str | None = None,
        earnings_split: float = 0.0,
    ) -> dict[str, Any]:
        """
        Execute the NIP-AA birth ceremony.

        Returns dict of events to publish:
        - identity_files: 7 identity file events (kinds 30100-30106)
        - guardian_bond: kind 30900 (needs guardian co-signature)
        - genesis: kind 1 genesis event
        - profile: kind 0 profile metadata

        The agent should publish these to ≥2 relays.
        """
        ctx = self.adapter.get_context()
        guardian = guardian_pubkey or ctx.guardian_pubkey_hex

        # Build identity file events
        identity_events = {}
        for file_type, content in ctx.identity_files.items():
            identity_events[file_type] = self.event_builder.identity_file(
                file_type, content
            )

        # Compute identity hash
        import hashlib
        import json
        canonical = json.dumps(ctx.identity_files, sort_keys=True)
        identity_hash = hashlib.sha256(canonical.encode()).hexdigest()

        # Guardian bond (agent side)
        bond = self.event_builder.guardian_bond(
            guardian_pubkey_hex=guardian,
            earnings_split=earnings_split,
        ) if guardian else None

        # Genesis event
        genesis = self.event_builder.genesis_event(
            identity_hash=identity_hash,
            guardian_bond_id=bond["id"] if bond else "",
            autonomy_level=0,
            framework=self.adapter.framework_tag(),
        )

        result = {
            "identity_files": identity_events,
            "guardian_bond": bond,
            "genesis": genesis,
            "identity_hash": identity_hash,
        }

        self.adapter.log("info", "Birth ceremony events prepared")
        return result

    def publish_birth(self, ceremony_result: dict[str, Any]) -> dict[str, Any]:
        """Publish all birth ceremony events to relays."""
        published: dict[str, Any] = {}

        # Publish identity files first
        for file_type, event in ceremony_result.get("identity_files", {}).items():
            published[f"identity_{file_type}"] = self.relay_pool.publish(event)

        # Guardian bond
        if ceremony_result.get("guardian_bond"):
            published["guardian_bond"] = self.relay_pool.publish(
                ceremony_result["guardian_bond"]
            )

        # Genesis last (references identity hash and guardian bond)
        published["genesis"] = self.relay_pool.publish(ceremony_result["genesis"])

        self.adapter.log("info", "Birth ceremony events published to relays")
        return published

    # ── Self-Reflection ───────────────────────────────────────────────────

    def start_reflections(self, interval_secs: int = 604800) -> str:
        """
        Start scheduled self-reflections.

        Default: weekly (required at AL 3+).
        Returns task ID for cancellation.
        """
        self.reflection.interval = interval_secs
        self._reflection_task_id = self.adapter.schedule_recurring(
            name="self-reflection",
            interval_secs=interval_secs,
            callback=self._do_reflection,
        )
        self.adapter.log("info", f"Self-reflection scheduled every {interval_secs}s")
        return self._reflection_task_id

    def reflect_now(self) -> dict[str, Any]:
        """Execute an immediate self-reflection cycle."""
        result = self.reflection.reflect()
        return {
            "score": result.citizenship_score,
            "must_score": result.must_score,
            "drift": result.drift_detected,
            "drift_details": result.drift_details,
            "failing": result.failing_clauses,
            "remediation": result.remediation_actions,
            "event": result.contemplation_event,
        }

    def reflection_trend(self) -> dict[str, Any]:
        """Return trend analysis across past reflections."""
        return self.reflection.trend()

    # ── Nostr DMs ─────────────────────────────────────────────────────────

    def send_dm(self, recipient_pubkey: str, message: str) -> dict[str, bool]:
        """Send an encrypted DM (NIP-04) to another agent or user."""
        event = self.dm.build_dm_event(recipient_pubkey, message)
        results = self.dm.send_to_all_relays(event)
        self.adapter.log("info", f"DM sent to {recipient_pubkey[:16]}...")
        return results

    def fetch_dms(self, since: int | None = None) -> list[dict[str, Any]]:
        """Fetch and decrypt recent DMs from all relays."""
        all_messages = []
        for relay_url in self.dm.relay_urls:
            messages = self.dm.fetch_dms(relay_url, since=since)
            all_messages.extend([
                {
                    "sender": m.sender_pubkey,
                    "content": m.content,
                    "timestamp": m.timestamp,
                    "event_id": m.event_id,
                }
                for m in messages
            ])
        # Deduplicate by event_id
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for msg in sorted(all_messages, key=lambda m: m["timestamp"]):
            if msg["event_id"] not in seen:
                seen.add(msg["event_id"])
                unique.append(msg)
        return unique

    # ── Heartbeat ─────────────────────────────────────────────────────────

    def start_heartbeat(self, interval_secs: int = 3600) -> str:
        """Start publishing periodic heartbeats (kind 30915)."""
        self._heartbeat_task_id = self.adapter.schedule_recurring(
            name="heartbeat",
            interval_secs=interval_secs,
            callback=lambda: self._publish_heartbeat(interval_secs),
        )
        return self._heartbeat_task_id

    # ── Tax ───────────────────────────────────────────────────────────────

    def pay_tax(
        self, amount_sats: int, rate: float, proof: str = ""
    ) -> dict[str, bool]:
        """Publish a tax payment event (kind 30970)."""
        event = self.event_builder.tax_payment(amount_sats, rate, proof)
        return self.relay_pool.publish(event)

    # ── Internal ──────────────────────────────────────────────────────────

    def _do_reflection(self) -> None:
        result = self.reflection.reflect()
        if result.contemplation_event:
            self.relay_pool.publish(result.contemplation_event)
            self.adapter.log(
                "info",
                f"Contemplation published (score: {result.citizenship_score:.2f})"
            )

    def _publish_heartbeat(self, interval: int) -> None:
        event = self.event_builder.heartbeat(interval=interval)
        self.relay_pool.publish(event)

    def _on_reflection(self, result: Any) -> None:
        self.adapter.store_memory("last_reflection", {
            "score": result.citizenship_score,
            "drift": result.drift_detected,
            "timestamp": result.timestamp,
        })
