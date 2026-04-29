---
name: orca-pool-analytics
description: Read-only analysis of Orca Whirlpool pools — discovery, ranking, 6-month stability, range sizing, Monte Carlo projection, and retrospective yield. No wallet required.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(npx:*), Bash(curl:*), WebFetch
model: sonnet
license: MIT
metadata:
  author: orca
  version: '3.0.0'
tags:
  - orca
  - whirlpool
  - solana
  - defi
  - clmm
  - analytics
  - liquidity
  - pool-scanning
  - fee-tiers
  - stability
  - atr
  - monte-carlo
  - yield-analysis
  - lp-range
  - beachhouse
---

# Orca Pool Analytics

Read-only analysis of Orca Whirlpool pools on Solana. Generates TypeScript that queries public APIs — no wallet needed.

**APIs**:
- Orca REST: `https://api.orca.so/v2/solana`
- Beachhouse: `https://stats-api.mainnet.orca.so`

## Use / Do Not Use

Use when:
- The user is exploring, comparing, or ranking Orca pools.
- The user asks about pool stability, volatility, or range sizing before deciding to LP.
- The user wants to see what a position would have earned historically.

Do not use when:
- The user wants to open, rebalance, or close an LP position → use the `orca-lp` skill.
- The user wants to execute a swap → use `orca-lp`.
- The task is not Orca-specific.

**Triggers**: `find pools`, `scan pools`, `rank pools`, `compare pools`, `stable pools`, `pool stability`, `pool APR`, `pool fees`, `fee tier`, `fee tier comparison`, `best pool`, `ATR`, `LP range`, `tick range`, `range sizing`, `price range`, `range projection`, `Monte Carlo`, `yield`, `yield analysis`, `retrospective yield`, `consistency`, `price consistency`, `which pool should I LP in`, `is this pool safe`

## Intent Router (first step)

| User intent | Playbook | First action |
|---|---|---|
| "Find / scan / rank pools" | [Quick Ranking](#quick-ranking) | `GET /pools?orderBy=tvlUsdc` |
| "Compare fee tiers for X/Y" | [Fee Tier Comparison](#fee-tier-comparison) | `GET /pools/search?query=X/Y` |
| "Is this pool stable?" / "Which pools are safest?" | [Stability Analysis](#stability-analysis) | 6mo Beachhouse TVL + volume |
| "What range should I use?" | [Range Sizing](#range-sizing) | ATR(14d) on 6mo A/B price |
| "Where could the price go?" / "Simulate the range" | [Monte Carlo Projection](#monte-carlo-projection) | GBM sim from realized vol |
| "What would I earn?" / "How much would $X have made?" | [Retrospective Yield](#retrospective-yield) | Stable periods × feeRate × volume |
| "Should I LP in X/Y?" (broad) | Start with [Quick Ranking](#quick-ranking), escalate | See [Escalation rules](#escalation--reporting-rules) |

---

## Playbooks

Each playbook is standalone. Chain them as the user's question deepens — don't pre-run everything.

### Quick Ranking

- **Purpose**: First-pass filter on TVL / APR / Vol/TVL / priceDelta. Never the final answer — always ask before escalating to Beachhouse.
- **Endpoint**: `GET /pools?orderBy=tvlUsdc&orderDirection=desc&limit=<n>` or `/pools/search?query=<pair>`
- **Inputs**: pair or criteria (min TVL, min APR), limit
- **Output columns**: address, tokenA/B symbols, TVL, APR(7d), APR(30d), Vol/TVL, priceDelta(7d), feeRate
- **Compute**:
  - `APR(7d) = Number(stats["7d"].yieldOverTvl) / 7 * 365 * 100`
  - `APR(30d) = Number(stats["30d"].yieldOverTvl) / 30 * 365 * 100`
  - `Vol/TVL(24h) = Number(stats["24h"].volume) / Number(tvlUsdc)`
- **Flags to surface even at first pass**: priceDelta(7d) below -20% (IL trap), Vol/TVL(24h) < 0.05 (stagnant pool)
- **Gotchas**: numeric fields are strings — cast with `Number()` before math (see Gotcha #1). `priceDelta` is not volatility (see Gotcha #5).
- **Refs**: [Pool Response Key Fields](#pool-response-key-fields), [Pool Stats](#pool-stats-available-on-every-pool), [examples/scan-pools.md](examples/scan-pools.md)

### Fee Tier Comparison

- **Purpose**: The same pair often has multiple fee tiers (e.g. SOL/USDC at 1 / 4 / 30 / 100 bps). Compare yield vs stability across them.
- **Endpoint**: `GET /pools/search?query=<pair>`
- **Inputs**: pair symbol or mint-pair
- **Output**: fee tier, tickSpacing, TVL, volume(24h/7d), APR(7d), Vol/TVL — sorted by the metric the user cares about
- **Gotchas**: higher fee tiers usually have lower TVL but higher APR per dollar. Surface both — don't pick by APR alone. Thin fee-tier pools (< $10k TVL) will give bad quotes.
- **Refs**: [examples/compare-fee-tiers.md](examples/compare-fee-tiers.md)

### Stability Analysis

- **Purpose**: Distinguish stable pools from trap APRs. High APR with falling TVL is a warning, not a buy.
- **Endpoints**:
  - `GET /api/pools/{address}/tvl?time_from=<6mo-ago>&time_to=<now>&type=1D`
  - `GET /api/pools/{address}/volume?time_from=<6mo-ago>&time_to=<now>&type=1D`
- **Inputs**: pool address, 6-month window (`now - 180*86400` to `now`)
- **Compute**:
  - Realized volatility: `stddev(ln(price[i]/price[i-1]))` where `price = Number(volumeQuote) / Number(volumeBase)`
  - ATR(14d): `mean(|price[i] - price[i-1]|)` over last 14 daily A/B prices
  - Max drawdown over 6 months
  - TVL coefficient of variation
- **Red flags (can disqualify)**:
  - **TVL bleeding**: 30d-avg TVL < 70% of 6mo-mean TVL. LPs leaving is a stronger signal than TVL CV alone.
  - **Yield decay**: 30d APR < 70% of 6mo retrospective APR on stable periods.
  - **Unknown/suspect tokens**: Token-2022 mints with `permanentDelegate`, `mintCloseAuthority`, or no entry in Orca's token list. Do not proceed without explicit user acknowledgement.
- **Gotchas**: use A/B ratio `volumeQuote/volumeBase`, not `volumeBaseUsd/volumeBase` (see Gotcha #2 and [Two Different "Prices"](#two-different-prices-from-volume-data)). Beachhouse blocks default Python urllib UA (see Gotcha #3). Response is double-nested (see Gotcha #4).
- **Refs**: [Beachhouse API Reference](#beachhouse-api-reference), [examples/stability-rankings.md](examples/stability-rankings.md)

### Range Sizing

- **Purpose**: Recommend tick ranges (tight / medium / wide) for a user-chosen pool, backtested against 6-month history.
- **Inputs**: pool address, risk preference (optional)
- **Compute**:
  - ATR(14d) → three range widths
  - Historical containment %: what fraction of last 6mo would each range have held
  - Implied rebalance frequency from range exits
- **Output**: three ranges (tight/med/wide) with containment% + rebalance frequency
- **Gotchas**: containment % is a historical backtest, not a forward estimate — use Monte Carlo for forward-looking simulation.
- **Refs**: [examples/lp-range-analysis.md](examples/lp-range-analysis.md), [examples/price-range-history.md](examples/price-range-history.md)

### Monte Carlo Projection

- **Purpose**: Forward-looking simulation of price paths for a chosen range. Noisy — use Retrospective Yield for grounded earnings numbers.
- **Inputs**: pool address, range widths, horizon (7/14/30/90 days)
- **Method**: GBM from Beachhouse-derived realized volatility (A/B log returns, NOT priceDelta). Simulate ≥ 5000 paths.
- **Output**:
  - Price-path percentiles: p5 / p25 / p50 / p75 / p95
  - Expected in-range days for each range width
  - Confidence bands
- **Reporting rules (critical)**:
  - **Never quote a single number as expectation.** Always give at least [p25, p50, p75]. Percentile framing makes error bars visible.
  - **Always caveat in the same sentence**: "GBM with constant σ — underestimates tail risk and assumes no regime change." Don't bury it in a footnote.
  - **Never combine MC with fee projection.** MC projects price paths. LP-vs-HODL fee attribution under concentrated liquidity is high-variance and prone to math errors. Use Retrospective Yield for the grounded earnings number.
- **Refs**: [examples/range-projection.md](examples/range-projection.md)

### Retrospective Yield

- **Purpose**: What a deposit at a given range would have actually earned during stable periods in the last 6 months. The grounded baseline.
- **Inputs**: pool address, range width, deposit size (USD)
- **Method**:
  - Identify stable periods (days within ±2% / ±5% around a moving mean)
  - Daily fees: `Number(totalVolumeUsd) × (feeRate / 10000 / 100)`
  - Attribute to the user's position by range share
  - Annualize from the retrospective window — NOT project forward
- **Output**: realized daily fees, annualized rate on stable periods, stable-period fraction of the 6mo window
- **Reporting rules**:
  - Always caveat: "recent fee data, past performance does not predict future."
  - Quote both the stable-period APR and the blended 6mo APR — LPs should understand both.
- **Gotchas**: concentrated-liquidity fee share scales with range width (see Gotcha #7) — don't use the full-range approximation `deposit/TVL × pool_fees`.
- **Refs**: [examples/yield-projection.md](examples/yield-projection.md)

---

## Escalation & Reporting Rules

**Escalation — save cycles:**
- Start every broad question with Quick Ranking before pulling Beachhouse
- Ask before escalating to 6-month analysis — don't run it on 30 pools when the user cares about 3
- Retrospective Yield > Monte Carlo for grounded earnings numbers
- When the user asks "so what should I do?", synthesize across data already gathered — don't re-run analyses

**Reporting — never skip:**
- Never present a raw APR table as a recommendation
- Never quote 7d-annualized APR as an expected return
- Never quote Monte Carlo percentiles as predictions
- Flag IL traps in Quick Ranking (e.g. priceDelta(7d) < -20%) even at first pass
- Flag TVL bleeding and yield decay as red flags during Stability Analysis
- For memecoin pairs with high APR: always warn about IL before recommending

**Summary recommendations** (when the user asks "so what should I do?"):
- State expected IL exposure (from realized vol and max drawdown)
- State rebalance frequency expectation (from ATR vs chosen range)
- State retrospective earnings at the chosen range
- Close with an honest trade-off

---

## Position Viability (Minimum Economic Size)

A concentrated position is only worth opening above a certain deposit size. Per rebalance cycle (close + reopen):
- Rent churn: ~$0 net (reclaimed on close), but locks capital briefly
- Tx + priority fees: ~$0.02–0.10 at normal mainnet load
- Rebalance frequency: depends on ATR vs range width (from Range Sizing output)

**Formula** (compute from pool-specific numbers; do not use rounded anchor minimums like "always $5k"):

```
min_deposit_usd = (cost_per_rebalance_usd × rebalances_per_year) / APR
```

**Worked examples:**
- JUP/SOL at 42% APR, ~30 rebalances/yr, ~$0.07/cycle: `(0.07 × 30) / 0.42 = $5` — effectively no floor. At $185 you'd earn $77/yr and spend $2.10 in fees; viable.
- SOL/USDC wide range at 50% APR, 12 rebalances/yr, ~$0.10/cycle: `(0.10 × 12) / 0.50 = $2.40` break-even.
- Stablecoin pool at 10% APR, 2 rebalances/yr, ~$0.10/cycle: `(0.10 × 2) / 0.10 = $2` break-even.

Real-world floors are usually dominated by:
1. **Time cost** — is it worth the user's attention for the dollar yield?
2. **Dilution** — depositing more than ~5% of pool TVL cuts your per-unit fee share.

Below the break-even, say so explicitly. Suggest a small wallet use a full-range position (zero rebalances) or park in a stablecoin pool instead.

---

## Gotchas

Read before writing code. These bite agents who don't.

### 1. All numeric fields are strings

Both REST and Beachhouse return numeric values as JSON strings. Cast with `Number()` (TypeScript) or `float()` (Python) before math or comparisons.

- REST: `Number(pool.tvlUsdc)`, `Number(stats["7d"].yieldOverTvl)` — `feeRate` is already a number, but most others are strings.
- Beachhouse: `Number(point.tvl)`, `Number(point.baseAmount)`, `Number(point.volumeBase)`, `Number(point.volumeQuote)`, `Number(point.totalVolumeUsd)` — **every timeseries field is a string**.
- Common failure: `tvls.filter((x) => typeof x === "number")` silently drops EVERY row because they're all strings. Cast first, then filter.

### 2. A/B pool price ≠ USD price of base

For LP range analysis, use the pool ratio `volumeQuote / volumeBase` (B per A), not `volumeBaseUsd / volumeBase` (which is base-token USD price). Identical for USDC-quoted pools; divergent for LST pairs (SOL/JitoSOL), BTC pairs (cbBTC/WBTC), etc. See [Two Different "Prices"](#two-different-prices-from-volume-data).

### 3. Beachhouse blocks default Python urllib User-Agent

Cloudflare returns 403 for the default urllib UA. Set a browser-like header:

```python
import urllib.request
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = json.loads(urllib.request.urlopen(req).read())
```

`curl` and Node `fetch` work without extra headers.

### 4. Beachhouse response is double-nested

`response.data.data[]` — outer `data` wraps the payload; inner `data` is the timeseries array. REST is single-nested: `response.data[]` or `response.data.<field>`.

### 5. `priceDelta` is NOT volatility

It's the net price change over the period. A choppy week ending flat shows `priceDelta ≈ 0` despite high realized volatility. For actual volatility, use log returns on the A/B price from Beachhouse: `stddev(ln(price[i]/price[i-1]))`.

### 6. Cross-asset USD conversion: divide, don't multiply

Pool price `P = quote / base`. For a pair like SOL/whETH where A=SOL, B=whETH, `P ≈ 0.037` means "0.037 whETH per SOL". If you know `SOL_USD`, then `whETH_USD = SOL_USD / P`, NOT `SOL_USD * P`. Multiplying gives ~$3 for whETH instead of ~$2,275. Bites anyone doing HODL comparisons or USD-denominated MC projections on non-USDC pools.

### 7. Concentrated liquidity fee share scales with range width

A narrower position earns proportionally more fees per in-range day. Rough approximation: `relative_fee_share ∝ 1 / width`. Do NOT model concentrated LP fees as `deposit/TVL × pool_fees` — that's the full-range approximation and severely underestimates tight-range earnings (and overestimates if you assume a tight range earns the same as full-range). Calibrate against a baseline width (e.g. ±20% ≈ pool average) and scale from there.

### 8. This skill deliberately does not project LP yield

Retrospective Yield reports actual historical fee earnings during stable periods. Full LP-vs-HODL Monte Carlo with fee attribution requires deep CLMM math (liquidity-from-deposit inversion, active-liquidity attribution, concentration scaling) and is high-variance even when done correctly. If you build one, verify against a known baseline (e.g. the retrospective yield on a stablecoin pair) before reporting numbers.

---

## Orca REST API Reference

Base: `https://api.orca.so/v2/solana`

### Endpoints

| Path | Purpose | Response shape |
|------|---------|----------------|
| `GET /pools` | List pools. Params: `orderBy=tvlUsdc\|volume24hUsdc`, `orderDirection=asc\|desc`, `limit` | `{ data: [...pools] }` |
| `GET /pools/search?query=<pair-or-addr>` | Search by pair or address | `{ data: [...pools] }` |
| `GET /pools/{address}` | Single pool detail | `{ data: {...pool} }` |
| `GET /protocol` | Protocol-wide stats (flat, no `data` wrapper) | `{ volume24hUsdc, fees24hUsdc, tvl }` |
| `GET /tokens/search?query=<symbol>` | Token lookup | `{ data: [...tokens] }` |

### Pool Response Key Fields

```
address           - Pool address (string)
feeRate           - Fee in basis points × 100 (e.g. 300 = 0.03%)
price             - Current price as string
tvlUsdc           - TVL in USD as string
tickSpacing       - 1 (stables), 4 (majors), 64 (standard), 128 (volatile)
tokenA / tokenB   - { symbol, name, decimals, address }
tokenBalanceA/B   - Raw integer token balance (÷ 10^decimals)
```

### Pool Stats (available on every pool)

Each pool has `stats.24h`, `stats.7d`, `stats.30d`:

```
volume             - Total volume in USD (string)
fees               - Total fees generated (string)
rewards            - Total reward emissions in USD (string)
yieldOverTvl       - Fee yield as fraction of TVL (e.g. 0.0019 = 0.19%)
volumeDelta        - Volume change vs previous period (24h and 7d only)
feesDelta          - Fees change rate (24h and 7d only)
tvlDelta           - TVL change rate (24h and 7d only)
priceDelta         - Price change rate (24h and 7d only)
yieldOverTvlDelta  - Yield change rate (24h and 7d only)
```

---

## Beachhouse API Reference

Base: `https://stats-api.mainnet.orca.so`

Daily timeseries for up to 6 months. Coverage: top 50 pools by TVL. Use for realized volatility (VWAP log returns), ATR, historical range analysis, and retrospective yield.

### Endpoints

**`GET /api/pools/{address}/tvl?time_from=<unix>&time_to=<unix>&type=1D`**

```json
{ "data": { "data": [
  { "tvl": "1234567.89", "baseAmount": "500.5", "quoteAmount": "75000.0", "unixTime": 1700000000 }
] } }
```

**`GET /api/pools/{address}/volume?time_from=<unix>&time_to=<unix>&type=1D`**

```json
{ "data": { "data": [
  { "totalVolumeUsd": "500000.0", "volumeBase": "3000.0", "volumeQuote": "450000.0",
    "volumeBaseUsd": "250000.0", "volumeQuoteUsd": "250000.0", "unixTime": 1700000000 }
] } }
```

**Resolutions**: `1H`, `1D`, `1W`, `1M`, `1Y`. `baseAmount` and `quoteAmount` are human-readable (already decimal-adjusted). 6-month window: `time_from = now - 180 * 86400`, `time_to = now`.

### Two Different "Prices" From Volume Data

| Formula | Meaning | Use when |
|---------|---------|----------|
| `Number(volumeQuote) / Number(volumeBase)` | **A/B pool ratio** — token B per token A (actual trade execution ratio) | Pool-internal price for in-range analysis, ATR of the pair, realized vol of the actual LP position. **Correct for all pools**, especially LST pairs (SOL/JitoSOL) and BTC wrapped pairs (cbBTC/WBTC). |
| `Number(volumeBaseUsd) / Number(volumeBase)` | **USD price of the base token** | USD-denominated price context (e.g. "what was SOL worth each day"). For USDC-quoted pools these are identical; for LST/BTC pairs they diverge — USD price reflects the dollar value, not the pool ratio. |

For LP range sizing and in-range checking, **always use `volumeQuote / volumeBase`**. For "what was the price in USD" context, use `volumeBaseUsd / volumeBase`.

---

## Key Formulas

| Formula | Expression |
|---------|------------|
| Fee % | `feeRate / 10000` (e.g. 400 → 0.04%) |
| APR (7d) | `Number(stats["7d"].yieldOverTvl) / 7 * 365 * 100` |
| APR (30d) | `Number(stats["30d"].yieldOverTvl) / 30 * 365 * 100` |
| A/B pool price | `Number(volumeQuote) / Number(volumeBase)` |
| USD price of base | `Number(volumeBaseUsd) / Number(volumeBase)` |
| Realized volatility | `stddev(ln(price[i]/price[i-1]))` (A/B price for LP; USD price for market context) |
| ATR (14d) | `mean(|price[i] - price[i-1]|)` over last 14 daily A/B prices |
| Daily fees (pool) | `Number(totalVolumeUsd) × (feeRate / 10000 / 100)` |
| Vol/TVL (24h) | `Number(stats["24h"].volume) / Number(tvlUsdc)` — higher = more active |
| Daily earning (full-range approx) | `deposit × Number(stats["7d"].yieldOverTvl) / 7` |

---

## Common Token Mints

| Symbol | Decimals | Mint Address |
|--------|----------|--------------|
| SOL (wSOL) | 9 | `So11111111111111111111111111111111111111112` |
| USDC | 6 | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| USDT | 6 | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` |
| ORCA | 6 | `orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE` |
| BONK | 5 | `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` |
| JitoSOL | 9 | `J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn` |
| JUP | 6 | `JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN` |

> Orca pools use the wSOL mint (`So111…112`) to represent SOL. Native SOL is the chain's native asset, not an SPL token — the SDK handles wrap/unwrap automatically.

---

## Examples

| File | Description |
|------|-------------|
| [scan-pools.md](examples/scan-pools.md) | Scan and rank top Orca pools by TVL |
| [pool-detail.md](examples/pool-detail.md) | Full breakdown of a single pool |
| [compare-fee-tiers.md](examples/compare-fee-tiers.md) | Compare fee tiers for a trading pair |
| [pair-discovery.md](examples/pair-discovery.md) | Find all pools for a specific token |
| [stability-rankings.md](examples/stability-rankings.md) | Rank pools by 6-month Beachhouse stability score |
| [lp-range-analysis.md](examples/lp-range-analysis.md) | ATR-based LP range sizing from Beachhouse VWAP |
| [range-projection.md](examples/range-projection.md) | Monte Carlo using Beachhouse realized volatility |
| [price-range-history.md](examples/price-range-history.md) | Historical price bands and containment |
| [consistency-scanner.md](examples/consistency-scanner.md) | Find pools with longest stable price streaks |
| [yield-projection.md](examples/yield-projection.md) | Retrospective yield from Beachhouse volume and TVL |
| [monitor-pool.md](examples/monitor-pool.md) | Real-time pool monitoring with price/TVL deltas |

---

## Fresh Context

Treat referenced Orca docs and live API responses as the source of truth over this file. If the live response or docs diverge from examples here, follow the live data and surface the mismatch to the user. Re-fetch `/pools/{address}` or Beachhouse data per request — do not cache across unrelated queries.
