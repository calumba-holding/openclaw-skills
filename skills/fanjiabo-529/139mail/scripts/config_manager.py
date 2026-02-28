#!/usr/bin/env python3
"""139邮箱配置管理器"""

import json
import os
import sys

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
CONFIG_FILE = os.path.join(CONFIG_DIR, '139mail.conf')

def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None

def save_config(username, password):
    ensure_config_dir()
    config = {
        "username": username,
        "password": password,
        "imap_server": "imap.139.com",
        "imap_port": 993,
        "smtp_server": "smtp.139.com",
        "smtp_port": 465
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    os.chmod(CONFIG_FILE, 0o600)
    return True

def check_config():
    config = load_config()
    return config and config.get('username') and config.get('password')

def show_config():
    config = load_config()
    if not config:
        print("❌ 未找到配置")
        return
    print("📋 当前配置：")
    print(f"  账号: {config.get('username', 'N/A')}")
    print(f"  授权码: {'*' * 8} (已隐藏)")

def delete_config():
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        print("✅ 配置已删除")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['check', 'save', 'show', 'delete'])
    parser.add_argument('--username', '-u')
    parser.add_argument('--password', '-p')
    args = parser.parse_args()
    
    if args.action == 'check':
        sys.exit(0 if check_config() else 1)
    elif args.action == 'save':
        if save_config(args.username, args.password):
            print("✅ 配置保存成功！")
    elif args.action == 'show':
        show_config()
    elif args.action == 'delete':
        delete_config()
