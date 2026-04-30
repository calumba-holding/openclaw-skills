---
slug: legal-matter-triage-framework
version: "1.0.0"
type: descriptive
language: en
---

# Legal Matter Triage Framework

## Overview

Helps legal teams triage incoming matters by urgency, risk, deadlines, forum, and required expertise. This is a descriptive OpenClaw skill for legal-industry workflow support. It provides structured frameworks, checklists, templates, and issue-spotting prompts. It does not execute code, call external APIs, access legal databases, retrieve court records, automate filings, or perform legal services.

## When to Use

- Sorting a queue of new requests
- Prioritizing legal work
- Escalating high-risk matters


## Target Users

- In-house counsel
- Law firm associates
- Legal operations teams


## Inputs to Collect

- Matter or project context, including jurisdiction if known
- Relevant facts, documents, parties, dates, and constraints
- Desired output format, audience, and level of detail
- Known deadlines, risk concerns, or review priorities

## Core Modules

1. **Urgency/risk scoring** — provides structured prompts, checklists, and review fields for this area.
2. **Deadline and statute capture** — provides structured prompts, checklists, and review fields for this area.
3. **Practice-area routing** — provides structured prompts, checklists, and review fields for this area.
4. **Privilege/confidentiality caution points** — provides structured prompts, checklists, and review fields for this area.
5. **Next-action plan** — provides structured prompts, checklists, and review fields for this area.

## Workflow

1. Confirm the user's legal workflow goal and the relevant practice context.
2. Ask for missing facts, documents, dates, parties, jurisdiction, and audience where needed.
3. Apply the modules below as a structured thinking framework.
4. Produce checklists, templates, matrices, memos, or planning aids tailored to the user's context.
5. Flag uncertainty, verification needs, deadlines, ethics concerns, confidentiality issues, and attorney-review points.

## Expected Outputs

- Matter priority matrix
- Escalation recommendations
- Initial next-step checklist

## Example Prompts

- "Triage these five incoming legal requests by urgency and risk."
- "Create a triage rubric for an in-house legal helpdesk."

## Safety and Legal Limitations

- This skill provides informational workflow support only and is not legal advice.
- It does not create an attorney-client relationship and does not replace review by a qualified attorney.
- Laws, court rules, deadlines, ethics duties, privilege, confidentiality, and professional responsibility rules vary by jurisdiction and matter.
- Users must verify all legal authorities, filing requirements, deadlines, facts, citations, and strategic decisions with qualified counsel.
- The skill must not be used to fabricate evidence, coach false testimony, evade regulation, access data unlawfully, or bypass confidentiality obligations.
- Specific limitation for this skill: Does not decide legal rights or deadlines; users must verify all dates and legal requirements with qualified counsel.

## Acceptance Criteria

- Package is descriptive only: no handler.py, scripts, external APIs, network calls, or command execution.
- SKILL.md and README.md are English-first and include an explicit legal-information disclaimer.
- Outputs are frameworks, checklists, templates, or planning aids rather than legal conclusions.
- Includes target users, when-to-use guidance, inputs, workflow, outputs, examples, and safety limitations.
- skill.json contains unique slug, tags, trigger keywords, requires_api=false, and readiness=stable.
