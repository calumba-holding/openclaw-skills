---
name: 139mail
description: 139邮箱IMAP/POP3操作技能。支持通过IMAP/POP3协议查看收件箱/未读邮件、发送邮件、搜索邮件、管理邮件、邮件分拣。首次使用需配置账号和授权码。当用户需要操作139邮箱（mail.10086.cn）时触发此技能。
---

# 139邮箱IMAP/POP3操作技能

## 概述

本技能通过IMAP/POP3协议直接连接139邮箱服务器，实现高效的邮件管理功能。

**重要：首次使用需配置账号和授权码**

## 安装依赖

本技能需要安装第三方依赖库：

```bash
pip install imapclient
```

**依赖说明**：
- `imapclient`：用于IMAP协议连接139邮箱服务器
- 标准库：`smtplib`, `email`, `json`, `argparse`（Python内置）

## SSL/TLS 安全说明

由于139邮箱服务器使用的是TLS协议，本技能使用兼容模式连接。

**安全建议**：
- 兼容模式会降低SSL安全性，建议仅在受信任的网络环境中使用

## 首次使用流程

当用户首次请求操作139邮箱时：

1. **询问用户是否已开启IMAP服务**
   - 告知用户需要前往 https://mail.10086.cn/ 开启IMAP服务
   - 获取授权码（代替密码使用）

2. **收集配置信息**
   - 139邮箱账号（如：136xxxxxxxxx@139.com）
   - 授权码（不是登录密码！）

3. **保存配置**
   - 调用 `scripts/config_manager.py save` 保存配置
   - 配置保存在 `config/139mail.conf`（JSON格式）

4. **测试连接**
   - 验证账号和授权码是否正确
   - 成功后开始执行用户请求的操作

## 配置管理

**脚本**：`scripts/config_manager.py`

**命令**：
- `python scripts/config_manager.py check` - 检查是否已配置
- `python scripts/config_manager.py save --username <账号> --password <授权码>` - 保存配置
- `python scripts/config_manager.py show` - 显示当前配置（隐藏授权码）

**配置文件**：`config/139mail.conf`

配置文件格式（JSON）：
```json
{
  "username": "136xxxxxxxxx@139.com",
  "password": "授权码",
  "imap_server": "imap.139.com",
  "imap_port": 993,
  "smtp_server": "smtp.139.com",
  "smtp_port": 465
}
```

## 核心功能

### 1. 查看收件箱/未读邮件

**触发场景**："查看139邮箱"、"有没有新邮件"

**流程**：
1. 检查配置是否存在（`config_manager.py check`）
2. 如无配置，执行首次使用流程
3. 调用 `scripts/check_mail.py --unread`

**命令示例**：
```bash
python scripts/check_mail.py --limit 10
python scripts/check_mail.py --unread
```

### 2. 查看指定邮件详情

**脚本**：`scripts/view_mail.py <邮件ID>`

**示例**：
```bash
python scripts/view_mail.py 123
```

### 3. 发送邮件

**脚本**：`scripts/send_mail.py <收件人> <主题> <正文>`

**示例**：
```bash
python scripts/send_mail.py "recipient@example.com" "主题" "正文内容"
```

### 4. 搜索邮件

**脚本**：`scripts/search_mail.py <关键词>`

**示例**：
```bash
python scripts/search_mail.py "工作汇报"
```

### 5. 管理邮件

**脚本**：`scripts/manage_mail.py`

**常用命令**：
```bash
# 列出邮件
python scripts/manage_mail.py --list

# 列出已删除邮件
python scripts/manage_mail.py --list-trash

# 标记已读/未读
python scripts/manage_mail.py --mark-read <ID>
python scripts/manage_mail.py --mark-unread <ID>

# 删除邮件（移动到已删除文件夹）
python scripts/manage_mail.py --delete <ID>

# 恢复邮件（从已删除文件夹恢复）
python scripts/manage_mail.py --restore <ID>

# 彻底删除（永久删除，不可恢复）
python scripts/manage_mail.py --permanent-delete <ID>
```

### 6. 邮件分拣

**脚本**：`scripts/move_mail.py`

**示例**：
```bash
# 列出所有文件夹
python scripts/move_mail.py --list-folders

# 移动邮件
python scripts/move_mail.py --move <邮件ID> --to <目标文件夹>
```

## 错误处理

**授权码失效时**：
- 提示用户重新获取授权码
- 更新配置文件
- 重新尝试操作

**SSL连接失败**：
如果遇到SSL握手错误，可能是网络问题或139邮箱服务器暂时不可用。请检查网络连接后重试。

## 首次使用提示模板

当检测到用户未配置时，使用以下提示：

```
首次使用139邮箱功能，需要您先完成以下设置：

1. 安装依赖：
   pip install imapclient

2. 登录 https://mail.10086.cn/
3. 进入 设置 → 账户 → IMAP/POP3服务
4. 开启 IMAP/POP3 服务
5. 获取授权码（不是登录密码！）

请提供：
- 139邮箱账号（如 136xxxxxxxxx@139.com）
- 授权码：______
```

## 安全说明

1. **配置文件权限**：配置文件 `config/139mail.conf` 保存时设置权限为 600（仅所有者可读写）
2. **SSL/TLS**：使用兼容模式连接139邮箱。由于139邮箱使用较旧TLS协议，此模式会降低SSL安全性，建议仅在受信任的网络环境中使用。
3. **授权码保护**：授权码仅保存在本地配置文件，不会上传到任何外部服务器。
4. **使用完成后**：如不再使用，建议删除配置文件并撤销邮箱授权码。

## 参考文档

- **IMAP操作指南**：参见 [references/imap_guide.md](references/imap_guide.md)
- **服务器配置**：参见 [references/credentials.md](references/credentials.md)
