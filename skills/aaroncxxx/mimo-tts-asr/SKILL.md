---
name: mimo-tts-asr
description: >-
  Xiaomi MiMo V2.5 TTS + ASR 全能语音技能。支持高质量中英文语音合成（TTS）和语音识别（ASR）。
  TTS: 三款模型（精品音色 / VoiceDesign 音色设计 / VoiceClone 音色克隆）、方言支持、情感控制、多格式输出。
  ASR: 音频转文字、多语言识别、方言、Code-Switch、强噪音场景。支持 API 调用和开源模型本地部署。
  触发词: 语音合成 / 文字转语音 / TTS / 朗读 / 说话 / 唱歌 / 语音识别 / 转文字 / 听写 / ASR /
  音色设计 / 音色克隆 / 声音克隆 / voice design / voice clone / voice / speech /
  read aloud / transcribe / speech-to-text / 语音转文字 / 音频转文字。
  Use when: 用户要求将文字转为语音、朗读文本、生成音频、识别音频内容、将音频转为文字、设计音色、克隆音色。
---

# Xiaomi MiMo-V2.5-TTS-Series + ASR — 你的声音，随心所"驭"

> v2.5.4 · 面向 Agent 时代的全链路语音模型系列

## 官方资源 / Official Links

| 资源 | 链接 |
|------|------|
| 📖 发布公告 | [MiMo-V2.5-TTS-Series + ASR 正式发布](https://platform.xiaomimimo.com/docs/news/v2.5-tts-release) |
| 📚 TTS API 文档 | [语音合成（MiMo-V2.5-TTS 系列）](https://platform.xiaomimimo.com/docs/usage-guide/speech-synthesis-v2.5) |
| 📚 ASR API 文档 | [音频理解](https://platform.xiaomimimo.com/docs/usage-guide/multimodal-understanding/audio-understanding) |
| 🎮 MiMo Studio 体验 | [aistudio.xiaomimimo.com/#/c](https://aistudio.xiaomimimo.com/#/c) |
| 🔧 官方 Skill 仓库 | [github.com/XiaomiMiMo/MiMo-Skills](https://github.com/XiaomiMiMo/MiMo-Skills) |
| 🤗 ASR 开源代码 | [github.com/XiaomiMiMo/MiMo-V2.5-ASR](https://github.com/XiaomiMiMo/MiMo-V2.5-ASR) |
| 🤗 ASR 模型权重 | [huggingface.co/XiaomiMiMo/MiMo-V2.5-ASR](https://huggingface.co/XiaomiMiMo/MiMo-V2.5-ASR) |
| 🤗 ASR Demo | [huggingface.co/spaces/XiaomiMiMo/MiMo-V2.5-ASR](https://huggingface.co/spaces/XiaomiMiMo/MiMo-V2.5-ASR) |
| 📋 定价与限速 | [定价说明](https://platform.xiaomimimo.com/docs/pricing) |
| 🌐 MiMo 开放平台 | [platform.xiaomimimo.com](https://platform.xiaomimimo.com) |

## 功能概览 / Overview

### TTS — 三款模型

| 模型 | 能力 | 场景 |
|------|------|------|
| 🎙️ **MiMo-V2.5-TTS** | 内置精品音色，语速/情绪/语气精细控制 | 通用语音合成 |
| 🎨 **MiMo-V2.5-TTS-VoiceDesign** | 自然语言描述从零生成新音色（无需参考音频） | 游戏NPC/虚拟主播/品牌IP |
| 🔁 **MiMo-V2.5-TTS-VoiceClone** | 短音频高保真克隆音色（数秒即可） | 播客克隆/配音复刻 |

> ⭐ **三款模型均已限时免费**

### ASR — 语音识别

| 能力 | 说明 |
|------|------|
| 🌍 中英双语 | 自由切换，无需预设语种 |
| 🗣️ 中文方言 | 吴语/粤语/闽南语/四川话 |
| 🔀 Code-Switch | 中英混杂自然转录 |
| 🎵 歌曲识别 | 中英文歌词，伴奏场景高精度 |
| 🔊 强噪音 | 高噪音/远场拾音鲁棒识别 |
| 👥 多说话人 | 会议等多人交叉对话 |
| 📝 原生标点 | 结合韵律与语义自动标点 |

> 🆓 **ASR 已开源** — [GitHub](https://github.com/XiaomiMiMo/MiMo-V2.5-ASR) / [HuggingFace](https://huggingface.co/XiaomiMiMo/MiMo-V2.5-ASR)

---

## ⚙️ 配置 / Setup

### 环境变量

```bash
# TTS API Key（独立于模型推理 Key）
export MIMO_API_KEY="your-tts-api-key"

# ASR API Key（如与 TTS 相同可复用）
export MIMO_ASR_KEY="your-asr-api-key"
```

或通过 OpenClaw 配置：
```bash
openclaw config set skills.entries.mimo-tts-asr.apiKey "your-key"
```

> ⚠️ TTS/ASR 的 API Key 独立于模型推理 Key，需前往 [platform.xiaomimimo.com](https://platform.xiaomimimo.com) 申请。

---

## 🎙️ TTS — 语音合成

### 基础用法

```bash
python3 "{baseDir}/scripts/tts.py" "要合成的文本" -o output.wav
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `text` | (必填) | 要合成的文本 |
| `-o` | `output.wav` | 输出文件路径 |
| `-m` | `tts` | 模型：tts / voice-design / voice-clone |
| `-v` | `mimo_default` | 音色（见音色列表） |
| `-s` | 无 | 风格标签 |
| `-f` | `wav` | 音频格式：wav / mp3 / ogg |
| `--voice-desc` | 无 | VoiceDesign：音色描述文本 |
| `--ref-audio` | 无 | VoiceClone：参考音频路径 |
| `--user-msg` | 无 | 用户角色上下文（调整语气） |
| `--api-key` | 环境变量 | API Key 覆盖 |
| `--max-retries` | 3 | 最大重试次数 |
| `--list-voices` | — | 列出可用音色 |
| `--list-formats` | — | 列出可用格式 |

### 音色列表（MiMo-V2.5-TTS）

| 名称 | voice 参数 | 说明 |
|------|-----------|------|
| MiMo-默认 | `mimo_default` | 通用女声 |
| MiMo-中文 | `default_zh` | 中文女声 |
| MiMo-英文 | `default_en` | 英文女声 |
| MiMo-男声 | `mimo_male` | 男声 |
| MiMo-童声 | `mimo_child` | 童声 |
| MiMo-粤语 | `mimo_cantonese` | 粤语 |
| MiMo-四川话 | `mimo_sichuan` | 四川话 |

> 🎧 试听音色：[MiMo Studio](https://aistudio.xiaomimimo.com/#/c)

### 风格标签

| 风格 | 场景 | 风格 | 场景 |
|------|------|------|------|
| 可爱 | 撒娇、软萌 | 悲伤 | 悲伤、失落 |
| 开心 | 欢快、兴奋 | 愤怒 | 愤怒、激动 |
| 东北话 | 方言、搞笑 | 平静 | 平静、舒缓 |
| 悄悄话 | 神秘、低语 | 惊讶 | 惊讶、意外 |
| 孙悟空 | 角色扮演 | 变快/变慢 | 语速控制 |
| 唱歌 | 儿歌、旋律 | | |

可组合：`-s "开心 变快"` / `-s "可爱 悄悄话"` / `-s "悲伤 变慢"`

### 行内音频标签

在文本中插入精细控制：
`(停顿)` `(叹气)` `(笑声)` `(清嗓子)` `(耳语)` `(紧张)` `(小声)` `(语速加快)` `(深呼吸)` `(沉默片刻)`

### 示例

```bash
# 基础合成
python3 "{baseDir}/scripts/tts.py" "你好，今天天气真好" -o hello.wav

# 方言
python3 "{baseDir}/scripts/tts.py" "哎呀妈呀，这天儿也忒冷了吧" -s "东北话" -o dongbei.wav

# 英文
python3 "{baseDir}/scripts/tts.py" "Hello, how are you?" -v default_en -o hello_en.wav

# 情感
python3 "{baseDir}/scripts/tts.py" "明天就是周五了，真开心！" -s "开心 变快" -o happy.wav

# 唱歌
python3 "{baseDir}/scripts/tts.py" "一闪一闪亮晶晶" -s "唱歌" -o sing.wav

# 男声 / 童声 / 方言
python3 "{baseDir}/scripts/tts.py" "大家好" -v mimo_male -o male.wav
python3 "{baseDir}/scripts/tts.py" "妈妈我要吃糖" -v mimo_child -o child.wav
python3 "{baseDir}/scripts/tts.py" "你好，今日天气好好" -v mimo_cantonese -o cantonese.wav
python3 "{baseDir}/scripts/tts.py" "这个火锅巴适得很" -v mimo_sichuan -o sichuan.wav

# MP3 / OGG
python3 "{baseDir}/scripts/tts.py" "测试" -f mp3 -o output.mp3
python3 "{baseDir}/scripts/tts.py" "测试" -f ogg -o output.ogg

# 🎨 VoiceDesign — 从描述生成新音色
python3 "{baseDir}/scripts/tts.py" "你好，欢迎来到我的世界" \
  -m voice-design \
  --voice-desc "一位年迈的东欧裔学者，低沉、略带嘶哑，说话节奏缓慢" \
  -o scholar.wav

python3 "{baseDir}/scripts/tts.py" "元气满满的一天开始啦！" \
  -m voice-design \
  --voice-desc "元气满满的少女，声线清脆，语尾带一点上扬" \
  -o genki.wav

# 🔁 VoiceClone — 用参考音频克隆音色
python3 "{baseDir}/scripts/tts.py" "这是克隆后的声音" \
  -m voice-clone \
  --ref-audio reference.wav \
  -o cloned.wav
```

---

## 🎧 ASR — 语音识别

### API 调用

```bash
python3 "{baseDir}/scripts/asr.py" audio.wav
python3 "{baseDir}/scripts/asr.py" audio.mp3 -o transcript.txt
python3 "{baseDir}/scripts/asr.py" audio.wav --lang zh --format json
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `audio` | (必填) | 音频文件路径（wav/mp3/ogg/m4a/flac） |
| `-o` | stdout | 输出文件路径（默认打印到终端） |
| `--lang` | `auto` | 语言：auto / zh / en / ja / ko |
| `--format` | `text` | 输出格式：text / json / srt |
| `--api-key` | 环境变量 | API Key 覆盖 |
| `--max-retries` | 3 | 最大重试次数 |

### 输出格式

| 格式 | 说明 | 适用场景 |
|------|------|----------|
| `text` | 纯文本 | 快速查看 |
| `json` | 带时间戳和置信度 | 程序处理 |
| `srt` | SRT 字幕格式 | 视频字幕 |

### 本地部署（开源模型）

ASR 已开源，支持本地部署：

```bash
# 克隆仓库
git clone https://github.com/XiaomiMiMo/MiMo-V2.5-ASR.git
cd MiMo-V2.5-ASR

# 安装依赖
pip install -r requirements.txt

# 使用 HuggingFace 权重
python inference.py --audio audio.wav --output result.txt
```

> 📖 详细文档：[github.com/XiaomiMiMo/MiMo-V2.5-ASR](https://github.com/XiaomiMiMo/MiMo-V2.5-ASR)
> 🤗 在线体验：[huggingface.co/spaces/XiaomiMiMo/MiMo-V2.5-ASR](https://huggingface.co/spaces/XiaomiMiMo/MiMo-V2.5-ASR)

### 示例

```bash
# 基础转录
python3 "{baseDir}/scripts/asr.py" recording.wav

# 保存到文件
python3 "{baseDir}/scripts/asr.py" meeting.mp3 -o meeting.txt

# 指定语言
python3 "{baseDir}/scripts/asr.py" english.mp3 --lang en

# JSON 格式（带时间戳）
python3 "{baseDir}/scripts/asr.py" audio.wav --format json

# SRT 字幕
python3 "{baseDir}/scripts/asr.py" video_audio.wav --format srt -o subtitles.srt
```

---

## 🔗 TTS + ASR 联合工作流

```bash
# 1. 先识别一段音频
python3 "{baseDir}/scripts/asr.py" input.wav -o transcript.txt

# 2. 修改文本后重新合成（用不同音色）
python3 "{baseDir}/scripts/tts.py" "$(cat transcript.txt)" -v mimo_male -o output.wav

# 3. 克隆音色后重新演绎
python3 "{baseDir}/scripts/tts.py" "$(cat transcript.txt)" \
  -m voice-clone --ref-audio original.wav -o cloned.wav
```

---

## 📋 交付

### TTS 输出
```bash
MEDIA:output.wav
```

### ASR 输出
直接回复转录文本，或保存到文件后回复路径。

---

## 故障排查

| 错误 | 原因 | 解决 |
|------|------|------|
| 401 Invalid API Key | Key 未配置或格式错误 | 确认已配置 TTS/ASR 专用 Key |
| 429 Too Many Requests | 触发限流 | 等几秒后重试（脚本自动重试） |
| 500 Server Error | 服务端异常 | 稍后重试 |
| 文件不存在 | 音频路径错误 | 检查文件路径 |

---

## 📋 版本历史

### v2.5.4 (2026-04-24)
- ✨ 新增 VoiceDesign（音色设计）模型支持
- ✨ 新增 VoiceClone（音色克隆）模型支持
- ✨ 新增官方资源链接汇总
- ✨ ASR 新增本地部署文档（开源模型）
- 📚 文档优化：对齐官方发布说明

### v2.5.2 (2026-04-24)
- ✨ TTS + ASR 一体化
- ✨ 7 种 TTS 音色 + 方言 + 情感控制
- ✨ ASR 支持 auto/zh/en/ja/ko 多语言
- ✨ ASR 输出格式：text / json / srt
- ✨ 行内音频标签精细控制
- ✨ MP3/OGG/WAV 多格式支持
- ✨ 自动重试 + 限流处理
