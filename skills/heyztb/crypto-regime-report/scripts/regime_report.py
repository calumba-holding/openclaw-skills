#!/usr/bin/env python3
"""
Crypto Regime Report Generator v2.0

Enhanced regime reports with additional metrics:
- Distance from Supertrend
- Volume vs 20-day average
- Funding rate change
- Open interest change
- Correlation to BTC
- Portfolio heat (optional, requires positions)
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Config path - can be overridden via REGIME_CONFIG env var
CONFIG_PATH = Path(os.environ.get(
    "REGIME_CONFIG",
    Path(__file__).parent.parent / "references" / "config.json"
))
with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

# Cache for BTC correlation calculation
_BTC_CANDLES = None

# Yahoo Finance symbol mapping for weekly reports
YAHOO_SYMBOLS = {
    "BTC": "BTC-USD",
    "ETH": "ETH-USD",
    "SOL": "SOL-USD",
    "AVAX": "AVAX-USD",
    "ADA": "ADA-USD",
    "DOT": "DOT-USD",
    "NEAR": "NEAR-USD",
    "ARB": "ARB-USD",
    "OP": "OP-USD",
    "POL": "POL-USD",
    "MATIC": "POL-USD",
    "UNI": "UNI-USD",
    "AAVE": "AAVE-USD",
    "LINK": "LINK-USD",
    "HYPE": "HYPE-USD",
    "RNDR": "RENDER-USD",
    "RENDER": "RENDER-USD",
    "SUI": "SUI-USD",
    "APT": "APT-USD",
}


def okx_request(endpoint: str) -> dict:
    """Make a request to OKX API using curl."""
    url = f"https://www.okx.com{endpoint}"
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        raise Exception(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)


def fetch_candles(symbol: str, bar: str = "1D", limit: int = 100) -> list:
    """Fetch OHLCV candles from OKX."""
    resp = okx_request(f"/api/v5/market/candles?instId={symbol}&bar={bar}&limit={limit}")
    if resp.get("code") != "0":
        raise Exception(f"OKX error: {resp.get('msg')}")
    candles = resp["data"][::-1]
    return [{
        "ts": int(c[0]),
        "open": float(c[1]),
        "high": float(c[2]),
        "low": float(c[3]),
        "close": float(c[4]),
        "vol": float(c[5])
    } for c in candles]


def fetch_funding_rate_history(symbol: str, limit: int = 2) -> list:
    """Fetch recent funding rates from OKX."""
    resp = okx_request(f"/api/v5/public/funding-rate-history?instId={symbol}&limit={limit}")
    if resp.get("code") != "0" or not resp.get("data"):
        return []
    return [{"rate": float(r["fundingRate"]), "time": int(r["fundingTime"])} for r in resp["data"]]


def fetch_open_interest(symbol: str) -> float:
    """Fetch current open interest from OKX."""
    resp = okx_request(f"/api/v5/public/open-interest?instId={symbol}")
    if resp.get("code") != "0" or not resp.get("data"):
        return 0
    return float(resp["data"][0].get("oiUsd", 0))


def fetch_yahoo_candles(symbol: str, period: str = "2y") -> list:
    """Fetch OHLCV candles from Yahoo Finance."""
    yahoo_sym = YAHOO_SYMBOLS.get(symbol, f"{symbol}-USD")
    
    code = f'''
import yfinance as yf
import json
ticker = yf.Ticker("{yahoo_sym}")
hist = ticker.history(period="{period}", interval="1wk")
data = []
for idx, row in hist.iterrows():
    if row["Close"] > 0:
        data.append({{
            "ts": int(idx.timestamp() * 1000),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "vol": float(row["Volume"])
        }})
print(json.dumps(data))
'''
    
    result = subprocess.run(
        ["uvx", "--from", "yfinance", "python3", "-c", code],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode != 0:
        raise Exception(f"Yahoo Finance error: {result.stderr}")
    
    return json.loads(result.stdout)


def calculate_atr(candles: list, period: int = 10) -> list:
    """Calculate ATR using Wilder's smoothing."""
    if len(candles) < period + 1:
        return [None] * len(candles)
    
    trs = []
    for i in range(len(candles)):
        if i == 0:
            trs.append(candles[i]["high"] - candles[i]["low"])
        else:
            h, l, pc = candles[i]["high"], candles[i]["low"], candles[i-1]["close"]
            trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    
    atr = [None] * period
    atr.append(sum(trs[:period]) / period)
    
    for i in range(period + 1, len(candles)):
        atr.append((atr[-1] * (period - 1) + trs[i]) / period)
    
    return atr


def calculate_supertrend(candles: list, period: int = 10, multiplier: float = 3.0) -> tuple:
    """Calculate Supertrend. Returns (values, directions)."""
    atr = calculate_atr(candles, period)
    supertrend, direction = [], []
    
    for i in range(len(candles)):
        if atr[i] is None:
            supertrend.append(None)
            direction.append(0)
            continue
        
        hl2 = (candles[i]["high"] + candles[i]["low"]) / 2
        upper, lower = hl2 + multiplier * atr[i], hl2 - multiplier * atr[i]
        
        if i == 0 or supertrend[-1] is None:
            supertrend.append(lower)
            direction.append(1)
            continue
        
        prev_st, prev_dir, prev_close = supertrend[-1], direction[-1], candles[i-1]["close"]
        
        final_lower = lower if (lower > prev_st or prev_close < prev_st) else prev_st
        final_upper = upper if (upper < prev_st or prev_close > prev_st) else prev_st
        
        if prev_dir >= 0:
            new_dir, new_st = (-1, final_upper) if candles[i]["close"] < final_lower else (1, final_lower)
        else:
            new_dir, new_st = (1, final_lower) if candles[i]["close"] > final_upper else (-1, final_upper)
        
        supertrend.append(new_st)
        direction.append(new_dir)
    
    return supertrend, direction


def calculate_adx(candles: list, period: int = 14) -> list:
    """Calculate ADX using Wilder's method."""
    if len(candles) < period * 2:
        return [None] * len(candles)
    
    plus_dm, minus_dm = [0], [0]
    for i in range(1, len(candles)):
        up = candles[i]["high"] - candles[i-1]["high"]
        down = candles[i-1]["low"] - candles[i]["low"]
        plus_dm.append(up if up > down and up > 0 else 0)
        minus_dm.append(down if down > up and down > 0 else 0)
    
    trs = [candles[0]["high"] - candles[0]["low"]]
    for i in range(1, len(candles)):
        h, l, pc = candles[i]["high"], candles[i]["low"], candles[i-1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    
    def smooth(vals, p):
        s = []
        for i, v in enumerate(vals):
            if i < p - 1: s.append(None)
            elif i == p - 1: s.append(sum(vals[:p]))
            else: s.append(s[-1] - s[-1]/p + v)
        return s
    
    s_tr, s_plus, s_minus = smooth(trs, period), smooth(plus_dm, period), smooth(minus_dm, period)
    
    dx = []
    for i in range(len(candles)):
        if s_tr[i] is None or s_tr[i] == 0:
            dx.append(None)
        else:
            pdi, mdi = 100 * s_plus[i] / s_tr[i], 100 * s_minus[i] / s_tr[i]
            di_sum = pdi + mdi
            dx.append(0 if di_sum == 0 else 100 * abs(pdi - mdi) / di_sum)
    
    adx = [None] * len(candles)
    valid_dx = [d for d in dx if d is not None]
    if len(valid_dx) < period:
        return adx
    
    first_valid = next((i for i, d in enumerate(dx) if d is not None), None)
    if first_valid is None:
        return adx
    
    adx[first_valid + period - 1] = sum(valid_dx[:period]) / period
    for i in range(first_valid + period, len(candles)):
        if dx[i] is not None:
            adx[i] = (adx[i-1] * (period - 1) + dx[i]) / period
    
    return adx


def calculate_correlation(returns1: list, returns2: list) -> Optional[float]:
    """Calculate Pearson correlation between two return series."""
    if len(returns1) < 10 or len(returns2) < 10:
        return None
    
    n = min(len(returns1), len(returns2))
    r1, r2 = returns1[-n:], returns2[-n:]
    
    mean1, mean2 = sum(r1)/n, sum(r2)/n
    
    num = sum((a - mean1) * (b - mean2) for a, b in zip(r1, r2))
    den1 = sum((a - mean1)**2 for a in r1) ** 0.5
    den2 = sum((b - mean2)**2 for b in r2) ** 0.5
    
    if den1 == 0 or den2 == 0:
        return None
    
    return num / (den1 * den2)


def get_regime(direction: int, adx_value: float, thresholds: dict) -> str:
    """Determine regime classification."""
    if adx_value is None:
        return "Unknown"
    
    strong, weak = thresholds["strong_threshold"], thresholds["weak_threshold"]
    
    if direction > 0:
        if adx_value >= strong: return "Strong Bull"
        if adx_value >= weak: return "Weak Bull"
        return "Ranging"
    else:
        if adx_value >= strong: return "Strong Bear"
        if adx_value >= weak: return "Weak Bear"
        return "Ranging"


def get_btc_candles() -> list:
    """Get BTC candles for correlation (cached)."""
    global _BTC_CANDLES
    if _BTC_CANDLES is None:
        try:
            _BTC_CANDLES = fetch_candles("BTC-USDT-SWAP", limit=100)
        except:
            _BTC_CANDLES = []
    return _BTC_CANDLES


def analyze_asset(asset: dict, btc_candles: list = None) -> dict:
    """Analyze a single asset with enhanced metrics."""
    symbol = asset["okx"]
    
    try:
        candles = fetch_candles(symbol, limit=CONFIG["report"]["candle_count"])
        if len(candles) < 30:
            return {"error": "Not enough data", "symbol": asset["symbol"]}
        
        # Calculate indicators
        st, direction = calculate_supertrend(
            candles, CONFIG["indicators"]["supertrend"]["period"],
            CONFIG["indicators"]["supertrend"]["multiplier"]
        )
        adx = calculate_adx(candles, CONFIG["indicators"]["adx"]["period"])
        
        current_price = candles[-1]["close"]
        current_st = st[-1]
        current_dir = direction[-1]
        current_adx = adx[-1]
        
        if current_st is None or current_adx is None:
            return {"error": "Indicator calculation failed", "symbol": asset["symbol"]}
        
        # Price change
        prev_close = candles[-2]["close"]
        price_change = ((current_price - prev_close) / prev_close) * 100
        
        # Regime
        regime = get_regime(current_dir, current_adx, CONFIG["indicators"]["adx"])
        
        # Distance from Supertrend (%)
        st_distance = ((current_price - current_st) / current_st) * 100
        
        # Volume vs 20-day average
        vol_20_avg = sum(c["vol"] for c in candles[-20:]) / 20
        vol_ratio = (candles[-1]["vol"] / vol_20_avg) * 100 if vol_20_avg > 0 else 100
        
        # Funding rate + change
        funding_current = fetch_funding_rate_history(symbol, limit=2)
        funding_rate = funding_current[0]["rate"] * 100 if funding_current else None
        funding_change = None
        if len(funding_current) >= 2:
            funding_change = (funding_current[0]["rate"] - funding_current[1]["rate"]) * 100
        
        # Open Interest (current only)
        oi_current = fetch_open_interest(symbol) / 1e9  # In billions
        
        # Correlation to BTC
        btc_corr = None
        if btc_candles and len(btc_candles) >= 20:
            returns_asset = [(candles[i]["close"] - candles[i-1]["close"]) / candles[i-1]["close"] 
                            for i in range(1, len(candles))]
            returns_btc = [(btc_candles[i]["close"] - btc_candles[i-1]["close"]) / btc_candles[i-1]["close"] 
                          for i in range(1, len(btc_candles))]
            btc_corr = calculate_correlation(returns_asset, returns_btc)
        
        return {
            "symbol": asset["symbol"],
            "name": asset["name"],
            "price": current_price,
            "change_24h": price_change,
            "supertrend": current_st,
            "st_distance": st_distance,
            "direction": "bullish" if current_dir > 0 else "bearish",
            "adx": current_adx,
            "regime": regime,
            "vol_ratio": vol_ratio,
            "funding_rate": funding_rate,
            "funding_change": funding_change,
            "open_interest": oi_current,
            "btc_correlation": btc_corr,
        }
    except Exception as e:
        return {"error": str(e), "symbol": asset["symbol"]}


def format_report(results: list) -> str:
    """Format results as enhanced Telegram report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M PST")
    
    lines = [f"📊 *Crypto Regime Report*", f"_{now}_", ""]
    
    regime_order = {"Strong Bull": 0, "Weak Bull": 1, "Ranging": 2, "Weak Bear": 3, "Strong Bear": 4, "Unknown": 5}
    sorted_results = sorted(results, key=lambda x: regime_order.get(x.get("regime", "Unknown"), 5))
    
    for r in sorted_results:
        if "error" in r:
            lines.append(f"❌ *{r['symbol']}*: {r['error']}")
            continue
        
        regime_emoji = {"Strong Bull": "🟢", "Weak Bull": "🟡", "Ranging": "⚪", 
                       "Weak Bear": "🟠", "Strong Bear": "🔴"}.get(r["regime"], "❓")
        
        # Price format
        if r["price"] >= 1000: price_str = f"${r['price']:,.0f}"
        elif r["price"] >= 1: price_str = f"${r['price']:,.2f}"
        else: price_str = f"${r['price']:,.4f}"
        
        change_emoji = "📈" if r["change_24h"] > 0 else "📉" if r["change_24h"] < 0 else "➡️"
        
        lines.append(f"{regime_emoji} *{r['symbol']}* {price_str} {change_emoji} {r['change_24h']:+.1f}%")
        
        # Line 2: Regime | ADX | Direction | ST Distance
        st_dist_str = f"ST: {r['st_distance']:+.1f}%" if r.get("st_distance") else ""
        lines.append(f"   _{r['regime']}_ | ADX: {r['adx']:.1f} | {r['direction'].capitalize()} {st_dist_str}")
        
        # Line 3: Volume + Funding + OI
        details = []
        if r.get("vol_ratio"):
            vol_emoji = "🔊" if r["vol_ratio"] > 150 else "🔇" if r["vol_ratio"] < 50 else ""
            details.append(f"Vol: {r['vol_ratio']:.0f}%{vol_emoji}")
        if r.get("funding_rate") is not None:
            fund_str = f"Fund: {r['funding_rate']:+.4f}%"
            if r.get("funding_change") is not None:
                arrow = "↑" if r["funding_change"] > 0 else "↓" if r["funding_change"] < 0 else "→"
                fund_str += f" {arrow}"
            if abs(r["funding_rate"]) > 0.01: fund_str += " 🔥"
            details.append(fund_str)
        if r.get("open_interest"):
            details.append(f"OI: ${r['open_interest']:.1f}B")
        
        if details:
            lines.append(f"   {' | '.join(details)}")
        
        # Line 4: BTC Correlation
        if r.get("btc_correlation") is not None:
            corr = r["btc_correlation"]
            corr_emoji = "🔗" if abs(corr) > 0.7 else "🔀" if abs(corr) < 0.3 else ""
            lines.append(f"   BTC Corr: {corr:.2f} {corr_emoji}")
        
        lines.append("")
    
    # Summary
    bull_count = sum(1 for r in sorted_results if "Bull" in r.get("regime", ""))
    bear_count = sum(1 for r in sorted_results if "Bear" in r.get("regime", ""))
    range_count = sum(1 for r in sorted_results if r.get("regime") == "Ranging")
    
    lines.append(f"📈 Bulls: {bull_count} | 📉 Bears: {bear_count} | ⚪ Range: {range_count}")
    
    return "\n".join(lines)


def fetch_weekly_candles(symbol: str, limit: int = 52) -> list:
    """Fetch weekly candles from Yahoo Finance with OKX fallback."""
    YAHOO_GAPS = {"POL", "MATIC", "UNI", "HYPE", "SUI", "APT", "ARB"}
    
    if symbol not in YAHOO_GAPS:
        try:
            return fetch_yahoo_candles(symbol, period="2y")
        except:
            pass
    
    return fetch_candles(f"{symbol}-USDT-SWAP", bar="1W", limit=100)


def analyze_asset_weekly(asset: dict) -> dict:
    """Analyze asset on weekly timeframe."""
    symbol, okx_symbol = asset["symbol"], asset["okx"]
    
    try:
        candles = fetch_weekly_candles(symbol, limit=100)
        if len(candles) < 30:
            return {"error": "Not enough data", "symbol": asset["symbol"]}
        
        st, direction = calculate_supertrend(candles, CONFIG["indicators"]["supertrend"]["period"],
                                              CONFIG["indicators"]["supertrend"]["multiplier"])
        adx = calculate_adx(candles, CONFIG["indicators"]["adx"]["period"])
        
        current_price = candles[-1]["close"]
        current_st, current_dir, current_adx = st[-1], direction[-1], adx[-1]
        
        if current_st is None or current_adx is None:
            return {"error": "Indicator calculation failed", "symbol": asset["symbol"]}
        
        prev_close = candles[-2]["close"]
        price_change = ((current_price - prev_close) / prev_close) * 100
        
        regime = get_regime(current_dir, current_adx, CONFIG["indicators"]["adx"])
        st_distance = ((current_price - current_st) / current_st) * 100
        
        funding = fetch_funding_rate_history(okx_symbol, limit=1)
        funding_rate = funding[0]["rate"] * 100 if funding else None
        oi_current = fetch_open_interest(okx_symbol) / 1e9
        
        prev_dir = direction[-2] if len(direction) > 1 else 0
        regime_change = None
        if prev_dir != current_dir and prev_dir != 0:
            regime_change = "bullish" if current_dir > 0 else "bearish"
        
        return {
            "symbol": asset["symbol"], "name": asset["name"], "price": current_price,
            "change_wtd": price_change, "supertrend": current_st, "st_distance": st_distance,
            "direction": "bullish" if current_dir > 0 else "bearish", "adx": current_adx,
            "regime": regime, "funding_rate": funding_rate, "open_interest": oi_current,
            "regime_change": regime_change
        }
    except Exception as e:
        return {"error": str(e), "symbol": asset["symbol"]}


def format_weekly_report(results: list) -> str:
    """Format weekly report."""
    now = datetime.now().strftime("%Y-%m-%d")
    lines = [f"📊 *Weekly Crypto Regime Report*", f"_{now}_", ""]
    
    regime_order = {"Strong Bull": 0, "Weak Bull": 1, "Ranging": 2, "Weak Bear": 3, "Strong Bear": 4, "Unknown": 5}
    sorted_results = sorted(results, key=lambda x: regime_order.get(x.get("regime", "Unknown"), 5))
    
    changes = [r for r in sorted_results if r.get("regime_change")]
    if changes:
        lines.append("🔄 *Regime Changes This Week*")
        for r in changes:
            emoji = "🟢" if r["regime_change"] == "bullish" else "🔴"
            lines.append(f"{emoji} *{r['symbol']}* flipped {r['regime_change']}")
        lines.append("")
    
    for r in sorted_results:
        if "error" in r: continue
        
        regime_emoji = {"Strong Bull": "🟢", "Weak Bull": "🟡", "Ranging": "⚪",
                       "Weak Bear": "🟠", "Strong Bear": "🔴"}.get(r["regime"], "❓")
        
        price_str = f"${r['price']:,.0f}" if r["price"] >= 1000 else f"${r['price']:,.2f}" if r["price"] >= 1 else f"${r['price']:,.4f}"
        change_emoji = "📈" if r["change_wtd"] > 0 else "📉" if r["change_wtd"] < 0 else "➡️"
        
        lines.append(f"{regime_emoji} *{r['symbol']}* {price_str} {change_emoji} {r['change_wtd']:+.1f}% (wk)")
        lines.append(f"   _{r['regime']}_ | ADX: {r['adx']:.1f} | ST: {r.get('st_distance', 0):+.1f}%")
        if r.get("funding_rate") is not None:
            lines.append(f"   Funding: {r['funding_rate']:+.4f}%")
        lines.append("")
    
    bull_count = sum(1 for r in sorted_results if "Bull" in r.get("regime", ""))
    bear_count = sum(1 for r in sorted_results if "Bear" in r.get("regime", ""))
    lines.append(f"📈 Bulls: {bull_count} | 📉 Bears: {bear_count}")
    
    return "\n".join(lines)


def main(timeframe: str = "daily"):
    """Main entry point."""
    btc_candles = get_btc_candles() if timeframe == "daily" else None
    
    if timeframe == "weekly":
        print("Fetching weekly market data...", file=sys.stderr)
        results = [analyze_asset_weekly(a) for a in CONFIG["watchlist"]]
        report = format_weekly_report(results)
    else:
        print("Fetching market data...", file=sys.stderr)
        results = [analyze_asset(a, btc_candles) for a in CONFIG["watchlist"]]
        report = format_report(results)
    
    print(report)
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate crypto regime reports")
    parser.add_argument("--weekly", action="store_true", help="Weekly report")
    parser.add_argument("--config", type=str, help="Custom config path")
    args = parser.parse_args()
    
    if args.config:
        with open(Path(args.config)) as f:
            CONFIG = json.load(f)
    
    main("weekly" if args.weekly else "daily")
