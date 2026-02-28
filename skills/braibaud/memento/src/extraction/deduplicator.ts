/**
 * Deduplication Engine
 *
 * Processes an array of ExtractedFacts from the LLM, applying one of three
 * outcomes for each:
 *
 *   1. Duplicate   — fact already exists; increment occurrence_count + log occurrence
 *   2. Update      — fact supersedes an older one; mark old inactive, insert new
 *   3. New         — genuinely new fact; insert + log first occurrence
 *
 * Deduplication is itself a SIGNAL: repeated mentions of a fact are tracked
 * in fact_occurrences with context (what was said, sentiment) for temporal analysis.
 */

import { randomUUID } from "node:crypto";
import type { ConversationDB } from "../storage/db.js";
import type { ExtractedFact } from "./extractor.js";
import type { FactRow, FactRelationRow } from "../storage/schema.js";
import type { PluginLogger } from "../types.js";

export type DeduplicationResult = {
  factsExtracted: number;  // genuinely new facts
  factsUpdated: number;    // facts that supersede an older fact
  factsDeduplicated: number; // facts identified as duplicates
};

/**
 * Process extracted facts against the database, applying dedup/supersede/insert logic.
 */
export function processExtractedFacts(
  facts: ExtractedFact[],
  conversationId: string,
  agentId: string,
  db: ConversationDB,
  logger: PluginLogger,
): DeduplicationResult {
  const now = Date.now();
  let factsExtracted = 0;
  let factsUpdated = 0;
  let factsDeduplicated = 0;

  for (const fact of facts) {
    try {
      // Track the final persisted fact ID for relation storage
      let persistedFactId: string | null = null;

      if (fact.duplicate_of && fact.increment_occurrence) {
        // ── Duplicate ─────────────────────────────────────────────────────
        // The LLM identified this as an existing fact seen again.
        // Increment occurrence_count, update last_seen_at, add to occurrences.
        db.updateFactOccurrence(
          fact.duplicate_of,
          conversationId,
          fact.content,
          fact.sentiment ?? "neutral",
          now,
        );
        persistedFactId = fact.duplicate_of;
        factsDeduplicated++;
        logger.debug?.(
          `memento: duplicate of ${fact.duplicate_of}: ${fact.content.slice(0, 60)}`,
        );
      } else if (fact.supersedes) {
        // ── Update ────────────────────────────────────────────────────────
        // This fact replaces an existing one (e.g. FTP changed from 250W to 260W).
        // Mark the old fact inactive, insert the new one, log its first occurrence.
        const newFact: FactRow = buildFactRow(fact, agentId, now);
        db.supersedeFact(fact.supersedes, newFact);
        db.updateFactOccurrence(
          newFact.id,
          conversationId,
          fact.content,
          fact.sentiment ?? "update",
          now,
        );
        persistedFactId = newFact.id;
        factsUpdated++;
        logger.debug?.(
          `memento: superseded ${fact.supersedes} → ${newFact.id}: ${fact.content.slice(0, 60)}`,
        );
      } else {
        // ── New fact ──────────────────────────────────────────────────────
        const newFact: FactRow = buildFactRow(fact, agentId, now);
        db.insertFact(newFact);
        db.updateFactOccurrence(
          newFact.id,
          conversationId,
          fact.content,
          fact.sentiment ?? "neutral",
          now,
        );
        persistedFactId = newFact.id;
        factsExtracted++;
        logger.debug?.(
          `memento: new fact ${newFact.id} [${fact.category}]: ${fact.content.slice(0, 60)}`,
        );
      }

      // ── Store graph relations ─────────────────────────────────────────
      if (persistedFactId && fact.relations && fact.relations.length > 0) {
        const relations: FactRelationRow[] = fact.relations
          .filter((r) => r.target_id !== persistedFactId) // no self-loops
          .map((r) => ({
            id: randomUUID(),
            source_id: persistedFactId!,
            target_id: r.target_id,
            relation_type: r.relation_type,
            strength: r.strength ?? 0.8,
            created_at: now,
            created_by: "extraction",
            metadata: null,
          }));

        if (relations.length > 0) {
          try {
            db.insertRelationsBatch(relations);
            logger.debug?.(
              `memento: stored ${relations.length} relation(s) for fact ${persistedFactId}`,
            );
          } catch (relErr) {
            logger.warn(
              `memento: failed to store relations for ${persistedFactId}: ${String(relErr)}`,
            );
          }
        }
      }
    } catch (err) {
      logger.warn(
        `memento: deduplicator error processing fact "${fact.content.slice(0, 60)}": ${String(err)}`,
      );
    }
  }

  return { factsExtracted, factsUpdated, factsDeduplicated };
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function buildFactRow(fact: ExtractedFact, agentId: string, now: number): FactRow {
  return {
    id: randomUUID(),
    agent_id: agentId,
    category: fact.category,
    content: fact.content,
    summary: fact.summary ?? null,
    visibility: fact.visibility ?? "shared",
    confidence: fact.confidence ?? 1.0,
    first_seen_at: now,
    last_seen_at: now,
    occurrence_count: 0, // updateFactOccurrence will increment to 1
    supersedes: fact.supersedes ?? null,
    is_active: 1,
    metadata: null,
    embedding: null, // populated later by the embedding backfill pass
  };
}
