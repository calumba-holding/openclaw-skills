#!/usr/bin/env python3
"""管理139邮箱邮件"""
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

def get_trash_folder(server):
    for name in ['已删除', 'Trash', 'Deleted']:
        try:
            server.select_folder(name)
            return name
        except:
            continue
    return None

def list_mails(server, folder='INBOX', limit=10):
    server.select_folder(folder)
    messages = server.search(['ALL'])
    if not messages:
        print("📭 没有邮件")
        return
    recent = list(messages)[-limit:]
    display = "收件箱" if folder == 'INBOX' else folder
    print(f"📧 [{display}] 最近{len(recent)}封\n")
    print("-" * 60)
    for msg_id in reversed(recent):
        msg_data = server.fetch([msg_id], ['ENVELOPE', 'FLAGS'])
        envelope = msg_data[msg_id][b'ENVELOPE']
        subject = envelope.subject
        if isinstance(subject, bytes):
            try: subject = subject.decode('utf-8')
            except: subject = subject.decode('gbk', errors='ignore')
        elif subject is None: subject = "(无主题)"
        sender = envelope.from_[0] if envelope.from_ else None
        sender_str = f"{sender.mailbox.decode()}@{sender.host.decode()}" if sender else "Unknown"
        is_unread = b'\\Seen' not in msg_data[msg_id][b'FLAGS']
        print(f"\n{'📬' if is_unread else '📧'} ID: {msg_id} | {sender_str} | {subject}")
    print("\n" + "-" * 60)

def delete_to_trash(server, msg_id):
    server.select_folder('INBOX')
    trash = get_trash_folder(server)
    if trash:
        server.copy([msg_id], trash)
    server.delete_messages([msg_id])
    server.expunge()
    print(f"✅ 邮件 {msg_id} 已删除（{'已移动到['+trash+']' if trash else '直接删除'}）")

def restore_mail(server, msg_id):
    trash = get_trash_folder(server)
    if not trash:
        print("❌ 找不到已删除文件夹")
        return
    server.select_folder(trash)
    server.copy([msg_id], 'INBOX')
    server.delete_messages([msg_id])
    server.expunge()
    print(f"✅ 邮件 {msg_id} 已从 [{trash}] 恢复到 [收件箱]")

def permanent_delete(server, msg_id, folder='INBOX'):
    server.select_folder(folder)
    server.delete_messages([msg_id])
    server.expunge()
    print(f"🗑️ 邮件 {msg_id} 已彻底删除")

def mark_read(server, msg_id):
    server.select_folder('INBOX')
    server.add_flags([msg_id], [b'\\Seen'])
    print(f"✅ 邮件 {msg_id} 已标记已读")

def mark_unread(server, msg_id):
    server.select_folder('INBOX')
    server.remove_flags([msg_id], [b'\\Seen'])
    print(f"✅ 邮件 {msg_id} 已标记未读")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--list', '-l', action='store_true', help='列出邮件')
    parser.add_argument('--list-trash', '-lt', action='store_true', help='列出已删除')
    parser.add_argument('--delete', '-d', type=int, help='删除到已删除文件夹')
    parser.add_argument('--restore', '-r', type=int, help='恢复邮件')
    parser.add_argument('--permanent-delete', '-pd', type=int, help='彻底删除')
    parser.add_argument('--mark-read', type=int, help='标记已读')
    parser.add_argument('--mark-unread', type=int, help='标记未读')
    parser.add_argument('--limit', type=int, default=10)
    args = parser.parse_args()
    
    config = get_config()
    server = connect_server(config)
    
    if args.list:
        list_mails(server, 'INBOX', args.limit)
    elif args.list_trash:
        trash = get_trash_folder(server)
        if trash: list_mails(server, trash, args.limit)
        else: print("❌ 找不到已删除文件夹")
    elif args.delete:
        delete_to_trash(server, args.delete)
    elif args.restore:
        restore_mail(server, args.restore)
    elif args.permanent_delete:
        permanent_delete(server, args.permanent_delete)
    elif args.mark_read:
        mark_read(server, args.mark_read)
    elif args.mark_unread:
        mark_unread(server, args.mark_unread)
    else:
        parser.print_help()
    
    server.logout()
