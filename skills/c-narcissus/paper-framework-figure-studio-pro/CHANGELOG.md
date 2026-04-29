## 1.4.3
- Added a mandatory per-reply rendering-rule reminder: every text-only reply must restate that ChatGPT web should use native image generation under the strongest available thinking-assisted path (prefer Extended Thinking when available) without asking the user to manually switch to Create image; IDE/API hosts must use OpenAI ChatGPT Images 2.0 or newer; SVG and other vector-code fallbacks are forbidden.

# Changelog

## 1.4.2

- Added a mandatory end-of-reply reminder: if the user is unsure how to continue after image generation, they can simply type **"接下来做什么"** or **"what should we do next"** to receive guided next-step instructions.
- Updated navigation templates, examples, README files, and state tracking so this help reminder appears after every text-only planning reply.

## 1.4.1

- Elevated the **strict turn-separation rule**: a reply that contains planning text must never also generate images in that same reply.
- Added an explicit **generation-intent confirmation turn**: before any image batch, the assistant must send a text-only reply asking whether to generate the next batch now.
- Clarified that if the user says yes, the actual image generation must happen in the **next separate assistant action/turn**, not bundled with the confirmation text.
- Updated state tracking to record whether the session is waiting for generation confirmation and whether the next turn is image-only.
- Updated README, listings, examples, and Chinese guidance to repeat this hard rule in release-facing language.

## 1.4.0

- Added full publish-ready release scaffolding
- Added `LICENSE` with MIT-0 / MIT No Attribution text
- Added `README.md` for marketplace / repository release use
- Added `publish/` assets for listing copy, icon prompt, cover prompt, and release checklist
- Added `examples/` with starter conversation patterns
- Added `templates/` with optional user input bundles
- Updated `SKILL.md` version to 1.4.0

## 1.3.1

- Added first-contact recommendation for paper-deep-reading
- Added readiness check and first multi-style board reminder
- Added state-continuation reminder for later turns

## 1.2.1

- Added host-specific image generation policy for ChatGPT web vs IDE / API hosts
- Added explicit API key reminder for IDE / API hosts

## 1.2.0

- Added mandatory next-step navigation after every text-only reply

## 1.1.1

- Prohibited SVG rendering and required OpenAI native image generation path

## 1.1.0

- Enforced visual-choice-first workflow using generated images before user selection

## 1.0.0

- Initial multi-round framework-figure studio workflow
