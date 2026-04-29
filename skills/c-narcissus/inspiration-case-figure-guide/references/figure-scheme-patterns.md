# Figure Scheme Patterns

Use these patterns to convert a structured request into concrete candidate figure directions.

## 1. Motivation Contrast Board

Design goal:
- make the problem feel inevitable rather than optional
- create enough tension that the reader wants the method before seeing it

Best for:
- `why_is_this_problem_real`
- `idea_motivation_or_problem_gap`
- `contrast_before_after`

What this figure is doing cognitively:
- it is not teaching the full method
- it is establishing that the old framing misses something important
- it should reduce the reader's resistance before they enter the method section

Best paper slot:
- `intro`: strongest default; this is where the figure can create necessity before the method appears
- `analysis`: useful when the paper introduces a new failure taxonomy later, but weaker than intro for first use
- `appendix`: only if the motivation is secondary and the main paper must stay narrow
- `method`: usually a poor fit unless the paper structure merges motivation and formulation tightly

Recommended panel recipe:
- Panel A: failure, contradiction, or bottleneck
- Panel B: why the old framing fails
- Panel C: the desired takeaway or target behavior

Design priorities:
- the failure signal should be legible in under three seconds
- the contrast should be structural, not just color-coded
- the conclusion should be a single takeaway, not a mini literature review

Typical failure mode:
- too much text and not enough visual contrast

Refinement lever:
- keep only one memorable failure case

## 2. Toy Case Storyboard

Design goal:
- compress an abstract idea into one concrete, inspectable path
- let the reader mentally replay the logic after leaving the page

Best for:
- `can_i_see_the_core_case`
- `toy_example_or_case_evidence`
- `storyboard_case_walkthrough`

What this figure is doing cognitively:
- it anchors the method in a case the reader can simulate
- it is useful when the abstraction would otherwise feel arbitrary
- it can also serve as a bridge from motivation to mechanism

Best paper slot:
- `intro`: strong when one case can teach the whole problem quickly
- `method`: strong when the case is the cleanest bridge into the mechanism
- `analysis`: useful when the case is mainly diagnostic or interpretive
- `appendix`: good for extended walkthroughs that would overload the core narrative

Recommended panel recipe:
- setup
- confusing state or failure
- intervention
- corrected or revealing outcome

Design priorities:
- keep the same example identity across all panels
- every stage should add one new piece of information
- annotations should sit on the transition, not all over the frame

Typical failure mode:
- too many case branches in one figure

Refinement lever:
- carry one single case consistently across all panels

## 3. Method Overview Pipeline

Design goal:
- give the reader a stable mental map of the whole method
- show where the novelty lives without making the whole pipeline look equally important

Best for:
- `what_are_the_parts_and_data_flow`
- `method_overview_or_architecture`
- `block_arrow_pipeline`

What this figure is doing cognitively:
- it reduces navigation cost for the rest of the paper
- it tells the reader what each block is responsible for
- it should support the section structure, not compete with it

Best paper slot:
- `method`: strongest default; this is usually the anchor figure for the whole section
- `intro`: useful when the paper needs one early high-level teaser of the system
- `analysis`: only if the figure is reframed as a diagnostic decomposition rather than a full overview
- `appendix`: suitable for expanded variants, implementation detail, or extended module breakdown

Recommended panel recipe:
- inputs and setup
- core modules and flow
- outputs and learning targets

Design priorities:
- preserve one dominant reading path
- visually emphasize novel modules, not routine plumbing
- name blocks the same way the text and caption name them

Typical failure mode:
- all modules are drawn with equal weight, so the novelty disappears

Refinement lever:
- visually emphasize only the novel or decision-critical blocks

## 4. Idea-to-Model Bridge

Design goal:
- turn "this idea sounds good" into "I now understand why these variables or losses exist"
- make the implementation feel logically earned

Best for:
- `how_does_the_idea_become_a_model`
- `idea_to_model_logic_bridge`
- `equation_diagram_hybrid`

What this figure is doing cognitively:
- it fills the gap between intuition and formalization
- it is often the missing figure when reviewers say the method feels heuristic
- it is especially useful when the paper introduces constraints, latent states, rewards, or multi-term losses

Best paper slot:
- `method`: strongest default; the figure usually belongs near the formalization or objective section
- `intro`: works if the paper needs an early intuitive bridge before equations
- `analysis`: useful when the bridge is mainly interpretive rather than definitional
- `appendix`: suitable for full derivational bridges or extra mechanism detail

Recommended panel recipe:
- intuition or principle
- intermediate state, variable, or constraint
- loss, module, or objective

Design priorities:
- the middle layer matters most; without it the bridge usually fails
- reuse symbols or visual motifs across concept and model sides
- equations should support the picture, not replace it

Typical failure mode:
- the figure jumps directly from intuition to equations

Refinement lever:
- add one intermediate representation or variable layer

## 5. Process Loop Unroll

Design goal:
- make a time-dependent or iterative contribution easy to follow
- reveal not just components, but state changes and feedback

Best for:
- `what_happens_over_time`
- `training_or_inference_process`
- `feedback_loop_or_cycle`

What this figure is doing cognitively:
- it helps the reader track evolution, not just structure
- it is useful for training curricula, agent loops, search, retrieval, planning, self-improvement, and multi-stage inference
- it usually answers questions the overview pipeline cannot answer alone

Best paper slot:
- `method`: strongest default when the process is part of the core contribution
- `analysis`: strong when the process view is mainly diagnostic or explanatory
- `intro`: useful if the procedural novelty is the paper's most memorable hook
- `appendix`: good for full traces, long rollouts, or implementation-level unrolling

Recommended panel recipe:
- current state
- action or update
- evaluation or feedback
- next state

Design priorities:
- a recurrent state should be clearly marked
- show one full cycle before abstracting
- numbered phases usually help more than extra arrows

Typical failure mode:
- arrows go in too many directions and the reader loses order

Refinement lever:
- force a dominant reading direction and number the stages

## 6. Dataset / Benchmark Protocol Figure

Design goal:
- make the evidence pipeline feel auditable and fair
- show how examples become benchmark units and how claims are measured

Best for:
- `data_or_benchmark_construction`
- `benchmark_or_dataset_protocol`
- `what_evidence_should_i_believe`

What this figure is doing cognitively:
- it builds trust in the benchmark or data contribution
- it prevents the reader from collapsing all evidence into "they collected some data somehow"
- it is especially valuable when curation, slicing, annotation, or evaluation axes are part of the contribution

Best paper slot:
- `method`: strongest when data or benchmark construction is a contribution section of its own
- `intro`: useful when the benchmark itself is the headline contribution
- `analysis`: works when protocol interpretation matters for reading the results
- `appendix`: appropriate for expanded curation details, annotation policies, or extra benchmark slices

Recommended panel recipe:
- source pool
- filtering / annotation
- benchmark slices or evaluation axes

Design priorities:
- counts, funnels, and splits should be visually aligned
- protocol figures should foreground process before headline numbers
- if there are multiple task slices, show the organizing principle once

Typical failure mode:
- protocol and final results are mixed together

Refinement lever:
- separate protocol explanation from evidence comparison

## 7. Evidence Comparison Panel

Design goal:
- make one claim believable with the minimum number of panels
- emphasize evidential force rather than architectural completeness

Best for:
- `result_or_ablation_evidence`
- `quantitative_result_plot`
- `ablation_or_mechanism_probe`

What this figure is doing cognitively:
- it converts results into conviction
- it should make it obvious what changed, whether it helped, and why that support matters
- it is often the strongest figure for rebuttal or camera-ready strengthening

Best paper slot:
- `analysis`: strongest default; this is where evidence boards usually have the most force
- `intro`: useful only when one evidence board is needed to sell the whole paper early
- `method`: usually a poor fit unless the method and evidence are intentionally interleaved
- `appendix`: ideal for extra ablations, failure taxonomies, or lower-priority comparisons

Recommended panel recipe:
- main metric comparison
- qualitative or mechanism evidence
- ablation or boundary case

Design priorities:
- one main panel should dominate
- supporting panels should answer "why believe this result"
- highlight only the comparison that matters to the claim

Typical failure mode:
- too many subplots without one main claim

Refinement lever:
- make one panel dominant and demote the rest to support

## 8. Theory Intuition Figure

Design goal:
- give the reader a picture for a theorem, bound, or proof strategy
- lower the cost of entering formal analysis

Best for:
- `theory_or_proof_intuition`
- `what_is_the_proof_intuition`
- `minimal_vector_or_plot`

What this figure is doing cognitively:
- it translates symbolic structure into spatial or causal structure
- it should explain the role of quantities, not restate the theorem
- it is especially useful when the proof depends on geometry, invariance, partitioning, or monotonic movement

Best paper slot:
- `method`: useful when the theoretical picture is part of the main technical story
- `analysis`: strongest when the theory is interpreted after the core method is already known
- `appendix`: common when the theory is important but not needed for first-pass reading
- `intro`: rare, but possible if the paper's main claim is fundamentally theoretical

Recommended panel recipe:
- visual metaphor
- key quantity
- intuitive consequence

Design priorities:
- minimalism matters more here than elsewhere
- the reader should know exactly which quantity to track
- labels should attach to shapes or directions, not float as prose

Typical failure mode:
- the figure becomes another theorem statement in disguise

Refinement lever:
- remove most symbolic detail and keep only the quantities the viewer must track

## Default Answer Pattern

When the user does not specify a figure family, propose:

1. one direction that solves the logic gap most directly
2. one direction that is easiest for readers to scan
3. one direction that is strongest for persuasion

Then recommend one of the three based on the user's `figure_slot` and `density`.
