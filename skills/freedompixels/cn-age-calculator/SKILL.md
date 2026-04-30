---
name: cn-age-calculator
description: "年龄计算器。精确计算年龄（年月日）、生日倒计时、星座生肖判定。支持多种日期格式输入，纯Python标准库，无需API Key。"
scope: "age, birthday, zodiac, countdown"
install: |
  无额外依赖，纯Python标准库
env: ""
entry:
  type: prompt
  prompt: |
    当用户需要计算年龄、生日倒计时、星座生肖时使用此skill。调用 scripts/age_calculator.py "YYYY-MM-DD"。
handler: |
  python3 scripts/age_calculator.py "<生日日期>"
---

# cn-age-calculator

年龄计算器。精确计算年龄、生日倒计时、星座生肖。

## 功能

- **精确年龄**：年/月/日精确计算
- **生日倒计时**：距离下次生日还有多少天
- **星座判定**：12星座自动识别
- **生肖判定**：12生肖自动识别
- **多格式输入**：YYYY-MM-DD / YYYY年MM月DD日 / MM-DD

## 安装要求

- Python 3.6+
- 无外部依赖

## 使用方法

```bash
# 计算全部信息
python3 scripts/age_calculator.py "1990-05-15"

# 指定计算类型
python3 scripts/age_calculator.py "1990-05-15" --action age
python3 scripts/age_calculator.py "1990-05-15" --action countdown
python3 scripts/age_calculator.py "1990-05-15" --action zodiac
```

## 示例

输入：`1990-05-15`
输出：
```
年龄: 35岁11个月12天
星座: 金牛座
生肖: 马
距离下次生日: 23天
```

## 分类

生活工具

## 关键词

年龄, 生日, 星座, 生肖, 倒计时, age, birthday, zodiac