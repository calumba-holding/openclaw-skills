---
name: cn-math-calculator
description: "数学表达式计算器。支持四则运算、科学函数(sin/cos/tan/log/sqrt)、常量(pi/e)、单位换算。安全求值不使用eval，纯Python标准库，无需API Key。"
scope: "calculator, math, unit conversion"
install: |
  无额外依赖，纯Python标准库
env: ""
entry:
  type: prompt
  prompt: |
    当用户需要计算数学表达式时使用此skill。调用 scripts/math_calculator.py "表达式"，例如 python3 math_calculator.py "2+3*4"。
handler: |
  python3 scripts/math_calculator.py "<表达式>"
---

# cn-math-calculator

数学表达式计算器。支持基本运算、科学计算。

## 功能

- 四则运算 + - * / ^(幂) %(取模)
- 科学函数：sin, cos, tan, log, sqrt, abs
- 常量：pi, e
- 表达式安全求值（不使用eval）
- 纯本地处理，无需API

## 使用方法

```bash
python3 scripts/math_calculator.py "2+3*4"
python3 scripts/math_calculator.py "sqrt(144)"
python3 scripts/math_calculator.py "sin(pi/2)"
```

## 示例

输入：`2+3*4` → 输出：`结果: 14.0`
