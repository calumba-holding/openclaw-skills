---
name: test-case-design
description: This skill should be used when generating test cases, writing test cases, designing test cases, supplementing exception scenarios and boundary values, designing complex interaction test cases, outputting standardized test cases, compatibility testing, adaptation testing, API testing, security testing, UI visual testing, mobile/App/mini-program/H5/desktop/PC Web testing, linkage testing, or routing testing. Only focuses on writing test cases, does not involve test plans, test strategies, or test automation scripts.
---

## Loading Guide

> **Progressive Disclosure Principle**: Read SKILL.md first to get the full picture, then load corresponding references files based on scenario keywords. No need to load all at once.

## Design Sequence

Function (Positive + Boundary + Exception) → API → Security → Platform Specific

## Output

- Default Markdown table, use xlsx Skill for Excel output
- No platform specified → General test cases only; Platform specified → General + Platform specific
- Structure: ID | Title | Type | Module | Priority | Preconditions | Steps | Expected Results

## Capability Boundaries
✅ Can generate: Functional testing, boundary values, exception scenarios, API testing, security awareness, UI visual test cases, performance experience test cases (response time, loading speed)
❌ Cannot generate: Test plans, test strategies, test plans, penetration test execution, vulnerability scanning, performance stress testing (concurrency, stress, load testing), automation scripts

## Command Mapping Table

| Keyword Trigger | Load File | Precise Positioning |
|-----------|---------|---------|
| "test case", "write test case", "design test case" (general) | `references/core-capabilities/common-testing.md` + `references/templates/common-rules.md` | common-testing.md full load |
| "mobile testing", "App testing" | `references/core-capabilities/common-testing.md` + `references/platform/mobile-app.md` + `references/templates/common-rules.md` | platform/mobile-app.md: specific test points |
| "mini program testing" | `references/core-capabilities/common-testing.md` + `references/platform/mini-program.md` + `references/templates/common-rules.md` | platform/mini-program.md: specific test points |
| "mobile Web testing", "H5 testing" | `references/core-capabilities/common-testing.md` + `references/platform/mobile-web.md` + `references/templates/common-rules.md` | platform/mobile-web.md: specific test points |
| "desktop testing", "desktop app testing" | `references/core-capabilities/common-testing.md` + `references/platform/desktop.md` + `references/templates/common-rules.md` | platform/desktop.md: specific test points |
| "PC Web testing", "Web testing" | `references/core-capabilities/common-testing.md` + `references/platform/pc-web.md` + `references/templates/common-rules.md` | platform/pc-web.md: specific test points |
| "linkage testing" | `references/core-capabilities/common-testing.md` | Lines 116-159: Part 3 Linkage Testing |
| "routing testing", "navigation testing" | `references/core-capabilities/common-testing.md` | Lines 160-214: Part 4 Routing Testing |
| "UI testing", "visual testing", "interface testing" | `references/core-capabilities/common-testing.md` | Lines 215-300: Part 5 UI Visual Testing |
| "API testing", "API testing" | `references/core-capabilities/common-testing.md` | Lines 301-375: Part 6 API Testing |
| "security testing" | `references/core-capabilities/common-testing.md` | Lines 376-443: Part 7 Security Testing |
| "boundary value", "exception scenario" | `references/core-capabilities/common-testing.md` | Lines 22-86: Part 1 Test Case Design Methods |
| "test quality", "quality standard" | `references/core-capabilities/common-testing.md` | Lines 87-115: Part 2 Test Case Quality Standards |
| "page interaction", "component interaction", "animation interaction" | `references/core-capabilities/common-testing.md` | Lines 444-549: Part 8-10 Interaction Testing |
| "compatibility testing", "adaptation testing" | `references/core-capabilities/common-testing.md` | Load corresponding platform/ file by platform |
| "accessibility testing" | `references/platform/mobile-app.md` | Section 6: Device Compatibility — Note: this skill does NOT include dedicated accessibility testing content; only device/screen/resolution compatibility is covered here. Accessibility testing (contrast, screen reader, focus management) is not yet documented in this skill. |
| "functional testing" | `references/core-capabilities/common-testing.md` + `references/templates/common-rules.md` + `references/examples/common.md` | examples/common.md Lines 20-86: Part 1 Functional Testing |
| Checklist (General) | `references/checklists/common-checklist.md` | |
| Checklist (Platform Specific) | `references/checklists/mobile-app-checklist.md` / `mobile-web-checklist.md` / `pc-web-checklist.md` / `desktop-checklist.md` / `mini-program-checklist.md` | |
| Example Reference | `references/examples/common.md` + `references/examples/{platform}.md` | examples/common.md contains table of contents |

## File Structure

> **Note**: This skill has no scripts/ or assets/ directories, all content is provided through references/.

```
references/
├── templates/               # Template rules
│   └── common-rules.md       # Test case template + test types + priority + numbering
├── core-capabilities/       # General testing capabilities
│   └── common-testing.md    # All general testing capabilities (with TOC)
├── platform/               # Platform specific test points
│   ├── mobile-app.md        # Mobile App: gestures/interruption/network/permissions/push/compatibility/performance
│   ├── mobile-web.md        # Mobile Web: responsive/touch/browser/viewport/login payment/H5/SEO
│   ├── pc-web.md           # PC Web: browser/layout/keyboard/forms/session/multi-window/routing/linkage/drag/richtext/i18n/dark/print
│   ├── desktop.md          # Desktop: window/shortcuts/files/system integration/multi-monitor/install update/compatibility
│   └── mini-program.md     # Mini Program: lifecycle/authorization/sharing/payment/navigation/subscription/platform differences
├── checklists/             # Test case design checklists
│   ├── common-checklist.md # General checklist (with TOC)
│   ├── mobile-app-checklist.md
│   ├── mobile-web-checklist.md
│   ├── pc-web-checklist.md
│   ├── desktop-checklist.md
│   └── mini-program-checklist.md
└── examples/              # Example references
    ├── common.md          # General test examples (with TOC)
    ├── mobile-app.md      # Mobile App examples
    ├── mobile-web.md      # Mobile Web examples
    ├── pc-web.md         # PC Web examples
    ├── desktop.md        # Desktop examples
    └── mini-program.md   # Mini Program examples
```
