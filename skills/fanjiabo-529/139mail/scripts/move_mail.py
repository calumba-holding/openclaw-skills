#!/usr/bin/env python3
"""移动139邮箱邮件"""
from imapclient import IMAPClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config

def get_config():
    config = load_config()
    if not config:
        print("❌ 未配置")
        sys.exit(1)
    return config

def connect_server(config):
    from ssl_helper import create_ssl_context
    ssl_context = create_ssl_context()
    server = IMAPClient(config['imap_server'], ssl=True, ssl_context=ssl_context)
    server.login(config['username'], config['password'])
    return server

def list_folders(server):
    folders = server.list_folders()
    print("📁 文件夹列表：")
    for _, _, name in folders:
        print(f"  - {name}")

def move_mail(server, msg_id, target_folder):
    server.select_folder('INBOX')
    try:
        server.copy([msg_id], target_folder)
        server.delete_messages([msg_id])
        server.expunge()
        print(f"✅ 邮件 {msg_id} 已移动到 [{target_folder}]")
    except Exception as e:
        print(f"❌ 移动失败: {e}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--list-folders', '-lf', action='store_true', help='列出文件夹')
    parser.add_argument('--move', '-m', type=int, help='移动邮件')
    parser.add_argument('--to', '-t', help='目标文件夹')
    args = parser.parse_args()
    
    config = get_config()
    server = connect_server(config)
    
    if args.list_folders:
        list_folders(server)
    elif args.move and args.to:
        move_mail(server, args.move, args.to)
    else:
        parser.print_help()
    
    server.logout()
