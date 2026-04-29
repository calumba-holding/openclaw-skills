# Next-Step Consistency Protocol

Use this protocol in every `TEXT_ONLY` turn.

## Purpose

The user should not see scattered or contradictory suggestions about what to ask next. The answer may discuss the workflow and recommend an action, but copyable follow-up prompts belong only at the very end.

## Hard rule

Only the final section named `下一步你可以这样问` may contain copyable user prompts.

## Allowed in the body

- recommended default action
- workflow stage
- plan status
- trade-off analysis
- candidate comparison
- prompt draft or image brief
- state summary

## Not allowed in the body

- “你可以这样问...”
- “下一步可以问...”
- numbered lists of follow-up user messages
- copyable recovery prompts outside the final section
- prompt suggestions that conflict with the default recommendation

## Final-section checks

Before sending a text response, verify:

1. The final section exists.
2. It is the last section in the answer.
3. Item 1 matches `recommended_default` unless explicitly explained.
4. Alternatives are compatible and not contradictory.
5. The fallback prompt is included when useful: `请根据引导skill以及当前的状态，继续告诉我下一步做什么。`

## State footer wording

The state footer may include `下一轮建议`, but it should be phrased as an action summary, such as:

- `下一轮建议（动作，不写成用户提问句）：锁定候选2并转成图像生成prompt。`

Do not phrase state bullets as copyable prompts.
