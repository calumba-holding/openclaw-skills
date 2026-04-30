#!/usr/bin/env python3
"""
飞书语音消息发送 · 封装现有 Node.js 实现
参考 agents/english-tutor/feishu-voice.js

用法:
  python3 feishu_voice.py <text>                     # 发送语音
  python3 feishu_voice.py <text> --dry-run           # 仅TTS，不发飞书
  python3 feishu_voice.py <text> --config <path>    # 指定配置文件
"""
import argparse, json, os, pathlib, subprocess, sys

SCRIPT_DIR = pathlib.Path(__file__).parent
DEFAULT_CONFIG = pathlib.Path.home() / ".openclaw" / "english-tutor" / "config.json"


def log(msg):
    print(f"[FeishuVoice] {msg}", file=sys.stderr)


def die(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def load_config(path):
    """加载 config.json"""
    p = pathlib.Path(path)
    if not p.exists():
        die(f"配置文件不存在: {p}\n请先完成引导设置（说「练习英语」触发）")
    cfg = json.loads(p.read_text())
    for k in ["feishu_app_id", "feishu_app_secret", "feishu_user_open_id"]:
        if not cfg.get(k):
            die(f"配置缺少 {k}，请重新运行引导设置")
    return cfg


def find_js_script():
    """找 feishu-voice.js，支持多个可能路径"""
    candidates = [
        # 绝对路径（当前工作环境）
        pathlib.Path("/vol1/@apphome/trim.openclaw/data/workspace/agents/english-tutor/feishu-voice.js"),
        # skill 包内（用户独立部署时，agents/ 在 skill 上一层）
        pathlib.Path(__file__).resolve().parent.parent / "agents" / "english-tutor" / "feishu-voice.js",
        # OpenClaw 共享 agents 目录
        pathlib.Path.home() / ".openclaw" / "agents" / "english-tutor" / "feishu-voice.js",
    ]
    for p in candidates:
        if p.exists():
            return p
    die(f"找不到 feishu-voice.js，请确认 agents/english-tutor 已部署。")


def write_env_file(js_dir, cfg):
    """将配置写入 Node.js 脚本同目录的 .env 文件（feishu-voice.js 从 __dirname 加载）"""
    env_content = "\n".join(
        f"{k}={v}"
        for k, v in {
            "MINIMAX_API_KEY":       cfg.get("minimax_api_key", ""),
            "FEISHU_APP_ID":         cfg.get("feishu_app_id", ""),
            "FEISHU_APP_SECRET":     cfg.get("feishu_app_secret", ""),
            "FEISHU_USER_OPEN_ID":   cfg.get("feishu_user_open_id", ""),
            "MINIMAX_TTS_MODEL":     cfg.get("minimax_tts_model", "speech-2.8-hd"),
            "MINIMAX_TTS_SPEED":     str(cfg.get("minimax_tts_speed", 1.05)),
            "MINIMAX_TTS_VOICE_ID":  cfg.get("minimax_tts_voice_id", "male-qn-qingse"),
            "TTS_PROVIDER":          cfg.get("tts_provider", "minimax"),
            "PIPER_BIN":             cfg.get("piper_bin", ""),
            "PIPER_MODEL":           cfg.get("piper_model", ""),
            "SENSE_VOICE_MODEL_DIR": cfg.get("sense_voice_model_dir", ""),
        }.items()
        if v
    )
    env_file = js_dir / ".env"
    old_env = env_file.read_text() if env_file.exists() else None
    env_file.write_text(env_content)
    log(f".env 已写入: {env_file} （已保存旧内容: {old_env is not None}）")
    return env_file, old_env


def restore_env(env_file, old_env):
    """恢复 .env 文件"""
    try:
        if old_env is not None:
            env_file.write_text(old_env)
        else:
            env_file.unlink(missing_ok=True)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="发送飞书语音消息")
    parser.add_argument("text", nargs="?", help="要发送的文字内容")
    parser.add_argument("--config", type=pathlib.Path, default=DEFAULT_CONFIG,
                        help=f"配置文件路径（默认: {DEFAULT_CONFIG}）")
    parser.add_argument("--dry-run", action="store_true", help="仅合成语音，不发送")
    args = parser.parse_args()

    if not args.text:
        die("用法: feishu_voice.py <文字内容> [--dry-run] [--config <配置路径>]")

    # 1. 加载配置
    cfg = load_config(args.config)
    log(f"加载配置: app_id={cfg['feishu_app_id']}, user={cfg['feishu_user_open_id']}, "
        f"tts={cfg.get('tts_provider','minimax')}")

    # 2. 找 Node.js 脚本
    js_path = find_js_script()
    log(f"找到脚本: {js_path}")

    # 3. 写 .env 到 Node.js 脚本同目录
    env_file, old_env = write_env_file(js_path.parent, cfg)

    # 4. 构造环境并运行
    node_env = {**os.environ, "NODE_ENV": "production"}
    cmd = ["node", str(js_path), args.text]
    if args.dry_run:
        cmd.append("--dry-run")

    log(f"调用: node {js_path.name} ...")

    try:
        proc = subprocess.run(
            cmd,
            env=node_env,
            cwd=str(js_path.parent),
            timeout=120,
            capture_output=True,
        )
    except subprocess.TimeoutExpired:
        restore_env(env_file, old_env)
        die("TTS/发送超时（120秒）")

    # 5. 恢复 .env
    restore_env(env_file, old_env)

    # 6. 解析输出
    stdout = proc.stdout.decode("utf-8", errors="replace").strip()
    stderr = proc.stderr.decode("utf-8", errors="replace").strip()

    # 过滤piper调试行，显示关键信息
    for line in stderr.splitlines():
        stripped = line.strip()
        if stripped and "[piper]" not in line and not stripped.startswith("["):
            log(stripped)

    if proc.returncode == 0:
        msg_id = next(
            (l.strip() for l in stdout.splitlines()
             if "message_id" in l or "msg_id" in l or l.strip().startswith("om_")),
            None
        )
        print(msg_id or (stdout.splitlines()[-1] if stdout else "OK"))
    else:
        error_lines = [l for l in stderr.splitlines() if "Error" in l or "error" in l or "FAIL" in l]
        die(f"发送失败: {error_lines[0] if error_lines else f'退出码 {proc.returncode}'}")


if __name__ == "__main__":
    main()
