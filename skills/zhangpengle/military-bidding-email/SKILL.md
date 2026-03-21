---
name: military-bidding-email
description: 军工采购商机邮件报告技能。自动抓取全军武器装备采购信息网、军队采购网、国防科大采购信息网的招标商机，生成 Excel 报告并发送邮件。当用户说"发送商机邮件"、"发邮件给我"、"商机报告"时触发。
---

# 军工采购商机邮件发送工具

自动抓取军工采购招标信息并发送邮件报告。

## 功能

1. 自动抓取三个数据源的招标信息：
   - 全军武器装备采购信息网 (weain.mil.cn)
   - 军队采购网 (plap.mil.cn)
   - 国防科大采购信息网 (nudt.edu.cn)

2. 各渠道自动获取最新日期数据

3. 自动筛选符合公司能力范围的商机

4. 生成Excel并发送邮件

## 配置

邮件通过 **himalaya** CLI 发送（已配置腾讯企业邮）：
- 发件人: formulas@formulas.cc
- 收件人: zhangpengle@formulas.cc
- 抄送: wangzilong@formulas.cc, fuyan@formulas.cc

## 使用方法

### 命令行执行

```bash
# 抓取并发送今日商机报告
python3 fetcher.py

# 抓取指定日期的报告
python3 fetcher.py --date 2026-03-11

# 抓取并指定关键词
python3 fetcher.py --keywords "模型,仿真,数据,AI,软件"
```

### Python调用

```python
from fetcher import send_bidding_report

# 发送今日报告
send_bidding_report()

# 发送指定日期报告
send_bidding_report(date="2026-03-11")

# 自定义关键词
send_bidding_report(keywords=["模型", "仿真", "AI"])
```

## 输出

- Excel文件: `商机信息汇总_YYYY-MM-DD.xlsx`
- 邮件正文包含各渠道高推荐项目列表
