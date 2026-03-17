---
name: research-analyst
description: AI-powered US/China/HK stock & crypto research with 8-dimension analysis, China market reports (东方财富/新浪/财联社/腾讯/同花顺), portfolio tracking, and trend detection | AI 驱动的美股/A股/港股/加密货币研究工具，提供 8 维度分析、中国市场多源报告（东方财富/新浪/财联社/腾讯/同花顺）、投资组合追踪和趋势检测
version: 1.0.1
verified_commit: 0d4db90  # v1.0.1 - Release with verified_commit
homepage: https://finance.yahoo.com
commands:
  - /stock - Analyze a stock or crypto (分析股票或加密货币)
  - /stock_compare - Compare multiple tickers (比较多个代码)
  - /stock_dividend - Analyze dividend metrics (分析股息指标)
  - /stock_watch - Add/remove from watchlist (添加/移除监控列表)
  - /stock_alerts - Check triggered alerts (检查触发的警报)
  - /stock_hot - Find trending stocks & crypto (发现热门股票和加密货币)
  - /stock_rumors - Find early signals, M&A rumors (发现早期信号、并购传闻)
  - /cn_market - China A-share & Hong Kong market report (中国市场报告)
  - /cn_rankings - Market rankings from 东方财富 (榜单数据)
  - /cn_quotes - Stock quotes from 新浪财经 (实时行情)
  - /cn_news - Financial news from 财联社 (财经快讯)
  - /cn_moneyflow - Money flow analysis from 腾讯财经 (资金流向)
  - /cn_diagnosis - Stock diagnosis from 同花顺 (个股诊断)
  - /portfolio - Show portfolio summary (显示投资组合摘要)
  - /portfolio_add - Add asset to portfolio (添加资产到投资组合)
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3","uv"],"env":["AUTH_TOKEN","CT0"]},"install":[{"id":"python3-check","kind":"shell","command":"python3 --version","bins":["python3"],"label":"Verify Python 3.10+ installed"},{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv package manager"},{"id":"bird-npm","kind":"shell","command":"npm install -g @steipete/bird","bins":["bird"],"label":"Install bird CLI (optional, for Twitter/X)"}]}}
---

# OpenClaw Research Analyst v1.0
# OpenClaw 研究分析师 v1.0

**⚠️ Installation Required**: This skill requires Python 3.10+, uv package manager, and optional dependencies. See installation instructions below.

**📦 Source Code**: https://github.com/ZhenRobotics/openclaw-research-analyst

**English** | [中文](#中文版本)

Analyze **US stocks, China A-shares, Hong Kong stocks**, and **cryptocurrencies** with 8-dimension analysis, **China market multi-source reports** (东方财富/新浪/财联社/腾讯/同花顺), portfolio management, watchlists, alerts, dividend analysis, and **viral trend detection**.

---

## Core Features

- 📊 **8-Dimension Analysis** — Comprehensive stock scoring (earnings, fundamentals, analysts, momentum, sentiment, sector, market, history)
- 💰 **Dividend Analysis** — Yield, payout ratio, 5-year growth, safety score
- 📈 **Portfolio Management** — Track holdings, P&L, concentration warnings
- ⏰ **Watchlist + Alerts** — Price targets, stop losses, signal changes
- 🔥 **Hot Scanner** — Multi-source viral trend detection (CoinGecko, Google News, Twitter/X)
- 🔮 **Rumor Detector** — Early signals for M&A, insider trades, analyst actions
- 🌏 **China Markets** — A-share & Hong Kong data (东方财富, 新浪, 财联社, 腾讯, 同花顺)
- 🪙 **Crypto Support** — Top 20 cryptos with BTC correlation
- ⚡ **Fast Mode** — Skip slow analyses for quick checks

## Quick Commands

### Stock Analysis
```bash
# Basic analysis
uv run {baseDir}/scripts/stock_analyzer.py AAPL

# Fast mode (skips insider trading & breaking news)
uv run {baseDir}/scripts/stock_analyzer.py AAPL --fast

# Compare multiple
uv run {baseDir}/scripts/stock_analyzer.py AAPL MSFT GOOGL

# Crypto
uv run {baseDir}/scripts/stock_analyzer.py BTC-USD ETH-USD
```

### Dividend Analysis
```bash
# Analyze dividends
uv run {baseDir}/scripts/dividend_analyzer.py JNJ

# Compare dividend stocks
uv run {baseDir}/scripts/dividend_analyzer.py JNJ PG KO MCD --output json
```

**Dividend Metrics:**
- Dividend Yield & Annual Payout
- Payout Ratio (safe/moderate/high/unsustainable)
- 5-Year Dividend Growth (CAGR)
- Consecutive Years of Increases
- Safety Score (0-100)
- Income Rating (excellent/good/moderate/poor)

### Watchlist + Alerts
```bash
# Add to watchlist
uv run {baseDir}/scripts/watchlist_manager.py add AAPL

# With price target alert
uv run {baseDir}/scripts/watchlist_manager.py add AAPL --target 200

# With stop loss alert
uv run {baseDir}/scripts/watchlist_manager.py add AAPL --stop 150

# Check for triggered alerts
uv run {baseDir}/scripts/watchlist_manager.py check
```

**Alert Types:**
- 🎯 **Target Hit** — Price >= target
- 🛑 **Stop Hit** — Price <= stop
- 📊 **Signal Change** — BUY/HOLD/SELL changed

### Portfolio Management
```bash
# Create portfolio
uv run {baseDir}/scripts/portfolio_manager.py create "Tech Portfolio"

# Add assets
uv run {baseDir}/scripts/portfolio_manager.py add AAPL --quantity 100 --cost 150

# View portfolio
uv run {baseDir}/scripts/portfolio_manager.py show
```

### 🌏 China Market Reports
```bash
# Complete China market report (all sources)
python3 {baseDir}/scripts/cn_market_report.py

# Market rankings from 东方财富
python3 {baseDir}/scripts/cn_market_rankings.py

# Stock quotes from 新浪财经
python3 {baseDir}/scripts/cn_stock_quotes.py 600519  # 贵州茅台

# Financial news from 财联社
python3 {baseDir}/scripts/cn_cls_telegraph.py

# Money flow analysis from 腾讯财经
python3 {baseDir}/scripts/cn_tencent_moneyflow.py

# Stock diagnosis from 同花顺
python3 {baseDir}/scripts/cn_ths_diagnosis.py 600519
```

**China Data Sources (5 Major Platforms):**
- 📊 **东方财富 (East Money)** — Market rankings, sector analysis, hot stocks
- 💹 **新浪财经 (Sina Finance)** — Real-time quotes, A-share & Hong Kong
- 📰 **财联社 (CLS)** — Breaking financial news, market telegraph
- 💰 **腾讯财经 (Tencent Finance)** — Money flow analysis, capital tracking
- 🔍 **同花顺 (THS)** — Stock diagnosis, technical analysis

**What You Get:**
- A-share (沪深) and Hong Kong stock data
- Market hot lists and sector rotations
- Real-time capital flow tracking
- Breaking financial news and announcements
- Individual stock technical diagnosis

### 🔥 Hot Scanner
```bash
# Full scan - find what's trending NOW
python3 {baseDir}/scripts/trend_scanner.py

# Fast scan (skip social media)
python3 {baseDir}/scripts/trend_scanner.py --no-social

# JSON output for automation
python3 {baseDir}/scripts/trend_scanner.py --json
```

**Data Sources:**
- 📊 CoinGecko Trending — Top 15 trending coins
- 📈 CoinGecko Movers — Biggest gainers/losers
- 📰 Google News — Finance & crypto headlines
- 📉 Yahoo Finance — Gainers, losers, most active
- 🐦 Twitter/X — Social sentiment (requires auth)

### 🔮 Rumor Scanner
```bash
# Find early signals, M&A rumors, insider activity
python3 {baseDir}/scripts/rumor_detector.py
```

**What it finds:**
- 🏢 **M&A Rumors** — Merger, acquisition, takeover bids
- 👔 **Insider Activity** — CEO/Director buying/selling
- 📊 **Analyst Actions** — Upgrades, downgrades, price target changes
- 🐦 **Twitter Whispers** — "hearing that...", "sources say...", "rumor"
- ⚖️ **SEC Activity** — Investigations, filings

## Analysis Dimensions

### Stocks (8 dimensions)
| Dimension | Weight | Description |
|-----------|--------|-------------|
| Earnings Surprise | 30% | EPS beat/miss |
| Fundamentals | 20% | P/E, margins, growth |
| Analyst Sentiment | 20% | Ratings, price targets |
| Historical | 10% | Past earnings reactions |
| Market Context | 10% | VIX, SPY/QQQ trends |
| Sector | 15% | Relative strength |
| Momentum | 15% | RSI, 52-week range |
| Sentiment | 10% | Fear/Greed, shorts, insiders |

### Crypto (3 dimensions)
- Market Cap & Category
- BTC Correlation (30-day)
- Momentum (RSI, range)

## Performance Options

| Flag | Effect | Speed |
|------|--------|-------|
| (default) | Full analysis | 60-120s |
| `--no-insider` | Skip SEC EDGAR | 50-90s |
| `--fast` | Skip insider + news | 45-75s |

## Supported Cryptos (Top 20)

BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, DOT, MATIC, LINK, ATOM, UNI, LTC, BCH, XLM, ALGO, VET, FIL, NEAR

(Use `-USD` suffix: `BTC-USD`, `ETH-USD`)

## Disclaimer

⚠️ **NOT FINANCIAL ADVICE.** For informational purposes only. Consult a licensed financial advisor before making investment decisions.

---

# 中文版本

**⚠️ 需要安装**: 本技能需要 Python 3.10+、uv 包管理器和可选依赖。详见下方安装说明。

**📦 源代码**: https://github.com/ZhenRobotics/openclaw-research-analyst

[English](#openclaw-research-analyst-v10) | **中文**

使用 8 维度分析系统分析**美股、A 股、港股**和**加密货币**，提供**中国市场多源报告**（东方财富/新浪/财联社/腾讯/同花顺）、投资组合管理、监控列表、警报、股息分析和**病毒式趋势检测**。

---

## 📦 安装与依赖

### 必需
- **Python 3.10+** - 核心运行环境
- **uv** - Python 包管理器 (`brew install uv` 或访问 https://github.com/astral-sh/uv)
- **Git** - 用于克隆仓库

### 可选
- **bird CLI** - Twitter/X 集成 (`npm install -g @steipete/bird`)
- **环境变量** (仅 Twitter/X 功能需要):
  - `AUTH_TOKEN` - X.com 认证令牌
  - `CT0` - X.com CT0 令牌

### 安装步骤
```bash
# 从 GitHub 克隆
git clone https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst

# 安装 Python 依赖
uv sync

# 验证安装
uv run scripts/stock_analyzer.py --help
```

### 安全说明
- ✅ 所有源代码可在 GitHub 查看（已验证）
- ✅ 核心功能无需凭证
- ✅ Twitter/X 凭证仅存储在本地 .env 文件
- ✅ 所有 API 调用使用公开端点（Yahoo Finance、CoinGecko 等）

## 核心功能

- 📊 **8 维度分析** — 综合股票评分（盈利、基本面、分析师、动量、情绪、板块、市场、历史）
- 💰 **股息分析** — 收益率、派息比率、5 年增长率、安全评分
- 📈 **投资组合管理** — 追踪持仓、盈亏、集中度警告
- ⏰ **监控列表 + 警报** — 目标价、止损、信号变化
- 🔥 **热点扫描器** — 多源病毒式趋势检测（CoinGecko、Google News、Twitter/X）
- 🔮 **传闻检测器** — M&A、内部交易、分析师行动的早期信号
- 🌏 **中国市场** — A 股和港股数据（东方财富、新浪、财联社、腾讯、同花顺）
- 🪙 **加密货币支持** — 前 20 大加密货币，含 BTC 相关性
- ⚡ **快速模式** — 跳过慢速分析以快速检查

## 快速命令

### 股票分析
```bash
# 基础分析
uv run {baseDir}/scripts/stock_analyzer.py AAPL

# 快速模式（跳过内部交易和突发新闻）
uv run {baseDir}/scripts/stock_analyzer.py AAPL --fast

# 比较多个股票
uv run {baseDir}/scripts/stock_analyzer.py AAPL MSFT GOOGL

# 加密货币
uv run {baseDir}/scripts/stock_analyzer.py BTC-USD ETH-USD
```

### 股息分析
```bash
# 分析股息
uv run {baseDir}/scripts/dividend_analyzer.py JNJ

# 比较股息股票
uv run {baseDir}/scripts/dividend_analyzer.py JNJ PG KO MCD --output json
```

**股息指标：**
- 股息率与年度派息
- 派息比率（安全/适中/高/不可持续）
- 5 年股息增长率（CAGR）
- 连续增长年数
- 安全评分（0-100）
- 收益评级（优秀/良好/适中/差）

### 监控列表 + 警报
```bash
# 添加到监控列表
uv run {baseDir}/scripts/watchlist_manager.py add AAPL

# 设置目标价警报
uv run {baseDir}/scripts/watchlist_manager.py add AAPL --target 200

# 设置止损警报
uv run {baseDir}/scripts/watchlist_manager.py add AAPL --stop 150

# 检查触发的警报
uv run {baseDir}/scripts/watchlist_manager.py check
```

**警报类型：**
- 🎯 **目标价触发** — 价格 >= 目标价
- 🛑 **止损触发** — 价格 <= 止损价
- 📊 **信号变化** — 买入/持有/卖出信号改变

### 投资组合管理
```bash
# 创建投资组合
uv run {baseDir}/scripts/portfolio_manager.py create "科技投资组合"

# 添加资产
uv run {baseDir}/scripts/portfolio_manager.py add AAPL --quantity 100 --cost 150

# 查看投资组合
uv run {baseDir}/scripts/portfolio_manager.py show
```

### 🌏 中国市场报告
```bash
# 完整中国市场报告（所有数据源）
python3 {baseDir}/scripts/cn_market_report.py

# 东方财富榜单数据
python3 {baseDir}/scripts/cn_market_rankings.py

# 新浪财经实时行情
python3 {baseDir}/scripts/cn_stock_quotes.py 600519  # 贵州茅台

# 财联社财经快讯
python3 {baseDir}/scripts/cn_cls_telegraph.py

# 腾讯财经资金流向
python3 {baseDir}/scripts/cn_tencent_moneyflow.py

# 同花顺个股诊断
python3 {baseDir}/scripts/cn_ths_diagnosis.py 600519
```

**中国数据来源（5 大平台）：**
- 📊 **东方财富** — 市场排行榜、板块分析、热门股票
- 💹 **新浪财经** — 实时行情、A 股与港股
- 📰 **财联社** — 突发财经新闻、市场电报
- 💰 **腾讯财经** — 资金流向分析、资金追踪
- 🔍 **同花顺** — 个股诊断、技术分析

**获取内容：**
- A 股（沪深）和港股数据
- 市场热点榜单和板块轮动
- 实时资金流向追踪
- 突发财经新闻和公告
- 个股技术诊断报告

### 🔥 热点扫描器
```bash
# 完整扫描 - 发现当前热门
python3 {baseDir}/scripts/trend_scanner.py

# 快速扫描（跳过社交媒体）
python3 {baseDir}/scripts/trend_scanner.py --no-social

# JSON 输出用于自动化
python3 {baseDir}/scripts/trend_scanner.py --json
```

**数据来源：**
- 📊 CoinGecko 热门榜 — 前 15 名热门币种
- 📈 CoinGecko 涨跌榜 — 最大涨幅/跌幅
- 📰 Google News — 财经和加密货币新闻
- 📉 Yahoo Finance — 涨幅榜、跌幅榜、最活跃
- 🐦 Twitter/X — 社交媒体情绪（需要认证）

### 🔮 传闻扫描器
```bash
# 发现早期信号、并购传闻、内部交易
python3 {baseDir}/scripts/rumor_detector.py
```

**发现内容：**
- 🏢 **并购传闻** — 合并、收购、收购要约
- 👔 **内部交易** — CEO/董事买入/卖出
- 📊 **分析师行动** — 升级、降级、目标价变化
- 🐦 **Twitter 传言** — "据说..."、"有消息称..."、"传闻"
- ⚖️ **SEC 活动** — 调查、文件

## 分析维度

### 股票（8 个维度）
| 维度 | 权重 | 描述 |
|------|------|------|
| 盈利惊喜 | 30% | EPS 超预期/低于预期 |
| 基本面 | 20% | 市盈率、利润率、增长率 |
| 分析师情绪 | 20% | 评级、目标价 |
| 历史模式 | 10% | 过往盈利反应 |
| 市场背景 | 10% | VIX、SPY/QQQ 趋势 |
| 板块 | 15% | 相对强度 |
| 动量 | 15% | RSI、52 周区间 |
| 情绪 | 10% | 恐惧贪婪、空头、内部交易 |

### 加密货币（3 个维度）
- 市值与分类
- BTC 相关性（30 天）
- 动量（RSI、区间）

## 性能选项

| 参数 | 效果 | 速度 |
|------|------|------|
| (默认) | 完整分析 | 60-120 秒 |
| `--no-insider` | 跳过 SEC EDGAR | 50-90 秒 |
| `--fast` | 跳过内部交易 + 新闻 | 45-75 秒 |

## 支持的加密货币（前 20）

BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, DOT, MATIC, LINK, ATOM, UNI, LTC, BCH, XLM, ALGO, VET, FIL, NEAR

（使用 `-USD` 后缀：`BTC-USD`、`ETH-USD`）

## 免责声明

⚠️ **非投资建议。** 仅供参考。投资前请咨询持牌财务顾问。
