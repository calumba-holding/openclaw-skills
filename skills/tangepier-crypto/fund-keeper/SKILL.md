---
name: fund-keeper
version: 2.6.0
description: 国内场外基金智能顾问 + 股票行情查询。实时估值、买卖建议、收益统计、定投计划、OCR 识图、股票 - 基金联动。支持离线模式、多数据源缓存。
metadata:
  openclaw:
    emoji: "🐔"
    category: finance
    requires:
      pip: ["akshare>=1.12", "pandas>=2.0", "requests>=2.28", "easyocr>=1.7"]
      bins: ["pyautogui"]
keywords:
  - 基金
  - 场外基金
  - 买卖建议
  - 基金估值
  - 养基宝
  - 天天基金
  - 股票行情
  - 收益统计
  - 定投计划
  - OCR 识图
---

# Fund Keeper - 基金智能顾问

参考养基宝 App 逻辑，为国内场外基金提供实时买卖建议。

## 快速开始

### 1. 安装依赖

```bash
pip install akshare pandas requests
```

### 2. 创建基金列表

在 `workspace/funds/my-funds.md` 创建你的持仓：

```markdown
# 我的基金持仓

## 持有基金

| 基金代码 | 基金名称 | 持有份额 | 成本净值 | 备注 |
|---------|---------|---------|---------|------|
| 000001  | 华夏成长混合 | 10000 | 1.500 | 定投中 |
| 110011  | 易方达中小盘 | 5000 | 2.300 | 长期持有 |
```

### 3. 使用命令

```bash
# 查看持仓盈亏
fund-keeper portfolio

# 获取买卖建议
fund-keeper advice

# 查看配置
fund-keeper config

# 修改配置
fund-keeper config --set profit_target_percent=10
fund-keeper config --set stop_loss_percent=15
fund-keeper config --set alert_threshold=2.0

# 重置配置
fund-keeper config --reset

# 添加基金（识图）
fund-keeper add-from-image screenshot.png

# 查看市场概览
fund-keeper market

# 设置提醒
fund-keeper alert --fund 000001 --price 1.800
```

### 配置命令详解

| 命令 | 说明 |
|-----|------|
| `config` | 显示当前配置 |
| `config --set key=value` | 修改配置项 |
| `config --reset` | 重置为默认配置 |

**可配置项**：
- `alert_threshold` - 涨跌幅提醒阈值（%）

**注意**：止盈、止损、定投日等参数在添加基金时单独设置，没有默认值。

## 核心功能

### 1. 实时估值

- 从天天基金网获取实时净值估算
- 对比历史净值，计算涨跌幅
- 支持 QDII 基金（港股/美股）

### 2. 买卖建议

基于以下因素综合评估：
- 📊 **估值水平**: PE/PB 历史百分位
- 📈 **技术面**: 均线、MACD、RSI
- 📰 **市场情绪**: 资金流向、新闻舆情
- 💰 **持仓成本**: 对比你的成本价

建议等级：
- 🔴 **强烈卖出**: 高估 + 技术顶背离
- 🟠 **考虑卖出**: 高估或盈利达标
- 🟢 **持有**: 正常区间
- 🔵 **考虑买入**: 低估或定投机会
- 🟦 **强烈买入**: 严重低估 + 技术底背离

### 3. 识图添加基金

支持从截图识别基金信息：
- 支付宝基金持仓截图
- 天天基金网截图
- 银行 App 基金页面

自动提取：
- 基金代码
- 基金名称
- 持有份额
- 持仓金额

### 4. 智能提醒

- 净值达到目标价
- 单日涨跌幅超过阈值
- 市场大幅波动
- 定投日期提醒

## 配置

### 基金搜索

**搜索基金**：
```bash
py fund_keeper.py search --name 黄金     # 按名称搜索
py fund_keeper.py search --name 芯片     # 按名称搜索
py fund_keeper.py search --fund 000218  # 查看基金详情
```

**显示内容**：
- 基金代码、名称、类型
- 当前净值、昨日净值
- 今日估值、更新时间
- 添加到持仓的命令

### 持仓管理

**编辑基金**：
```bash
py fund_keeper.py edit --fund 000218    # 交互式编辑
py fund_keeper.py edit --fund 000218 --field amount --value 10000  # 直接修改
```

**可编辑字段**：
- `name` - 基金名称
- `amount` - 持有金额
- `profit` - 止盈目标%
- `stop` - 止损线%
- `day` - 定投日
- `note` - 备注

**删除基金**：
```bash
py fund_keeper.py remove --fund 000218  # 需确认
py fund_keeper.py remove --fund 000218 --force  # 强制删除
```

### 黄金投资报告

```bash
py fund_keeper.py gold
```

**包含内容**：
- 国际金价（现货黄金 AUTD）
- 黄金基金（000218 国泰黄金ETF联接A）实时净值
- 投资建议（补仓/止盈/持有）

**信号触发**：
- 今日跌幅 < -3%：🔵 强烈建议补仓
- 今日跌幅 < -2%：🟢 建议补仓
- 今日涨幅 > +3%：🔴 建议部分止盈
- 今日涨幅 > +2%：🟡 关注止盈机会

### 收益可视化

**持仓统计**：
```bash
py fund_keeper.py stats           # 基础统计
py fund_keeper.py stats --chart   # 含可视化图表
```

**收益趋势**：
```bash
py fund_keeper.py trend           # 最近7天趋势
py fund_keeper.py trend --count 30  # 最近30天趋势
```

**图表说明**：
- **持仓分布图**：按金额比例显示
- **收益对比图**：各基金盈亏对比
- **收益趋势图**：每日收益变化（需积累历史数据）

**提示**：每日运行 `stats` 会自动保存历史数据，积累后可查看趋势图。

### 数据源与缓存

**多数据源支持**：
- 天天基金网（默认，最快）
- 东方财富网
- 新浪财经（备用）

**缓存机制**：
- 自动缓存查询结果（30分钟有效）
- 网络断开时自动使用缓存
- 离线模式：`--offline` 仅使用缓存数据

**命令示例**：
```bash
# 正常查询（优先使用缓存）
py fund_keeper.py portfolio

# 强制交叉验证（多数据源）
py fund_keeper.py portfolio --cross-validate

# 离线模式（仅使用缓存）
py fund_keeper.py portfolio --offline
```

### 配置文件

`funds/config.json`:

```json
{
  "alert_threshold": 3.0
}
```

**重要说明**：
- 止盈、止损、定投日等参数**没有默认值**
- 添加基金时必须自己定义这些参数
- 每支基金可以单独设置不同的参数

### 数据源

- **天天基金网**: 实时净值估算（免费）
- **东方财富**: 基金公告、持仓
- **AKShare**: 历史数据、市场指标

## 输出示例

### 持仓概览

```
📊 我的基金持仓 (2024-03-07 15:00)

┌─────────┬──────────────┬─────────┬─────────┬─────────┐
│ 基金代码 │ 基金名称     │ 持有收益│ 收益率  │ 建议    │
├─────────┼──────────────┼─────────┼─────────┼─────────┤
│ 000001  │ 华夏成长混合 │ +2,350  │ +15.6%  │ 🟢 持有 │
│ 110011  │ 易方达中小盘 │ -890    │ -4.2%   │ 🔵 买入 │
└─────────┴──────────────┴─────────┴─────────┴─────────┘

总收益：+1,460 元 (+5.8%)
```

### 买卖建议详情

```
🔵 110011 - 易方达中小盘 - 考虑买入

📊 估值分析:
  • 当前净值：2.185 (估算 +1.2%)
  • PE 百分位：35% (偏低估)
  • 历史位置：低于 65% 的时间

📈 技术面:
  • 均线：站上年线
  • MACD: 金叉第 3 天
  • RSI: 42 (中性)

💡 建议:
  • 当前适合定投或分批买入
  • 目标仓位：20%
  • 止损位：1.950 (-10%)
```

## 注意事项

⚠️ **投资有风险**
- 本技能仅供参考，不构成投资建议
- 市场有风险，决策需谨慎
- 建议分散投资，不要 All in

⚠️ **数据延迟**
- 场外基金净值每天更新一次（晚上）
- 实时估值仅供参考，以晚上公布净值为准
- QDII 基金有 T+2 延迟

## 🆕 股票 - 基金联动（v2.2）

Fund Keeper 现已与 stock-analysis 技能联动，支持：

### 1. 根据股票热点推荐基金

```bash
# 发现半导体板块强势，推荐对应基金
python ~/.openclaw/skills/stock-analysis/scripts/stock_fund_linkage.py --sector 半导体
```

**使用场景**：
- 发现某板块股票大涨
- 想投资该板块但不会选股
- 通过基金分散投资整个板块

### 2. 分析基金重仓股表现

```bash
# 查看持有基金的重仓股
python ~/.openclaw/skills/stock-analysis/scripts/stock_fund_linkage.py --fund 000218
```

**使用场景**：
- 了解基金持仓的股票表现
- 判断基金后续走势
- 验证基金投资逻辑

### 3. 完整联动报告

```bash
# 分析所有主要板块的股票 + 基金
python ~/.openclaw/skills/stock-analysis/scripts/stock_fund_linkage.py report
```

**输出**：
- 半导体、芯片、科技、白酒、航天、黄金、医药、新能源
- 每个板块的股票表现和基金推荐
- 统一数据源交叉验证

### 4. 板块 - 基金映射

| 板块 | 推荐基金 |
|------|---------|
| 半导体 | 008223, 012608, 007300 |
| 芯片 | 008223, 012608, 017470 |
| 科技 | 001186, 002969, 008223 |
| 白酒 | 002190, 161725 |
| 航天 | 001838, 005669 |
| 黄金 | 000218, 000219, 161226 |
| 医药 | 000363, 002708, 004075 |
| 新能源 | 001245, 002190, 003834 |

**详细说明**：查看 `stock-analysis/scripts/LINKAGE_README.md`

---

## 定时任务

建议配置以下 cron 任务：

```bash
# 每个交易日 15:00 收盘后查看估值
openclaw cron add --name "基金收盘检查" --cron "0 15 * * 1-5" \
  --session isolated --message "查看基金持仓估值，生成简报"

# 每周一 8:00 生成周报
openclaw cron add --name "基金周报" --cron "0 8 * * 1" \
  --session isolated --message "生成本周基金持仓报告"
```

## 相关文件

- `funds/my-funds.md` - 持仓列表
- `funds/config.json` - 配置参数
- `funds/history.md` - 交易记录
- `memory/fund-learnings.md` - 投资心得

---

*养基千日，用基一时。理性投资，长期主义。* 🐔
