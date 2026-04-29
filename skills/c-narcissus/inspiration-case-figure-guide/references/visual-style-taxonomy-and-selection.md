# Visual Style Taxonomy and Selection Protocol

Use this reference when the conversation reaches visual language, style-family selection, candidate-board design, or image-prompt construction.

## Core rule: style is chosen after effect

Do not start a scientific figure from style. First define the reader effect, paper claim, figure role, and layout logic. Then choose a style that helps the reader interpret the figure quickly and safely.

A style choice should answer:

1. What does this style help the reader understand faster?
2. What paper slot does it fit: introduction hero, method overview, case walkthrough, result intuition, rebuttal, or appendix?
3. What reviewer risk does it create: too playful, too decorative, too dense, too photorealistic, too product-like, or too vague?
4. How robust is it for ChatGPT Images 2.0 generation?

## Mandatory style-family matrix

When style is a live decision, present 4–8 relevant styles from the matrix below and recommend one default. Do not present every style every time.

| Style family | Best for | Strength | Risk | Prompt cues |
|---|---|---|---|---|
| Clean editorial flat | Intro hero, cross-domain explanation, concept bridge | Clear, paper-safe, readable | May feel generic if not anchored by a strong metaphor | clean flat scientific illustration, minimal labels, soft shadows, high contrast |
| Formal architecture schematic | Technical method overview, ML/system papers | Reviewer-safe, precise module relations | Can become dry or box-heavy | formal architecture diagram style, structured modules, crisp arrows, restrained palette |
| Mechanism snapshot | Abstract algorithm intuition, core mechanism | Shows action and causality | May omit implementation detail | central mechanism, callouts, cause-effect arrows, compact mini-panels |
| Premium scientific illustration | High-impact intro figure, interdisciplinary journal | Polished, memorable, publication-facing | Can become over-rendered or decorative | premium scientific illustration, clean depth, refined lighting, minimal text |
| Isometric / soft 3D | Systems, networks, spatial relations, layered processes | Makes depth, hierarchy, and components tangible | Risk of toy-like or product-render look | isometric 3D scientific diagram, soft depth, clean materials, controlled perspective |
| Low-poly / abstract 3D | Conceptual landscapes, optimization, latent spaces | Good for abstract spaces and gradients | Can become vague if not panel-anchored | abstract low-poly 3D landscape, scientific metaphor, sparse labels |
| Cartoon / comic-lite | Case walkthrough, failure mode story, human-centered examples | Intuitive, friendly, memorable | May look childish or less serious | mature editorial cartoon style, restrained, not childish, research-paper appropriate |
| Storyboard panels | Before/after, one-case evolution, intervention path | Strong temporal logic | Can become too narrative if mechanism is missing | storyboard scientific figure, sequential panels, short labels, clear transitions |
| Tile / card / mosaic board | Taxonomy, multiple cases, method components, comparison grid | Great for modular comparison and scannability | Can feel like a poster if hierarchy is weak | tile-based scientific infographic, modular cards, consistent icons, grouped hierarchy |
| Paper-cut / layered collage | Inspiration-source, real-world-to-model bridge, multi-source intuition | Distinctive and approachable | Can look decorative if overused | layered paper-cut scientific illustration, clean edges, limited palette |
| Blueprint / technical drawing | Method mechanics, system process, design constraints | Precise, technical tone | Too cold for broad readers | blueprint-style scientific schematic, thin lines, labeled components, minimal text |
| Dashboard / interface metaphor | Evaluation logic, monitoring, data pipeline, decision support | Makes state, metrics, and feedback loops visible | Risk of fake UI clutter | clean research dashboard metaphor, abstract panels, no fake app details |
| Mini-evidence infographic | Need to connect concept to empirical signal | Bridges idea and evidence | Can be too dense for first-chapter hero figure | mini plots, small evidence cards, concise annotations, caption-heavy |
| Minimal line-art schematic | Theory, equation-to-intuition bridge, formal argument | Extremely readable and safe | May look plain | minimal line-art scientific schematic, sparse labels, strong whitespace |
| Photorealistic / cinematic | Rare: physical experiments or concrete material scenes | High realism and attention | Usually risky for conceptual ML figures; noise and fake detail | use only when concrete realism is necessary; avoid photorealistic noise |

## Default recommendation heuristics

If no style preference is supplied, choose the safest style according to the paper slot:

- First chapter / introduction hero: **clean editorial flat** or **premium scientific illustration**.
- Technical method figure: **formal architecture schematic** or **mechanism snapshot**.
- Case schematic: **storyboard panels** or **cartoon / comic-lite** if human intuition matters.
- Inspiration-source figure: **paper-cut / layered collage**, **clean editorial flat**, or restrained **premium scientific illustration**.
- Multi-case / taxonomy / component comparison: **tile / card / mosaic board**.
- System / network / layered pipeline: **isometric / soft 3D** only if depth helps; otherwise formal schematic.
- Abstract latent space / optimization intuition: **low-poly / abstract 3D** only if the spatial metaphor is central.
- Reviewer-sensitive venue: prefer **formal architecture schematic**, **mechanism snapshot**, **minimal line-art**, or **clean editorial flat**.

## Style-board protocol

When style selection is useful, create a style board with 3–5 candidates. Hold fixed:

- figure thesis
- panel structure
- labels
- color semantics
- anchor case

Vary only the style family. For each style candidate, provide:

- style name
- why it helps the paper claim
- what could go wrong
- best paper slot
- prompt cue
- recommendation score: high / medium / low

Always include one `默认推荐风格` with reasons.

## Reference image use for style

If the user provides reference figures, analyze their style as principles rather than copying them:

- line weight / shape language
- depth model: flat, layered, isometric, full 3D
- object realism: symbolic, cartoon, semi-realistic, photorealistic
- color semantics
- density and whitespace
- label placement
- panel rhythm
- seriousness / playfulness level

Do not copy distinctive artwork, exact composition, branding, or unique labels from references.

## Style prompt safety rules

- Avoid vague style-only prompts such as `make it beautiful`, `high-tech`, or `Nature style` without concrete visual rules.
- Specify style through concrete features: line weight, depth, material, panel rhythm, label density, palette role, and icon realism.
- Use `research-paper appropriate`, `minimal text`, and `clear hierarchy` in most prompts.
- For cartoon style, add `mature`, `restrained`, `not childish` unless the paper context explicitly wants playful visuals.
- For 3D style, add `controlled perspective`, `clean surfaces`, `no photorealistic clutter`, and `labels remain flat/readable`.
- For tile/card style, add `clear grouping`, `one idea per card`, and `dominant central thesis`.
- For premium illustration, add `not decorative`, `mechanism-driven`, and `paper-safe`.

## State fields to update

When style is selected or explored, update:

- `figure_decisions.style_family`
- `figure_decisions.style_candidates_considered`
- `figure_decisions.default_style_recommendation`
- `figure_decisions.style_rationale`
- `figure_decisions.style_risks`
- `visual_candidate_history.varied_axis: style_family`
