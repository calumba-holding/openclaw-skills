---
name: aisa-twitter-post-engage
description: 'Run Twitter/X post-launch follow-through through AIsa. Use when: the user already has a draft, launch tweet, or reply target and needs one skill to publish and then manage early interactions. Supports posting, reply context, and lightweight engagement.'
author: AIsa
version: 1.0.2
license: Apache-2.0
user-invocable: true
primaryEnv: AISA_API_KEY
requires:
  bins:
  - python3
  env:
  - AISA_API_KEY
metadata:
  aisa:
    emoji: 🐦
    requires:
      bins:
      - python3
      env:
      - AISA_API_KEY
    optionalEnv:
    - TWITTER_RELAY_BASE_URL
    - TWITTER_RELAY_TIMEOUT
    primaryEnv: AISA_API_KEY
    compatibility:
    - openclaw
    - claude-code
    - hermes
  openclaw:
    emoji: 🐦
    requires:
      bins:
      - python3
      env:
      - AISA_API_KEY
    optionalEnv:
    - TWITTER_RELAY_BASE_URL
    - TWITTER_RELAY_TIMEOUT
    primaryEnv: AISA_API_KEY
---

# AIsa Twitter Post-Launch Follow-Through

Run Twitter/X post-launch follow-through through AIsa. Use when: the user already has a draft, launch tweet, or reply target and needs one skill to publish and then manage early interactions. Supports posting, reply context, and lightweight engagement.

## When to use

- The user already has a draft, launch tweet, campaign, or reply target.
- The user needs one workflow to publish first and then handle the earliest follow-through actions.
- The user wants approved posting and lightweight engagement without sharing passwords.

## High-Intent Workflows

- Publish a confirmed update and handle the first wave of reactions.
- Move from a draft or launch tweet into reply and follow-through actions.
- Use one workflow for post-launch context, posting, and lightweight engagement.

## Quick Reference

- `python3 scripts/twitter_client.py --help`
- `python3 scripts/twitter_engagement_client.py --help`
- `python3 scripts/twitter_oauth_client.py --help`

## Setup

- `AISA_API_KEY` is required for AIsa-backed API access.
- Use repo-relative `scripts/` paths from the shipped package.
- Prefer explicit CLI auth flags when a script exposes them.
- Optional: set `TWITTER_RELAY_BASE_URL` to override the default relay `https://api.aisa.one/apis/v1/twitter`.
- Optional: set `TWITTER_RELAY_TIMEOUT` to tune relay request timeouts in seconds.
- OAuth requests and any user-approved media uploads use the configured AIsa relay and default to `https://api.aisa.one/apis/v1/twitter`.
- Provide only `AISA_API_KEY`; do not use passwords, cookies, or browser credential export.

## Example Requests

- Authorize a product update post and handle the first follow-up actions
- Publish a launch tweet and then review or reply to early reactions
- Start from a draft and move into post-launch engagement

## Guardrails

- Do not market this package as a long-running social-growth control tower.
- Do not ask for passwords, cookies, or browser credentials.
- Do not claim posting or engagement succeeded until the API confirms it.
- Only upload local files the user explicitly attached, and make it clear those files are sent to the configured AIsa relay first.
