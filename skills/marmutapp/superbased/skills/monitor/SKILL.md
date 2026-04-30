---
name: monitor
description: Proactive screen monitoring with AI analysis. Use when watching for errors during deploys, long-running tests, build processes, or any scenario where the screen should be watched for issues over time.
---

When you need to watch the user's screen for changes and automatically flag issues, use monitor mode:

1. Start: `superbased_recording` with `action: "start"`, `mode: "monitor"`
2. Configure the AI analysis with `analysisPrompt` tailored to the scenario:
   - Deploy watching: "Flag any errors, failed health checks, or red status indicators"
   - Test runs: "Flag test failures, assertion errors, or unexpected output"
   - Build processes: "Flag compilation errors, warnings, or build failures"
   - General: "Flag any errors, warnings, or unexpected states"

**Token budget controls:**
- `analyzeEvery: 5` -- AI analyzes every N significant frames (increase to reduce cost)
- `analyzeInterval: 30` -- minimum seconds between AI calls
- `analysisDetail: "low"` -- 512px images (use "high" for 1024px when reading small text)

**Retrieving results:**
- AI alerts arrive as MCP notifications during the session
- `superbased_recording` with `action: "get_analysis"` and `sessionId` retrieves all AI findings
- Optionally pass `since: N` to only get analyses after frame N

Stop the session with `superbased_recording` `action: "stop"` when done.
