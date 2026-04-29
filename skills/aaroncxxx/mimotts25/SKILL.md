---
name: mimotts25
description: 小米大模型 MiMo TTS 2.5 语音合成。支持多种预设音色（中文/英文/默认）、风格控制（情感、方言、角色扮演、语速）、音频标签精细控制。Use when the user asks to convert text to speech, generate audio, read text aloud with a specific style/emotion/dialect, or create voice files.
metadata: {"openclaw":{"requires":{"env":["MIMO_API_KEY"]},"primaryEnv":"MIMO_API_KEY","emoji":"🎙️"}}
---

# MiMo TTS 2.5.2 — 语音合成

小米大模型 MiMo TTS 2.5.2 版本，高质量中文/英文语音合成。

## 🆕 2.5.2 版本更新

### 新增音色
- `mimo_male` - 男声音色
- `mimo_child` - 童声音色
- `mimo_cantonese` - 粤语音色
- `mimo_sichuan` - 四川话语音

### 新增音频格式
- `mp3` - 更小的文件大小，适合网络传输
- `ogg` - 更好的兼容性，开源格式

### 优化功能
- ✅ 重试机制：自动处理API限流
- ✅ 改进错误处理：更详细的错误信息
- ✅ 超时设置：避免长时间等待

## 首次配置

⚠️ **TTS 的 API Key 独立于模型推理 Key。** 即使 `mimo-v2-pro` 能正常调用，TTS 仍需单独配置 Key。

1. 前往小米 MiMo 开放平台获取 TTS API Key：https://api.xiaomimimo.com
2. 通过 OpenClaw 配置：

```
openclaw config set skills.entries.mimotts25.apiKey "your-tts-api-key-here"
```

或直接设置环境变量 `MIMO_API_KEY`。
配置后需重启会话。

### 故障排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `401 Invalid API Key` | API Key 未传入或格式不对 | 确认已用 `config set` 配置 TTS 专用 Key，重启会话 |
| 工具调用被 abort | 上下文过长或系统繁忙 | 等几秒后重试 |

## 生成语音

使用 `scripts/tts.py` 合成语音：

```bash
python3 "{baseDir}/scripts/tts.py" "要合成的文本" -o output.wav
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `-o` | `output.wav` | 输出文件路径 |
| `-v` | `mimo_default` | 音色：`mimo_default`、`default_zh`、`default_en`、`mimo_male`、`mimo_child`、`mimo_cantonese`、`mimo_sichuan` |
| `-s` | 无 | 风格标签，如 `开心`、`东北话`、`悄悄话`、`孙悟空` |
| `-f` | `wav` | 音频格式：`wav`、`mp3`、`ogg` |
| `--user-msg` | 无 | 可选的用户角色上下文，用于调整语气 |
| `--api-key` | 环境变量 `MIMO_API_KEY` | API Key 覆盖 |
| `--max-retries` | `3` | API调用最大重试次数 |
| `--list-voices` | 无 | 列出所有可用音色 |
| `--list-formats` | 无 | 列出所有可用音频格式 |

### 使用示例

```bash
# 基础合成
python3 "{baseDir}/scripts/tts.py" "你好，今天天气真好" -o hello.wav

# 方言风格
python3 "{baseDir}/scripts/tts.py" "哎呀妈呀，这天儿也忒冷了吧" -s "东北话" -o dongbei.wav

# 英文音色
python3 "{baseDir}/scripts/tts.py" "Hello, how are you today?" -v default_en -o hello_en.wav

# 情感 + 语速
python3 "{baseDir}/scripts/tts.py" "明天就是周五了，真开心！" -s "开心 变快" -o happy.wav

# 唱歌
python3 "{baseDir}/scripts/tts.py" "一闪一闪亮晶晶" -s "唱歌" -o sing.wav

# 🆕 2.5.2 新功能示例

# 男声音色
python3 "{baseDir}/scripts/tts.py" "大家好，我是你们的主持人" -v mimo_male -o male.wav

# 童声音色
python3 "{baseDir}/scripts/tts.py" "妈妈，我想吃糖" -v mimo_child -o child.wav

# 粤语
python3 "{baseDir}/scripts/tts.py" "你好，今日天气好好" -v mimo_cantonese -o cantonese.wav

# 四川话
python3 "{baseDir}/scripts/tts.py" "这个火锅巴适得很" -v mimo_sichuan -o sichuan.wav

# MP3格式（更小的文件）
python3 "{baseDir}/scripts/tts.py" "今天心情不错" -f mp3 -o output.mp3

# OGG格式（开源格式）
python3 "{baseDir}/scripts/tts.py" "测试音频" -f ogg -o output.ogg

# 列出所有可用音色
python3 "{baseDir}/scripts/tts.py" --list-voices

# 列出所有可用音频格式
python3 "{baseDir}/scripts/tts.py" --list-formats
```

## 风格与音频标签

- 在文本开头使用 `<style>风格</style>` 设置整体风格
- 行内音频标签精细控制：`(紧张)`、`(小声)`、`(语速加快)`、`(深呼吸)`、`(苦笑)`、`(沉默片刻)`
- 多风格组合：`<style>开心 变快</style>文本内容`

### 🆕 2.5.2 新增风格标签
- `(停顿)` - 自然停顿
- `(叹气)` - 叹气声
- `(笑声)` - 轻笑
- `(清嗓子)` - 清嗓子声音
- `(耳语)` - 耳语效果

## 音色列表

| 名称 | voice 参数 |
|------|-----------|
| MiMo-默认 | `mimo_default` |
| MiMo-中文女声 | `default_zh` |
| MiMo-英文女声 | `default_en` |
| MiMo-男声 | `mimo_male` |
| MiMo-童声 | `mimo_child` |
| MiMo-粤语 | `mimo_cantonese` |
| MiMo-四川话 | `mimo_sichuan` |

## 参考风格

| 风格 | 适用场景 |
|------|---------|
| `可爱` | 撒娇、软萌 |
| `开心` | 欢快、兴奋 |
| `东北话` | 方言、搞笑 |
| `悄悄话` | 神秘、低语 |
| `孙悟空` | 角色扮演 |
| `唱歌` | 儿歌、旋律 |
| `变快` / `变慢` | 语速控制 |
| 🆕 `悲伤` | 悲伤、失落 |
| 🆕 `愤怒` | 愤怒、激动 |
| 🆕 `平静` | 平静、舒缓 |
| 🆕 `惊讶` | 惊讶、意外 |
| 可自由组合 | `开心 变快`、`可爱 悄悄话`、`悲伤 变慢` |

## 交付

生成音频后，用 `MEDIA:` 指令交付给用户：

```
MEDIA:output.wav
```

## 📋 版本历史

### v2.5.2 (2026-04-23)
- ✨ 新增4种音色：男声、童声、粤语、四川话
- ✨ 新增音频格式：mp3、ogg
- ✨ 新增重试机制，自动处理API限流
- ✨ 改进错误处理，提供更详细的错误信息
- ✨ 新增风格标签：停顿、叹气、笑声、清嗓子、耳语
- ✨ 新增情感风格：悲伤、愤怒、平静、惊讶
- ✨ 新增命令行参数：--list-voices、--list-formats
- ✨ 新增max-retries参数，可配置重试次数

### v2.5.1
- 🐛 修复了一些已知问题
- 🚀 性能优化

### v2.5.0
- 🎉 初始版本
- ✨ 支持3种基础音色
- ✨ 支持风格控制和音频标签
- ✨ 支持wav格式
