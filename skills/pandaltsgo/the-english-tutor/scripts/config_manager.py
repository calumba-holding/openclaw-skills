#!/usr/bin/env python3
"""
英语助教 · 配置状态管理器
读写 ~/.openclaw/english-tutor/config.json
"""
import json, os, sys, pathlib

CONFIG_DIR = pathlib.Path.home() / ".openclaw" / "english-tutor"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 字段名与 agents/english-tutor/config.js 保持一致
DEFAULTS = {
    "setup_complete": False,
    "word_list_path": "",
    "daily_words": 5,
    "schedule_times": ["08:00"],
    # LLM
    "llm_provider": "openclaw",
    "llm_model": "",
    # 飞书
    "feishu_app_id": "",
    "feishu_app_secret": "",
    "feishu_bot_token": "",
    "feishu_user_open_id": "",
    # TTS
    "tts_provider": "minimax",
    "minimax_api_key": "",
    "minimax_tts_model": "speech-2.8-hd",
    "minimax_tts_speed": 1.05,
    "minimax_tts_voice_id": "male-qn-qingse",
    # Piper 本地 TTS（可选）
    "piper_bin": "",
    "piper_model": "",
    # SenseVoice 本地 ASR（可选）
    "sense_voice_model_dir": "",
    # 多维表格（可选）
    "bitable_app_token": "",
    "bitable_words_table_id": "",
    "bitable_chat_table_id": "",
    "created_at": "",
}


def load():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        return {**DEFAULTS}
    try:
        return {**DEFAULTS, **json.loads(CONFIG_FILE.read_text())}
    except Exception:
        return {**DEFAULTS}


def save(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2))


def get(key):
    return load().get(key)


def set_(key, value):
    cfg = load()
    cfg[key] = value
    save(cfg)


def check():
    cfg = load()
    required = [
        "setup_complete",
        "word_list_path",
        "feishu_app_id",
        "feishu_app_secret",
        "feishu_user_open_id",
    ]
    missing = [k for k in required if not cfg.get(k)]
    if not missing:
        print("✅ 配置完整，可以开始练习")
        return True
    else:
        print("❌ 缺少必要配置:", ", ".join(missing))
        return False


def init():
    if CONFIG_FILE.exists():
        resp = input(f"配置已存在: {CONFIG_FILE}，覆盖？(y/N): ")
        if resp.lower() != 'y':
            print("取消。")
            return
    save({**DEFAULTS})
    print(f"✅ 已创建默认配置: {CONFIG_FILE}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "get":
        print(get(sys.argv[2] if len(sys.argv) > 2 else ""))
    elif cmd == "set":
        if len(sys.argv) < 4:
            print("用法: config_manager.py set <key> <value>")
            sys.exit(1)
        set_(sys.argv[2], sys.argv[3])
        print(f"✅ {sys.argv[2]} = {sys.argv[3]}")
    elif cmd == "check":
        ok = check()
        sys.exit(0 if ok else 1)
    elif cmd == "init":
        init()
    elif cmd == "path":
        print(CONFIG_FILE)
    else:
        print(json.dumps(load(), ensure_ascii=False, indent=2))
