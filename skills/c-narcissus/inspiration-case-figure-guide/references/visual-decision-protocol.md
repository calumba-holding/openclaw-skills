# Visual Decision Protocol

Version: 2.7.0

Use this reference whenever the next decision is visual.

## Visual-decision-first rule

If the user is deciding among style, layout, density, visual metaphor, figure direction, or image direction, do not rely only on prose. Prepare an exploratory candidate image board when the choice is primarily visual.

Do not postpone all visual comparison until the final figure-generation round. Early boards are allowed and encouraged when they help the user choose a direction.

## Candidate counts

- Early visual decision board: 3–5 candidates
- Exploration: 3–5 candidates
- Narrow refinement: 2–4 candidates
- Final repair: 1–2 candidates

## Batch design

Each board should vary exactly one dominant axis unless the user explicitly asks for a broad first exploration:

- figure direction / category
- layout skeleton
- style family, using the visual style taxonomy when style is the varied axis
- density
- visual metaphor
- evidence integration
- label policy
- color semantics
- reviewer tone

Keep the paper thesis, selected scheme, and anchor case fixed unless the user asks to change them.

## Style-family board

When the visual decision is style, offer a compact style-family board with 4–8 relevant choices. Include mainstream choices when they fit the figure: clean editorial flat, formal architecture schematic, mechanism snapshot, premium scientific illustration, isometric / soft 3D, low-poly abstract 3D, cartoon / comic-lite, storyboard panels, tile / card / mosaic board, paper-cut collage, blueprint / technical drawing, dashboard metaphor, mini-evidence infographic, and minimal line-art.

For each style candidate, state: best fit, main benefit, main risk, prompt cue, and suitability for the current paper slot. Always provide `默认推荐风格`.

Do not treat style as decoration. Tie every style option to reader effect, paper claim, reviewer risk, and generation robustness.

## Text-only pre-board / pre-generation reply

Before a batch, state:

- what is fixed
- what varies
- how many candidates will be generated
- whether this is an exploratory decision board or the final candidate batch
- what the user should evaluate after images appear
- the rendering rule: native image generation / ChatGPT Images 2.0; no SVG or code fallback

## Image-only generation turn

The generation turn contains no prose. Generate the images only.

## Post-image reply

After generation, ask the user to choose by image number / letter and comment on:

- layout clarity
- paper-claim fit
- mechanism clarity
- density / clutter
- text readability
- style fit
- whether the figure feels appropriate for the target paper slot


## Default recommendation in visual decisions

A visual decision reply must not be a neutral catalog only. It should include:

- fixed elements
- varied axis
- candidate count
- evaluation criteria
- `默认推荐路线` or `我建议优先选择`

Choose the default based on reader effect, panel clarity, paper-claim fit, reviewer risk, and likely image-generation robustness.

## Reference images in visual decisions

At suitable visual decision points, ask whether the user has 1–3 reference images. If supplied, analyze:

- reading path
- panel structure
- hierarchy
- density
- label policy
- color semantics
- metaphor / object vocabulary
- what to borrow as design principles
- what not to copy

Use reference images to improve the current figure, not to imitate the source exactly. If no references are supplied, continue with the best inferred direction.


## Related reference

Use `visual-style-taxonomy-and-selection.md` for detailed style choices, defaults, risks, and prompt cues.

## Visual decision board types

Use `visual-first-decision-board-protocol.md` for the full rules. Supported early boards include:

- figure-direction board;
- layout board;
- style board;
- metaphor board;
- density board;
- refinement board.

A board is a decision aid, not the final polished figure.
