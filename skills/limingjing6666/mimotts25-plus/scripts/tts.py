#!/usr/bin/env python3
"""MiMo TTS 2.5 Plus — 统一入口 (兼容官方 + 增强模式)

三种使用方式：
1. （官方兼容）直接调三个独立脚本：mimo_tts.py / mimo_tts_voicedesign.py / mimo_tts_voiceclone.py
2. （增强模式）本脚本统一入口：python3 tts.py "你好" -v 冰糖
3. （增强模式）声音设计/克隆快捷参数：--design / --clone

增强特性：
- 默认模型 mimo-v2.5-tts
- 默认音色 冰糖，默认格式 mp3
- 支持 token-plan-cn 集群（国内可用）
- 兼容官方的 --list-voices / --list-models
- 兼容官方的 MIMO_API_KEY 和 OPENAI_API_KEY
- 新增 MIMO_API_BASE 环境变量切换 API 端点
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API_BASE = os.getenv("MIMO_API_BASE", "https://token-plan-cn.xiaomimimo.com/v1")

V25_VOICES = ["mimo_default", "冰糖", "茉莉", "苏打", "白桦", "Mia", "Chloe", "Milo", "Dean"]
V2_VOICES = ["mimo_default", "default_zh", "default_en", "mimo_male", "mimo_child", "mimo_cantonese", "mimo_sichuan"]

AVAILABLE_MODELS = {
    "mimo-v2.5-tts": V25_VOICES,
    "mimo-v2-tts": V2_VOICES,
    "mimo-v2.5-tts-voiceclone": V25_VOICES,
    "mimo-v2.5-tts-voicedesign": ["使用声音设计不需要指定音色"],
}

DEFAULT_MODEL = "mimo-v2.5-tts"
DEFAULT_VOICE = "冰糖"


class TtsError(Exception):
    pass


def _extract_style(text: str, style: str | None) -> tuple[str, str | None]:
    text_clean = text
    extracted_style = style
    style_match = re.match(r'^<style>(.+?)</style>\s*', text)
    if style_match:
        extracted_style = style_match.group(1)
        text_clean = text[style_match.end():]
    return text_clean, extracted_style


def _get_api_key() -> str:
    api_key = os.getenv("MIMO_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise TtsError("请提供 --api-key 或设置 MIMO_API_KEY / OPENAI_API_KEY 环境变量")
    return api_key


def _call_api(payload: dict, api_key: str, max_retries: int = 3) -> bytes:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{API_BASE}/chat/completions",
        data=data,
        headers={"Content-Type": "application/json", "api-key": api_key},
        method="POST",
    )
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = json.loads(resp.read())
            break
        except urllib.error.HTTPError as exc:
            err_body = exc.read().decode(errors="replace")
            if exc.code == 429 and attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"Rate limited, retrying in {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            raise TtsError(f"API error {exc.code}: {err_body}") from exc
        except Exception as exc:
            if attempt < max_retries - 1:
                print(f"Error: {exc}, retrying...", file=sys.stderr)
                time.sleep(1)
                continue
            raise TtsError(f"Failed after {max_retries} attempts: {exc}") from exc

    audio_b64 = body.get("choices", [{}])[0].get("message", {}).get("audio", {}).get("data")
    if not audio_b64:
        raise TtsError("No audio data returned")
    return base64.b64decode(audio_b64)


def synthesize(text: str, voice: str, api_key: str, model: str = DEFAULT_MODEL,
               style: str | None = None, user_msg: str | None = None,
               fmt: str = "mp3", max_retries: int = 3,
               is_voicedesign: bool = False) -> bytes:
    text_clean, extracted_style = _extract_style(text, style)
    if extracted_style:
        assistant_content = f"（{extracted_style}）{text_clean}"
    else:
        assistant_content = text_clean

    audio_params = {"format": fmt}
    if not is_voicedesign:
        audio_params["voice"] = voice

    messages = []
    if user_msg:
        messages.append({"role": "user", "content": user_msg})
    messages.append({"role": "assistant", "content": assistant_content})

    payload = {"model": model, "messages": messages, "audio": audio_params}
    return _call_api(payload, api_key, max_retries)


def _read_clone_audio(path: str) -> tuple[str, str]:
    if not os.path.exists(path):
        raise TtsError(f"音频文件不存在: {path}")
    with open(path, "rb") as f:
        voice_bytes = f.read()
    voice_b64 = base64.b64encode(voice_bytes).decode("utf-8")
    mime = "audio/mpeg" if path.endswith(".mp3") else "audio/wav"
    return f"data:{mime};base64,{voice_b64}", mime


def _print_voices():
    print("可用音色:")
    for model_name, voices in AVAILABLE_MODELS.items():
        print(f"\n[{model_name}]")
        for voice in voices:
            print(f"  - {voice}")


def main() -> int:
    parser = argparse.ArgumentParser(description="MiMo TTS 2.5 Plus 语音合成")
    parser.add_argument("text", nargs="?", help="要合成的文本")
    parser.add_argument("-o", "--output", default="output.mp3", help="输出文件路径")
    parser.add_argument("-m", "--model", default=DEFAULT_MODEL,
                        choices=list(AVAILABLE_MODELS.keys()),
                        help=f"模型 (default: {DEFAULT_MODEL})")
    parser.add_argument("-v", "--voice", default=DEFAULT_VOICE,
                        help=f"音色预设 (default: {DEFAULT_VOICE})")
    parser.add_argument("-s", "--style", default=None,
                        help="风格标签, e.g. '开心', '东北话', '悄悄话'")
    parser.add_argument("-f", "--format", default="mp3", choices=["wav", "mp3", "ogg"],
                        help="音频格式")
    parser.add_argument("--design", default=None, metavar="音色描述",
                        help="声音设计模式：用文字描述音色")
    parser.add_argument("--clone", default=None, metavar="音频文件路径",
                        help="声音克隆模式：用音频样本复刻音色")
    parser.add_argument("--user-msg", default=None,
                        help="自然语言风格指令 / 导演模式")
    parser.add_argument("--api-key", default=None, help="API Key 覆盖")
    parser.add_argument("--list-voices", action="store_true", help="列出所有可用音色")
    parser.add_argument("--list-models", action="store_true", help="列出所有可用模型")
    parser.add_argument("--list-formats", action="store_true", help="列出所有可用音频格式")
    parser.add_argument("--max-retries", type=int, default=3, help="API调用最大重试次数")
    args = parser.parse_args()

    if args.list_voices:
        _print_voices()
        return 0
    if args.list_models:
        print("可用模型:")
        for m in AVAILABLE_MODELS:
            print(f"  - {m}")
        return 0
    if args.list_formats:
        print("可用音频格式:")
        for f in ["wav", "mp3", "ogg"]:
            print(f"  - {f}")
        return 0
    if not args.text:
        parser.print_help()
        return 1

    if args.design:
        model = "mimo-v2.5-tts-voicedesign"
        user_msg = args.design
        is_voicedesign = True
    elif args.clone:
        model = "mimo-v2.5-tts-voiceclone"
        voice_uri, _ = _read_clone_audio(args.clone)
        args.voice = voice_uri
        user_msg = args.user_msg or ""
        is_voicedesign = False
    else:
        model = args.model
        user_msg = args.user_msg
        is_voicedesign = False

    try:
        api_key = args.api_key or _get_api_key()
    except TtsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    try:
        audio = synthesize(
            text=args.text, voice=args.voice, model=model,
            api_key=api_key, style=args.style, user_msg=user_msg,
            fmt=args.format, max_retries=args.max_retries,
            is_voicedesign=is_voicedesign,
        )
    except TtsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    with open(args.output, "wb") as f:
        f.write(audio)
    print(f"已保存 {len(audio)} 字节 → {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
