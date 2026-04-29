# Image Generation Policy

## Banned Outputs

Do not generate or provide:

- SVG
- inline SVG
- Mermaid
- TikZ
- Graphviz
- HTML/CSS diagrams as final figure
- Python/matplotlib diagrams as final figure
- code that the user must render as the figure

## Required Route

Use ChatGPT Images 2.0 / available image generation for final visuals.

In ChatGPT web: use Create Image / image generation.

In other environments: if no image generation API/tool exists, output a text-only prompt and tell the user to run it in ChatGPT Images 2.0 or another image-generation API.

## Text in Generated Figures

Image models may distort dense text. Therefore:

- use minimal labels
- keep labels short
- avoid equations unless central and simple
- put long explanation in the caption, not inside the image
- if exact typography is critical, generate a near-final visual with minimal text and ask for a separate human/layout pass outside this skill

## Visual-first exploratory boards

Image generation is not reserved only for the final polished figure. If the user needs to choose figure direction, layout, visual style, metaphor, or density, the assistant may use an exploratory `IMAGE_ONLY` multi-candidate board earlier in the workflow.

These boards must still obey turn separation: the preceding text turn explains what stays fixed and what varies; the board turn contains images only; the following text turn reviews candidates and updates state.
