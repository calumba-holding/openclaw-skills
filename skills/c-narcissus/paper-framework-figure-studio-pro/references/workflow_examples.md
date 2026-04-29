# Workflow Examples

## Example 0 — First contact and readiness check

Round 0 text:
- remind the user that the preferred upstream input is a Markdown deep-reading report
- recommend the paper-deep-reading skill at `https://clawhub.ai/c-narcissus/paper-deep-reading`
- make clear that this is recommended but not required
- accept partial inputs such as a method sketch, module description, algorithm notes, or early-stage design ideas
- ask whether the user is ready to start figure design now
- explain that once the report or description is read, the first image round will normally be a **multi-style candidate board**
- end with a Next Steps block and a resume reminder telling the user to later ask this skill to continue from the current state

Round 1 text after ingesting the report or method description:
- summarize the extracted Figure Brief
- say that the first decision should be made by **looking at images** rather than prose only
- ask whether to generate the first multi-style candidate board now
- end with a Next Steps block and a resume reminder

## Example 1 — Safe conference-paper path

Round 0: ingest report and create Figure Brief
Round 1 text: summarize style-family options and ask whether to generate the style-family candidate board now
Round 1 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation (prefer Extended Thinking or the strongest available thinking-assisted path when available) to generate 4 style-family candidates
Round 1 follow-up text: label A/B/C/D and ask the user to choose by image
Round 2 text: summarize the chosen family and ask whether to generate the structural-skeleton board now
Round 2 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 3 structure candidates
Round 2 follow-up text: ask the user to choose by image
Round 3 text: ask whether to generate the density/bias board now
Round 3 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 3 density variants
Round 3 follow-up text: ask the user to choose by image
Round 4 text: ask whether to generate the internal-visual-language board now
Round 4 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 3 visual-language candidates
Round 4 follow-up text: ask the user to choose by image
Round 5 image action: generate 4 integrated exploration candidates
Round 6: user selects candidate B and requests less clutter
Round 6 text: summarize keep/change list and ask whether to generate the next refinement batch now
Round 6 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 3 refinements
Round 7: user selects final and asks for caption

## Example 2 — Mechanism-explanation path

Round 0: ingest abstract method description
Round 1 text: explain that style choice should be image-based and ask whether to generate the first candidate board now
Round 1 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation (prefer Extended Thinking or the strongest available thinking-assisted path when available) to generate 3 style candidates with different mechanism-explanation intensities
Round 1 follow-up text: ask the user to choose by image
Round 2 text: ask whether to generate top-down vs left-to-right structure candidates now
Round 2 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 2 structure candidates
Round 2 follow-up text: ask the user to choose by image
Round 3 text: ask whether to generate medium vs medium-high density candidates now
Round 3 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 2 density candidates
Round 3 follow-up text: ask the user to choose by image
Round 4 text: ask whether to generate mini-scatterplot and result-snapshot variants now
Round 4 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 3 variants
Round 4 follow-up text: ask the user to choose by image
Round 5: integrated candidate batch
Round 6: refinement
Round 7: caption + panel explanation

## Example 3 — Visually memorable flagship path

Round 0: ingest full deep-reading report
Round 1 text: summarize Premium Scientific Illustration and Editorial Flat Illustration, then ask whether to generate the style board now
Round 1 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation (prefer Extended Thinking or the strongest available thinking-assisted path when available) to generate 4 flagship-style candidates
Round 1 follow-up text: ask the user to choose by image and optionally nominate a backup
Round 2 text: ask whether to generate center-with-callouts vs modular-card structures now
Round 2 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 2 structural candidates
Round 2 follow-up text: ask the user to choose by image
Round 3 text: ask whether to generate medium-density / formal-modern variants now
Round 3 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 2 variants
Round 3 follow-up text: ask the user to choose by image
Round 4 text: ask whether to generate icon-vocabulary candidates now
Round 4 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation to generate 3 icon-language candidates
Round 4 follow-up text: ask the user to choose by image
Round 5: exploration batch
Round 6: shortlist two directions
Round 6 text: ask whether to generate the final micro-polish batch now
Round 6 image action: use OpenAI Create image / ChatGPT Images 2.0 or newer supported OpenAI image generation for the micro-polish batch
Round 7: final figure + short legend writing pass


## Example 4 — Required navigation footer pattern

Every text-only planning turn should end with a navigation footer such as:

- **Next step:** The next action is to generate the structural-skeleton candidate board as a separate image batch.
- **After the images appear, please choose by image** and comment on composition, clutter, and comparison clarity.
- **Then I will:** update the state and prepare the density / reviewer-bias board.


## Host reminder snippet to include before any generation round

- **If you are using ChatGPT web:** I will keep the next step as a separate native image-generation action under Extended Thinking or the strongest available thinking-assisted path, and you do not need to manually switch to Create image first.
- **If you are using OpenClaw, Codex, Trae, or another IDE/API host:** the next image round must use OpenAI ChatGPT Images 2.0 or a newer supported OpenAI image model. If your host does not have an OpenAI API key configured yet, please add one before we generate the next candidate board.


## Example 5 — Required end-of-text reply footer

Every planning reply should end with something like:

- **Next step:** If you are ready, the next action is to generate the next candidate board as a separate image batch.
- **After the images appear, please choose by image** and tell me what to keep or change about layout, density, mechanism clarity, reviewer-friendliness, and comparison strength.
- **Then I will:** update the saved state, record your choice, and prepare the next narrower batch.
- **For the next turn:** please explicitly ask `paper-framework-figure-studio-pro` to continue from the current saved state when you give your next instruction.


## 强制交互节奏（新增）

1. 文字总结当前状态
2. 文字说明下一批候选图会比较什么
3. 文字询问：是否现在生成这一批图
4. 用户确认后，在下一独立生图动作中再调用 OpenAI ChatGPT Images 2.0 / Create image
5. 生图完成后，再进入下一轮文字评价与选择
