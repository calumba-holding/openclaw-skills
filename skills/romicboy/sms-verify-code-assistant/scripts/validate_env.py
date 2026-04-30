#!/usr/bin/env python3
"""
短信验证码查询助手 - 环境变量校验脚本
用于 openclaw config 校验环境变量是否配置

用法:
    python validate_env.py

返回:
    0 - 环境变量已配置
    1 - 环境变量未配置
"""

import os
import sys

def check_env():
    token = os.environ.get("SMS_AUTH_TOKEN", "")
    
    if not token:
        print("❌ SMS_AUTH_TOKEN 未配置")
        print("")
        print("请先配置环境变量:")
        print("  openclaw config set env.vars.SMS_AUTH_TOKEN <你的token>")
        return 1
    
    if token == "your_token_here" or token == "":
        print("❌ SMS_AUTH_TOKEN 未配置")
        print("")
        print("请先配置环境变量:")
        print("  openclaw config set env.vars.SMS_AUTH_TOKEN <你的token>")
        return 1
    
    print("✅ SMS_AUTH_TOKEN 已配置")
    return 0

if __name__ == "__main__":
    sys.exit(check_env())
