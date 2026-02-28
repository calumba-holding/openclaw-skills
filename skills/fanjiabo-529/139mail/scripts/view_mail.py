#!/usr/bin/env python3
"""查看指定邮件详情"""
from imapclient import IMAPClient
import email
from email.header import decode_header
from email.utils import parseaddr
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config
from ssl_helper import create_ssl_context

def decode_subject(subject):
    if subject is None: return "(无主题)"
    decoded = decode_header(subject)
    result = []
    for fragment, charset in decoded:
        if isinstance(fragment, bytes):
            try: result.append(fragment.decode(charset or 'utf-8'))
            except: result.append(fragment.decode('gbk', errors='ignore'))
        else: result.append(fragment)
    return ''.join(result)

def get_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    body = payload.decode(charset, errors='ignore')
                    break
                except: continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or 'utf-8'
            body = payload.decode(charset, errors='ignore')
        except: body = str(msg.get_payload())
    return body

def view_mail(msg_id):
    config = load_config()
    if not config:
        print("❌ 未配置")
        sys.exit(1)
    
    ssl_context = create_ssl_context()
    server = IMAPClient(config['imap_server'], ssl=True, ssl_context=ssl_context)
    server.login(config['username'], config['password'])
    server.select_folder('INBOX')
    
    msg_data = server.fetch([msg_id], ['RFC822', 'FLAGS', 'INTERNALDATE'])
    if msg_id not in msg_data:
        print(f"❌ 找不到邮件 {msg_id}")
        return
    
    raw_email = msg_data[msg_id][b'RFC822']
    flags = msg_data[msg_id][b'FLAGS']
    internal_date = msg_data[msg_id][b'INTERNALDATE']
    
    msg = email.message_from_bytes(raw_email)
    subject = decode_subject(msg.get('Subject', ''))
    from_name, from_addr = parseaddr(msg.get('From', ''))
    from_name = decode_subject(from_name) if from_name else from_addr
    date_str = internal_date.strftime('%Y-%m-%d %H:%M:%S') if internal_date else "未知"
    is_unread = b'\\Seen' not in flags
    body = get_body(msg)
    
    print("=" * 60)
    print(f"📧 {'📬 未读 ' if is_unread else ''}邮件详情")
    print("=" * 60)
    print(f"ID: {msg_id}")
    print(f"主题: {subject}")
    print(f"发件人: {from_name} <{from_addr}>")
    print(f"日期: {date_str}")
    print("=" * 60)
    print("\n📄 正文：\n")
    print(body[:2000] + ("\n... (截断)" if len(body) > 2000 else ""))
    print("\n" + "=" * 60)
    
    if is_unread:
        server.add_flags([msg_id], [b'\\Seen'])
        print("✅ 已自动标记已读")
    
    server.logout()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('msg_id', type=int, help='邮件ID')
    args = parser.parse_args()
    view_mail(args.msg_id)
