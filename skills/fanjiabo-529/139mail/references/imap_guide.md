# IMAP/POP3 操作指南

## Python 依赖
```bash
pip install imapclient
```

## IMAP 常用操作

### 连接服务器（标准SSL）
```python
from imapclient import IMAPClient

server = IMAPClient('imap.139.com', ssl=True)
server.login('username@139.com', 'password')
```

### 连接服务器（兼容模式，针对139邮箱）
```python
from imapclient import IMAPClient
import ssl

# 139邮箱需要兼容模式
context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
context.set_ciphers('DEFAULT:@SECLEVEL=1')

server = IMAPClient('imap.139.com', ssl=True, ssl_context=context)
server.login('username@139.com', 'password')
```

### 列出文件夹
```python
folders = server.list_folders()
```

### 选择收件箱
```python
server.select_folder('INBOX')
```

### 搜索邮件
```python
messages = server.search(['ALL'])  # 所有邮件
messages = server.search(['UNSEEN'])  # 未读邮件
```

### 标记已读
```python
server.add_flags([msg_id], [b'\\Seen'])
```

### 删除邮件
```python
server.delete_messages([msg_id])
server.expunge()
```
