# Visual-First Decision Board Protocol

Version: 2.7.0

This protocol prevents the inspiration/case figure guide from becoming a text-only questionnaire that only generates images once at the end. For inspiration-source, case-schematic, and idea-to-model bridge figures, many choices are inherently visual: category, panel skeleton, metaphor strength, style family, and density.

## Core principle

When a decision is primarily visual, let the user compare generated visual samples earlier in the workflow. A visual decision board is not the final polished figure; it is a quick multi-candidate board for selecting a direction.

## When to use a visual decision board

Use or recommend an `IMAGE_ONLY` exploratory board when:

- the user is choosing among inspiration-source figure, case walkthrough, motivation board, idea-to-model bridge, or introduction hero;
- the user is comparing style families such as editorial flat, formal schematic, mechanism snapshot, premium scientific illustration, isometric / soft 3D, cartoon / comic-lite, tile / card / mosaic, paper-cut, blueprint, dashboard, or minimal line-art;
- the layout choice is visual: bridge, storyboard, before-after, layered stack, tile board, radial loop, or central mechanism with callouts;
- the metaphor choice is visual: bridge, funnel, lens, map, loop, scaffold, or card board;
- the user asks for multiple candidates, different styles, different types, or says they cannot decide;
- more text would likely not resolve the choice.

Do not use a board when the paper claim is still too unclear, the user explicitly asks not to generate images yet, or the decision is mainly about argument logic rather than visual form.

## Board types

### 1. Figure-direction board

Purpose: select the role of the figure.

Typical batch: 3–5 images.

Examples: inspiration-source bridge vs case walkthrough vs problem-gap board vs idea-to-model bridge vs intro hero.

Prompt discipline: keep the paper thesis, anchor case, and core labels fixed; vary only figure role and composition.

### 2. Layout board

Purpose: choose the panel skeleton.

Typical batch: 3–5 images.

Examples: horizontal bridge, split before-after, storyboard panels, tile matrix, layered stack, central mechanism with callouts.

Prompt discipline: keep figure role and style fixed; vary only layout.

### 3. Style board

Purpose: choose visual communication style.

Typical batch: 3–5 images.

Examples: clean editorial flat, formal architecture schematic, mechanism snapshot, premium scientific illustration, isometric / soft 3D, mature cartoon / storyboard, tile/card/mosaic, paper-cut layered collage, blueprint / technical drawing, minimal line-art.

Prompt discipline: keep thesis, panel plan, labels, color semantics, and object vocabulary fixed; vary only style family.

### 4. Metaphor board

Purpose: choose the central visual metaphor.

Typical batch: 3–5 images.

Examples: bridge, funnel, lens, loop, map, scaffold, card board, evidence trail.

Prompt discipline: keep role, panel count, and style fixed; vary only metaphor.

### 5. Density board

Purpose: choose the amount of information.

Typical batch: 2–4 images.

Examples: sparse intro hero, balanced 3-panel figure, moderate case walkthrough, dense mini-evidence board.

Prompt discipline: keep role, layout, and style fixed; vary only density and label amount.

## Required text turn before a board

Unless the user already asked for direct visual candidates and the state is sufficient, the preceding `TEXT_ONLY` reply should briefly state:

- board type;
- candidate count;
- what stays fixed;
- what varies;
- what the user should compare;
- the default recommendation if the user wants to proceed.

Do not over-explain. The purpose is to move from imagined options to visual evidence.

## Image-only generation turn

The board-generation turn must be `IMAGE_ONLY`: no prose, no state footer, no explanation.

## After a board

The next `TEXT_ONLY` reply must:

1. identify the strongest candidate;
2. explain why it fits the reader effect, paper slot, and figure thesis;
3. note risks or required modifications;
4. record the board in state;
5. provide one default recommendation;
6. end with the standard `当前状态与产物` and `下一步你可以这样问` sections.

## State fields

Track:

```yaml
visual_decision_mode: text_only | exploratory_image_board | final_image_batch
visual_board_recommended: true | false
visual_board_type: figure_direction | layout | style | metaphor | density | refinement | final_candidate
visual_board_axis_varied:
visual_board_candidate_count:
visual_board_status: proposed | confirmed | generated | reviewed | skipped
visual_board_fixed_elements:
visual_candidate_history:
selected_visual_candidate:
default_visual_recommendation:
```

## Non-goals

- Do not use exploratory boards to bypass the reader-effect contract or paper logic compression.
- Do not vary category, layout, style, metaphor, density, labels, and colors all at once except in a deliberately broad first exploration.
- Do not treat the first exploratory board as final. It is a decision aid.
