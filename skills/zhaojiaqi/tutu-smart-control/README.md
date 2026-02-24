# 图图智控 TUTU Smart Control — AI Skill

图图智控（TUTU）是一款 USB 即插即用的 AI 硬件设备，无需安装 App，让 AI 像人一样远程操控你的 Android 手机。本 Skill 支持 30+ 种操作，涵盖 GUI 自动化、通讯管理、文件操作、系统管理等全场景。

## 功能概览

| 类别 | 操作数量 | 包含功能 |
|------|---------|---------|
| GUI 控制 | 8 项 | 截图、点击、长按、输入、滚动、拖拽、打开App、按键 |
| 高级 UI | 4 项 | 按文字点击、按ID点击、查找元素、UI节点树 |
| 系统信息 | 3 项 | 设备信息、在线状态、服务端版本 |
| 通讯功能 | 3 项 | 发短信、读短信、打电话 |
| 位置通知 | 2 项 | GPS定位、系统通知 |
| 反馈输出 | 2 项 | 震动、语音播报(TTS) |
| 文件管理 | 6 项 | 列目录、读/写/删文件、存储分析、大文件查找 |
| 媒体与Shell | 2 项 | 搜索媒体文件、执行Shell命令 |

## 安装

### 通过 ClawHub 安装

```bash
/skills install @tutuai/tutu-smart-control
```

### 手动安装

将 `android-remote-control/` 文件夹复制到 `~/.openclaw/skills/` 或项目的 `skills/` 目录下。

## 配置

### 必需配置

| 参数 | 说明 | 获取方式 |
|------|------|---------|
| `TUTU_API_TOKEN` | 图图智控加密 Token（包含设备身份信息） | 设备管理页面或扫描设备二维码 |

### 获取 Token

1. 购买图图智控（TUTU）硬件设备
2. 将 TUTU 插入 Android 手机 USB-C 口，自动完成连接
3. 访问 [https://tutuai.me](https://tutuai.me) 注册账号，在「设备管理」页面查看已绑定设备
4. 获取加密 Token（通过设备管理页面或扫描设备二维码）
5. Token 已包含设备身份信息，无需另外记录设备序列号

### 配置示例

在 `openclaw.json` 中：

```json
{
  "skills": {
    "entries": {
      "tutu-smart-control": {
        "enabled": true,
        "apiKey": "your_encrypted_token_here"
      }
    }
  }
}
```

或者在使用时，AI 会自动引导你提供 Token 和 SN。

## 使用场景

- **日常操控**：打开App、发消息、查短信、打电话
- **自动化任务**：App签到、批量操作、定时截图
- **系统管理**：存储清理、大文件查找、应用管理
- **信息获取**：查通知、读验证码、获取位置
- **远程协助**：帮助他人操作手机、远程排查问题
- **手机找回**：定位 + 震动 + 语音播报

## 技术架构

```
AI Agent → curl HTTP API → 图图智控云端 → MQTT Broker → TUTU 硬件 → Android 手机
```

- API 端点：`https://tutuai.me/api/phone_action.php`
- 通信协议：MQTT over SSL (端口 8883)
- 硬件连接：USB-C 即插即用，通过 ADB 协议控制手机
- 截图传输：MQTT 分片传输 + JPG 压缩
- 权限级别：system_server 级（通过 JAR 注入反射实现）

## 要求

- 图图智控（TUTU）硬件设备已插入 Android 手机并在线
- 设备需要有稳定的网络连接（WiFi 或移动数据）
- 发短信/打电话功能需要 SIM 卡
- GPS 定位需要开启位置服务

## 安全说明

- Token 采用 AES-256-CBC 加密，内含设备身份信息，不明文传输设备序列号
- Token 绑定设备，无法跨设备使用
- 所有通信通过 SSL 加密
- 截图等敏感数据定期清理
- 建议不要在公开场合暴露 Token

## 版本历史

- **v1.2.0** — 适配 ClawHub 平台，品牌升级为「图图智控 TUTU」，Token 动态配置，新增 17 个场景示例
- **v1.1.0** — 新增 19 项扩展功能（文件管理、通讯、Shell等）
- **v1.0.0** — 基础 GUI 控制（截图、点击、输入、滚动等）

## 支持

- 官网：[https://tutuai.me](https://tutuai.me)（图图智控 TUTU Smart Control）
- 问题反馈：在 ClawHub skill 页面提交 issue
