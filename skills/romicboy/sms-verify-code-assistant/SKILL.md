---
name: "sms-verify-code-assistant"
description: 短信验证码查询助手（Python3实现）。通过手机号查询最新短信验证码，返回验证码、短信内容和发送时间。
metadata:
  {"openclaw": {"requires": {"env": ["SMS_AUTH_TOKEN"]}}}
---

# 短信验证码查询助手 (Python3)

## 功能

- **验证码查询**：通过手机号查询最新短信验证码
- **详细信息**：返回验证码、短信内容和发送时间
- **格式化输出**：清晰展示查询结果
- **调试模式**：显示API请求和响应详情

## 首次配置

使用前需要配置 API Token：

```bash
openclaw config set env.vars.SMS_AUTH_TOKEN <你的token>
```

重启 gateway 后生效。

## 环境变量校验

```bash
python3 scripts/validate_env.py
```

- 返回 `0` 且显示 `✅ SMS_AUTH_TOKEN 已配置` 表示配置成功
- 返回 `1` 且显示 `❌ SMS_AUTH_TOKEN 未配置` 表示未配置

**通过 openclaw skills check 检查全部 skill 状态：**
```bash
openclaw skills check
```

## 使用方式

### 命令格式

```bash
python3 scripts/sms_verify_code.py [--debug] <手机号>
```

### 示例

**基本查询**：
```bash
python3 scripts/sms_verify_code.py 13888888888
```

**调试模式**：
```bash
python3 scripts/sms_verify_code.py 13888888888 --debug
```

## 输出格式

### 成功示例
```
查询手机号: 13888888888
========================================
           短信验证码查询结果
========================================
手机号: 13888888888
验证码: 302476
短信内容: 登录短信验证码：302476
发送时间: 2026-03-25 17:50:45
========================================
=== 查询完成 ===
```

### 错误示例
```
查询手机号: 13888888888
查询失败: 未配置环境变量 SMS_AUTH_TOKEN
```

## 技术要求

- Python 3.x
- 标准库 urllib
- 有效的 Authorization token（配置在 `SMS_AUTH_TOKEN` 环境变量中）