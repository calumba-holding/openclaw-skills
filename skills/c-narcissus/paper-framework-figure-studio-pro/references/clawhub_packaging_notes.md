# ClawHub Packaging Notes

This bundle is prepared for ClawHub / OpenClaw style packaging:

- directory name matches the publish slug: `paper-framework-figure-studio-pro`
- `SKILL.md` uses YAML frontmatter
- the frontmatter `name` is the lowercase publish-safe skill identifier
- the human-readable display name is stored in `metadata.display_name`
- the license is declared as `MIT-0` and the full MIT No Attribution text is included in `LICENSE`
- the package version is recorded in both `SKILL.md` metadata and `VERSION`
- OpenClaw runtime metadata is declared under `metadata.openclaw`
- no conflicting license terms are added inside `SKILL.md`

If a publish UI asks separately for display name, use:

- **Slug**: `paper-framework-figure-studio-pro`
- **Name / Display Name**: `Paper Framework Figure Studio Pro`


## Image-rendering constraint

This skill is intentionally authored for **native image generation** rather than SVG synthesis. In hosts that support separate image actions, the recommended path is a distinct **Create image** step, ideally using **Thinking** or **Extended Thinking / images with thinking** when available for complex framework figures.


Additional host policy for v1.2.1:
- ChatGPT web: keep the user in chat, prefer Extended Thinking or the strongest available thinking-assisted image path, and do not ask the user to manually switch tools before generation.
- IDE / API hosts such as OpenClaw, Codex, and Trae: use OpenAI ChatGPT Images 2.0 at minimum; if credentials are missing, stop and ask the user to configure an OpenAI API key before any generation round.
- Never downgrade framework-figure rendering to SVG.
