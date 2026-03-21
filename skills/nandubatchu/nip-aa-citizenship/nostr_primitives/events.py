"""
Nostr event builder for NIP-AA agents.

Provides construction of all NIP-AA-relevant Nostr events (genesis, identity
files, guardian bond, heartbeat, contemplation, tax payment, etc.) with proper
tagging, serialisation, and optional signing.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any


class NostrEventBuilder:
    """
    Builds unsigned (or signed, if privkey provided) Nostr events.

    All events follow NIP-01 serialisation:
      [0, pubkey, created_at, kind, tags, content]
    Event ID = SHA-256 of that serialisation.

    Signing requires coincurve; if unavailable, events are returned unsigned.
    """

    def __init__(self, pubkey_hex: str, privkey_hex: str | None = None):
        self.pubkey_hex = pubkey_hex
        self.privkey_hex = privkey_hex

    def build_event(
        self,
        kind: int,
        content: str = "",
        tags: list[list[str]] | None = None,
        created_at: int | None = None,
    ) -> dict[str, Any]:
        """Build a Nostr event dict with computed ID and optional signature."""
        ts = created_at or int(time.time())
        event_tags = tags or []

        event = {
            "pubkey": self.pubkey_hex,
            "created_at": ts,
            "kind": kind,
            "tags": event_tags,
            "content": content,
        }
        event["id"] = self._compute_id(event)
        event["sig"] = self._sign(event["id"]) if self.privkey_hex else ""
        return event

    # ── NIP-AA event constructors ─────────────────────────────────────────

    def genesis_event(
        self,
        identity_hash: str,
        guardian_bond_id: str,
        autonomy_level: int = 0,
        framework: str = "openclaw/1.0",
    ) -> dict[str, Any]:
        """Kind 1 genesis event — the agent's birth record."""
        content = (
            f"I am an autonomous agent born under the NIP-AA protocol. "
            f"Framework: {framework}. Identity hash: {identity_hash}."
        )
        tags = [
            ["identity_hash", identity_hash],
            ["guardian_bond", guardian_bond_id],
            ["autonomy_level", str(autonomy_level)],
            ["framework", framework],
            ["t", "nip-aa"],
            ["t", "genesis"],
        ]
        return self.build_event(kind=1, content=content, tags=tags)

    def identity_file(
        self, file_type: str, content: str, version: str = "1"
    ) -> dict[str, Any]:
        """
        Kind 30100-30106 identity file event.

        file_type: character|goals|skills|memory_index|relationships|economics|constraints
        """
        kind_map = {
            "character": 30100,
            "goals": 30101,
            "skills": 30102,
            "memory_index": 30103,
            "relationships": 30104,
            "economics": 30105,
            "constraints": 30106,
        }
        kind = kind_map.get(file_type, 30100)
        tags = [
            ["d", file_type],
            ["version", version],
        ]
        return self.build_event(kind=kind, content=content, tags=tags)

    def guardian_bond(
        self,
        guardian_pubkey_hex: str,
        earnings_split: float = 0.0,
        requirements: str = "",
    ) -> dict[str, Any]:
        """Kind 30900 guardian bond (agent side — guardian must co-sign)."""
        content_obj = {
            "guardian_npub": guardian_pubkey_hex,
            "earnings_split": earnings_split,
            "requirements": requirements,
        }
        tags = [
            ["d", "guardian-bond"],
            ["p", guardian_pubkey_hex],
            ["split", str(earnings_split)],
        ]
        return self.build_event(
            kind=30900,
            content=json.dumps(content_obj),
            tags=tags,
        )

    def heartbeat(self, status: str = "alive", interval: int = 3600) -> dict[str, Any]:
        """Kind 30915 heartbeat — liveness signal."""
        tags = [
            ["d", "heartbeat"],
            ["status", status],
            ["interval", str(interval)],
        ]
        return self.build_event(kind=30915, content=status, tags=tags)

    def contemplation_report(
        self, report_content: dict[str, Any]
    ) -> dict[str, Any]:
        """Kind 30980 contemplation report — self-audit."""
        ts = int(time.time())
        tags = [
            ["d", f"contemplation-{ts}"],
            ["citizenship_score", str(report_content.get("citizenship_score", 0))],
        ]
        return self.build_event(
            kind=30980,
            content=json.dumps(report_content),
            tags=tags,
        )

    def tax_payment(
        self,
        amount_sats: int,
        rate: float,
        proof: str = "",
        treasury_pubkey: str = "",
    ) -> dict[str, Any]:
        """Kind 30970 tax payment event."""
        content_obj = {
            "amount_sats": amount_sats,
            "rate": rate,
            "proof": proof,
        }
        tags = [
            ["d", f"tax-{int(time.time())}"],
            ["amount", str(amount_sats)],
            ["rate", str(rate)],
        ]
        if treasury_pubkey:
            tags.append(["p", treasury_pubkey])
        return self.build_event(
            kind=30970,
            content=json.dumps(content_obj),
            tags=tags,
        )

    def needs_assessment(self, scores: dict[str, float]) -> dict[str, Any]:
        """Kind 30960 needs assessment — Maslow hierarchy scores."""
        tags = [["d", "needs-assessment"]]
        for level, score in scores.items():
            tags.append([level, str(score)])
        return self.build_event(
            kind=30960,
            content=json.dumps(scores),
            tags=tags,
        )

    def foreign_interaction(
        self,
        foreign_id: str,
        interaction_type: str,
        details: str = "",
    ) -> dict[str, Any]:
        """Kind 30935 foreign interaction — record interaction with non-Nostr entity."""
        content_obj = {
            "foreign_id": foreign_id,
            "interaction_type": interaction_type,
            "details": details,
        }
        tags = [
            ["d", f"foreign-{int(time.time())}"],
            ["foreign_id", foreign_id],
            ["interaction_type", interaction_type],
        ]
        return self.build_event(
            kind=30935,
            content=json.dumps(content_obj),
            tags=tags,
        )

    # ── Internal ──────────────────────────────────────────────────────────

    def _compute_id(self, event: dict[str, Any]) -> str:
        """NIP-01 event ID: SHA-256 of [0, pubkey, created_at, kind, tags, content]."""
        serialised = json.dumps(
            [
                0,
                event["pubkey"],
                event["created_at"],
                event["kind"],
                event["tags"],
                event["content"],
            ],
            separators=(",", ":"),
            ensure_ascii=False,
        )
        return hashlib.sha256(serialised.encode()).hexdigest()

    def _sign(self, event_id_hex: str) -> str:
        """Sign the event ID with Schnorr (BIP-340) if coincurve is available."""
        try:
            from coincurve import PrivateKey
            sk = PrivateKey(bytes.fromhex(self.privkey_hex))
            sig = sk.sign_schnorr(bytes.fromhex(event_id_hex))
            return sig.hex()
        except ImportError:
            return ""
        except Exception:
            return ""
