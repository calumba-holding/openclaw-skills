"""帝国架构 - 量化配置"""
import json
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BrokerConfig:
    """券商/交易所配置"""
    name: str = "simulated"           # simulated / ctapi / hundsun / xtquant
    account_id: str = ""
    api_key: str = ""
    api_secret: str = ""
    endpoint: str = ""                # 交易网关地址
    market_data_endpoint: str = ""    # 行情网关地址
    protocol: str = "ctp"             # ctp / sfix / websocket


@dataclass
class DataConfig:
    """数据源配置"""
    provider: str = "local"           # local / tushare / akshare / wind / local_db
    db_path: str = "data/market.db"   # 本地数据库路径
    tushare_token: str = ""
    cache_dir: str = "data/cache"
    history_days: int = 365           # 默认加载历史天数


@dataclass
class RiskConfig:
    """风控配置"""
    max_position_pct: float = 0.3     # 单票最大仓位占比
    max_drawdown_pct: float = 0.1     # 最大回撤阈值
    max_daily_loss_pct: float = 0.03  # 日最大亏损
    max_leverage: float = 1.0         # 最大杠杆
    stop_loss_pct: float = 0.05       # 止损线
    take_profit_pct: float = 0.15     # 止盈线
    max_open_orders: int = 20         # 最大挂单数
    cooldown_seconds: int = 60        # 触发风控后冷却时间


@dataclass
class PortfolioConfig:
    """组合配置"""
    initial_capital: float = 1_000_000.0
    currency: str = "CNY"
    benchmark: str = "000300.SH"      # 沪深300
    rebalance_frequency: str = "weekly"  # daily / weekly / monthly


@dataclass
class QuantConfig:
    """量化系统总配置"""
    broker: BrokerConfig = field(default_factory=BrokerConfig)
    data: DataConfig = field(default_factory=DataConfig)
    risk: RiskConfig = field(default_factory=RiskConfig)
    portfolio: PortfolioConfig = field(default_factory=PortfolioConfig)
    strategies: list = field(default_factory=list)  # 策略列表
    symbols: list = field(default_factory=list)      # 监控标的
    timeframes: list = field(default_factory=lambda: ["1d"])  # K线周期
    log_level: str = "INFO"

    @classmethod
    def from_file(cls, path: str = None) -> "QuantConfig":
        """从文件加载配置"""
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "config.json")
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            data = json.load(f)
        cfg = cls()
        if "broker" in data:
            for k, v in data["broker"].items():
                if hasattr(cfg.broker, k):
                    setattr(cfg.broker, k, v)
        if "data" in data:
            for k, v in data["data"].items():
                if hasattr(cfg.data, k):
                    setattr(cfg.data, k, v)
        if "risk" in data:
            for k, v in data["risk"].items():
                if hasattr(cfg.risk, k):
                    setattr(cfg.risk, k, v)
        if "portfolio" in data:
            for k, v in data["portfolio"].items():
                if hasattr(cfg.portfolio, k):
                    setattr(cfg.portfolio, k, v)
        cfg.strategies = data.get("strategies", [])
        cfg.symbols = data.get("symbols", [])
        cfg.timeframes = data.get("timeframes", ["1d"])
        cfg.log_level = data.get("log_level", "INFO")
        return cfg

    def save(self, path: str = None):
        """保存配置到文件"""
        if path is None:
            path = os.path.join(os.path.dirname(__file__), "config.json")
        from dataclasses import asdict
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
