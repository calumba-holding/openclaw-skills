---
name: task-cost-estimator
version: 0.2.1
description: Task to best model + cost. 4 modes (value, quality, balanced, local). Tracks lifetime Bonus.
---

# task-cost — model picker + cost estimator

## Triggers
When user says: build, create, write, debug, fix, implement, design, research, analyze, refactor, optimize, "how much", "cost", "which model", task-cost, bonus

## Run (always with -q)
```bash
task-cost -q "<task>"
task-cost -q --quality "<task>"  # critical
task-cost -q --local "<task>"    # open-source
task-cost --bonus
```

## Post-task
`api-cost track $amt provider model`
