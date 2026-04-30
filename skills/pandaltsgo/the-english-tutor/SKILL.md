---
name: english-tutor
description: 英语口语陪练助手。触发词：「练习英语」「我要说英语」「英语陪练」。功能：上传生词表 → 每日定时情景对话 → 语音输入即时纠错 → 飞书语音推送 → 自动艾宾浩斯复习。
---

# English Tutor · 英语口语陪练

## 功能概览

| 功能 | 说明 |
|------|------|
| 飞书语音推送 | 将任意文本转为语音，直接发到用户飞书（audio 消息） |
| 每日定时练习 | cron 触发，自动选词 → 生成场景对话 → 语音推送飞书 |
| 主动练习 | 用户说「练习英语」立即开始一轮 |
| 语音纠错 | 接收用户语音回复，ASR 转写后 LLM 纠错 |
| 艾宾浩斯复习 | 多维表格记录，智能计算下次复习时间 |

---

## 环境变量参考

所有配置通过环境变量注入，**不硬编码任何路径或密钥**：

```bash
# ===== 飞书（必须）=====
FEISHU_APP_ID=cli_xxx          # 飞书应用 App ID
FEISHU_APP_SECRET=xxx           # 飞书应用 Secret
FEISHU_USER_OPEN_ID=ou_xxx     # 接收语音消息的用户 Open ID

# ===== MiniMax（必须）=====
MINIMAX_API_KEY=eyxxx           # MiniMax API Key
MINIMAX_TTS_MODEL=speech-2.8-hd # TTS 模型，默认 speech-2.8-hd
MINIMAX_TTS_VOICE_ID=male-qn-qingse  # 音色，默认 male-qn-qingse
MINIMAX_TTS_SPEED=1.05          # 语速，默认 1.05

# ===== 多维表格（必须）=====
BITABLE_APP_TOKEN=Bo8RbDzMYaX3LuscmAHcgbLLndg
BITABLE_WORDS_TABLE_ID=tblt29VL6DWwU0Fg   # 单词表
BITABLE_CHAT_TABLE_ID=tblIku7hSn7kXlBx   # 对话记录表

# ===== 本地 TTS 兜底（可选，不填则跳过）=====
PIPER_BIN=/vol1/@apphome/trim.openclaw/data/workspace/piper/piper
PIPER_LIB=/vol1/@apphome/trim.openclaw/data/workspace/piper
PIPER_MODEL=/vol1/@apphome/trim.openclaw/data/workspace/piper/voices/en_US-lessac-medium.onnx
PIPER_MODEL_JSON=/vol1/@apphome/trim.openclaw/data/workspace/piper/voices/en_US-lessac-medium.onnx.json

# ===== 本地 ASR（可选，不填则使用 MiniMax ASR）=====
SENSE_VOICE_MODEL_DIR=/vol1/@apphome/trim.openclaw/data/workspace/models/sherpa-onnx-sense-voice-small

# ===== 每日新词上限 =====
DAILY_WORD_MAX=15
```

---

## 核心模块 API

### 1. 飞书语音发送 — `feishu-voice.js`

**发送语音消息到飞书（audio 类型，可直接播放）**

```javascript
const { sendVoiceMessage } = require('./feishu-voice');

// 发送文本语音（自动 TTS → ffmpeg → 上传 → 发送）
await sendVoiceMessage('Hello, how are you today?', userOpenId);
// → Promise<{ message_id: string }>

// 兜底逻辑：MiniMax 配额耗尽 → 自动切换 Piper 本地 TTS
// 如两者都失败，抛异常
```

**CLI 用法：**
```bash
FEISHU_USER_OPEN_ID=ou_xxx node feishu-voice.js "Hello world"
```

**流程：**
```
文本 → MiniMax TTS → MP3 → ffmpeg 转 Opus → 上传飞书(file_key) → 发送 audio 消息
                            ↑
                      配额耗尽时自动切换
                            ↓
                    Piper 本地 TTS → WAV → Opus
```

---

### 2. 本地 TTS — `local-tts.js`

**Piper 完全离线语音合成（MiniMax 兜底方案）**

```javascript
const { speakLocal } = require('./local-tts');

// 直接合成 + 发送飞书语音
await speakLocal('要说的文本', userOpenId);
```

**前提：** 需下载 Piper 二进制 + 模型（见下方「下载命令」）

---

### 3. ASR 语音识别 — `asr.js`

**本地 SenseVoice 离线转写**

```javascript
const { transcribe } = require('./asr');

const text = await transcribe('/path/to/audio.ogg', { sampleRate: 16000 });
// → Promise<string> 转写文字
```

**前提：** 需下载 sherpa-onnx 模型（见下方「下载命令」）

---

### 4. 记忆模块 — `memory.js`

**多维表格读写（单词记录 + 对话历史）**

```javascript
const BitableMemory = require('./memory');
const memory = new BitableMemory(config);

// 单词操作
await memory.getWordRecord(userId, 'commute');     // 查询单词
await memory.upsertWordRecord(userId, 'commute', { mastery: 3, review_count: 2 });
await memory.getReviewRecords(userId);             // 获取到期复习单词
await memory.getTodayNewWords(userId, 15);         // 获取今日新词

// 对话历史
await memory.appendChatLog(userId, { role: 'ai', text: '...' }, { role: 'user', text: '...' });
await memory.getChatHistory(userId, 10);
```

---

### 5. 主 Agent — `agent.js`

**完整对话流程**

```javascript
const { run } = require('./agent');

// 交互模式（用户发消息触发）
const result = await run(userInputText, feishuEvent, 'morning');

// 课程模式（定时任务，无用户输入时自动生成）
const result = await run('', event, 'evening');
// → 自动生成3段跟读对话，发送飞书语音，等待用户回复
```

**返回：**
```javascript
{
  success: true,
  aiReply: '...',         // AI 回复文本
  voiceUrl: 'file://...',  // 语音文件路径
  pushText: '...',        // 飞书推送文本
  lessonMode: false,      // 是否为课程模式
}
```

---

## 定时任务配置

每个时间点创建独立 cron：

```json
{
  "name": "英语陪练·每日练习 08:00",
  "schedule": { "kind": "cron", "expr": "0 8 * * *", "tz": "Asia/Shanghai" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "执行每日英语练习：加载配置和今日单词（艾宾浩斯优先），生成情景对话，用飞书语音发送今日单词到飞书，等待用户回复并纠错，最后更新单词复习日期。",
    "timeoutSeconds": 300
  },
  "delivery": { "mode": "none" }
}
```

**环境变量注入：** cron `env` 字段注入所有配置（见上方环境变量参考）

---

## 模型下载命令

### Piper TTS（本地语音合成）

```bash
# 下载 piper 主程序（Linux x86_64）
mkdir -p /vol1/@apphome/trim.openclaw/data/workspace/piper
curl -L https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz \
  -o /tmp/piper.tar.gz && tar xf /tmp/piper.tar.gz -C /tmp

# 下载美语语音模型（Lessac Medium）
curl -L "https://hf-mirror.com/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx" \
  -o /vol1/@apphome/trim.openclaw/data/workspace/piper/voices/en_US-lessac-medium.onnx

# 验证
echo "hello" | /tmp/piper/piper_phonemize --model /vol1/@apphome/trim.openclaw/data/workspace/piper/voices/en_US-lessac-medium.onnx -f /dev/stdin -w /tmp/test.wav
```

### SenseVoice ASR（本地语音识别）

```bash
pip install --user --break-system-packages numpy sherpa-onnx

mkdir -p /vol1/@apphome/trim.openclaw/data/workspace/models/sherpa-onnx-sense-voice-small
curl -L "https://huggingface.co/py1337/sherpa-onnx-sense-voice-small/resolve/main/model.onnx" \
  -o /vol1/@apphome/trim.openclaw/data/workspace/models/sherpa-onnx-sense-voice-small/model.onnx
curl -L "https://huggingface.co/py1337/sherpa-onnx-sense-voice-small/resolve/main/tokens.txt" \
  -o /vol1/@apphome/trim.openclaw/data/workspace/models/sherpa-onnx-sense-voice-small/tokens.txt

# 验证
python3 -c "import sherpa_onnx; print('OK')"
```

---

## 引导设置流程

当 `setup_complete == false` 时，按以下步骤引导用户：

**步骤 1：模型配置**（见上方环境变量说明）

**步骤 2：飞书配置**（提供 app_id / app_secret / user_open_id）

**步骤 3：飞书连通验证**（让用户向 Bot 发消息，确认能收到）

**步骤 4：上传单词表**（CSV 或纯文本格式）

**步骤 5：每日词数**（默认 15）

**步骤 6：练习时间**（默认 08:00 / 12:00 / 20:00）

**步骤 7：创建 cron 定时任务**

---

## 单词表格式

**CSV（推荐）：**
```csv
word,pronunciation,meaning,example
commute,/kəˈmjuːt/,通勤,I commute by subway every day.
subway,/ˈsʌbweɪ/,地铁,The subway is faster than the bus.
```

**纯文本（每行一个）：**
```csv
commute,通勤
subway,地铁
transfer,换乘
```

---

## 艾宾浩斯复习周期

| 复习轮次 | 间隔 |
|---------|------|
| 第 1 次 | 次日 |
| 第 2 次 | 3 天后 |
| 第 3 次 | 7 天后 |
| 第 4 次 | 15 天后 |
| 第 5 次+ | 掌握（不再自动提醒）|

---

## 文件结构

```
english-tutor/
├── SKILL.md               ← 本文件
├── agent.js               ← 主 Agent（课程模式 + 交互模式）
├── feishu-voice.js         ← 飞书语音发送（核心功能）
├── local-tts.js           ← Piper 本地 TTS（MiniMax 兜底）
├── asr.js                 ← SenseVoice 本地 ASR
├── minimax.js             ← MiniMax TTS + Chat API
├── memory.js              ← 多维表格记忆模块
├── config.js              ← 配置加载（环境变量）
└── scripts/
    ├── check_env.py       ← 环境检测
    ├── wordlist_parser.py ← 词表解析
    └── download_model.sh  ← 模型下载脚本
```

---

## 安全原则

- **所有密钥和路径必须通过环境变量注入**，禁止硬编码
- `.env` 文件仅用于本地开发，生产环境由 cron `env` 字段注入
- `config.js` 加载 .env 但**不设默认值**（缺失环境变量时相关功能报错）
- Python 代码块使用 `JSON.stringify` 防注入，不直接拼接 shell 变量