"""帝国架构 - 行情数据模块"""
import asyncio
import json
import os
import time
import hashlib
from dataclasses import dataclass, field
from typing import Optional, Callable
from enum import Enum
from datetime import datetime, timedelta


class BarFrequency(Enum):
    """K线周期"""
    MIN_1 = "1m"
    MIN_5 = "5m"
    MIN_15 = "15m"
    MIN_30 = "30m"
    MIN_60 = "60m"
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1M"


@dataclass
class Bar:
    """K线数据"""
    symbol: str
    timestamp: float          # Unix timestamp
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float = 0.0     # 成交额
    frequency: str = "1d"
    extra: dict = field(default_factory=dict)

    @property
    def datetime(self) -> datetime:
        return datetime.fromtimestamp(self.timestamp)

    @property
    def body_size(self) -> float:
        return abs(self.close - self.open)

    @property
    def upper_shadow(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_shadow(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def is_bullish(self) -> bool:
        return self.close > self.open

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "open": self.open, "high": self.high,
            "low": self.low, "close": self.close,
            "volume": self.volume, "turnover": self.turnover,
            "frequency": self.frequency,
        }


@dataclass
class Tick:
    """逐笔数据"""
    symbol: str
    timestamp: float
    last_price: float
    volume: float
    turnover: float
    bid1_price: float = 0.0
    bid1_volume: float = 0.0
    ask1_price: float = 0.0
    ask1_volume: float = 0.0
    extra: dict = field(default_factory=dict)


@dataclass
class OrderBook:
    """盘口数据"""
    symbol: str
    timestamp: float
    bids: list = field(default_factory=list)  # [(price, volume), ...]
    asks: list = field(default_factory=list)
    last_price: float = 0.0
    volume: float = 0.0


class DataFeed:
    """
    行情数据源

    支持多种数据后端：
    - local: 本地 CSV/JSON 文件
    - sqlite: SQLite 数据库
    - tushare: Tushare API
    - akshare: AkShare API
    - simulated: 模拟数据（回测用）
    """

    def __init__(self, provider: str = "local", **kwargs):
        self.provider = provider
        self.kwargs = kwargs
        self._cache: dict[str, list[Bar]] = {}
        self._subscribers: list[Callable] = []
        self._running = False

    async def get_bars(
        self,
        symbol: str,
        frequency: str = "1d",
        start_date: str = None,
        end_date: str = None,
        limit: int = 500,
    ) -> list[Bar]:
        """获取历史K线"""
        cache_key = f"{symbol}_{frequency}_{start_date}_{end_date}_{limit}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self.provider == "local":
            bars = await self._load_local(symbol, frequency, start_date, end_date, limit)
        elif self.provider == "sqlite":
            bars = await self._load_sqlite(symbol, frequency, start_date, end_date, limit)
        elif self.provider == "akshare":
            bars = await self._load_akshare(symbol, frequency, start_date, end_date, limit)
        elif self.provider == "tushare":
            bars = await self._load_tushare(symbol, frequency, start_date, end_date, limit)
        elif self.provider == "simulated":
            bars = self._generate_simulated(symbol, frequency, limit)
        else:
            bars = []

        self._cache[cache_key] = bars
        return bars

    async def subscribe(self, callback: Callable):
        """订阅实时行情"""
        self._subscribers.append(callback)

    async def _notify(self, tick: Tick):
        """通知订阅者"""
        for cb in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(tick)
                else:
                    cb(tick)
            except Exception:
                pass

    async def _load_local(
        self, symbol: str, frequency: str,
        start_date: str, end_date: str, limit: int,
    ) -> list[Bar]:
        """从本地文件加载"""
        data_dir = self.kwargs.get("data_dir", "data")
        file_path = os.path.join(data_dir, f"{symbol}_{frequency}.json")

        if not os.path.exists(file_path):
            return []

        with open(file_path) as f:
            records = json.load(f)

        bars = []
        for r in records[-limit:]:
            bars.append(Bar(
                symbol=r["symbol"],
                timestamp=r["timestamp"],
                open=r["open"], high=r["high"],
                low=r["low"], close=r["close"],
                volume=r["volume"],
                turnover=r.get("turnover", 0),
                frequency=frequency,
            ))
        return bars

    async def _load_sqlite(
        self, symbol: str, frequency: str,
        start_date: str, end_date: str, limit: int,
    ) -> list[Bar]:
        """从 SQLite 加载"""
        import aiosqlite
        db_path = self.kwargs.get("db_path", "data/market.db")

        async with aiosqlite.connect(db_path) as db:
            query = """
                SELECT symbol, timestamp, open, high, low, close, volume, turnover
                FROM bars
                WHERE symbol = ? AND frequency = ?
            """
            params = [symbol, frequency]
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()

        bars = []
        for row in reversed(rows):
            bars.append(Bar(
                symbol=row[0], timestamp=row[1],
                open=row[2], high=row[3], low=row[4], close=row[5],
                volume=row[6], turnover=row[7],
                frequency=frequency,
            ))
        return bars

    async def _load_akshare(
        self, symbol: str, frequency: str,
        start_date: str, end_date: str, limit: int,
    ) -> list[Bar]:
        """从 AkShare 加载"""
        try:
            import akshare as ak
            period_map = {"1d": "daily", "1w": "weekly", "1M": "monthly"}
            period = period_map.get(frequency, "daily")

            # AkShare 需要纯数字代码
            code = symbol.split(".")[0]
            df = ak.stock_zh_a_hist(
                symbol=code, period=period,
                start_date=start_date.replace("-", "") if start_date else "",
                end_date=end_date.replace("-", "") if end_date else "",
                adjust="qfq",
            )

            bars = []
            for _, row in df.tail(limit).iterrows():
                ts = datetime.strptime(str(row["日期"]), "%Y-%m-%d").timestamp()
                bars.append(Bar(
                    symbol=symbol, timestamp=ts,
                    open=float(row["开盘"]), high=float(row["最高"]),
                    low=float(row["最低"]), close=float(row["收盘"]),
                    volume=float(row["成交量"]),
                    turnover=float(row.get("成交额", 0)),
                    frequency=frequency,
                ))
            return bars
        except ImportError:
            return []
        except Exception:
            return []

    async def _load_tushare(
        self, symbol: str, frequency: str,
        start_date: str, end_date: str, limit: int,
    ) -> list[Bar]:
        """从 Tushare 加载"""
        try:
            import tushare as ts
            token = self.kwargs.get("tushare_token", "")
            if not token:
                return []
            pro = ts.pro_api(token)

            ts_code = symbol.replace(".SH", ".SH").replace(".SZ", ".SZ")
            freq_map = {"1d": "D", "1w": "W", "1M": "M"}
            df = pro.daily(
                ts_code=ts_code,
                start_date=start_date.replace("-", "") if start_date else "",
                end_date=end_date.replace("-", "") if end_date else "",
            )

            bars = []
            for _, row in df.tail(limit).iterrows():
                ts_val = datetime.strptime(row["trade_date"], "%Y%m%d").timestamp()
                bars.append(Bar(
                    symbol=symbol, timestamp=ts_val,
                    open=float(row["open"]), high=float(row["high"]),
                    low=float(row["low"]), close=float(row["close"]),
                    volume=float(row["vol"]),
                    turnover=float(row.get("amount", 0)),
                    frequency=frequency,
                ))
            return list(reversed(bars))
        except ImportError:
            return []
        except Exception:
            return []

    def _generate_simulated(
        self, symbol: str, frequency: str, limit: int,
    ) -> list[Bar]:
        """生成模拟数据（回测/测试用）"""
        import random
        bars = []
        price = 100.0
        now = time.time()
        interval = {"1d": 86400, "1w": 604800, "1M": 2592000}.get(frequency, 86400)

        for i in range(limit):
            ts = now - (limit - i) * interval
            change = random.gauss(0, 0.02)
            open_price = price
            close_price = price * (1 + change)
            high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, 0.01)))
            low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, 0.01)))
            volume = random.uniform(10000, 100000)

            bars.append(Bar(
                symbol=symbol, timestamp=ts,
                open=round(open_price, 2),
                high=round(high_price, 2),
                low=round(low_price, 2),
                close=round(close_price, 2),
                volume=round(volume, 0),
                frequency=frequency,
            ))
            price = close_price
        return bars

    def clear_cache(self):
        """清除缓存"""
        self._cache.clear()
