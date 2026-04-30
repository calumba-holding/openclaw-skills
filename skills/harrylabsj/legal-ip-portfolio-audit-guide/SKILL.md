---
slug: legal-ip-portfolio-audit-guide
version: "1.0.0"
type: descriptive
language: en
---

# Legal IP Portfolio Audit Guide

## Overview

Helps organize intellectual property assets, ownership records, registrations, licenses, enforcement needs, and commercialization risks. This is a descriptive OpenClaw skill for legal-industry workflow support. It provides structured frameworks, checklists, templates, and issue-spotting prompts. It does not execute code, call external APIs, access legal databases, retrieve court records, automate filings, or perform legal services.

## When to Use

- Preparing an IP audit
- Reviewing ownership before financing
- Organizing brand/patent/copyright assets


## Target Users

- IP lawyers
- Startup counsel
- Product teams
- Technology companies


## Inputs to Collect

- Matter or project context, including jurisdiction if known
- Relevant facts, documents, parties, dates, and constraints
- Desired output format, audience, and level of detail
- Known deadlines, risk concerns, or review priorities

## Core Modules

1. **IP asset inventory** — provides structured prompts, checklists, and review fields for this area.
2. **Ownership and chain-of-title checklist** — provides structured prompts, checklists, and review fields for this area.
3. **Registration and renewal tracker** — provides structured prompts, checklists, and review fields for this area.
4. **License and encumbrance map** — provides structured prompts, checklists, and review fields for this area.
5. **Enforcement/commercialization issue list** — provides structured prompts, checklists, and review fields for this area.

## Workflow

1. Confirm the user's legal workflow goal and the relevant practice context.
2. Ask for missing facts, documents, dates, parties, jurisdiction, and audience where needed.
3. Apply the modules below as a structured thinking framework.
4. Produce checklists, templates, matrices, memos, or planning aids tailored to the user's context.
5. Flag uncertainty, verification needs, deadlines, ethics concerns, confidentiality issues, and attorney-review points.

## Expected Outputs

- IP inventory table
- Ownership gap list
- Renewal tracker
- License issue map

## Example Prompts

- "Create an IP portfolio audit checklist for a software startup."
- "Help organize trademarks, patents, and copyrights before fundraising."

## Safety and Legal Limitations

- This skill provides informational workflow support only and is not legal advice.
- It does not create an attorney-client relationship and does not replace review by a qualified attorney.
- Laws, court rules, deadlines, ethics duties, privilege, confidentiality, and professional responsibility rules vary by jurisdiction and matter.
- Users must verify all legal authorities, filing requirements, deadlines, facts, citations, and strategic decisions with qualified counsel.
- The skill must not be used to fabricate evidence, coach false testimony, evade regulation, access data unlawfully, or bypass confidentiality obligations.
- Specific limitation for this skill: Does not file IP rights or determine validity; users must consult qualified IP counsel.

## Acceptance Criteria

- Package is descriptive only: no handler.py, scripts, external APIs, network calls, or command execution.
- SKILL.md and README.md are English-first and include an explicit legal-information disclaimer.
- Outputs are frameworks, checklists, templates, or planning aids rather than legal conclusions.
- Includes target users, when-to-use guidance, inputs, workflow, outputs, examples, and safety limitations.
- skill.json contains unique slug, tags, trigger keywords, requires_api=false, and readiness=stable.
