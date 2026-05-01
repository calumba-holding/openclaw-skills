# Changelog

## 0.3.4 - 2026-05-01

### Highlights
- recommend dedicated persistent companion sessions for live cron jobs, e.g. `session:companion-owner`
- clarify that `main` + `systemEvent` is legacy-compatible but can leak into heartbeat or owner-chat context
- refresh OpenClaw live cron templates to include explicit session routing and explicit delivery targets
- align the main `SKILL.md` architecture guidance with the updated OpenClaw integration docs

### Notes
This is a documentation and template release. The bundled pacing/state script behavior is unchanged; the update focuses on safer OpenClaw wiring and clearer publish-ready guidance.
