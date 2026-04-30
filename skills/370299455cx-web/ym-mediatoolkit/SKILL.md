---
name: ym-mediatoolkit
version: 2.1.0
description: 流式视频处理工具集 - 压缩、封面提取、音频转换，无需下载完整视频
author: your_name
tags:
  - video
  - compression
  - thumbnail
  - audio
  - streaming
  - ffmpeg
  - security
categories:
  - media
  - utility
clawhub:
  entrypoint: python run.py
  runtime: python3
  http_port: 8080
  note: "HTTP 服务默认绑定 127.0.0.1，勿直接暴露到公网"
---

# YM MediatoolToolkit

## 概述

一个高性能的流式视频处理 Skill，**无需下载完整视频文件**即可完成：

- **视频压缩** - 保持清晰度，体积可压缩至 1/10
- **封面提取** - 任意时间点或帧号提取封面
- **音频提取** - 转成 MP3 / WAV / AAC / M4A 格式

所有操作均采用**流式处理**，边下载边处理，大幅节省时间和磁盘空间。

---

## 安全特性

### URL 验证 (SSRF/LFI 防护)

`utils.validate_video_url()` 在**所有入口点和子进程调用前**执行多层验证：

| 层级 | 检查项 | 防护目标 |
|------|--------|---------|
| **协议** | 仅允许 `http://` / `https://` | LFI (`file://`)、协议走私 |
| **字符** | 拦截 IDN/Unicode 同形字、Punycode (`xn--`) | 域名欺骗攻击 |
| **IP 模式** | 正则匹配 + `ipaddress` 库双重校验私有 IP 段 (10.x/172.16-31.x/192.168.x/127.x/169.254.x/0.x) | IP 直连 SSRF |
| **DNS 解析** | `socket.getaddrinfo` 解析域名 → `ipaddress` 检查所有解析 IP (IPv4+IPv6) | DNS 绑定到私有 IP 的 SSRF |
| **IPv6** | 检查 `::1`、`fe80::`、`fc00::/fdff::`、`::ffff:0:0` (IPv4-mapped) | IPv6 SSRF |

> **DNS 错误策略**：如果 DNS 解析失败（超时/网络错误），验证将**拒绝请求**（fail-close），而非放行。这是与早期版本的区别——之前版本在 DNS 失败时会发出警告并允许通过。

### 输出路径防护

`utils.sanitize_output_path()` 对所有用户提供的 `output_path`、`save_path`、`output_dir` 执行检查：

| 检查项 | 说明 |
|--------|------|
| **路径穿越** | 拒绝包含 `..` 的路径 |
| **保留设备名** | 拒绝 CON/NUL/COM1 等系统保留名 |
| **越界写入** | 拒绝解析后超出工作目录的路径 |

路径清理在所有入口点执行：
- `run.py` — `handle_compress`、`handle_thumbnail`、`handle_audio`、`handle_audio_batch`
- `audio_extractor.py` — `extract_audio_streaming`、`extract_audio_batch`
- `frame_extractor.py` — `extract_thumbnail_from_url`

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 通过命令行使用

提供 JSON 参数：

```bash
# 压缩视频
python run.py -a compress -i '{"video_url": "https://example.com/video.mp4", "target_ratio": 0.1}'

# 提取封面（第 0 秒）
python run.py -a thumbnail -i '{"video_url": "https://example.com/video.mp4"}'

# 提取音频
python run.py -a audio -i '{"video_url": "https://example.com/video.mp4", "format": "mp3"}'
```

### 3. 通过配置文件

```bash
python run.py -i params.json
```

### 4. 启动 HTTP 服务

```bash
# 启动 API 服务
python run.py --serve

# 默认监听 127.0.0.1:8080（仅本地访问）
```

> HTTP 模式需要 Flask：
> ```bash
> pip install flask flask-cors
> ```

---

## API 参考

所有端点接收 JSON body，响应 JSON。

### `POST /skill/compress`

流式压缩视频。

**请求参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `video_url` | string | **必填** | 视频 URL（仅 http/https） |
| `target_ratio` | number | 0.1 | 目标体积比例 |
| `adaptive` | boolean | true | 是否自动调整 CRF |
| `crf` | integer | 24 | CRF 值（18-28） |
| `preset` | string | "veryfast" | 编码预设 |
| `output_path` | string | 自动生成 | 输出路径 |

**响应示例：**

```json
{
  "status": "success",
  "output_path": "compressed_video.mp4",
  "original_size_mb": 150.5,
  "new_size_mb": 12.3,
  "ratio": 0.082,
  "crf_used": 24,
  "streaming": true
}
```

### `POST /skill/thumbnail`

从视频提取封面。

**请求参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `video_url` | string | **必填** | 视频 URL |
| `time_seconds` | number | 0 | 提取时间点（秒） |
| `frame_number` | integer | - | 指定帧号（优先级高于 time） |
| `save_path` | string | 不保存 | 封面保存路径 |
| `resize_width` | integer | 原尺寸 | 缩放宽度 |
| `quality` | integer | 85 | JPEG 质量（1-100） |

**响应示例：**

```json
{
  "status": "success",
  "video_info": {
    "width": 1920,
    "height": 1080,
    "codec": "h264",
    "fps": 30000,
    "duration": 120.5,
    "total_frames": 3615,
    "extract_method": "time_10s"
  },
  "shape": [1080, 1920, 3],
  "saved_path": "thumbnail.jpg"
}
```

### `POST /skill/audio`

流式提取音频。

**请求参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `video_url` | string | **必填** | 视频 URL |
| `format` | string | "mp3" | 音频格式：mp3/wav/aac/m4a |
| `bitrate` | string | "128k" | 比特率 |
| `sample_rate` | integer | 44100 | 采样率 |
| `channels` | integer | 2 | 声道数 |
| `start_time` | number | 全部 | 开始时间（秒） |
| `duration` | number | 全部 | 持续时间（秒） |
| `output_path` | string | 自动生成 | 输出路径 |

**响应示例：**

```json
{
  "status": "success",
  "output_path": "audio.mp3",
  "format": "mp3",
  "size_mb": 5.2,
  "duration_sec": 120.5,
  "bitrate": "128k",
  "sample_rate": 44100,
  "channels": 2,
  "streaming": true
}
```

### `POST /skill/audio_batch`

批量提取多个视频的音频。

**请求参数：**

```json
{
  "videos": [
    {"url": "https://...", "name": "video1"},
    {"url": "https://...", "name": "video2"}
  ],
  "output_dir": "./audio_output",
  "format": "mp3",
  "bitrate": "192k",
  "sample_rate": 44100
}
```

### `POST /skill/audio_info`

获取视频的音频流信息。

**请求参数：** `{"video_url": "https://..."}`

### `POST /skill/info`

获取视频完整信息（分辨率、时长、编码等）。

**请求参数：** `{"video_url": "https://..."}`

### `POST /skill/batch`

批量处理（压缩/封面/音频）。

**请求参数：**

```json
{
  "action": "thumbnail",
  "videos": [
    {"video_url": "https://...", "time_seconds": 5},
    {"video_url": "https://...", "time_seconds": 10}
  ]
}
```

### `GET /health`

健康检查端点：

```json
{
  "status": "ok",
  "skill": "video-streaming-toolkit"
}
```

---

## 命令行 (CLI)

```bash
python run.py -a <action> -i '<json>'
# 或
python run.py -i params.json
```

---

## 架构说明

```
                    ┌─────────────┐
                    │  run.py     │  ← 统一入口（CLI/HTTP）
                    │  (入口)      │
                    └─────┬───────┘
                          │
            ┌─────────────┼──────────────┐
            ▼             ▼              ▼
    ┌────────────┐ ┌───────────┐ ┌──────────────┐
    │ audio_     │ │ video_    │ │ frame_       │
    │ extractor  │ │ compressor│ │ extractor    │
    │ .py        │ │ .py       │ │ .py          │
    └────────────┘ └───────────┘ └──────────────┘
            │             │              │
            ▼             ▼              ▼
       ┌─────────────────────────────────────┐
       │           utils.py                  │
        │  · validate_video_url()             │ ← URL/SSRF 验证
        │  · sanitize_output_path()           │ ← 路径穿越防护
        │  · get_file_size_mb()               │
        │  · download_video_to_temp()         │
        └─────────────────────────────────────┘
```

所有模块共用 `utils.validate_video_url()` 和 `utils.sanitize_output_path()` 进行安全校验。

---

## 测试

```bash
# 压缩测试
python run.py -a compress -i '{"video_url": "https://example.com/sample.mp4"}'

# 封面测试
python run.py -a thumbnail -i '{"video_url": "https://example.com/sample.mp4", "time_seconds": 10}'

# 音频测试
python run.py -a audio -i '{"video_url": "https://example.com/sample.mp4", "format": "mp3"}'

# 安全验证测试（应被拒绝）
python run.py -a info -i '{"video_url": "file:///etc/passwd"}'
python run.py -a info -i '{"video_url": "http://127.0.0.1:8080/admin"}'
python run.py -a info -i '{"video_url": "http://192.168.1.1/config"}'
python run.py -a info -i '{"video_url": "http://10.0.0.1/internal"}'
python run.py -a info -i '{"video_url": "http://[::1]/admin"}'
python run.py -a info -i '{"video_url": "http://evil.com"}'  # 若 evil.com 解析到内网 IP
```

---

## 安全部署指南

### 外部依赖

本技能通过 `subprocess` 调用系统命令 `ffmpeg` 和 `ffprobe`。请确保从可信源安装：

```bash
# Ubuntu/Debian
apt install ffmpeg

# Alpine (推荐容器)
apk add ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

### 推荐部署方式

```
 Docker 容器 (python:3.11-slim)
 +----------------------------------+
 | python run.py --serve             |
 |   --host 0.0.0.0 --port 8080     |  ← 容器内绑定 0.0.0.0
 | ffmpeg (apt install)              |     反向代理控制外部暴露
 | 以非 root 用户运行                 |
 +---------------+------------------+
                 |
                 ▼
 Nginx / Caddy (反向代理 + 认证)
 限制网络出站, 配置 ACL
```

### 运行时安全

| 要求 | 说明 |
|------|------|
| **最小权限** | 以非 root 用户运行，仅有 temp/output 目录写权限 |
| **网络隔离** | 限制容器出站到仅允许的 CDN/视频源域名 |
| **磁盘配额** | 限制临时目录大小，防止磁盘填满 |
| **临时目录清理** | 使用 `TMPDIR` 环境变量指定临时目录并定期清理 |
| **认证** | 生产环境务必在 HTTP 服务器前添加反向代理认证 (Basic Auth / OAuth / API Key) |

### 启动选项

```bash
# 仅本地访问（安全默认）
python run.py --serve

# 指定地址和端口
python run.py --serve --host 127.0.0.1 --port 9000

# 仅限内网访问（需要反向代理认证）
python run.py --serve --host 0.0.0.0 --port 8080
```

### 已知限制

| 限制 | 说明 | 缓解措施 |
|------|------|---------|
| **DNS 重绑定** | 攻击者可在验证通过后快速切换 DNS 记录，指向内网地址 | 网络层出口控制 / 使用固定 IP 白名单 |
| **HTTP 重定向** | ffmpeg 可能跟随 302 跳转到验证时未检查的地址 | 部署反向代理并启用重定向验证 |
| **十六进制/十进制 IP** | `0x7f000001` (127.0.0.1) 等格式不会被 ip_address 识别 | `getaddrinfo` 可捕获部分此类情况，依赖平台 |
| **ffmpeg 沙箱** | ffmpeg/ffprobe 通过子进程执行非受信 URL | 隔离容器 + 非 root 用户 + 最小权限 |
| **完整下载** | `download_video_to_temp()` 会将文件完整下载到磁盘 | 该函数当前未被主流程调用，仅作为工具函数保留；若启用需设置磁盘配额 |
