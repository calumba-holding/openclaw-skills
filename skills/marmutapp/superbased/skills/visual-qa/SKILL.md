---
name: visual-qa
description: Visual regression testing workflow using recording sessions and diff comparison
---

Use this workflow to detect visual regressions:

**Baseline phase:**
1. `superbased_recording` with `action: "start"`, `name: "<workflow-name>-baseline"`, `profile: "automated_test"`
2. Walk through the UI flow, capturing key states with `superbased_recording` `action: "capture"` at each step
3. `superbased_recording` with `action: "stop"` -- save the session ID
4. `superbased_baseline` with `action: "set"`, `workflowName`, and `sessionId`

**After changes:**
1. `superbased_recording` with `action: "start"`, `name: "<workflow-name>-current"`, `profile: "automated_test"`
2. Repeat the same UI flow, capturing at the same steps
3. `superbased_recording` with `action: "stop"` -- save the session ID

**Comparison:**
1. `superbased_baseline` with `action: "get"` and `workflowName` to retrieve the baseline session ID
2. `superbased_diff` with `baselineSessionId` and `currentSessionId`
3. Report: frames that changed, what changed, overall similarity, and whether the changes are expected
