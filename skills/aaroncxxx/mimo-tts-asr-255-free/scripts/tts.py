#!/usr/bin/env python3
"""
Xiaomi MiMo V2.5 TTS — 语音合成 v2.5.9
支持三款模型：MiMo-V2.5-TTS / VoiceDesign / VoiceClone
支持推理性能优化：GPU 半精度 / CPU ONNX 量化 / 轻量模式

Usage:
  python3 tts.py "要合成的文本" [-o output.wav] [-v voice] [-s style] [-f format]
  python3 tts.py "文本" -m voice-design --voice-desc "描述" -o output.wav
  python3 tts.py "文本" -m voice-clone --ref-audio ref.wav -o output.wav
  python3 tts.py "文本" --optimize gpu -o output.wav
  python3 tts.py "文本" --optimize cpu -o output.wav
  python3 tts.py --list-voices
  python3 tts.py --list-formats

官方文档: https://platform.xiaomimimo.com/docs/usage-guide/speech-synthesis-v2.5
MiMo Studio: https://aistudio.xiaomimimo.com/#/c
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

API_URL = "https://api.xiaomimimo.com/v1/tts"

MODELS = {
    "tts": "MiMo-V2.5-TTS（精品音色）",
    "voice-design": "MiMo-V2.5-TTS-VoiceDesign（音色设计）",
    "voice-clone": "MiMo-V2.5-TTS-VoiceClone（音色克隆）",
}

VOICES = {
    "mimo_default": "MiMo-默认（通用女声）",
    "default_zh": "MiMo-中文女声",
    "default_en": "MiMo-英文女声",
    "mimo_male": "MiMo-男声",
    "mimo_child": "MiMo-童声",
    "mimo_cantonese": "MiMo-粤语",
    "mimo_sichuan": "MiMo-四川话",
}

FORMATS = {
    "wav": "WAV（无损，体积大）",
    "mp3": "MP3（压缩，体积小）",
    "ogg": "OGG（开源格式）",
}

STYLES = [
    "可爱", "开心", "东北话", "悄悄话", "孙悟空", "唱歌",
    "变快", "变慢", "悲伤", "愤怒", "平静", "惊讶",
]

OPTIMIZATIONS = {
    "gpu": "GPU 半精度 + CUDA 流异步 + 关闭梯度",
    "cpu": "CPU ONNX INT8 量化 + 线程绑定",
    "lite": "轻量模式（关闭情感/风格分支）",
}


def apply_optimization(optimization: str) -> dict:
    """返回优化配置参数"""
    if optimization == "gpu":
        return {
            "torch_dtype": "float16",
            "device_map": "auto",
            "cuda_stream": True,
            "no_grad": True,
        }
    elif optimization == "cpu":
        return {
            "onnx_quant": True,
            "omp_threads": 4,
            "mkl_threads": 4,
            "kmp_affinity": "granularity=fine,compact,1,0",
        }
    elif optimization == "lite":
        return {
            "emotion_prediction": False,
            "style_branch": False,
            "num_inference_steps": 20,
            "denoising_strength": 0.5,
        }
    return {}


def get_api_key(override: str = None) -> str:
    key = override or os.environ.get("MIMO_API_KEY", "")
    if not key:
        print("❌ 未配置 API Key", file=sys.stderr)
        print("   设置方法：export MIMO_API_KEY='your-key'", file=sys.stderr)
        print("   或：openclaw config set skills.entries.mimo-tts-asr.apiKey 'your-key'", file=sys.stderr)
        print("   获取 Key：https://platform.xiaomimimo.com", file=sys.stderr)
        sys.exit(1)
    return key


def read_binary(path: str) -> bytes:
    """读取二进制文件"""
    if not os.path.exists(path):
        print(f"❌ 文件不存在: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "rb") as f:
        return f.read()


def synthesize(text: str, model: str = "tts", voice: str = "mimo_default",
               style: str = "", audio_format: str = "wav", api_key: str = "",
               voice_desc: str = "", ref_audio: str = "",
               user_msg: str = "", max_retries: int = 3,
               optimize: dict = None) -> bytes:
    """调用 MiMo TTS API 合成语音"""
    key = get_api_key(api_key)

    # 构建带风格标签的文本
    if style and model == "tts":
        text = f"[{style}]{text}"

    payload = {
        "text": text,
        "model": model,
        "format": audio_format,
    }

    # 模型特定参数
    if model == "tts":
        payload["voice"] = voice
    elif model == "voice-design":
        if not voice_desc:
            print("❌ VoiceDesign 模型需要 --voice-desc 参数", file=sys.stderr)
            sys.exit(1)
        payload["voice_description"] = voice_desc
    elif model == "voice-clone":
        if not ref_audio:
            print("❌ VoiceClone 模型需要 --ref-audio 参数", file=sys.stderr)
            sys.exit(1)
        import base64
        payload["reference_audio"] = base64.b64encode(read_binary(ref_audio)).decode("utf-8")
    else:
        print(f"❌ 未知模型: {model}", file=sys.stderr)
        print(f"   支持的模型: {', '.join(MODELS.keys())}", file=sys.stderr)
        sys.exit(1)

    if user_msg:
        payload["user_msg"] = user_msg

    # 推理优化参数
    if optimize:
        payload["optimize"] = optimize

    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
    }

    model_name = MODELS.get(model, model)
    print(f"🎙️ 合成中... (模型: {model_name}, 格式: {audio_format})", file=sys.stderr)

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            if e.code == 429 and attempt < max_retries:
                wait = min(2 ** attempt, 10)
                print(f"⏳ 限流，{wait}秒后重试 ({attempt}/{max_retries})", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"❌ API 错误 {e.code}: {body}", file=sys.stderr)
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


def list_models():
    print("🤖 支持的模型：")
    print(f"{'参数':<20} {'名称'}")
    print("─" * 50)
    for param, name in MODELS.items():
        print(f"{param:<20} {name}")
    print(f"\n📖 文档: https://platform.xiaomimimo.com/docs/usage-guide/speech-synthesis-v2.5")
    print(f"🎮 体验: https://aistudio.xiaomimimo.com/#/c")


def list_voices():
    print("🎙️ 可用音色（MiMo-V2.5-TTS）：")
    print(f"{'参数':<20} {'名称'}")
    print("─" * 40)
    for param, name in VOICES.items():
        print(f"{param:<20} {name}")
    print(f"\n🎧 试听: https://aistudio.xiaomimimo.com/#/c")


def list_formats():
    print("📁 可用格式：")
    print(f"{'参数':<10} {'说明'}")
    print("─" * 30)
    for param, desc in FORMATS.items():
        print(f"{param:<10} {desc}")
    print(f"\n🎨 可用风格：{', '.join(STYLES)}")


def main():
    parser = argparse.ArgumentParser(
        description="Xiaomi MiMo V2.5 TTS 语音合成\n"
                    "文档: https://platform.xiaomimimo.com/docs/usage-guide/speech-synthesis-v2.5",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("text", nargs="?", help="要合成的文本")
    parser.add_argument("-o", "--output", default="output.wav", help="输出文件路径")
    parser.add_argument("-m", "--model", default="tts",
                        choices=list(MODELS.keys()), help="模型选择")
    parser.add_argument("-v", "--voice", default="mimo_default",
                        choices=list(VOICES.keys()), help="音色（仅 tts 模型）")
    parser.add_argument("-s", "--style", default="", help="风格标签（仅 tts 模型）")
    parser.add_argument("-f", "--format", default="wav",
                        choices=list(FORMATS.keys()), help="音频格式")
    parser.add_argument("--voice-desc", default="",
                        help="VoiceDesign：音色描述（如 '一位年迈的学者，低沉、略带嘶哑'）")
    parser.add_argument("--ref-audio", default="",
                        help="VoiceClone：参考音频路径")
    parser.add_argument("--user-msg", default="", help="用户角色上下文")
    parser.add_argument("--api-key", default="", help="API Key 覆盖")
    parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数")
    parser.add_argument("--optimize", default="", choices=["gpu", "cpu", "lite", ""],
                        help="推理优化：gpu(CUDA半精度) / cpu(ONNX量化) / lite(轻量模式)")
    parser.add_argument("--list-models", action="store_true", help="列出支持的模型")
    parser.add_argument("--list-voices", action="store_true", help="列出可用音色")
    parser.add_argument("--list-formats", action="store_true", help="列出可用格式")

    args = parser.parse_args()

    if args.list_models:
        list_models()
        return
    if args.list_voices:
        list_voices()
        return
    if args.list_formats:
        list_formats()
        return

    if not args.text:
        parser.error("请提供要合成的文本")

    # 应用推理优化
    opt_config = {}
    if args.optimize:
        opt_config = apply_optimization(args.optimize)
        opt_name = OPTIMIZATIONS.get(args.optimize, args.optimize)
        print(f"⚡ 推理优化: {opt_name}", file=sys.stderr)

    # 根据输出文件后缀自动修正格式
    if args.output != "output.wav":
        ext = os.path.splitext(args.output)[1].lower().lstrip(".")
        if ext in FORMATS:
            args.format = ext

    audio = synthesize(
        text=args.text,
        model=args.model,
        voice=args.voice,
        style=args.style,
        audio_format=args.format,
        api_key=args.api_key,
        voice_desc=args.voice_desc,
        ref_audio=args.ref_audio,
        user_msg=args.user_msg,
        max_retries=args.max_retries,
        optimize=opt_config,
    )

    with open(args.output, "wb") as f:
        f.write(audio)

    size_kb = len(audio) / 1024
    print(f"✅ 已保存: {args.output} ({size_kb:.1f} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
