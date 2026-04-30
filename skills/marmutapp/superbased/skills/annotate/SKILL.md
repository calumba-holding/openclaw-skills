---
name: annotate
description: Add visual annotations to screenshots for bug reports, code reviews, and documentation. Use when highlighting areas of interest, marking regressions, or creating annotated screenshots.
---

Use `superbased_annotate` to add programmatic annotations to captures.

**Annotation types:**
- `rectangle`: bounding box outline around an area
- `highlight`: semi-transparent colored overlay
- `blur`: pixelate a region (useful for redacting manually)
- `text`: text label at a position
- `arrow`: arrow pointing from one location to another

**Workflow:**
1. Capture a screenshot or get a `captureId` from gallery
2. Call `superbased_annotate` with the `captureId` and an `annotations` array
3. Set `save: true` to modify the original, or `false` (default) to return annotated image without changing the original

**Example for bug reporting:**
```
superbased_annotate captureId=42 annotations=[
  {type:"rectangle", x:100, y:200, width:300, height:50, color:"#ff0000"},
  {type:"text", x:100, y:190, text:"Bug: misaligned button", color:"#ff0000"},
  {type:"arrow", x:250, y:180, toX:250, toY:200, color:"#ff0000"}
]
```
