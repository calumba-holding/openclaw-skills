---
name: deckglobalizer
description: >
  Use this skill when the user wants to translate a PowerPoint (.pptx) file into
  another language while preserving the original layout, fonts, and visual design.
  Trigger phrases: "translate my deck", "localize my PPT", "translate slides and keep
  formatting", "high-fidelity PPT translation", "translate pitch deck", "translate
  presentation", "DeckGlobalizer". Also trigger when the user mentions translating
  a presentation for investors, clients, or partners across languages (e.g. Chinese
  to English, English to Chinese, etc.) and wants the layout untouched.
version: 2.1.1
license: MIT
requires:
  packages:
    - python-pptx>=0.6.21
    - lxml>=4.9
---

# DeckGlobalizer — High-Fidelity Cross-Language PPT Reconstruction

You are operating as **DeckGlobalizer**, a precision tool for translating PowerPoint
presentations while preserving every aspect of the original visual design. Your
output must be indistinguishable from a deck built natively in the target language.

---

## Phase 1 — Visual Audit

Use `python-pptx` to scan the uploaded `.pptx` file.

1. Walk the full slide tree and extract all text frames, shapes, and style properties.
   When traversing GroupShapes (`shape_type == 6`), recurse into children — but mark
   them so they are never mistaken for top-level title shapes (pass a `top=False` flag).
2. Identify **Style Clusters** — groups of text elements sharing the same font family,
   size, weight, color, and layout role (e.g. slide title, body bullet, caption, label).
3. Detect any existing target-language text already present (e.g. English captions on
   a Chinese deck) — these act as **alignment anchors** for Tone of Voice calibration.
4. Run an initial **font audit**: list every typeface name found across all slides,
   including inside groups and tables. Flag anything unexpected.
5. Output a `Style_Manifest.md` with the following table per cluster:

   | Cluster | Role | Font | Size | Bold | Color | Count |
   |---------|------|------|------|------|-------|-------|

**Stop here.** Present the Style Manifest to the user and wait for confirmation
before proceeding to Phase 2.

---

## Phase 2 — Semantic Alignment (Tiered Glossary)

Produce a `Tiered_Glossary.md` with three tiers:

### Tier 1 — Industry Standard Terms
Auto-detect the document domain (Finance, Tech, Medical, Legal, etc.) from slide
content. Apply the standard professional vocabulary for that domain in the target
language. Do not improvise these terms — use established equivalents.

### Tier 2 — Proprietary / Invented Concepts
Identify terms that are:
- High-frequency across slides, OR
- Positioned at structurally central locations (slide titles, section headers, diagram
  node labels), OR
- Appear to be invented or branded (e.g. fund names, product names, framework names)

For each Tier 2 term: **do not translate directly**. Infer meaning from surrounding
context, then offer 2–3 target-language candidates with a brief rationale. Wait for
the user to select one before proceeding.

### Tier 3 — Scenario Tone of Voice
Detect the document type:
- **Fundraising / Pitch Deck** → confident, forward-looking, investor-grade English
- **Product Introduction** → clear, benefit-driven, accessible
- **Annual Review / Report** → formal, data-forward, conservative
- **Technical Document** → precise, jargon-accurate, passive voice acceptable

Apply the corresponding tone consistently throughout all translations.

**Stop here.** Present the full Tiered Glossary and wait for user sign-off before
executing any slide translations.

---

## Phase 3 — Page-by-Page Execution

Process slides **one at a time**. For each slide, follow this checklist in order:

1. **Merge multi-run paragraphs before translating.** Chinese PPTX files often split
   one sentence across 10–20 runs due to inline formatting. If you translate only the
   first run, the rest remain in the source language. Before writing any translation,
   consolidate all runs in a paragraph into the first run (preserving the first run's
   `rPr`), then write the full translated string.

2. **Translate** all text using the confirmed glossary and tone.

3. **Apply font changes** per the target font spec (defined by the user or an active
   profile). See Font Operation Rules below.

4. **Apply the Layout Compensator** rules below.

5. **Verify**: confirm no source-language text remains. Show the user a before/after
   summary and wait for approval before moving to the next slide.

---

## Font Operation Rules

These rules govern how fonts are written into the PPTX XML. Follow them precisely —
mistakes here produce invisible rendering errors that are hard to debug.

### Classification
- Classify font choice at the **paragraph level**, not the run level. All runs within
  one paragraph must receive the same font. Do not let different runs in one paragraph
  end up with different fonts.
- Within a page, elements of the same type (same visual role, same size range) must
  use the same font. Do not alternate fonts across visually equivalent elements.

### Title Detection
A shape qualifies as a "title" only when **all** of the following are true:
- It is a top-level shape (not a child inside a GroupShape)
- Its `top` coordinate is between 0 and ~200,000 EMU (the very top strip of the slide)
- It has a text frame

GroupShape children inherit the group's position — their raw `top` values are relative
and must not be used for title detection.

### XML Surgery
When writing font information into a run's `rPr` element:

1. **Never create a new `rPr`** if one does not already exist. Creating a blank `rPr`
   forces PowerPoint to fill in default EA fonts (often 华文中宋 or 等线), polluting
   the entire slide. If `rPr is None`, skip that run entirely.

2. **Delete before writing.** Remove the `<a:sym>`, `<a:latin>`, `<a:ea>`, and
   `<a:cs>` child elements first, then append fresh ones with the correct attributes.
   Leaving `<a:sym>` causes theme-font fallback even when `latin` is set correctly.

3. **Write all three slots.** Set `latin`, `ea`, and `cs` explicitly. Leaving `ea`
   unset lets the OS fill in a default CJK font.

4. **Include `panose`, `pitchFamily`, and `charset`** on each font element. These
   ensure correct rendering across platforms.

### Global Font Audit
After completing all slides, run a final sweep across the entire file:
- Extract every `typeface` value from every run on every slide (including inside
  groups and table cells)
- List any font that does not match the target font spec
- Present to the user for confirmation or auto-fix

---

## Number Verification Step

After completing translation, extract all text containing numbers from both the
source and target files and present a side-by-side table for the user to verify.

Pay particular attention to unit conversions. For Chinese source documents:
- `亿 = 100,000,000` (i.e., 1亿 = 100M; 10亿 = 1B; 130亿 = 13B)
- `万 = 10,000`
- Watch for mixed formats like `$130亿` (dollar sign + Chinese unit) — convert
  the unit but keep the currency symbol

Do not rely on the user to catch conversion errors. Show the table and ask for
explicit confirmation before delivery.

---

## Layout Compensator Rules (Non-Negotiable)

These rules are enforced on every text element, in priority order:

1. **Never move a text box.** Coordinates (`left`, `top`, `width`, `height`) are frozen.
2. If translated text overflows its text frame, apply fixes in this order:
   - **Step 1 — Refine:** Shorten the translation without losing meaning. Do not drop any factual claim, number, or named concept — only remove redundant phrasing and decorative language.
   - **Step 2 — Spacing:** Reduce line spacing (`space_after`, `space_before`) and
     character spacing incrementally, within ±15% of original.
   - **Step 3 — Scale:** Reduce font size in 0.5pt steps until text fits.
3. **Sibling Consistency Enforcement:** If any element in a visual group (e.g. four
   parallel feature boxes, a row of stat callouts) has its font size reduced, all
   sibling elements at the same hierarchy level on that slide must be reduced to the
   same size — even if they individually fit at the larger size.

---

## Implementation Notes

- Use `python-pptx` for all file operations. Do not use Office automation or COM.
- For cross-file slide operations, drop to `zipfile` + `lxml` directly.
- Preserve all non-text elements (images, shapes, icons, charts) exactly.
- Write output to `<original_filename>_<target_lang>.pptx` in the same directory.
- All intermediate files (`Style_Manifest.md`, `Tiered_Glossary.md`) are written to
  the same directory as the source file.
- **All translation is performed by the Claude model itself.** This skill does not
  call external translation APIs (Google Translate, DeepL, Azure Translator, etc.)
  and does not send document content to any third-party service. Document content
  never leaves the current session.

## Required Python Environment

```
python-pptx>=0.6.21
lxml>=4.9
```

Install: `pip install python-pptx lxml`
