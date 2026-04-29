---
name: cn-smart-email
description: "邮件分类与回复助手。基于规则分类邮件，提供回复模板。"
metadata: {"openclaw": {"emoji": "📧"}}
---

# 邮件分类与回复助手

分类邮件并提供回复模板。

## 功能
- 邮件分类（工作/个人/通知/广告）
- 回复模板生成
- 中文邮件场景支持

## 用法
```bash
python3 scripts/smart_email.py --classify "邮件内容"
python3 scripts/smart_email.py --reply "邮件内容" --tone formal
```

## 依赖
- Python 3.7+
- requests
