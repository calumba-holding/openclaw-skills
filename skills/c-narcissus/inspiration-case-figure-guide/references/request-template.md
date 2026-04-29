# Request Compression Template

Use this template internally when the user provides a figure need.

## Slots

- `claim`:
- `gap`:
- `evidence`:
- `anchor_case`:
- `figure_slot`:
- `density`:
- `style_bias`:

## Conversion Rule

Convert the slots into:

- one primary reader question
- one primary logical gap
- one primary figure role
- one preferred rhetoric
- one preferred visual grammar

## Response Rule

Return:

1. interpreted need
2. three candidate directions
3. strongest recommendation
4. one next-step refinement
