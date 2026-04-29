# MiMo TTS 2.5 官方 API 文档参考

来源：小米 MiMo 开放平台官方文档 (2026-04)

## API 地址

- 官方: `https://api.xiaomimimo.com/v1`
- 中国集群（当前使用）: `https://token-plan-cn.xiaomimimo.com/v1`

## 鉴权

```bash
header "api-key: $MIMO_API_KEY"
# 或 Authorization: Bearer (部分集群兼容)
```

## 模型列表

| 模型 ID | 功能 |
|---------|------|
| `mimo-v2.5-tts` | 预置音色合成（当前默认） |
| `mimo-v2.5-tts-voicedesign` | 文本描述定制音色 |
| `mimo-v2.5-tts-voiceclone` | 音频样本复刻音色 |

## 非流式调用 (wav/mp3/ogg)

```python
from openai import OpenAI
import base64

client = OpenAI(
    api_key=os.environ.get("MIMO_API_KEY"),
    base_url="https://api.xiaomimimo.com/v1"
)

completion = client.chat.completions.create(
    model="mimo-v2.5-tts",
    messages=[
        {"role": "user", "content": "风格指令"},
        {"role": "assistant", "content": "要合成的文本"}
    ],
    audio={"format": "wav", "voice": "冰糖"}
)

audio_bytes = base64.b64decode(completion.choices[0].message.audio.data)
```

## 流式调用 (pcm16)

```python
import numpy as np
import soundfile as sf

client = OpenAI(...)
completion = client.chat.completions.create(
    ...,
    audio={"format": "pcm16", "voice": "冰糖"},
    stream=True
)

collected_chunks = np.array([], dtype=np.float32)
for chunk in completion:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    audio = getattr(delta, "audio", None)
    if audio is not None:
        pcm_bytes = base64.b64decode(audio["data"])
        np_pcm = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        collected_chunks = np.concatenate((collected_chunks, np_pcm))

sf.write("output.wav", collected_chunks, samplerate=24000)
```

## 预置音色列表 (v2.5-tts)

| 音色名 | Voice ID | 语言 | 性别 |
|--------|----------|------|------|
| MiMo-默认 | mimo_default | 因集群而异 | 中国集群=冰糖 |
| 冰糖 | 冰糖 | 中文 | 女性 |
| 茉莉 | 茉莉 | 中文 | 女性 |
| 苏打 | 苏打 | 中文 | 男性 |
| 白桦 | 白桦 | 中文 | 男性 |
| Mia | Mia | 英文 | 女性 |
| Chloe | Chloe | 英文 | 女性 |
| Milo | Milo | 英文 | 男性 |
| Dean | Dean | 英文 | 男性 |

## 风格控制

### 1. 自然语言控制（在 user message 中）
```
"用轻快上扬的语调，语速稍快，带着开心和期待"
```

### 2. 导演模式（在 user message 中）
```
【角色】写清人物的身份、性格底色
【场景】交代此刻发生了什么
【指导】语速、气息、停顿、重音等
```

### 3. 音频标签控制（在 assistant content 中）
```
<style>开心 变快</style>文本内容
```
支持格式: `()` `（）` `[]`

### 4. 细粒度音频标签
```
（紧张，深呼吸）呼……（语速加快）完蛋了！（笑）算了
```
支持: 吸气/叹气/紧张/撒娇/颤抖/轻笑/哽咽/沉默片刻/耳语 等

### 5. 唱歌
```
(唱歌)原谅我这一生不羁放纵爱自由
```

## 声音设计 (voicedesign)

使用 `mimo-v2.5-tts-voicedesign` 模型，在 user message 中描述音色：

```
"young woman in her mid-20s, warm and confident, casual and colloquial"
```

关键维度：性别年龄、音色质感、情绪语气、语速节奏、角色人设、说话风格
长度建议：1-4 句
支持中英文

## 注意事项

- 合成文本必须放在 assistant 消息中，不可放在 user
- user 消息可选，用于调整风格（voicedesign 模型为必填）
- 流式调用格式必须为 pcm16
- 不支持同时要求矛盾的特征

## 声音克隆 (voiceclone)

使用 `mimo-v2.5-tts-voiceclone` 模型，通过音频样本复刻任意音色。

### 调用方式

将音频文件转换为 Base64 编码字符串，在 `audio.voice` 字段传入：

```
data:{MIME_TYPE};base64,$BASE64_AUDIO
```

- MIME_TYPE: `audio/mpeg` (mp3) 或 `audio/wav`
- Base64 大小不超过 10MB

### Python 示例

```python
import base64
from openai import OpenAI

client = OpenAI(
    api_key=os.environ.get("MIMO_API_KEY"),
    base_url="https://api.xiaomimimo.com/v1",
)

with open("voice.mp3", "rb") as f:
    voice_bytes = f.read()
voice_base64 = base64.b64encode(voice_bytes).decode("utf-8")

completion = client.chat.completions.create(
    model="mimo-v2.5-tts-voiceclone",
    messages=[
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "要合成的文本"}
    ],
    audio={
        "format": "wav",
        "voice": f"data:audio/mpeg;base64,{voice_base64}"
    }
)
```

### 流式调用 (pcm16)

```python
import numpy as np
import soundfile as sf

completion = client.chat.completions.create(
    ...,
    audio={"format": "pcm16", "voice": "data:audio/mpeg;base64,..."},
    stream=True
)

collected_chunks: np.ndarray = np.array([], dtype=np.float32)
for chunk in completion:
    if not chunk.choices:
        continue
    delta = chunk.choices[0].delta
    audio = getattr(delta, "audio", None)
    if audio is not None:
        pcm_bytes = base64.b64decode(audio["data"])
        np_pcm = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        collected_chunks = np.concatenate((collected_chunks, np_pcm))

sf.write("output.wav", collected_chunks, samplerate=24000)
```

### 注意事项

- Base64 前缀必须包含 `data:{MIME_TYPE};base64,` 格式
- 流式调用只支持 pcm16 格式
- 当前流式为兼容模式（仅推理完成后一次性返回）
