# Figure Taxonomy Reference

This file contains the text reference for the figure classification system. Use it when turning a vague figure need into a structured figure plan.

## Recommended Retrieval Order

When the user is vague, classify in this order:

1. `Reader Question`
2. `Logical Gap Type`
3. `Function / Narrative Role`
4. `Visual Rhetoric`
5. `Visual Grammar / Style`
6. `Evidence Type`
7. `Density / Layout`
8. `Editing Lever`

This order is better than starting from style, because users usually describe what is still unclear, not what drawing primitive they want.

## 1. Reader Question

- `why_is_this_problem_real`
  - Use when the reader still does not buy the problem, failure mode, or practical need.
- `can_i_see_the_core_case`
  - Use when the core intuition is best conveyed through one example, counterexample, or walk-through.
- `how_does_the_idea_become_a_model`
  - Use when the idea is understandable in words, but the jump to variables, losses, modules, or objectives feels abrupt.
- `what_are_the_parts_and_data_flow`
  - Use when the reader needs a stable map of components, interfaces, and data flow.
- `what_happens_over_time`
  - Use when the contribution is procedural: training loop, inference process, retrieval chain, agent interaction, or iterative update.
- `what_evidence_should_i_believe`
  - Use when the job of the figure is persuasion through comparison, ablation, protocol, or case evidence.
- `what_is_the_proof_intuition`
  - Use when a theorem, bound, or proof needs a visual explanation.
- `what_is_the_main_message`
  - Use when the figure should compress the main takeaway into one memorable message.

## 2. Logical Gap Type

- `phenomenon_to_problem`
  - Bridge from observed phenomenon to a well-defined problem.
- `problem_to_hypothesis`
  - Bridge from problem statement to the key hypothesis or principle.
- `hypothesis_to_mechanism`
  - Bridge from high-level intuition to a concrete mechanism.
- `mechanism_to_objective`
  - Bridge from mechanism to variables, constraints, losses, or objective terms.
- `objective_to_algorithm`
  - Bridge from the mathematical target to a computable procedure.
- `algorithm_to_system`
  - Bridge from a local algorithmic step to the full system or workflow.
- `system_to_evidence`
  - Bridge from system description to believable evidence.
- `theory_to_intuition`
  - Bridge from theorem or bound to a visual picture.

## 3. Function / Narrative Role

- `idea_motivation_or_problem_gap`
  - Expose the limitation, bottleneck, contradiction, failure case, or missing signal.
- `toy_example_or_case_evidence`
  - Use one concrete case to explain the central intuition.
- `method_overview_or_architecture`
  - The main framework figure or module overview.
- `idea_to_model_logic_bridge`
  - Make the bridge from intuition to variables, modules, losses, constraints, or search operators explicit.
- `training_or_inference_process`
  - Explain training, inference, retrieval, planning, or iterative refinement over time.
- `data_or_benchmark_construction`
  - Explain how a dataset, benchmark, task family, or evaluation protocol is constructed.
- `result_or_ablation_evidence`
  - Support a claim through quantitative or qualitative evidence.
- `theory_or_proof_intuition`
  - Provide a visual interpretation of theory.
- `general_explanatory_figure`
  - A fallback category for explanatory figures that do not fit neatly elsewhere.

## 4. Visual Rhetoric

- `contrast_before_after`
  - Before vs after, failure vs success, old vs new.
- `progressive_stage_reveal`
  - Reveal the explanation in stages.
- `causal_chain`
  - Make cause -> mechanism -> outcome explicit.
- `decompose_then_recompose`
  - Split the system into pieces, then show how they recombine.
- `zoom_in_zoom_out`
  - Move between global overview and local detail.
- `mapping_alignment`
  - Align two spaces, modalities, roles, or state sets.
- `feedback_loop_or_cycle`
  - Emphasize iteration, recurrence, or feedback.
- `search_space_or_design_space`
  - Show a frontier, family map, design space, or trade-off structure.
- `storyboard_case_walkthrough`
  - Walk through one concrete example like a storyboard.
- `direct_exposition`
  - Plain explanation with minimal rhetorical structure.

## 5. Visual Grammar / Style

- `block_arrow_pipeline`
  - Block modules connected by arrows.
- `input_output_triptych`
  - Input / intermediate / output or 3-part explanation board.
- `graph_or_network_schematic`
  - Graph, topology, relation network, or structured state diagram.
- `sequence_token_timeline`
  - Ordered steps, token progression, timeline, or recurrent sequence.
- `image_grid_or_qualitative_panel`
  - Image board, qualitative strip, or example gallery.
- `matrix_heatmap_or_chart_hybrid`
  - Heatmap, matrix, chart board, or mixed evidence panel.
- `equation_diagram_hybrid`
  - Equations, variables, and visual mechanism in one board.
- `trajectory_or_environment_scene`
  - Trajectory, environment, planning, robotics, or embodied setting.
- `wide_landscape_multi_panel`
  - Wide horizontal figure with several coordinated panels.
- `vertical_stack`
  - Top-to-bottom layered explanation.
- `minimal_vector_or_plot`
  - Sparse theory-style diagram or minimal plot.

## 6. Evidence Type

- `toy_case_or_counterexample`
  - Synthetic or toy support.
- `real_case_study`
  - Concrete real example.
- `quantitative_result_plot`
  - Quantitative curves, bars, or metrics.
- `ablation_or_mechanism_probe`
  - Ablation, probing, or mechanism analysis.
- `benchmark_or_dataset_protocol`
  - Benchmark or protocol explanation.
- `theory_or_bound_support`
  - Formal support such as bounds or proof-related evidence.
- `visual_output_evidence`
  - Qualitative visual results.
- `system_trace_or_log`
  - Workflow traces, trajectories, logs, or state transitions.
- `conceptual_support`
  - Conceptual support that is explanatory rather than empirical.

## 7. Density / Layout

- `hero_single_panel`
  - Strong, memorable main figure with one dominant frame.
- `wide_ribbon`
  - Wide ribbon-like method figure.
- `two_stage_split`
  - Two major blocks, often concept vs implementation.
- `2x2_grid`
  - Symmetric multi-panel board.
- `dense_reference_sheet`
  - Dense technical summary or appendix-style board.
- `vertical_story`
  - Narrative stack.
- `landscape_story`
  - Horizontal story progression.

## 8. Editing Lever

- `simplify_text_load`
  - Remove excess text and push explanation into structure.
- `strengthen_flow`
  - Make the dominant reading path obvious.
- `add_case_anchor`
  - Introduce one memorable example.
- `add_intermediate_state`
  - Show the missing intermediate representation or variable.
- `make_bridge_explicit`
  - Make the logic jump visible.
- `tighten_color_semantics`
  - Ensure color has stable meaning.
- `separate_evidence_from_method`
  - Avoid mixing architecture and evaluation too early.
- `reduce_panel_redundancy`
  - Remove repeated panels that do not add information.
- `increase_reader_guidance`
  - Add numbering, phase labels, or callouts that support reading order.

## Practical Rule

When the user says:

- "the motivation is weak" -> start with `why_is_this_problem_real`
- "the jump to the model is abrupt" -> start with `how_does_the_idea_become_a_model`
- "the method is hard to follow" -> start with `what_are_the_parts_and_data_flow`
- "the process is unclear" -> start with `what_happens_over_time`
- "the evidence is not convincing" -> start with `what_evidence_should_i_believe`
- "the theory is too dense" -> start with `what_is_the_proof_intuition`
