# Consistency Scanner

Find pools where price has stayed within a tight band for the longest consecutive period. Measures deviation from 30-day rolling mean to find truly stable pairs — the "gold mines" where LP ranges hold for months.

> **Playbook**: [Stability Analysis](../SKILL.md#stability-analysis) — streak-based variant (complements volatility/drawdown ranking).

## Usage

```bash
npx tsx consistency-scanner.ts
```

## What It Measures

For each pool, at every threshold (±0.5%, ±1%, ±2%, ±3%, ±5%, ±10%):

- **Longest streak** — maximum consecutive days where daily price stayed within ±X% of the 30-day rolling mean
- **Current streak** — how many consecutive days from today the price has been within band
- **Tightest 30d band** — the narrowest ±X% that held for at least 30 consecutive days

This is different from simple price range — it uses a **rolling mean** so it measures consistency, not just a lucky snapshot. A pool that slowly drifts from $1.00 to $1.10 over 6 months can still score well because the daily deviation from the rolling mean is small.

## Output

```
╔════════════════════════════════════════════════════════════════════════════════════════════════════════╗
║                     PRICE CONSISTENCY SCANNER — Consecutive Days Within Band                         ║
║                     (deviation from 30d rolling mean)                                                ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Pair              TVL        Vol/day    │ ±0.5%  ±1%   ±2%    ±3%    ±5%    ±10%  │ Tightest 30d   ║
║                                          │ longest consecutive days in band        │ band held      ║
╠════════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  ONyc/USDC           $5.0M    $1.6M/d │   92d  109d  128d   128d   129d   180d │  ±0.5%         ║
║  USX/USDC           $11.5M    $3.3M/d │   18d   26d   80d    82d    83d   181d │  ±1.5%         ║
║  PYUSD/USDC         $26.3M   $15.8M/d │   10d   19d   55d    71d   151d   180d │  ±1.5%         ║
║  eUSX/USX            $2.4M    $1.0M/d │    9d   18d   39d    61d   116d   116d │  ±2.0%         ║
║  CASH/USDC          $18.5M   $17.1M/d │    6d   10d   25d    25d    25d    96d │  ±6.0%         ║
║  USDG/USDC          $14.7M   $12.3M/d │    8d   21d   24d    44d    44d    92d │  ±2.5%         ║
║  SOL/USDC           $30.4M  $393.9M/d │    2d    3d    5d     6d    15d    74d │  ±5.5%         ║
║  cbBTC/USDC          $4.7M   $23.7M/d │    2d    3d    4d    10d    37d    75d │  ±4.0%         ║
  ...
╚════════════════════════════════════════════════════════════════════════════════════════════════════════╝

🏆 GOLD MINES — Pools with 30+ consecutive days within ±2% of rolling mean

  ONyc/USDC (0.01%)
  ├─ ±2% streak: 128 days (2025-10-04 → 2026-02-08)
  │  During that period: $1.0256 — $1.0821
  ├─ ±1% streak: 109 days | ±0.5% streak: 92 days
  ├─ Tightest band held 30d: ±0.5% ($1.0374 — $1.0493)
  └─ Pool: 7jhhyxPUKpu42hPGSYwgMXbR2dtVJHKhs8DW3sAAgAvX

  USX/USDC (0.01%)
  ├─ ±2% streak: 80 days (2025-10-07 → 2025-12-25)
  │  During that period: $0.9808 — $1.0148
  ├─ Current streaks: ±2%=21d | ±1%=21d | ±0.5%=18d
  └─ Pool: 2e3WeM4WwdEqwTtRnWN3gJSbhNg1P6Aj2y7kEdfrYbix
```

> Representative output. "Gold mines" are pools where the price barely moved relative to its rolling average — ideal for tight LP ranges that hold for months without rebalancing.
