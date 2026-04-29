# Paper Framework Figure Studio Pro

A professional scientific-figure skill for creating **paper framework diagrams** through a guided, stateful workflow.

## Best for

- method overview figures
- paper framework diagrams
- top-conference / top-journal style exploration
- iterative image-based refinement
- users who want multiple style options before deciding

## Why it is different

Unlike one-shot prompt generators, this skill behaves like a **figure studio**:

- reads a deep-reading report or method description
- constructs a Figure Brief
- generates **multiple candidate images** before style decisions
- records user choices and rejected directions
- keeps text planning separate from image generation
- asks for user confirmation before every new generation batch
- can finish by drafting caption, legend, and panel explanation text

## Rendering rule

Framework figures must be rendered through **OpenAI native image generation**. SVG / mermaid / graphviz / tikz are not used as fallbacks for figure-rendering rounds.

## Strict interaction rule

This skill enforces a hard split between **text turns** and **image turns**. It will first explain the next batch and ask whether to generate it. Only after the user confirms will it perform the next separate image-generation action.
