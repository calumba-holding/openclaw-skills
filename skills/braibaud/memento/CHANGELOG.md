# Changelog

## v0.5.0 — 2026-02-28

### Changed
- **OpenClaw model routing**: Extraction now delegates to OpenClaw's `runEmbeddedPiAgent` instead of making direct HTTP calls to LLM providers. Memento transparently inherits the agent's configured model, fallback chain, and auth profile.
- **No more standalone API key management**: `MEMENTO_API_KEY` / provider-specific env vars are no longer needed when running inside OpenClaw. Direct API fallback remains for CLI/standalone usage.
- **New module**: `src/extraction/embedded-runner.ts` — thin wrapper around `runEmbeddedPiAgent`.
- **README**: Updated privacy note and model config docs to reflect OpenClaw routing behaviour.

## v0.4.0 — 2026-02-XX

### Changed
- ClawHub trust score improvements: honest messaging, `optionalEnv` + `dataFiles` declarations
- `@anthropic-ai/sdk` removed from dependencies
- `autoExtract: false` default (opt-in extraction)
- Hardcoded paths removed → auto-discovery via `os.homedir()`
- Secret-filtering security comments expanded
- Published to ClawHub as `memento@0.4.0`

### Added
- Side-learning: ingest pipeline from Claude Code JSONL sessions
- Knowledge graph: `fact_relations` table with 6 typed relation types, 1-hop recall traversal
- Fact clusters: `fact_clusters` + `cluster_members` tables, incremental + deep consolidation
- Mission Control tab: Knowledge Graph SVG visualisation (force-directed, cluster hulls)
- Deep consolidation: soft confidence decay, cluster merging, runs at 3 AM via cron

## v0.3.0

- Renamed from Engram → Memento
- Git history rewritten (no personal data)
- Pushed to GitHub: https://github.com/braibaud/Memento

## v0.2.0

- Provider-agnostic refactor: Anthropic, OpenAI, Mistral, Ollama, OpenAI-compatible
- Configurable extraction model
- Temporal recency weighting in recall
- Category priority weights (decisions > routine)
- Confidence threshold (0.6 minimum)
- Per-agent memory + master KB (shared facts)

## v0.1.0

- Initial release: fact extraction, SQLite storage, FTS5 search, auto-recall hook
