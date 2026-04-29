#!/usr/bin/env python3
"""MiMo TTS 2.5 — 小米大模型语音合成"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error

API_BASE = "https://api.xiaomimimo.com/v1"
MODEL = "mimo-v2-tts"

VOICES = ["mimo_default", "default_zh", "default_en", "mimo_male", "mimo_child", "mimo_cantonese", "mimo_sichuan"]


def synthesize(text: str, voice: str, api_key: str, style: str | None = None,
               user_msg: str | None = None, fmt: str = "wav", max_retries: int = 3) -> bytes:
    """Call MiMo TTS API and return raw audio bytes."""
    assistant_content = text
    if style:
        assistant_content = f"<style>{style}</style>{text}"

    messages = []
    if user_msg:
        messages.append({"role": "user", "content": user_msg})
    messages.append({"role": "assistant", "content": assistant_content})

    payload = json.dumps({
        "model": MODEL,
        "messages": messages,
        "audio": {"format": fmt, "voice": voice},
    }).encode()

    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "api-key": api_key,
        },
        method="POST",
    )

    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read())
            break
        except urllib.error.HTTPError as e:
            err_body = e.read().decode(errors="replace")
            if e.code == 429 and attempt < max_retries - 1:  # Rate limit
                wait_time = 2 ** attempt
                print(f"Rate limited, retrying in {wait_time}s...", file=sys.stderr)
                time.sleep(wait_time)
                continue
            print(f"API error {e.code}: {err_body}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error: {e}, retrying...", file=sys.stderr)
                time.sleep(1)
                continue
            print(f"Failed after {max_retries} attempts: {e}", file=sys.stderr)
            sys.exit(1)

    audio_b64 = body["choices"][0]["message"]["audio"]["data"]
    return base64.b64decode(audio_b64)


def main():
    parser = argparse.ArgumentParser(description="MiMo TTS 2.5 语音合成")
    parser.add_argument("text", nargs="?", help="要合成的文本")
    parser.add_argument("-o", "--output", default="output.wav",
                        help="输出文件路径 (default: output.wav)")
    parser.add_argument("-v", "--voice", default="mimo_default", choices=VOICES,
                        help="音色预设 (default: mimo_default)")
    parser.add_argument("-s", "--style", default=None,
                        help="风格标签, e.g. '开心', '东北话', '悄悄话'")
    parser.add_argument("-f", "--format", default="wav", choices=["wav", "mp3", "ogg"],
                        help="音频格式 (default: wav)")
    parser.add_argument("--user-msg", default=None,
                        help="可选的用户角色上下文消息")
    parser.add_argument("--api-key", default=None,
                        help="API Key (或设置 MIMO_API_KEY 环境变量)")
    parser.add_argument("--list-voices", action="store_true",
                        help="列出所有可用音色")
    parser.add_argument("--list-formats", action="store_true",
                        help="列出所有可用音频格式")
    args = parser.parse_args()

    if args.list_voices:
        print("可用音色:")
        for voice in VOICES:
            print(f"  - {voice}")
        sys.exit(0)

    if args.list_formats:
        print("可用音频格式:")
        for fmt in ["wav", "mp3", "ogg"]:
            print(f"  - {fmt}")
        sys.exit(0)

    if not args.text:
        parser.error("请提供要合成的文本")

    api_key = args.api_key or os.environ.get("MIMO_API_KEY")
    if not api_key:
        print("Error: 请提供 --api-key 或设置 MIMO_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    audio = synthesize(
        text=args.text,
        voice=args.voice,
        api_key=api_key,
        style=args.style,
        user_msg=args.user_msg,
        fmt=args.format,
    )

    with open(args.output, "wb") as f:
        f.write(audio)

    print(f"已保存 {len(audio)} 字节 → {args.output}")


if __name__ == "__main__":
    main()
