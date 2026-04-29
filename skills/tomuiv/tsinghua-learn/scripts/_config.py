#!/usr/bin/env python3
"""
_config.py — 网络学堂凭证加载器
所有脚本通过 import _config 获取账号密码
不要在任何脚本里硬编码账号密码

路径说明：
  _config.py 位于 skills/tsinghua-learn/scripts/
  credentials.json 位于 skills/tsinghua-learn/
  相对路径：../../credentials.json
"""
import os, json

# skills/tsinghua-learn/scripts/ → 上两级是 skill 根目录
_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CRED_FILE = os.path.join(_SKILL_DIR, "credentials.json")
_STATE_FILE = os.path.join(_SKILL_DIR, "sessions", "learn_session.json")
_FP_FILE = r"D:\testclaw\learn_fingerprint.json"
_PROFILE_DIR = os.path.join(_SKILL_DIR, "profiles", "learn_profile")


def load_credentials():
    """加载账号密码，若文件不存在或格式错误则提示用户"""
    if not os.path.exists(_CRED_FILE):
        raise FileNotFoundError(
            "credentials.json 未找到！\n"
            "请复制 config_example.json 为 credentials.json，"
            "并填入你的学号和密码。\n"
            "路径: " + _CRED_FILE
        )
    try:
        cred = json.load(open(_CRED_FILE, encoding="utf-8"))
        u = cred.get("username", "").strip()
        p = cred.get("password", "").strip()
        if not u or not p:
            raise ValueError("username 或 password 为空")
        return u, p
    except Exception as e:
        raise RuntimeError(
            f"credentials.json 读取失败: {e}\n"
            "请检查文件格式是否正确（需包含 username 和 password 字段）"
        )


def get_state_file():
    return _STATE_FILE


def get_fp_file():
    return _FP_FILE


def get_profile_dir():
    return _PROFILE_DIR


def get_skill_dir():
    return _SKILL_DIR