# Detailed Design Principles by Figure Type

This reference gives richer verbal guidance for how each major figure type should be designed. Use it when the user asks for design philosophy, when a candidate direction needs deeper explanation, or when you want stronger refinement advice without relying on images or code.

## How to Read This Reference

Each figure type is described through:

- `Purpose`: what this type is trying to accomplish in the paper
- `Reader effect`: what should become easier for the reader after seeing it
- `Best paper slot`: where this figure usually belongs in the paper and why
- `Structural priorities`: what must be clear in the layout
- `Text strategy`: how much wording belongs in the figure
- `Typical misuse`: how this type often goes wrong
- `Refinement cues`: how to improve it without changing its role

## A. Motivation / Problem-Gap Figure

### Purpose

This figure establishes necessity. Its job is to make the reader feel that the problem is concrete, the existing framing misses something, and the new method is not solving an invented inconvenience.

### Reader effect

After reading it, the reader should say:

- "I see the failure mode."
- "I understand why current methods do not fully solve it."
- "I now expect the method section to address this exact gap."

### Best paper slot

- `intro`: strongest default; this figure prepares the reader to accept the method
- `analysis`: useful when the paper later returns to a richer failure taxonomy
- `appendix`: acceptable when the motivation is real but not central to the final contribution mix
- `method`: usually only when the paper's structure merges the problem framing tightly into formulation

### Structural priorities

- Put the failure signal first, not the explanation.
- Use a small number of contrasts.
- Organize the figure so the problematic phenomenon is visible before any fix is shown.
- If there is a baseline, show why it fails in the same coordinate system or narrative frame.

### Text strategy

- Use short labels for the failure, missing signal, or bottleneck.
- Keep long explanation out of the figure body.
- If one sentence must appear inside the figure, it should express the entire takeaway.

### Typical misuse

- The figure becomes a mini related-work board.
- The failure only becomes understandable after reading the caption twice.
- The figure announces the method too early and weakens the problem setup.

### Refinement cues

- Remove one panel if two panels already establish the gap.
- Replace explanatory text with one visual contradiction.
- If the problem still feels abstract, swap the broad overview for one strong case.

## B. Toy Example / Case Walkthrough Figure

### Purpose

This figure makes the idea concrete through one controlled example. It is often the best way to show why the method matters when the method itself is conceptually simple but easy to misunderstand.

### Reader effect

After reading it, the reader should be able to retell the example in words and explain what changed between the failing state and the corrected state.

### Best paper slot

- `intro`: use here when one simple case can teach the problem immediately
- `method`: use here when the case is the cleanest bridge into the proposed mechanism
- `analysis`: use here when the case mainly serves interpretation or diagnosis
- `appendix`: use here for longer walkthroughs that would otherwise slow the main story

### Structural priorities

- Keep the same entities, tokens, or objects across all stages.
- Make the transition point visually explicit.
- If there are four panels, they should usually follow setup -> conflict -> intervention -> resolution.
- Avoid branching unless the whole point is comparison.

### Text strategy

- Labels should attach to states or changes, not narrate the whole case.
- Use arrows or numbered stage labels to preserve order.
- Avoid mixing two examples unless the user explicitly needs comparison.

### Typical misuse

- Different examples appear across panels and the reader cannot track identity.
- Every panel contains multiple sub-events, so the story loses rhythm.
- The case is too realistic and noisy for the intended conceptual point.

### Refinement cues

- Reduce to one exemplary transition.
- Replace decorative detail with stage clarity.
- If the figure feels flat, add one intermediate state rather than more commentary.

## C. Method Overview / Architecture Figure

### Purpose

This figure provides the navigational map for the paper. It is the figure readers return to when they forget where a module sits or what flows into what.

### Reader effect

After reading it, the reader should know:

- the major components
- the direction of information flow
- what enters and leaves each important stage
- where the paper's novelty sits

### Best paper slot

- `method`: strongest default; this is normally the anchor figure of the section
- `intro`: useful as an early teaser if the full pipeline is simple enough to preview
- `analysis`: only if the figure is being reused as a decomposition tool rather than as the main architecture
- `appendix`: good for expanded versions, engineering detail, or alternative variants

### Structural priorities

- One dominant reading path is mandatory.
- Novel modules should be visually distinct from routine ones.
- Inputs and outputs should be clearly typed: data, prompts, states, embeddings, losses, actions, etc.
- If there are multiple flows, choose one primary flow and subordinate the rest.

### Text strategy

- Module names should match the paper text exactly.
- Put detail in the caption, not inside every block.
- If a block needs explanation longer than a short phrase, it may belong in a secondary figure.

### Typical misuse

- Every block has the same weight, so novelty and plumbing look identical.
- Auxiliary losses, data sources, and evidence panels are all squeezed into the same board.
- The figure tries to be both an overview and a full algorithm trace.

### Refinement cues

- Pull evidence out into a separate figure if the overview is crowded.
- Highlight only the interfaces the reader must remember.
- Use grouping, spacing, or background regions to show hierarchy.

## D. Idea-to-Model Bridge Figure

### Purpose

This figure explains why the formal model is the right implementation of the intuitive idea. It is especially important when the method introduces new variables, losses, latent states, rewards, constraints, or optimization structures.

### Reader effect

After reading it, the reader should be able to answer:

- why this variable exists
- why this constraint or objective is needed
- how the intuitive principle is encoded in the model

### Best paper slot

- `method`: strongest default because the bridge usually belongs near formalization
- `intro`: useful when the paper needs an intuition-preserving preview before equations
- `analysis`: useful when the bridge is primarily explanatory after the fact
- `appendix`: useful for extended derivational bridges or extra interpretive detail

### Structural priorities

- Preserve a visible path from idea -> intermediate representation -> formal mechanism.
- The middle layer is usually the decisive one.
- Reuse symbols, shapes, or color semantics between the conceptual and formal sides.
- If equations appear, they should anchor the structure rather than dominate it.

### Text strategy

- Prefer naming one quantity per visual role.
- Use concise phrases such as "shared latent factor", "consistency score", or "routing signal".
- Put derivational detail in the caption or body text.

### Typical misuse

- The figure jumps directly from intuition to equations.
- The visual side and formal side use unrelated language and symbols.
- The figure explains the model but never explains why this model reflects the idea.

### Refinement cues

- Add one intermediate state, map, or variable family.
- Mirror notation across left and right halves.
- If the figure feels too mathematical, convert one equation block into a semantic diagram.

## E. Process / Loop / Timeline Figure

### Purpose

This figure explains how the system evolves. Use it when the novelty is procedural, iterative, agentic, or time-dependent.

### Reader effect

After reading it, the reader should understand state transition: what exists before the step, what is updated, what feedback is collected, and how the next step differs.

### Best paper slot

- `method`: strongest default when the process itself is part of the contribution
- `analysis`: strong when the loop view mainly explains behavior or diagnostics
- `intro`: good when procedural novelty is the paper's core hook
- `appendix`: appropriate for long traces, rollout detail, or implementation-specific unrolling

### Structural priorities

- Make the recurrent state explicit.
- Make stage boundaries explicit.
- Show one full cycle before collapsing into abstraction.
- If the loop is complex, number the phases.

### Text strategy

- Time markers help more than long descriptions.
- State names should be stable across the whole loop.
- If arrows proliferate, replace some arrows with stage regions or numbered bands.

### Typical misuse

- The figure is drawn like an overview pipeline even though the point is recurrence.
- Inputs, states, and outputs are visually indistinguishable.
- Feedback arrows overwhelm the main forward path.

### Refinement cues

- Reduce secondary arrows.
- Emphasize the one state that persists across iterations.
- If the loop still feels opaque, add one side panel showing a concrete trace.

## F. Dataset / Benchmark / Protocol Figure

### Purpose

This figure builds trust in the evidence pipeline. It tells the reader how raw material becomes benchmark items, what the evaluation slices are, and why the final evidence should be considered valid.

### Reader effect

After reading it, the reader should understand the benchmark's construction logic rather than treating it as an opaque source of numbers.

### Best paper slot

- `method`: strongest when dataset or benchmark construction is part of the technical contribution
- `intro`: appropriate when the benchmark itself is the headline contribution
- `analysis`: useful when protocol interpretation matters for understanding downstream evidence
- `appendix`: appropriate for curation rules, annotation detail, and extra slice definitions

### Structural priorities

- Funnels, filters, and slices should be aligned.
- Counts or scale markers should be easy to compare.
- If there are multiple benchmark dimensions, show the organizing principle once and reuse it.
- Keep protocol separate from results whenever possible.

### Text strategy

- Use counts, stage names, and slice labels.
- Avoid stuffing definitions and evaluation claims into the same panel.
- If there are many labels, prefer tables or aligned lists outside the main graphic flow.

### Typical misuse

- The protocol is reduced to one tiny box before the paper jumps to results.
- The figure is dominated by decorative arrows but hides the actual curation logic.
- Benchmark taxonomy and metric reporting are mixed into one unreadable sheet.

### Refinement cues

- Split source -> curation -> evaluation into explicit stages.
- Add counts only where they clarify scale.
- If trust is the issue, emphasize filtering criteria rather than ornament.

## G. Evidence / Result / Ablation Figure

### Purpose

This figure persuades. It should tell the reader what to believe, why the claim is supported, and which comparison matters.

### Reader effect

After reading it, the reader should know the main claim and the strongest supporting evidence without scanning every subplot equally.

### Best paper slot

- `analysis`: strongest default; this is where evidence boards usually deliver the most value
- `intro`: use only for one especially persuasive evidence figure that helps sell the paper early
- `method`: usually a weak fit unless evidence is intentionally threaded into the method exposition
- `appendix`: ideal for extra ablations, stress tests, and secondary comparisons

### Structural priorities

- One panel should dominate.
- Supporting panels should answer a clear question such as "is it robust?", "why does it work?", or "where does it fail?"
- The comparison target should be intentional rather than exhaustive.

### Text strategy

- Highlight the claimed result, not every result.
- Use legends and annotations only where the reader may misread the claim.
- Keep axes and legends aligned across related subplots.

### Typical misuse

- The figure is just a dump of all experimental outputs.
- Qualitative and quantitative evidence are mixed with no hierarchy.
- The main claim is hidden because every panel is equally emphasized.

### Refinement cues

- Promote one main comparison.
- Move secondary ablations to appendix if they dilute the message.
- Add a subtitle for the board-level claim if the evidence is visually diverse.

## H. Theory / Proof Intuition Figure

### Purpose

This figure lowers the barrier to formal reasoning. It should provide an intuitive picture for the theorem, proof strategy, or geometry behind the result.

### Reader effect

After reading it, the reader should know what quantity moves, what structure constrains it, and why the formal conclusion is plausible.

### Best paper slot

- `method`: useful when theoretical framing is central to the technical definition
- `analysis`: strongest when the figure interprets theory after the reader already knows the method
- `appendix`: common when the theory matters but is not required for first-pass understanding
- `intro`: rare, but possible when the paper is primarily theoretical and the theorem-level intuition is the main hook

### Structural priorities

- Keep the number of tracked objects very small.
- Spatial structure should correspond to logical structure.
- If there is a bound, show what is bounded and in which direction the argument works.

### Text strategy

- Use labels for quantities, sets, regions, directions, or boundaries.
- Avoid full theorem statements inside the figure.
- Use the caption to connect the visual metaphor to the formal claim.

### Typical misuse

- The figure simply redraws the theorem statement with arrows.
- Too many symbols make the "intuition" harder than the proof sketch.
- The visual metaphor conflicts with the actual logic of the theorem.

### Refinement cues

- Keep only the minimal quantities necessary.
- Turn algebraic dependence into spatial dependence when possible.
- If the theorem has multiple claims, illustrate only the one that unlocks intuition.

## Cross-Type Principles

### 1. Design around the reader's bottleneck

The strongest figure is usually the one that resolves the reader's hardest unresolved question, not the one with the most content.

### 2. Prefer one dominant message per figure

If a figure is trying to motivate, explain the method, and prove the result at once, it usually underperforms on all three jobs.

### 3. Use visual hierarchy as argument hierarchy

The most important panel, path, or quantity should be visually dominant. If everything is equally strong, nothing is prioritized.

### 4. Let captions carry prose

Figures should carry structure. Captions should carry the explanatory sentences that are too long for the drawing.

### 5. Add detail by clarifying transitions, not by adding decoration

When a figure feels weak, the missing piece is often:

- an intermediate state
- a clearer stage boundary
- a stronger case anchor
- a more explicit comparison

It is less often solved by extra icons, colors, or visual embellishment.

### 6. Match the figure to the paper slot

The same figure type changes character depending on placement:

- in `intro`, the figure should reduce entry cost and build motivation quickly
- in `method`, the figure should stabilize the technical map
- in `analysis`, the figure should strengthen belief or interpretation
- in `appendix`, the figure can afford density, edge cases, and extended detail

If a figure feels misplaced, the problem is often not the drawing style but the slot.
