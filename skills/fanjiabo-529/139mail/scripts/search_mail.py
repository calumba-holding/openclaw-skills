#!/usr/bin/env python3
"""搜索139邮箱邮件"""
from imapclient import IMAPClient
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config
from ssl_helper import create_ssl_context

def search_mail(keyword, limit=20):
    config = load_config()
    if not config:
        print("❌ 未配置")
        sys.exit(1)
    
    ssl_context = create_ssl_context()
    server = IMAPClient(config['imap_server'], ssl=True, ssl_context=ssl_context)
    server.login(config['username'], config['password'])
    server.select_folder('INBOX')
    
    messages = server.search(['OR', ['SUBJECT', keyword], ['FROM', keyword]])
    
    if not messages:
        print(f"📭 没有找到 '{keyword}'")
        return
    
    recent = list(messages)[-limit:]
    print(f"🔍 '{keyword}' 找到 {len(messages)}封（显示{len(recent)}封）\n")
    print("-" * 60)
    
    for msg_id in reversed(recent):
        msg_data = server.fetch([msg_id], ['ENVELOPE', 'FLAGS', 'INTERNALDATE'])
        envelope = msg_data[msg_id][b'ENVELOPE']
        flags = msg_data[msg_id][b'FLAGS']
        internal_date = msg_data[msg_id][b'INTERNALDATE']
        
        subject = envelope.subject
        if isinstance(subject, bytes):
            try: subject = subject.decode('utf-8')
            except: subject = subject.decode('gbk', errors='ignore')
        elif subject is None: subject = "(无主题)"
        
        sender = envelope.from_[0] if envelope.from_ else None
        sender_str = f"{sender.mailbox.decode()}@{sender.host.decode()}" if sender else "Unknown"
        date_str = internal_date.strftime('%Y-%m-%d %H:%M') if internal_date else "未知"
        
        is_unread = b'\\Seen' not in flags
        unread_mark = "📬" if is_unread else "📧"
        
        print(f"\n{unread_mark} ID: {msg_id}")
        print(f"   发件人: {sender_str}")
        print(f"   主题: {subject}")
        print(f"   日期: {date_str}")
    
    print("\n" + "-" * 60)
    server.logout()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('keyword', help='搜索关键词')
    parser.add_argument('--limit', '-l', type=int, default=20)
    args = parser.parse_args()
    search_mail(args.keyword, args.limit)
