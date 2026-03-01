---
name: Doubao ASR / 豆包语音转写
description: "Transcribe audio via Doubao Seed-ASR 2.0 (豆包录音文件识别模型2.0) API from ByteDance/Volcengine. Best-in-class Chinese speech recognition. 调用字节跳动火山引擎「豆包录音文件识别模型2.0」转写音频，中文识别效果业界领先。Use when the user needs high-quality Chinese transcription, or asks for Doubao/豆包/Volcengine/火山引擎 transcription."
homepage: https://www.volcengine.com/docs/6561/1354868
metadata:
  {
    "openclaw":
      {
        "emoji": "🫘",
        "requires": { "bins": ["python3"], "env": ["VOLCENGINE_API_KEY", "VOLCENGINE_ACCESS_KEY_ID", "VOLCENGINE_SECRET_ACCESS_KEY", "VOLCENGINE_TOS_BUCKET"], "pip": ["requests"] },
        "primaryEnv": "VOLCENGINE_API_KEY",
        "envHelp":
          {
            "VOLCENGINE_API_KEY":
              {
                "required": true,
                "description": "豆包 ASR API Key (UUID format). 从火山引擎语音控制台获取 / Get from Volcengine Speech console",
                "howToGet": "1. 打开 https://console.volcengine.com/speech/new/（确认进入的是新版「豆包语音」控制台）\n2. 左侧菜单 →「语音识别」\n3. 点击「开通模型」，开通「录音文件识别2.0」\n4. 点击页面右上角「API 调用」\n5. 在 Step 1「获取 API Key」中，点击创建 API Key\n6. 复制生成的 UUID 格式 Key（如 57e620a4-179c-4b3d-bd8d-990bd1f9a1e2）\n\n1. Open https://console.volcengine.com/speech/new/ (make sure you are in the new 'Doubao Speech' console)\n2. Left sidebar → 'Speech Recognition'\n3. Click 'Activate Model', activate 'Audio File Recognition 2.0'\n4. Click 'API Call' button at the top-right of the page\n5. In Step 1 'Get API Key', click to create an API Key\n6. Copy the generated UUID-format key (e.g. 57e620a4-179c-4b3d-bd8d-990bd1f9a1e2)",
                "url": "https://console.volcengine.com/speech/new/",
              },
            "VOLCENGINE_ACCESS_KEY_ID":
              {
                "required": true,
                "description": "IAM Access Key ID (starts with AKLT). 通过 IAM 子用户创建 / Create via IAM sub-user",
                "howToGet": "1. 打开 https://console.volcengine.com/iam/usermanage\n2. 点「新建用户」，填写用户名（如 doubao-asr）\n3. 访问方式确保勾选「编程访问」和「允许用户管理自己的API密钥」，其他选项保持默认即可\n4. 点击确定，创建成功后页面会显示 Access Key ID（以 AKLT 开头）和 Secret Access Key，复制保存\n   这一步不需要添加任何 IAM 权限策略，权限将在 Step 3 通过 TOS 桶策略授予（仅限单桶读写）\n   提示：如需再次查看密钥，进入用户列表 → 点击子用户名 → 切换到「密钥」tab\n\n1. Open https://console.volcengine.com/iam/usermanage\n2. Click 'Create User', enter username (e.g. doubao-asr)\n3. Make sure 'Programmatic Access' and 'Allow user to manage own API keys' are checked. Leave all other options as default\n4. Click confirm. The success page shows Access Key ID (starts with AKLT) and Secret Access Key — copy both\n   No IAM permission policies needed here — access will be granted via TOS bucket policy in Step 3 (single-bucket read/write only)\n   Tip: To view keys again, go to user list → click sub-user name → switch to 'Keys' tab",
                "url": "https://console.volcengine.com/iam/usermanage",
              },
            "VOLCENGINE_SECRET_ACCESS_KEY":
              {
                "required": true,
                "description": "IAM Secret Access Key. 与 Access Key ID 配对 / Paired with Access Key ID",
                "howToGet": "在创建 Access Key ID 时一起生成（见上一步），创建后可在控制台随时查看。\n\nGenerated together with Access Key ID (see previous step). Can be viewed anytime in the console.",
              },
            "VOLCENGINE_TOS_BUCKET":
              {
                "required": true,
                "description": "TOS 存储桶名称 / TOS bucket name for audio upload",
                "howToGet": "1. 打开 https://console.volcengine.com/tos\n2. 首次进入会看到「开通对象存储」引导页，点击确认开通\n3. 开通后如果页面没有自动跳转到管理控制台，请手动重新访问 https://console.volcengine.com/tos 进入\n4. 在左侧菜单栏找到「桶列表」。如果看不到已创建的桶，检查页面顶部的项目选择器，切换到创建桶时所用的项目\n5. 点击「创建桶」，输入桶名称，根据服务器位置选择区域：\n   - 中国内地服务器 → cn-beijing\n   - 海外服务器（美国/欧洲/东南亚）→ cn-hongkong（必须！否则上传约 15KB/s）\n6. 创建完成后，点击桶名称进入桶控制面板\n7. 左侧导航栏 →「权限管理」→「存储桶授权策略管理」→「创建策略」\n8. 选择「文件夹读写」模板 → 下一步 → 授权用户选择「当前主账号」→ 资源范围选择「所有对象」→ 确定\n9. 回到桶列表，复制桶名称\n\n1. Open https://console.volcengine.com/tos\n2. First-time users will see an 'Activate Object Storage' page — click to activate\n3. If the page does not auto-redirect to the management console after activation, manually re-visit https://console.volcengine.com/tos\n4. In the left sidebar, find 'Bucket List'. If you don't see your bucket, check the project selector at the top of the page and switch to the project used when creating the bucket\n5. Click 'Create Bucket', enter a bucket name and choose region based on server location:\n   - China mainland server → cn-beijing\n   - Overseas server (US/EU/SEA) → cn-hongkong (REQUIRED, otherwise ~15KB/s)\n6. After creation, click the bucket name to enter bucket dashboard\n7. Left sidebar → 'Permission Management' → 'Bucket Authorization Policy' → 'Create Policy'\n8. Select 'Folder Read/Write' template → Next → Authorized user: 'Current main account' → Resource scope: 'All objects' → Confirm\n9. Go back to bucket list, copy the bucket name",
                "url": "https://console.volcengine.com/tos",
              },
            "VOLCENGINE_TOS_REGION":
              {
                "required": false,
                "description": "TOS 区域代码（默认 cn-beijing）。海外服务器必须设为 cn-hongkong / TOS region code. Overseas servers MUST use cn-hongkong",
                "howToGet": "填写你在创建 TOS 存储桶时选择的区域代码。\n如果服务器在中国大陆以外，必须设为 cn-hongkong。\n海外服务器切勿使用 cn-beijing/cn-shanghai，否则上传极慢（约 15KB/s）。\n\nEnter the region code you selected when creating the TOS bucket.\nIf your server is outside China mainland, MUST use cn-hongkong.\nDo NOT use cn-beijing/cn-shanghai for overseas servers — upload ~15KB/s.",
              },
          },
      },
  }
---

# Doubao ASR / 豆包语音转写

Transcribe audio files via ByteDance Volcengine's **Seed-ASR 2.0 Standard** (豆包录音文件识别模型2.0-标准版) API. Best-in-class accuracy for Chinese (Mandarin, Cantonese, Sichuan dialect, etc.) and supports 13+ languages.

调用字节跳动火山引擎**豆包录音文件识别模型2.0-标准版**（Seed-ASR 2.0 Standard）转写音频文件。中文识别（普通话、粤语、四川话等方言）准确率业界领先，支持 13+ 种语言。

## Sending audio to OpenClaw

Currently, audio files can be sent to OpenClaw via **Discord** or **WhatsApp**. Send the audio file in a chat message and ask the bot to transcribe it.

目前可通过 **Discord** 或 **WhatsApp** 向 OpenClaw 发送音频文件，发送后让 bot 转写即可。

> **Note**: Direct voice recording in the OpenClaw web UI is not yet supported. Use a messaging app to send pre-recorded audio files.
>
> **提示**：OpenClaw 网页端暂不支持直接录音，请通过即时通讯应用发送预录制的音频文件。

## Quick start

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a
```

Defaults:

- Model: Seed-ASR 2.0 Standard / 豆包录音文件识别模型2.0-标准版
- Speaker diarization: enabled / 说话人分离：默认开启
- Output: stdout (transcript text with speaker labels / 带说话人标签的转写文本)

## Useful flags

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --out /tmp/transcript.txt
python3 {baseDir}/scripts/transcribe.py /path/to/audio.mp3 --format mp3
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --json --out /tmp/result.json
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --no-speakers  # disable speaker diarization / 关闭说话人分离
python3 {baseDir}/scripts/transcribe.py https://example.com/audio.mp3  # direct URL (skip upload)
```

## How it works

The Doubao API accepts audio via URL (not direct file upload). The script:

1. **Uploads audio to Volcengine TOS** (object storage) via presigned URL — audio stays within Volcengine infrastructure, no third-party services involved
2. Submits transcription task to Seed-ASR 2.0
3. Polls until complete (typically 1-3 minutes for a 10-min audio)
4. Returns transcript text

> **Privacy**: By default, audio is uploaded to your own Volcengine TOS bucket via presigned URL. No data is sent to third-party services.

You can also pass a direct audio URL as the argument to skip upload entirely:

```bash
python3 {baseDir}/scripts/transcribe.py https://your-bucket.tos.volces.com/audio.m4a
```

## Dependencies

- Python 3.9+
- `requests`: `pip install requests`

## Credentials

### Step 1: Doubao ASR API Key / 第一步：豆包 ASR API Key

1. 打开 https://console.volcengine.com/speech/new/（确认进入的是新版「豆包语音」控制台）
2. 左侧菜单 →「语音识别」
3. 点击「开通模型」，开通「录音文件识别2.0」
4. 点击页面右上角「API 调用」
5. 在 Step 1「获取 API Key」中，点击创建 API Key
6. 复制生成的 UUID 格式 Key

```bash
export VOLCENGINE_API_KEY="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### Step 2: IAM Access Key / 第二步：创建 IAM 子用户和访问密钥

1. 打开 https://console.volcengine.com/iam/usermanage
2. 点「新建用户」，填写用户名（如 `doubao-asr`）
3. 访问方式确保勾选「编程访问」和「允许用户管理自己的API密钥」，其他选项保持默认即可
4. 点击确定，创建成功后页面会显示 Access Key ID（以 `AKLT` 开头）和 Secret Access Key，复制保存

> **提示**：这一步不需要添加任何 IAM 权限策略。权限将在 Step 3 通过 TOS 桶策略授予（仅限单桶读写）。
> 如需再次查看密钥，进入用户列表 → 点击子用户名 → 切换到「密钥」tab。

```bash
export VOLCENGINE_ACCESS_KEY_ID="AKLTxxxx..."
export VOLCENGINE_SECRET_ACCESS_KEY="xxxx..."
```

### Step 3: TOS Bucket / 第三步：开通并创建 TOS 存储桶

豆包 API 要求音频通过 URL 访问。TOS 对象存储提供安全的临时上传，数据留在火山引擎内部。

1. 打开 https://console.volcengine.com/tos
2. 首次进入会看到「开通对象存储」引导页，点击确认开通
3. 开通后如果页面没有自动跳转到管理控制台，请手动重新访问 https://console.volcengine.com/tos 进入
4. 在左侧菜单栏找到「桶列表」。如果看不到已创建的桶，检查页面顶部的项目选择器，切换到创建桶时所用的项目
5. 点击「创建桶」，输入桶名称，**根据服务器位置选择区域**（见下方表格）
6. 创建完成后，点击桶名称进入桶控制面板
7. 左侧导航栏 →「权限管理」→「存储桶授权策略管理」→「创建策略」
8. 选择「文件夹读写」模板 → 下一步 → 授权用户选择「当前主账号」→ 资源范围选择「所有对象」→ 确定
9. 回到桶列表，复制桶名称

**Region selection / 区域选择：**

| Server location / 服务器位置 | Recommended TOS region / 推荐 TOS 区域 | Region code |
|---|---|---|
| China mainland / 中国内地 | cn-beijing, cn-shanghai, cn-guangzhou | `cn-beijing` |
| Hong Kong / 香港 | cn-hongkong | `cn-hongkong` |
| Southeast Asia / 东南亚 | ap-southeast-1 (Singapore) | `ap-southeast-1` |
| US, Europe, other overseas / 美国、欧洲等海外 | **cn-hongkong** (recommended) | `cn-hongkong` |

> **Important**: If your server is **outside China mainland**, do NOT use `cn-beijing` / `cn-shanghai` — cross-border upload will be extremely slow (~15KB/s). Use `cn-hongkong` instead.
>
> **重要**：如果你的服务器在**中国大陆以外**，不要用 `cn-beijing` / `cn-shanghai`——跨境上传会非常慢（约 15KB/s）。请使用 `cn-hongkong`。

```bash
export VOLCENGINE_TOS_BUCKET="your_bucket_name"
export VOLCENGINE_TOS_REGION="cn-hongkong"  # see region table above / 见上方区域表
```

### Summary of all environment variables / 环境变量汇总

| Variable | Required | Description |
|---|---|---|
| `VOLCENGINE_API_KEY` | Yes | ASR API key (UUID format) from Speech console / 语音控制台的 API Key |
| `VOLCENGINE_ACCESS_KEY_ID` | Yes | IAM Access Key ID (starts with `AKLT`) / IAM 访问密钥 ID |
| `VOLCENGINE_SECRET_ACCESS_KEY` | Yes | IAM Secret Access Key / IAM 访问密钥 |
| `VOLCENGINE_TOS_BUCKET` | Yes | TOS bucket name / TOS 存储桶名称 |
| `VOLCENGINE_TOS_REGION` | No | TOS region (default: `cn-beijing`). Overseas servers MUST use `cn-hongkong` / 海外服务器必须用 `cn-hongkong` |

## Supported formats

WAV, MP3, MP4, M4A, OGG, FLAC — up to 5 hours, 512MB max.

支持格式：WAV、MP3、MP4、M4A、OGG、FLAC——最长 5 小时，最大 512MB。
