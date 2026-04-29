# Recommendation and Reference Image Protocol

This reference governs two small but important behaviors in every research-figure design conversation.

## 1. Give the user a recommended choice

After presenting multiple options, always identify one recommended default so the user can continue without decision fatigue.

Recommended wording:

- `我建议优先选择：方案 X。理由：...`
- `默认推荐路线：...`
- `如果你想直接推进，我建议下一步做：...`

A good recommendation should be:

1. **claim-aligned**: it supports the paper's main claim and Figure Effect Contract.
2. **reader-centered**: it improves the 10-second and 60-second understanding.
3. **reviewer-safe**: it reduces likely misunderstanding.
4. **visually feasible**: it can be rendered clearly with limited labels.
5. **reversible**: it says when another option would be better.

Do not make the recommendation purely aesthetic.

## 2. Ask for optional reference images at useful moments

Ask for 1–3 reference images when they would help determine layout, density, style family, visual metaphor, or revision direction.

Use this low-friction sentence:

`如果你有1–3张参考图，可以发给我，我会分析它们的布局、信息层级、文字密度和视觉语言；如果没有，我也会继续按论文主张推进。`

Do not ask in every turn. Good moments include:

- initial intake for a visually ambitious figure
- before style-family or layout-skeleton candidate generation
- before converting a selected scheme into an image prompt
- when the user has feedback like “更像顶会论文图” or “更像某篇论文的图”
- when reviewing generated images

## 3. How to analyze provided reference images

Analyze reference images as design evidence. Extract:

- figure role and reader effect
- reading path
- panel count and panel boundaries
- visual hierarchy
- label density and label placement
- color semantics
- object vocabulary and icon style
- metaphor strength
- what is transferable to the current paper
- what should be avoided

## 4. What not to do

- Do not require reference images.
- Do not stop if no reference images are supplied.
- Do not copy the exact composition, distinctive style, marks, or labels of a reference figure.
- Do not let a reference image override the paper's own claim.
- Do not recommend an option without explaining why it serves the reader effect.
