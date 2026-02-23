# Current Context

<!--
  Version-specific gotchas, behavioral changes, and active risk areas.

  Keep this file updated when upgrading OpenClaw versions.
  You can update it manually by reading the top 2 version sections of CHANGELOG.md,
  or automate it via a cron/sync script that detects changelog changes.

  Retention: Keep the 4 most recent version sections. Drop older ones to control file size.
  The "Foundational Gotchas" section is permanent and must be manually maintained.

  Last updated: 2026-02-22
  Source: CHANGELOG.md versions 2026.2.22 (Unreleased) through 2026.2.21
-->

---

## Active Version

- Current: 2026.2.22 (Unreleased)
- Previous stable: 2026.2.21

---

## Foundational Gotchas (Folk Knowledge)

These are architectural traps that have no CHANGELOG entry. They exist since early codebase design and must be manually maintained.

1. **`loadConfig()` is synchronous with caching** -- First call reads disk (`fs.readFileSync`). Never call in hot paths. Use `clearConfigCache()` to invalidate.
2. **Route resolution uses `WeakMap` cache on config object** -- Spreading/cloning config causes cache miss. Pass config by reference.
3. **Session keys are hierarchical** -- Format: `agent:<id>:<channel>:<kind>:<peerId>[:thread:<threadId>]`. Functions like `isSubagentSessionKey()` depend on exact format.
4. **`agents/` <-> `auto-reply/` is bidirectional by design** -- Not a circular dependency bug. `agents/` provides runtime, `auto-reply/` orchestrates it.
5. **`pi-embedded-subscribe.ts` is a streaming state machine** -- Adding/removing events can break tool call parsing, block chunking, or reasoning block extraction.
6. **`VerboseLevel` enum values are persisted in sessions** -- Changing enum values in `auto-reply/thinking.ts` breaks session persistence.
7. **`channels/dock.ts` returns lightweight metadata** -- Must be updated when channel capabilities change, even though it doesn't import heavy channel code.
8. **`infra/outbound/deliver.ts` is dual-use** -- Used by both cron delivery AND message tool sends. Test both paths.
9. **File locking is required for stores** -- `sessions/` and `cron/` use file locking. Removing lock wrappers causes race conditions and data corruption.
10. **JSON5 vs JSON parsers** -- Config files are JSON5 (comments, trailing commas). Session files, cron store, auth profiles are strict JSON. Don't mix parsers.
11. **`config.patch` nesting trap** -- Patching `{"telegram":{"streamMode":"off"}}` writes to an ignored top-level key. Correct: `{"channels":{"telegram":{"streamMode":"off"}}}`. Always verify full nested structure.
12. **Telegram HTML formatting** -- `telegram/format.ts` converts Markdown to Telegram's limited HTML subset. Broken HTML fails silently.
13. **Discord 2000 char limit** -- `discord/chunk.ts` enforces limits with fence-aware splitting. Don't bypass the chunker.
14. **Signal styled text uses byte positions** -- Not character positions. Multi-byte chars shift ranges.
15. **WhatsApp target normalization** -- Converts between E.164, JID (`@s.whatsapp.net`), and display formats. Wrong format = silent failure.

---

## Recent Behavioral Changes (v2026.2.21 - v2026.2.22)

### From v2026.2.22 (Unreleased) -- Major security wave + new Synology Chat extension

**⚠️ BREAKING CHANGES:**

- **Device-auth `v1` signature REMOVED** -- Clients must now sign `v2` payloads with `connect.challenge` nonce and send `device.nonce`. Nonce-less connects are rejected.
- **Channel preview-streaming config unified** -- `channels.<channel>.streaming` with enum values `off | partial | block | progress`. Slack native stream toggle moved to `channels.slack.nativeStreaming`. Legacy `streamMode` keys still read+migrated by `openclaw doctor --fix`.
- **Channels/Delivery: hardcoded WhatsApp delivery fallbacks removed** -- Must provide explicit/session channel context or auto-pick the sole configured channel (#23357).
- **Security/Exec env: `HOME` and `ZDOTDIR` blocked in host exec env** -- Prevents shell startup-file execution. Next npm release.
- **Security/Exec approvals: `allow-always` for shell-wrapper commands** -- Now persists inner executable allowlist patterns instead of the wrapper shell, preventing broad shell allowlisting (#23276).
- **Security/Exec: sandbox host fails closed** -- `tools.exec.host=sandbox` with no sandbox runtime = hard fail, not fallback to gateway (#23398).
- **Security/Hooks transforms: symlink-safe containment enforced** -- `hooks.transformsDir` and `hooks.mappings[].transform.module` must resolve within root via realpath. Next npm release.
- **Security/Agents: owner-ID hashing now uses dedicated `ownerDisplaySecret`** -- Gateway token fallback removed. Next npm release.
- **Security/Exec approvals: env/shell-dispatch wrappers now transparent** -- Policy checks match effective executable, not wrapper binary. Next npm release.
- **Security/SSRF: IPv4 fetch guard expanded** -- Now blocks RFC special-use ranges: benchmarking, TEST-NET, multicast, reserved/broadcast.
- **ACP/Gateway: gateway hello required before ACP requests** -- Fast-fail on pre-hello connect failures.
- **Config/Channels: `channels.modelByChannel` now whitelisted** -- Previously triggered `unknown channel id` validation errors (#23412).
- **Gateway/Pairing: `operator.admin` satisfies `operator.*` checks** -- Fixes pairing loops for CLI/TUI sessions (#22062, #22193, #21191).
- **Security/Config: prototype-key traversal blocked** -- `__proto__`, `constructor`, `prototype` blocked during config merge/patch (#22968).

**New features:**
- Synology Chat extension added (`extensions/synology-chat/`)
- Fish shell completion added (`src/cli/completion-fish.ts`)
- Logger log-level validation added (`src/logging/env-log-level.ts`)
- `openclaw security audit` now detects: open groups with runtime/FS tools, dangerous `allowCommands` overrides, real-IP fallback severity conditional on loopback

### From v2026.2.21 -- Large feature release

**⚠️ Notable behavioral changes:**

- **Telegram streaming simplified** -- `channels.telegram.streaming` (boolean). Legacy `streamMode` values auto-mapped. Block-vs-partial branching removed.
- **Subagent spawn depth default changed** -- `maxSpawnDepth=2` now shared. Depth-1 orchestrator spawning enabled by default.
- **`tools.exec.host` exec path routing** -- `gateway` is now the default when no sandbox runtime exists (previously could produce unexpected fallback behavior).
- **Discord lifecycle reactions** -- Configurable emoji for queued/thinking/tool/done/error phases. Shared controller with Telegram reactions.
- **`alsoAllow`/`allow` in subagent tool config now respected** -- Previously blocked by built-in deny defaults (#23359).
- **Cron `maxConcurrentRuns` now honored** -- Previously always ran serially (#11595).
- **Plugin enable flow updated** -- `openclaw plugins enable` now updates allowlists via policy, preventing allowlist mismatch (#23190).
- **Config arrays now structurally compared** -- `memory.qmd.paths` and `memory.qmd.scope.rules` no longer trigger false restart-required reloads (#23185).
- **Cron expression validation added** -- Malformed persisted jobs report clear error instead of crashing (#23223).
- **Memory/QMD: legacy unscoped collections migrated** -- `memory-root` → `memory-root-main` at startup (#23228).
- **`✅ Done.` default reply added** -- Tool-only completions that return no final text now get a default acknowledgement (#22834).
- **Agents/Transcripts: tool-call name validation added** -- Malformed tool names rejected before persistence (#23324).

---

## Recent Gotchas (v2026.2.19 - v2026.2.20)

### From v2026.2.20

- **Gateway auth defaults to token mode.** `gateway.auth.mode` is no longer implicitly open. Auto-generated `gateway.auth.token` persisted on first start.
- **`hooks.token` must differ from `gateway.auth.token`** -- startup validation rejects identical values.
- **YAML 1.2 core schema for frontmatter** -- `on`/`off`/`yes`/`no` are now strings, not booleans.
- **Cron webhook delivery is SSRF-guarded** -- private addresses, metadata endpoints blocked.
- **SSRF bypass via IPv6 transition addresses blocked** -- NAT64, 6to4, Teredo, ISATAP.
- **Browser relay requires gateway-token auth** on `/extension` and `/cdp`.
- **`tools.exec.safeBins` validates trusted bin directories** -- trojan binaries in late PATH rejected.
- **Canvas/A2UI uses node-scoped session capability URLs** -- shared-IP fallback auth removed.
- **Control-plane RPCs rate-limited** -- `config.apply`, `config.patch`, `update.run` at 3/min per device+IP.
- **Plaintext `ws://` to non-loopback hosts blocked** -- only `wss://` for remote WebSocket.
- **Discord moderation enforces guild permissions** on trusted sender.
- **Heartbeat skips when HEARTBEAT.md missing/empty** -- cron-event fallback preserved.
- **Cron/heartbeat Telegram topic delivery fixed** -- explicit `<chatId>:topic:<threadId>` targets work correctly.
- **macOS LaunchAgent SQLite fix** -- `TMPDIR` forwarded into installed service environments.

### From v2026.2.19

- **Agents**: Preserve pi-ai default OAuth beta headers when `context1m` injects `anthropic-beta`.
- **Telegram**: Fix draft stream cleanup ordering -- `finally` block must run after fallback delivery logic.
- **Telegram**: Fix `disableBlockStreaming` evaluation order -- ternary producing `undefined` instead of `true` when `streamMode === "off"`.

---

## Recently Active High-Risk Areas

Modules appearing frequently in v2026.2.21 and v2026.2.22:

| Module | Recent Activity | Risk |
| --- | --- | --- |
| Security | MASSIVE wave: SSRF, exec guards, symlink traversal, prototype pollution, device-auth v1 removal | CRITICAL |
| Gateway | Pairing loops fixed, operator.admin scope compat, ACP hello ordering | HIGH |
| Channels | Preview streaming unified, WhatsApp fallback removed, modelByChannel added | HIGH |
| Agents | Subagent tool allowlist, transcript validation, compaction usage fix, default reply | HIGH |
| Memory/QMD | Collection migration, BM25 Han-script normalization, mcporter routing | MEDIUM |
| Discord | Voice commands, streaming preview, lifecycle reactions, subagent threads | MEDIUM |
| Telegram | WSL2 autoSelectFamily, streaming lanes, update-offset persistence | MEDIUM |
| Cron | maxConcurrentRuns, expression validation, delivered state persistence | MEDIUM |
| Config | modelByChannel whitelist, array structural comparison, prototype pollution block | CRITICAL |

---

## Pre-PR Checklist Additions (Version-Specific)

These supplement the stable checklist in STABLE-PRINCIPLES.md:

```
[] If touching gateway auth: verify gateway.auth.mode explicitly. Ensure hooks.token != gateway.auth.token.
[] If touching device-auth: use v2 signature (connect.challenge nonce + device.nonce). v1 is REMOVED.
[] If touching security: run `openclaw security audit` and triage all findings first.
[] If using YAML frontmatter: use explicit true/false, not on/off/yes/no.
[] If touching cron webhooks: verify targets are publicly reachable HTTPS.
[] If installing plugins: use --pin flag. Record name, version, spec, integrity.
[] If touching canvas/A2UI: use scoped session capability URLs, not shared-IP auth.
[] If touching protocol schemas: recommend user runs pnpm protocol:gen:swift && pnpm protocol:check.
[] If touching config loading: test negative path for out-of-root $include and symlink escape.
[] If touching cron schedules: verify both expression and persisted schedule.staggerMs.
[] If touching channel streaming config: use channels.<channel>.streaming enum (off/partial/block/progress), NOT legacy streamMode.
[] If touching exec approvals/safeBins: test wrapper transparency -- policy must match effective executable.
[] If touching hooks transforms: verify module path resolves within root via realpath (symlink-safe containment).
[] If touching subagent tools: check alsoAllow/allow entries are not blocked by built-in deny defaults.
[] If touching config merge/patch: ensure no __proto__/constructor/prototype key traversal.
```
