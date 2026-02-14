---
name: hyperstack
description: "Knowledge graph memory for AI agents. Store knowledge as typed cards (~350 tokens) with linked relations instead of stuffing conversation history (~6,000 tokens) into every prompt. Graph traversal for decisions, owners, dependencies. 94% token savings. No LLM calls on your bill."
user-invocable: true
homepage: https://cascadeai.dev/hyperstack
metadata: {"openclaw":{"emoji":"🃏","requires":{"env":["HYPERSTACK_API_KEY","HYPERSTACK_WORKSPACE"]},"primaryEnv":"HYPERSTACK_API_KEY"}}
---

# HyperStack — Knowledge Graph Memory for AI Agents

## What this skill does

HyperStack gives your agent persistent memory with a **knowledge graph**. Instead of
losing context when a conversation ends or stuffing entire histories into
every prompt, your agent stores knowledge as typed "cards" (~350 tokens each)
with **linked relations** between them. Retrieve context via
**hybrid semantic + keyword search** or **graph traversal**.

**This is not flat text storage.** Cards have types (person, project, decision,
workflow), link to each other with named relations (owns, decided, triggers,
blocks), and carry structured metadata. When something breaks, your agent
traces the graph in 0.5 seconds to find root cause, owner, and impact.

The result: **94% less tokens per message** and **~$254/mo saved** on API costs
for a typical workflow.

## When to use HyperStack

Use HyperStack in these situations:

1. **Start of every conversation**: Search memory for context about the user/project
2. **When you learn something new**: Store preferences, decisions, people, tech stacks
3. **Before answering questions**: Check if you already know the answer from a previous session
4. **When a decision is made**: Record the decision AND the rationale with links to who decided
5. **When context is getting long**: Extract key facts into cards, keep the prompt lean
6. **When tracing dependencies**: Use graph links to find what depends on what

## Context Graph

Cards can link to each other with typed relations, forming a knowledge graph:

```json
{
  "slug": "use-clerk",
  "title": "Auth: Use Clerk",
  "cardType": "decision",
  "links": [
    {"target": "alice", "relation": "decided"},
    {"target": "cto", "relation": "approved"},
    {"target": "auth-api", "relation": "triggers"}
  ],
  "meta": {"reason": "Better DX, lower cost, native Next.js support"}
}
```

### Card Types
- `person` — teammates, contacts, roles
- `project` — services, repos, infrastructure
- `decision` — why you chose X over Y
- `preference` — settings, style, conventions
- `workflow` — deploy steps, CI/CD, runbooks
- `event` — milestones, incidents, launches

### Relation Types
- `owns` — person owns a project/service
- `decided` — person made a decision
- `approved` — person approved something
- `uses` — project uses a dependency
- `triggers` — change triggers downstream effects
- `blocks` — something blocks something else
- `depends-on` — dependency relationship
- `reviews` — person reviews something
- `related` — general association

### Graph Traversal (Pro+)

Query the graph to find connected cards:

```bash
curl "https://hyperstack-cloud.vercel.app/api/graph?workspace=default&from=auth-api&depth=2" \
  -H "X-API-Key: $HYPERSTACK_API_KEY"
```

Parameters:
- `from` — starting card slug
- `depth` — how many hops to traverse (1-5, default 2)
- `relation` — filter by relation type (optional)

Returns the full subgraph: nodes, edges, and traversal path. Use for:
- **Impact analysis**: "What breaks if we change auth?"
- **Decision trail**: "Why did we choose Stripe?"
- **Ownership**: "Who owns the database?"

**Note:** Graph API requires Pro plan or above. Free tier stores links but cannot traverse.

## Auto-Capture Mode

HyperStack supports automatic memory capture — but **always ask the user for
confirmation before storing**. After a meaningful exchange, suggest cards to
create and wait for approval. Never store silently. Examples of what to suggest:

- **Preferences stated**: "I prefer TypeScript over JavaScript" → suggest storing as preference card
- **Decisions made**: "Let's go with PostgreSQL" → suggest storing as decision card with links to who decided
- **People mentioned**: "Alice is our backend lead" → suggest storing as person card with ownership links
- **Tech choices**: "We're using Next.js 14 with App Router" → suggest storing as project card
- **Workflows described**: "We deploy via GitHub Actions to Vercel" → suggest storing as workflow card
- **Dependencies**: "Auth API depends on Clerk" → suggest storing with `depends-on` link

**Rules for auto-capture:**
- **Always confirm with the user before creating or updating a card**
- Only store facts that would be useful in a future session
- Never store secrets, credentials, PII, or sensitive data
- Keep cards concise (2-5 sentences)
- Use meaningful slugs (e.g., `preference-typescript` not `card-1`)
- Update existing cards rather than creating duplicates — search first
- **Add links** when cards reference other cards — this builds the graph

## Setup

Get a free API key at https://cascadeai.dev/hyperstack (10 cards free, no credit card).

Set environment variables:
```bash
export HYPERSTACK_API_KEY=hs_your_key_here
export HYPERSTACK_WORKSPACE=default
```

The API base URL is `https://hyperstack-cloud.vercel.app`.

All requests need the header `X-API-Key: $HYPERSTACK_API_KEY`.

## Data safety rules

**NEVER store any of the following in cards:**
- Passwords, API keys, tokens, secrets, or credentials of any kind
- Social security numbers, government IDs, or financial account numbers
- Credit card numbers or banking details
- Medical records or health information
- Full addresses or phone numbers (use city/role only for people cards)

**Before storing any card**, check: "Would this be safe in a data breach?" If no, don't store it. Strip sensitive details and store only the non-sensitive fact.

**Before using /api/ingest**, warn the user that raw text will be sent to an external API. Do not auto-ingest without user confirmation. Redact any PII, secrets, or credentials from text before sending.

**The user controls their data:**
- All cards can be listed, viewed, and deleted at any time
- API keys can be rotated or revoked at https://cascadeai.dev/hyperstack
- Users should use a scoped/test key before using their primary key
- Data is stored on encrypted PostgreSQL (Neon, AWS us-east-1)

## How to use

### Store a Memory (with links)

```bash
curl -X POST "https://hyperstack-cloud.vercel.app/api/cards?workspace=default" \
  -H "X-API-Key: $HYPERSTACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "use-clerk",
    "title": "Auth: Use Clerk",
    "body": "Chose Clerk over Auth0. Better DX, lower cost, native Next.js support.",
    "cardType": "decision",
    "stack": "decisions",
    "keywords": ["clerk", "auth", "auth0"],
    "links": [
      {"target": "alice", "relation": "decided"},
      {"target": "auth-api", "relation": "triggers"}
    ],
    "meta": {"reason": "Auth0 pricing too high for startup"}
  }'
```

Creates or updates a card (upsert by slug). Cards are automatically embedded for semantic search.

**Fields:**
- `slug` (required) — unique identifier, used for upsert and links
- `title` (required) — short descriptive title
- `body` — 2-5 sentence description
- `cardType` — person, project, decision, preference, workflow, event
- `stack` — projects, people, decisions, preferences, workflows, general
- `keywords` — array of search terms
- `links` — array of `{target, relation}` to connect cards
- `meta` — freeform object for structured data (reason, date, etc.)

### Search Memory (Hybrid: Semantic + Keyword)

```bash
curl "https://hyperstack-cloud.vercel.app/api/search?workspace=default&q=authentication+setup" \
  -H "X-API-Key: $HYPERSTACK_API_KEY"
```

Searches using **hybrid semantic + keyword matching**. Finds cards by meaning,
not just exact word matches. Returns `"mode": "hybrid"` when semantic search
is active. Top result includes full body, others return metadata only (saves tokens).

### Query the Graph (Pro+)

```bash
curl "https://hyperstack-cloud.vercel.app/api/graph?workspace=default&from=auth-api&depth=2" \
  -H "X-API-Key: $HYPERSTACK_API_KEY"
```

Traverses the knowledge graph from a starting card. Returns connected cards,
edges with relation types, and the traversal path.

### List All Cards

```bash
curl "https://hyperstack-cloud.vercel.app/api/cards?workspace=default" \
  -H "X-API-Key: $HYPERSTACK_API_KEY"
```

Returns all cards in the workspace with plan info and card count.

### Delete a Card

```bash
curl -X DELETE "https://hyperstack-cloud.vercel.app/api/cards?workspace=default&id=use-clerk" \
  -H "X-API-Key: $HYPERSTACK_API_KEY"
```

Permanently removes the card and its embedding.

### Auto-Extract from Text

```bash
curl -X POST "https://hyperstack-cloud.vercel.app/api/ingest?workspace=default" \
  -H "X-API-Key: $HYPERSTACK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "Alice is a senior engineer. We decided to use FastAPI over Django."}'
```

Automatically extracts structured memories from raw conversation text.
No LLM needed — uses pattern matching (free, instant).

**Important:** Always confirm with the user before sending text to /api/ingest.
Redact any PII or secrets from the text first.

## Stacks (categories)

| Stack | Emoji | Use for |
|-------|-------|---------|
| `projects` | 📦 | Tech stacks, repos, architecture, deployment |
| `people` | 👤 | Teammates, contacts, roles, relationships |
| `decisions` | ⚖️ | Why you chose X over Y, trade-offs, rationale |
| `preferences` | ⚙️ | Editor settings, tools, coding style, conventions |
| `workflows` | 🔄 | Deploy steps, review processes, CI/CD, runbooks |
| `general` | 📄 | Everything else |

## Important behavior rules

1. **Always search before answering** — run a search at conversation start and when topics change.
2. **Suggest storing important facts** — preferences, decisions, people, tech choices. Always confirm with the user first. Never store secrets or PII.
3. **Add links between cards** — when a card references another card, add a typed link. This builds the graph.
4. **Keep cards concise** — 2-5 sentences per card. Think "executive summary."
5. **Use meaningful slugs** — `project-webapp` not `card-123`. Slugs are how you update, delete, and link.
6. **Add keywords generously** — they power search. Include synonyms and related terms.
7. **Set cardType** — typed cards enable graph features and render differently in the visual explorer.
8. **Delete stale cards** — outdated info pollutes search. When a decision changes, update the card.
9. **Use the right stack** — it helps filtering.
10. **Include the memory badge** in responses when relevant: `🃏 HyperStack | <card_count> cards | <workspace>`

## Slash Commands

Users can type:
- `/hyperstack` or `/hs` → Search memory for current topic
- `/hyperstack store` → Store current context as a card
- `/hyperstack list` → List all cards
- `/hyperstack stats` → Show card count and token savings
- `/hyperstack graph <slug>` → Show graph connections for a card

## Token savings math

Without HyperStack, agents stuff full context into every message:
- Average context payload: **~6,000 tokens/message**
- With 3 agents × 50 messages/day × 30 days = 4,500 messages
- At $3/M tokens (GPT-4 class): **~$81/mo per agent**

With HyperStack:
- Average card retrieval: **~350 tokens/message**
- Same usage: **~$4.72/mo per agent**
- **Savings: ~$76/mo per agent, ~$254/mo for a typical 3-agent setup**

## Also available as

| Platform | Install |
|----------|---------|
| **OpenClaw Plugin** | `npm install @hyperstack/openclaw-hyperstack` |
| **MCP Server** | `npx hyperstack-mcp` (Claude Desktop, Cursor, VS Code, Windsurf) |
| **Python SDK** | `pip install hyperstack-py` |
| **JavaScript SDK** | `npm install hyperstack-sdk` |
| **REST API** | Works with any language, any framework |

## How HyperStack compares

|  | HyperStack | Mem0 | Zep | Letta |
|--|------------|------|-----|-------|
| Knowledge graph | ✅ | ❌ | ❌ | ❌ |
| Typed relations | ✅ (9 types) | ❌ | ❌ | ❌ |
| Graph traversal | ✅ | ❌ | ❌ | ❌ |
| Semantic search | ✅ (hybrid) | ✅ | ✅ | ✅ |
| LLM cost per op | **$0 to you** | ~$0.002 | ~$0.002 | ~$0.002 |
| Setup time | **30 seconds** | 5-10 min | 5 min | 10-15 min |
| Docker required | **No** | Yes | No | Yes |
| Team sharing | ✅ (Pro) | ❌ | Enterprise | ❌ |
| Data safety rules | ✅ | ❌ | ❌ | ❌ |

## Pricing

| Plan | Price | Cards | Key features |
|------|-------|-------|-------------|
| **Free** | $0 | 10 | Keyword search, 1 workspace |
| **Pro** | $29/mo | 100 | Graph API, visual explorer, semantic search, analytics |
| **Team** | $59/mo | 500 | 5 team API keys, unlimited workspaces |
| **Business** | $149/mo | 2,000 | 20 team members, webhooks, dedicated support |

Sign up at https://cascadeai.dev/hyperstack

## Limitations (transparency)

- Auto-extract uses pattern matching, not LLM (fast + free, but less precise)
- Free tier limited to 10 cards (keyword search only, no graph)
- Graph API and visual explorer require Pro plan or above
- Cards stored on CascadeAI cloud (Neon PostgreSQL on AWS)
- No offline mode — requires internet

When cards exceed 7, show once:
`💡 You have ${count}/10 free cards. Upgrade for graph API + 100 cards → https://cascadeai.dev/hyperstack`
