---
name: 经期管理 / Period Tracker
description: "经期管理 / Period Tracker - 女性健康周期追踪工具。功能：(1) 经期记录（开始/结束/天数）；(2) 症状记录（痛经等级/情绪/经血量/症状标签）；(3) 周期预测（下次经期/排卵日/安全期）；(4) 排卵期管理（7天受孕概率日历）；(5) 健康统计（平均周期/规律性/常见症状）；(6) 年度日历视图（含排卵日/易孕期标注）；(7) 数据导出 JSON/CSV。触发词：记录经期、月经来了、大姨妈、排卵期、安全期、易孕期、受孕概率、备孕、经期统计、月经周期、经期日历、经期提醒。"
---

# 经期管理 / Period Tracker

核心脚本：`scripts/period_tracker.py`
数据文件：`~/.openclaw/workspace/period_tracker/data.json`
依赖：Python 3（标准库，无需安装额外包）

---

## 命令总览

```bash
SCRIPT=~/.openclaw/skills/period-tracker/scripts/period_tracker.py

# 今日状态（经期中 / 排卵日 / 安全期 + 受孕概率）
python3 $SCRIPT today

# 添加经期记录
python3 $SCRIPT add 2025-03-01 --end 2025-03-06 \
  --pain 3 --flow 中 --mood 烦躁 --tags 头痛,腰痛

# 预测下次经期 + 排卵期 + 安全期 + 今日受孕概率
python3 $SCRIPT predict

# 排卵期管理（7天受孕概率日历 + 备孕建议）
python3 $SCRIPT ovulation

# 健康统计报告
python3 $SCRIPT stats

# 年度日历（含排卵日/易孕期标注）
python3 $SCRIPT calendar --year 2025

# 历史记录列表
python3 $SCRIPT list --limit 10

# 导出数据
python3 $SCRIPT export --format csv   # 或 json

# 编辑/删除记录
python3 $SCRIPT edit 2025-03-01 --end 2025-03-06
python3 $SCRIPT delete 2025-03-01
```

---

## 用户请求处理指南

### 记录经期

| 用户说 | 操作 |
|--------|------|
| "月经来了" / "大姨妈来了" | 询问开始日期 → `add <start>` |
| "月经结束了" | 询问结束日期 → `edit <start> --end <end>` |
| "从3月1号到6号，痛经比较严重" | `add 2025-03-01 --end 2025-03-06 --pain 4` |

### 症状参数

| 参数 | 取值 | 说明 |
|------|------|------|
| `--pain` | 1-5 | 1=轻微，5=剧烈 |
| `--flow` | 少/中/多 | 经血量 |
| `--mood` | 开心/平静/烦躁/低落/焦虑 | 情绪 |
| `--tags` | 逗号分隔 | 头痛、腰痛、痘痘、浮肿等 |

### 排卵期 & 受孕概率

用户说"排卵期" / "易孕期" / "受孕概率" / "备孕"
→ 调用 `ovulation`

受孕概率分级：
- 🔴 排卵日：最高（25-30%）
- 🟠 排卵前1-2天：高（20-25%）
- 🟡 排卵前3-5天：中（10-15%）
- 🔵 排卵后1-2天：低（5-10%）
- 🟢 其他时间：极低（< 3%）

### 今日状态

用户说"今天是什么时期" / "今天安全吗"
→ 调用 `today`，输出：经期中/排卵日/易孕期/安全期 + 受孕概率

---

## 数据格式

详见 `references/data-schema.md`
