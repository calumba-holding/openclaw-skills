---
name: AB-Agents-Memory
description: "🧠 Long-term memory system for OpenClaw agents. Manages entities, context, and knowledge base with Obsidian integration. By AB-Agents (Alex Burr)."
version: 1.0.0
author: AB-Agents
homepage: https://github.com/ab-agents/memory
license: MIT
tags: ["memory", "agents", "openclaw", "obsidian", "knowledge-base", "entities", "context", "ab-agents"]
acceptLicenseTerms: true
---

# AB Agents Memory 🦀

**Long-term memory system for OpenClaw agents**

---

## Features

- 🗂️ **Entity Management** — Store info about People, Companies, Topics
- 🔗 **Entity Linking** — Connect entities with relationships
- 📊 **Context Summaries** — Auto-generated summaries for agents
- 🌙 **Nightly Processing** — Automatic data processing pipeline
- 📁 **Obsidian Integration** — Ready-to-use vault with templates
- 🤖 **AB-Archivus Agent** — Dedicated memory agent included

## Quick Start

```bash
# Install via clawhub
clawhub install AB-Agents-Memory

# Or manually
git clone https://github.com/ab-agents/memory.git
cd memory
./setup.sh
```

## Structure

```
AB-Memory/
├── agents/
│   └── AB-Archivus/       # Memory agent
│       ├── SOUL.md
│       ├── IDENTITY.md
│       └── AGENTS.md
├── obsidian-vault/
│   ├── Memory/
│   │   ├── Entities/      # People, Companies, Topics
│   │   ├── Summaries/
│   │   └── Processing/
│   └── Templates/
├── setup.sh              # Installation script
├── SKILL.md              # ClawHub metadata
└── README.md
```

## What's Included

### AB-Archivus Agent

Dedicated OpenClaw agent for memory management:
- Reads/writes to Obsidian vault
- Updates entity database
- Processes session logs
- Maintains context summaries

### Obsidian Vault

Ready-to-use vault with:
- Entity templates (Person, Company, Topic)
- Folder structure for memory organization
- Nightly processing scripts
- Summary templates

## Brand

- **By:** AB-Agents (Alex Burr)
- **Telegram:** @ab_agents
- **Colors:** Red (#E53935) + Black

## Requirements

- OpenClaw 2024+
- Obsidian (optional, for vault editing)
- bash, cron

## License

MIT

---

**AB-Agents Memory** — Your second brain for OpenClaw 🦀
