# 🃏 HyperStack — Knowledge Graph Memory for AI Agents

**Your agent forgets everything. HyperStack fixes that.**

Instead of stuffing 6,000 tokens of conversation history into every prompt, your agent stores knowledge as typed cards (~350 tokens) with linked relations and retrieves only what matters. Graph traversal finds root causes in 0.5 seconds. 94% less tokens. ~$254/mo saved. 30-second setup.

## The Problem

Every time your agent starts a new conversation, it has amnesia. The project stack? Gone. User preferences? Gone. That decision you made last Tuesday? Gone.

The current fix is ugly: dump everything into MEMORY.md or stuff the system prompt with thousands of tokens of "context." It's expensive, slow, and hits context limits fast.

**Nobody is giving agents a knowledge graph. HyperStack does.**

## How It Works

| Without HyperStack | With HyperStack |
|---------------------|-----------------|
| ~6,000 tokens/message (full history dump) | ~350 tokens/message (1-2 relevant cards) |
| $81/mo per agent (GPT-4 class) | $4.72/mo per agent |
| Context limit hit after 20 cards | Unlimited cards, retrieves only what's needed |
| Loses memory between sessions | Persistent across all sessions |
| Flat text, no structure | Knowledge graph with typed relations |
| "I don't have enough context" | Root cause in 0.5 seconds |

## Install (30 seconds)

### Option 1: ClawHub (recommended)

```bash
clawhub install hyperstack
```

### Option 2: MCP Server (Claude Desktop, Cursor, VS Code, Windsurf)

```bash
npx hyperstack-mcp
```

### Option 3: SDK

```bash
pip install hyperstack-py    # Python
npm install hyperstack-sdk   # JavaScript
```

### Option 4: Raw REST API

Works with any language. Just `curl` and go.

**One env var. No Docker. No LLM calls on your bill. Just set your API key.**

```bash
export HYPERSTACK_API_KEY=hs_your_key    # Get free at cascadeai.dev/hyperstack
```

## What Your Agent Does

Ask your OpenClaw: *"What do you know about the project?"*

HyperStack searches cards and returns relevant context in ~350 tokens instead of dumping everything.

```
Store a memory     → POST /api/cards       (upsert by slug, with links)
Search memory      → GET  /api/search      (hybrid semantic + keyword)
Traverse graph     → GET  /api/graph       (follow relations, find impact)
List all cards     → GET  /api/cards       (lightweight index)
Delete stale info  → DELETE /api/cards     (keep memory clean)
Auto-extract       → POST /api/ingest      (pipe raw text, get cards back)
```

### Card Anatomy (with graph links)

```json
{
  "slug": "use-clerk",
  "title": "Auth: Use Clerk",
  "body": "Chose Clerk over Auth0. Better DX, lower cost.",
  "cardType": "decision",
  "stack": "decisions",
  "keywords": ["clerk", "auth"],
  "links": [
    {"target": "alice", "relation": "decided"},
    {"target": "auth-api", "relation": "triggers"}
  ],
  "meta": {"reason": "Auth0 pricing too high"}
}
```

### Stacks (Categories)

| Stack | Use for |
|-------|---------|
| `projects` 📦 | Tech stacks, repos, architecture |
| `people` 👤 | Teammates, contacts, roles |
| `decisions` ⚖️ | Why X over Y, trade-offs |
| `preferences` ⚙️ | Editor, tools, coding style |
| `workflows` 🔄 | Deploy steps, CI/CD, runbooks |
| `general` 📄 | Everything else |

### Card Types

`person` · `project` · `decision` · `preference` · `workflow` · `event`

### Relation Types

`owns` · `decided` · `approved` · `uses` · `triggers` · `blocks` · `depends-on` · `reviews` · `related`

## How It Compares

|  | HyperStack | Mem0 | Zep | Letta |
|--|------------|------|-----|-------|
| Knowledge graph | ✅ | ❌ | ❌ | ❌ |
| Typed relations | ✅ (9 types) | ❌ | ❌ | ❌ |
| Graph traversal | ✅ | ❌ | ❌ | ❌ |
| Setup | 1 env var | 6+ env vars | SDK required | Own server |
| LLM cost per op | **$0 to you** | ~$0.002 | ~$0.002 | ~$0.002 |
| Docker required | **No** | Yes (self-hosted) | No | Yes |
| Setup time | **30 seconds** | 5-10 minutes | 5 minutes | 10-15 minutes |
| MCP server | ✅ | Partial | ❌ | Partial |
| Team sharing | ✅ (Pro) | ❌ | Enterprise | ❌ |

## Token Savings Math

3 agents × 50 messages/day × 30 days = 4,500 messages/month

- **Without**: 4,500 × 6,000 tokens = 27M tokens → **~$81/agent/mo** at $3/MTok
- **With**: 4,500 × 350 tokens = 1.6M tokens → **~$4.72/agent/mo**
- **Savings**: ~$76/agent/mo → **~$254/mo for 3 agents**

## Honest Limitations

- Auto-extract uses pattern matching, not LLM (fast + free, but less precise)
- Free tier capped at 10 cards per workspace (keyword search only, no graph)
- Graph API requires Pro plan or above
- Requires internet — no offline mode
- Cards stored on CascadeAI cloud (Neon PostgreSQL on AWS)

## Pricing

| Plan | Price | Cards | Key features |
|------|-------|-------|-------------|
| **Free** | $0 | 10 | Keyword search, 1 workspace |
| **Pro** | $29/mo | 100 | Graph API, visual explorer, semantic search |
| **Team** | $59/mo | 500 | 5 team API keys, unlimited workspaces |
| **Business** | $149/mo | 2,000 | 20 team members, webhooks, support |

[HyperStack Pro](https://cascadeai.dev/hyperstack) unlocks graph traversal, visual explorer, and analytics.

## Verify It Works

After installing, ask your OpenClaw:

> "Store a memory: I prefer dark mode and use VS Code"

Then start a new conversation and ask:

> "What editor do I use?"

If it answers correctly — your agent has memory. 🃏

---

**Built for agents that need to remember. Stop wasting tokens on amnesia.**

[Website](https://cascadeai.dev/hyperstack) · [MCP](https://www.npmjs.com/package/hyperstack-mcp) · [Python](https://pypi.org/project/hyperstack-py/) · [JavaScript](https://www.npmjs.com/package/hyperstack-sdk) · [Discord](https://discord.gg/tdnXaV6e)
