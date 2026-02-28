#!/usr/bin/env python3
"""发送139邮箱邮件"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_manager import load_config

def send_email(to_addr, subject, body, html=False):
    config = load_config()
    if not config:
        print("❌ 未配置")
        sys.exit(1)
    
    msg = MIMEMultipart()
    msg['From'] = Header(config['username'], 'utf-8')
    msg['To'] = Header(to_addr, 'utf-8')
    msg['Subject'] = Header(subject, 'utf-8')
    msg.attach(MIMEText(body, 'html' if html else 'plain', 'utf-8'))
    
    server = smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port'])
    server.login(config['username'], config['password'])
    server.sendmail(config['username'], [to_addr], msg.as_string())
    server.quit()
    print(f"✅ 邮件发送成功！收件人: {to_addr}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('to', help='收件人')
    parser.add_argument('subject', help='主题')
    parser.add_argument('body', help='正文')
    parser.add_argument('--html', action='store_true')
    args = parser.parse_args()
    send_email(args.to, args.subject, args.body, args.html)
