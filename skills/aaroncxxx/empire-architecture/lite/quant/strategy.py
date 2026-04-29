"""帝国架构 - 策略模块"""
import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from .data_feed import Bar, DataFeed


class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Signal:
    """交易信号"""
    symbol: str
    signal_type: SignalType
    price: float
    timestamp: float
    strength: float = 1.0        # 信号强度 0-1
    reason: str = ""
    target_pct: float = 0.0      # 目标仓位百分比
    stop_loss: float = 0.0       # 止损价
    take_profit: float = 0.0     # 止盈价
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "type": self.signal_type.value,
            "price": self.price,
            "timestamp": self.timestamp,
            "strength": self.strength,
            "reason": self.reason,
            "target_pct": self.target_pct,
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
        }


class Strategy:
    """
    策略基类

    所有量化策略继承此类，实现 compute() 方法。
    类似帝国架构中的"谋略参谋"，负责分析行情并产生交易信号。
    """

    def __init__(self, name: str, symbols: list[str] = None, **kwargs):
        self.name = name
        self.symbols = symbols or []
        self.params = kwargs
        self._signals: list[Signal] = []
        self._positions: dict[str, float] = {}  # symbol -> 持仓比例
        self._initialized = False

    async def initialize(self, data_feed: DataFeed):
        """策略初始化，加载历史数据"""
        self._data_feed = data_feed
        self._initialized = True

    async def compute(self, bars: dict[str, list[Bar]], timestamp: float) -> list[Signal]:
        """
        计算策略信号

        Args:
            bars: {symbol: [Bar, ...]} 各标的的历史K线
            timestamp: 当前时间戳

        Returns:
            信号列表
        """
        raise NotImplementedError

    def add_signal(self, signal: Signal):
        """添加信号"""
        self._signals.append(signal)

    def get_signals(self, limit: int = 100) -> list[Signal]:
        """获取最近的信号"""
        return self._signals[-limit:]

    def update_position(self, symbol: str, pct: float):
        """更新持仓"""
        self._positions[symbol] = pct

    def get_positions(self) -> dict[str, float]:
        return self._positions.copy()

    def describe(self) -> dict:
        """策略描述"""
        return {
            "name": self.name,
            "symbols": self.symbols,
            "params": self.params,
            "signals_count": len(self._signals),
            "positions": self._positions,
        }


# ─── 内置策略示例 ─────────────────────────────────────────

class DualMAStrategy(Strategy):
    """
    双均线策略

    短期均线上穿长期均线 → 买入
    短期均线下穿长期均线 → 卖出
    """

    def __init__(self, short_window: int = 5, long_window: int = 20, **kwargs):
        super().__init__(name="DualMA", **kwargs)
        self.short_window = short_window
        self.long_window = long_window

    async def compute(self, bars: dict[str, list[Bar]], timestamp: float) -> list[Signal]:
        signals = []
        for symbol, bar_list in bars.items():
            if len(bar_list) < self.long_window + 1:
                continue

            closes = [b.close for b in bar_list]
            ma_short = sum(closes[-self.short_window:]) / self.short_window
            ma_long = sum(closes[-self.long_window:]) / self.long_window
            prev_short = sum(closes[-self.short_window - 1:-1]) / self.short_window
            prev_long = sum(closes[-self.long_window - 1:-1]) / self.long_window

            current_price = closes[-1]

            # 金叉：短均线从下穿上
            if prev_short <= prev_long and ma_short > ma_long:
                signals.append(Signal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=current_price,
                    timestamp=timestamp,
                    strength=min(1.0, (ma_short - ma_long) / ma_long * 10),
                    reason=f"MA{self.short_window} 上穿 MA{self.long_window}，金叉",
                    target_pct=0.3,
                    stop_loss=current_price * 0.95,
                    take_profit=current_price * 1.1,
                ))
            # 死叉：短均线从上穿下
            elif prev_short >= prev_long and ma_short < ma_long:
                signals.append(Signal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    price=current_price,
                    timestamp=timestamp,
                    strength=min(1.0, (ma_long - ma_short) / ma_long * 10),
                    reason=f"MA{self.short_window} 下穿 MA{self.long_window}，死叉",
                    target_pct=0.0,
                ))

        return signals


class RSIStrategy(Strategy):
    """
    RSI 策略

    RSI < 30 → 超卖，买入
    RSI > 70 → 超买，卖出
    """

    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70, **kwargs):
        super().__init__(name="RSI", **kwargs)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def _compute_rsi(self, closes: list[float]) -> float:
        if len(closes) < self.period + 1:
            return 50.0

        deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
        recent = deltas[-self.period:]

        gains = [d for d in recent if d > 0]
        losses = [-d for d in recent if d < 0]

        avg_gain = sum(gains) / self.period if gains else 0
        avg_loss = sum(losses) / self.period if losses else 0.0001

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    async def compute(self, bars: dict[str, list[Bar]], timestamp: float) -> list[Signal]:
        signals = []
        for symbol, bar_list in bars.items():
            if len(bar_list) < self.period + 1:
                continue

            closes = [b.close for b in bar_list]
            rsi = self._compute_rsi(closes)
            prev_rsi = self._compute_rsi(closes[:-1])
            current_price = closes[-1]

            if prev_rsi >= self.oversold and rsi < self.oversold:
                signals.append(Signal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=current_price,
                    timestamp=timestamp,
                    strength=(self.oversold - rsi) / self.oversold,
                    reason=f"RSI({self.period})={rsi:.1f}，超卖",
                    target_pct=0.25,
                    stop_loss=current_price * 0.95,
                ))
            elif prev_rsi <= self.overbought and rsi > self.overbought:
                signals.append(Signal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    price=current_price,
                    timestamp=timestamp,
                    strength=(rsi - self.overbought) / (100 - self.overbought),
                    reason=f"RSI({self.period})={rsi:.1f}，超买",
                    target_pct=0.0,
                ))

        return signals


class ChannelBreakoutStrategy(Strategy):
    """
    通道突破策略（Donchian Channel）

    价格突破 N 日最高 → 买入
    价格跌破 N 日最低 → 卖出
    """

    def __init__(self, window: int = 20, **kwargs):
        super().__init__(name="ChannelBreakout", **kwargs)
        self.window = window

    async def compute(self, bars: dict[str, list[Bar]], timestamp: float) -> list[Signal]:
        signals = []
        for symbol, bar_list in bars.items():
            if len(bar_list) < self.window + 1:
                continue

            recent = bar_list[-self.window - 1:-1]
            high_channel = max(b.high for b in recent)
            low_channel = min(b.low for b in recent)
            current = bar_list[-1]

            if current.close > high_channel:
                signals.append(Signal(
                    symbol=symbol,
                    signal_type=SignalType.BUY,
                    price=current.close,
                    timestamp=timestamp,
                    strength=1.0,
                    reason=f"突破 {self.window}日 高点 {high_channel:.2f}",
                    target_pct=0.3,
                    stop_loss=low_channel,
                ))
            elif current.close < low_channel:
                signals.append(Signal(
                    symbol=symbol,
                    signal_type=SignalType.SELL,
                    price=current.close,
                    timestamp=timestamp,
                    strength=1.0,
                    reason=f"跌破 {self.window}日 低点 {low_channel:.2f}",
                    target_pct=0.0,
                ))

        return signals
