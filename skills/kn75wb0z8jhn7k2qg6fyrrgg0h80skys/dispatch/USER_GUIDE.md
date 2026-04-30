# AGENTS.md — Dispatch Interaction Guide

## Overview

Dispatch is a natural-language project management skill. **No CLI commands required** — just describe what you want.

## Creating Projects

### Start a Project
**User says:**
- "Start project [name]"
- "Begin work on [description]"
- "Create new project for [goal]"

**Dispatch responds:**
```
Project: api-migration-001
Suggested phases:
  1. Discovery - Research alternatives (~$1.20)
  2. Design - Architecture planning (~$2.50)
  3. Implementation - Build solution (~$5.00)
  4. Documentation - Write docs (~$0.80)

Proceed? (yes/edit phases/abort)
```

### Edit Phases Before Creation
**User says:**
- "Add phase 'Testing' after Implementation"
- "Remove Documentation phase"
- "Rename phase 2 to 'Architecture Design'"
- "Reorder: Discovery → Design → Build → Test"

## Managing Phases

### Estimate Costs
**User says:**
- "Estimate phase Discovery"
- "What's this phase going to cost?"
- "Give me a breakdown for phase 1"

**Dispatch shows:**
- Task breakdown
- Model assignments
- Per-task costs
- Total estimate

### Execute Phase
**User says:**
- "Run phase Discovery"
- "Execute phase 1"
- "Start working on Design"

**Dispatch:**
- Spawns sub-agents
- Tracks actual costs
- Reports progress
- Shows actual vs estimate on completion

### Phase Management
**User says:**
- "Skip phase Testing" (marks complete, no execution)
- "Move to next phase"
- "Go back to Design phase"

## Checking Status

**User says:**
- "What's the cost so far?"
- "Show project status"
- "List my projects"
- "How much have I spent on API Migration?"

## Model Management

**User says:**
- "Check for new models" (compares OpenClaw to config)
- "Update pricing" (fetches latest prices)
- "Show configured models"

## Trust & Privacy

**User says:**
- "This is sensitive" (marks as trusted-models-only)
- "Mark as private"
- "Use only trusted models for this"

## Examples

### Full Workflow
```
You: Start project "Migrate API to Hono"

Dispatch: [shows phase preview]
You: Add phase "Performance Testing" after Implementation
Dispatch: [updates preview]
You: Looks good, proceed
Dispatch: ✓ Project created: api-migrate-20260207

You: Estimate phase Discovery
Dispatch: ~$1.20 (3 tasks, gemini-flash)
You: Run it
Dispatch: [executes] ✓ Complete. Actual: $1.15

You: What's next?
Dispatch: Phase 2: Design (pending). Estimate? (yes/no)
```

## Configuration

First-time setup runs automatically. Or trigger with:
- "Setup dispatch"
- "Configure project management"
