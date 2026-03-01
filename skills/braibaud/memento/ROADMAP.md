# Memento — Roadmap & Ideas Tracker

## ✅ Done

### Core Plugin
- [x] Fact extraction from conversations (capture + extract pipeline)
- [x] SQLite storage with FTS5 full-text search
- [x] Visibility model: shared / private / secret (keyword + LLM classifier)
- [x] Duplicate detection & fact superseding with provenance chain
- [x] Auto-recall injection before each AI turn (`before_prompt_build` hook)
- [x] Per-agent memory + master KB aggregating "shared" facts
- [x] Provider-agnostic refactor (Anthropic, OpenAI, Mistral, Ollama, OpenAI-compatible)
- [x] Configurable extraction model (default: `anthropic/claude-sonnet-4-6`)
- [x] Temporal recency weighting in recall scoring
- [x] Category priority weights (decisions & corrections > routine)
- [x] Confidence scoring (0-1) with minimum threshold (0.6)

### ClawHub Publishing
- [x] Published as `memento@0.3.0` on ClawHub (@braibaud)
- [x] Renamed from Engram → Memento
- [x] Git history rewritten (no personal info leaks)
- [x] Removed credential snooping (no more reading auth-profiles.json)
- [x] TypeScript: zero errors

### Mission Control Tab
- [x] Dashboard with 6 hero stat cards, category bars, donut charts, growth timeline
- [x] Extraction pipeline health monitor
- [x] Top 10 most-reinforced facts
- [x] Recent 20 facts stream with category pills, visibility/agent badges
- [x] Expandable fact cards (full content, metadata, timestamps)
- [x] Feedback actions: 👍 Helpful, 👎 Not relevant, 🗑️ Remove, 💬 Correct
- [x] Toast notifications, inline confirmation for destructive actions
- [x] Auto-refresh every 60s, category click-to-filter

## ✅ Recently Completed (v0.4.0)

### ClawHub Trust Score — DONE
- [x] Honest messaging (no "Everything stays local"), recommends Ollama for local
- [x] Structured `optionalEnv` + `dataFiles` declarations in SKILL.md
- [x] `@anthropic-ai/sdk` removed from package-lock
- [x] `autoExtract: false` default (opt-in)
- [x] Migration docs: explicit filesystem access + security notes
- [x] Secret-filtering: expanded security comments for audit trail
- [x] Hardcoded paths removed from CLI → auto-discovery via os.homedir()
- [x] Published as `memento@0.4.0`

### Git / GitHub — DONE  
- [x] Git history rewritten (no personal info)
- [x] Pushed to `https://github.com/braibaud/Memento`

---

## 🔧 In Progress

### Side-Learning (Claude Code → Memento bridge)
- [x] Staging schema (v1 JSON format for fact exports)
- [x] Ingest pipeline: reads `~/.engram/staging/*.json`, validates, deduplicates, promotes to KB
- [x] `/memento-export` slash command installed at `~/.claude/commands/`
- [ ] **Automatic bridge** — scan `~/.claude/projects/**/*.jsonl`, extract facts via LLM, push to staging. Works regardless of macOS app vs CLI. No user action required.
- [ ] Cron job to run ingest pipeline periodically

### Knowledge Graph & Multi-Layer Memory
- [x] Schema v4: `fact_relations` table — typed weighted edges between facts
- [x] 6 relation types: related_to, elaborates, contradicts, supports, caused_by, part_of
- [x] Extraction prompt identifies relations to existing facts
- [x] Relations stored during deduplication pipeline
- [x] Recall enriched with 1-hop graph traversal (graph-sourced facts at 40% parent score)
- [x] Context builder shows graph-sourced facts with 🔗 provenance tag
- [x] Visibility filtering in graph traversal (shared < private < secret)
- [x] Schema v5: `fact_clusters` + `cluster_members` tables
- [x] Incremental consolidation after each extraction (no LLM, fast)
  - Assigns unclustered facts to existing clusters via graph edges
  - Creates new clusters from 3+ unclustered facts in same category
- [x] Deep consolidation ("sleep" pass)
  - Soft confidence decay: 0.5%/day after 30-day grace, floor 0.3
  - Clustered facts decay 50% slower, high-occurrence 30% slower
  - Cluster summary refresh from member facts
  - Cluster merging when Jaccard overlap > 60%
- [x] Deep consolidation runs at 3 AM via cron
- [ ] LLM-assisted semantic grouping in deep consolidation
- [ ] Layer 3+ meta-cluster creation
- [x] MC tab: Knowledge Graph visualization (force-directed SVG, cluster hulls, hover/click/drag, collapsible section)

## 📋 Planned — Next Up

### Interview / Onboarding Process
Structured conversation where an agent "interviews" the user to rapidly build a knowledge base. Solves the cold-start problem.
- Targeted questions across categories: identity, family, preferences, tools, work, home
- Facts from interviews start at lower confidence (~0.7)
- Confidence reinforced when facts confirmed in real conversations (natural trust-building)
- Track interview completion by category
- Trigger via CLI command or Telegram `/memento interview`
- **Priority: HIGH** — biggest UX impact for new users

### Value Measurement / Analytics
How do we know Memento is actually helping?
- **Recall precision**: % of injected facts that get 👍 vs 👎 (foundation already built with feedback buttons)
- **Question avoidance**: does the agent ask fewer clarifying questions over time?
- **User correction rate**: do "no, I told you..." messages decrease?
- **Fact staleness tracking**: how many recalled facts are thumbed down as outdated?
- **Feedback analytics panel** on MC tab (once enough data exists)
- Target: >80% recall precision = clearly adding value
- **Priority: MEDIUM** — needs data from feedback buttons first

### Fact Discussion / Conversational Correction (V3)
Full multi-turn conversation about a specific fact, beyond the current inline correction.
- Clicking "Discuss" opens a chat-like interface (or triggers a Telegram message)
- Agent can ask clarifying questions, propose corrections, negotiate final fact
- Could be embedded in MC tab or route to Telegram with fact pre-loaded as context
- Current V2 inline correction gets ~80% of the value
- **Priority: LOW** — V2 correction covers most use cases

## 💡 Ideas / Backlog

### Visibility Model Improvements
- Secret vs Private distinction is muddy — consider renaming "secret" → "sensitive"?
- Keyword classifier is too aggressive (e.g., "Ben prefers his medication in the morning" = preference, not medical secret)
- Consider user-configurable sensitivity rules

### Feedback Loop into Extraction
- Thumbs up/down patterns should feed back into extraction quality
- If certain categories consistently get thumbed down → tune extraction prompt
- If certain agents produce more low-quality facts → diagnostic signal
- Track feedback analytics per category and per agent

### Embedding Improvements
- [ ] BGE-M3 embedding backfill (blocked: needs `sudo apt install cmake`)
- Semantic search for recall (currently FTS5 keyword + recency)
- Embedding-based duplicate detection

### Data Migration
- [ ] Migrate all agents' `memory/*.md` files into Memento knowledge base (warm start)
- Migration script exists but hasn't been run on production data

### Packaging & Documentation
- [ ] Blog post covering architecture and design decisions
- [ ] Logo generation (blocked: OpenAI API key expired)
- [ ] Phase 5 final packaging review

### MC Tab Enhancements
- Feedback analytics panel (charts showing precision over time)
- Fact search/filter by content text
- Agent-specific views (filter by agent)
- Fact timeline view (chronological, not just "recent 20")
- Export facts as JSON/CSV

---
*Created: 2026-02-25 by Greg*
*Last updated: 2026-02-25 08:20*

## ✅ Recently Completed (v0.5.0)

### OpenClaw Model Routing Integration
- [x] Extraction now uses OpenClaw's `runEmbeddedPiAgent` instead of direct provider HTTP calls
- [x] Memento transparently inherits the agent's configured model (provider, fallbacks, auth)
- [x] No more standalone API key management in Memento — all delegated to OpenClaw
- [x] Graceful fallback to direct API if running outside OpenClaw (CLI mode)
- [x] New `src/extraction/embedded-runner.ts` module wraps the OpenClaw integration
- [x] `ExtractionTrigger` and `extractFacts()` updated to thread `api.config` through
- [x] README and docs updated to reflect model routing behaviour

## ✅ Recently Completed (v0.5.1)

### AMA-Agent Inspired Features — ALL DONE (from arxiv 2602.22769)

#### 1. Causality Edges in fact_relations — DONE
- [x] Added `precondition_of` edge type (alongside `caused_by`)
- [x] Extraction prompt instructs LLM to prefer causal types for cause-effect / prerequisite relationships
- [x] `causal_weight` column added to `fact_relations` (schema v7); set to `1.5` for causal edges
- [x] Graph traversal in `search.ts` applies **1.5× score boost** for `caused_by` / `precondition_of` edges vs. 0.4× for associative edges
- [x] `deduplicator.ts` stores `causal_weight` when persisting relation edges

#### 2. Query Planning Before Retrieval — DONE
- [x] `planQuery()` function in `search.ts` calls LLM to expand query with synonyms/entities/categories
- [x] `recall.autoQueryPlanning` config option (default: `false`, opt-in)
- [x] Graceful fallback: if planning fails or times out, falls back to raw FTS query
- [x] Uses OpenClaw model routing via `runViaOpenClaw`

#### 3. Temporal State Transitions — DONE
- [x] `previous_value` column added to `facts` table (schema v7)
- [x] `db.supersedeFact()` automatically captures old fact's content as `previous_value` on the new fact
- [x] `context-builder.ts` shows `_(previously: ...)_` in recall output for facts that have changed
- [x] `deduplicator.buildFactRow()` initialises `previous_value: null`; actual value set atomically in `supersedeFact`

### What was NOT implemented (by design)
Full trajectory-based reasoning from AMA-Bench — designed for agent-environment interactions (web nav, code editing), not personal assistant conversations. Memento's dialogue-centric approach is correct for this use case.
