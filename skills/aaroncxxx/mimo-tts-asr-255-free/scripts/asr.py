#!/usr/bin/env python3
"""
Xiaomi MiMo V2.5 ASR — 语音识别 v2.5.4
支持 API 调用和开源模型本地部署

Usage:
  python3 asr.py audio.wav
  python3 asr.py audio.mp3 -o transcript.txt
  python3 asr.py audio.wav --lang zh --format json
  python3 asr.py audio.wav --format srt -o subtitles.srt

API 文档: https://platform.xiaomimimo.com/docs/usage-guide/multimodal-understanding/audio-understanding
开源代码: https://github.com/XiaomiMiMo/MiMo-V2.5-ASR
模型权重: https://huggingface.co/XiaomiMiMo/MiMo-V2.5-ASR
在线体验: https://huggingface.co/spaces/XiaomiMiMo/MiMo-V2.5-ASR
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

API_URL = "https://api.xiaomimimo.com/v1/asr"

LANGUAGES = {
    "auto": "自动检测",
    "zh": "中文",
    "en": "英文",
    "ja": "日语",
    "ko": "韩语",
}

FORMATS = {
    "text": "纯文本",
    "json": "JSON（带时间戳和置信度）",
    "srt": "SRT 字幕格式",
}

AUDIO_EXTS = {".wav", ".mp3", ".ogg", ".m4a", ".flac", ".aac", ".wma"}


def get_api_key(override: str = None) -> str:
    key = override or os.environ.get("MIMO_ASR_KEY", "") or os.environ.get("MIMO_API_KEY", "")
    if not key:
        print("❌ 未配置 API Key", file=sys.stderr)
        print("   设置方法：export MIMO_ASR_KEY='your-key'", file=sys.stderr)
        print("   或：export MIMO_API_KEY='your-key'（复用 TTS Key）", file=sys.stderr)
        print("   获取 Key：https://platform.xiaomimimo.com", file=sys.stderr)
        print(f"\n   💡 也可以使用开源模型本地部署（无需 Key）：", file=sys.stderr)
        print(f"      https://github.com/XiaomiMiMo/MiMo-V2.5-ASR", file=sys.stderr)
        sys.exit(1)
    return key


def read_audio(path: str) -> bytes:
    """读取音频文件"""
    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path}", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(path)[1].lower()
    if ext not in AUDIO_EXTS:
        print(f"⚠️ 不支持的格式 {ext}，尝试继续...", file=sys.stderr)

    with open(path, "rb") as f:
        return f.read()


def transcribe(audio_path: str, lang: str = "auto", api_key: str = "",
               max_retries: int = 3) -> dict:
    """调用 MiMo ASR API 识别语音"""
    key = get_api_key(api_key)
    audio_data = read_audio(audio_path)

    # 用 multipart 上传音频
    boundary = "----MiMoASRBoundary"
    body = bytearray()

    # lang 字段
    body += f"--{boundary}\r\n".encode()
    body += b"Content-Disposition: form-data; name=\"lang\"\r\n\r\n"
    body += f"{lang}\r\n".encode()

    # 音频文件
    filename = os.path.basename(audio_path)
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="audio"; filename="{filename}"\r\n'.encode()
    body += b"Content-Type: application/octet-stream\r\n\r\n"
    body += audio_data
    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "Authorization": f"Bearer {key}",
    }

    print(f"🎧 识别中... (语言: {lang})", file=sys.stderr)

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(API_URL, data=bytes(body), headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=120) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            if e.code == 429 and attempt < max_retries:
                wait = min(2 ** attempt, 10)
                print(f"⏳ 限流，{wait}秒后重试 ({attempt}/{max_retries})", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"❌ API 错误 {e.code}: {err_body}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            if attempt < max_retries:
                print(f"⏳ 网络错误，重试 ({attempt}/{max_retries})", file=sys.stderr)
                time.sleep(2)
                continue
            print(f"❌ 网络错误: {e.reason}", file=sys.stderr)
            sys.exit(1)

    print("❌ 超过最大重试次数", file=sys.stderr)
    sys.exit(1)


def format_srt(result: dict) -> str:
    """将结果转为 SRT 字幕格式"""
    segments = result.get("segments", [])
    lines = []
    for i, seg in enumerate(segments, 1):
        start = format_srt_time(seg.get("start", 0))
        end = format_srt_time(seg.get("end", 0))
        text = seg.get("text", "")
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def format_srt_time(seconds: float) -> str:
    """秒数转 SRT 时间格式 HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_json(result: dict) -> str:
    """格式化 JSON 输出"""
    return json.dumps(result, ensure_ascii=False, indent=2)


def format_text(result: dict) -> str:
    """提取纯文本"""
    return result.get("text", "")


def list_languages():
    print("🌐 支持的语言：")
    print(f"{'参数':<10} {'说明'}")
    print("─" * 25)
    for param, desc in LANGUAGES.items():
        print(f"{param:<10} {desc}")
    print(f"\n📖 更多方言支持见开源模型：https://github.com/XiaomiMiMo/MiMo-V2.5-ASR")


def list_output_formats():
    print("📄 输出格式：")
    print(f"{'参数':<10} {'说明'}")
    print("─" * 35)
    for param, desc in FORMATS.items():
        print(f"{param:<10} {desc}")


def print_resources():
    """打印相关资源链接"""
    print("📚 MiMo-V2.5-ASR 资源：")
    print("  📖 API 文档: https://platform.xiaomimimo.com/docs/usage-guide/multimodal-understanding/audio-understanding")
    print("  🔧 开源代码: https://github.com/XiaomiMiMo/MiMo-V2.5-ASR")
    print("  🤗 模型权重: https://huggingface.co/XiaomiMiMo/MiMo-V2.5-ASR")
    print("  🎮 在线体验: https://huggingface.co/spaces/XiaomiMiMo/MiMo-V2.5-ASR")


def main():
    parser = argparse.ArgumentParser(
        description="Xiaomi MiMo V2.5 ASR 语音识别\n"
                    "文档: https://platform.xiaomimimo.com/docs/usage-guide/multimodal-understanding/audio-understanding\n"
                    "开源: https://github.com/XiaomiMiMo/MiMo-V2.5-ASR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("audio", nargs="?", help="音频文件路径")
    parser.add_argument("-o", "--output", default="", help="输出文件路径（默认打印到终端）")
    parser.add_argument("--lang", default="auto",
                        choices=list(LANGUAGES.keys()), help="语言")
    parser.add_argument("--format", default="text",
                        choices=list(FORMATS.keys()), help="输出格式")
    parser.add_argument("--api-key", default="", help="API Key 覆盖")
    parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数")
    parser.add_argument("--list-languages", action="store_true", help="列出支持的语言")
    parser.add_argument("--list-formats", action="store_true", help="列出输出格式")
    parser.add_argument("--resources", action="store_true", help="打印相关资源链接")

    args = parser.parse_args()

    if args.list_languages:
        list_languages()
        return
    if args.list_formats:
        list_output_formats()
        return
    if args.resources:
        print_resources()
        return

    if not args.audio:
        parser.error("请提供音频文件路径")

    result = transcribe(
        audio_path=args.audio,
        lang=args.lang,
        api_key=args.api_key,
        max_retries=args.max_retries,
    )

    # 格式化输出
    if args.format == "json":
        output = format_json(result)
    elif args.format == "srt":
        output = format_srt(result)
    else:
        output = format_text(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"✅ 已保存: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
