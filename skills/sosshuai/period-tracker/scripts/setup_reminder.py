#!/usr/bin/env python3
"""
setup_reminder.py - 经期提醒设置脚本
通过 cron 在预测经期前 N 天发送系统通知
"""

import argparse
import subprocess
import json
import sys
from datetime import date, timedelta
from pathlib import Path

DATA_PATH = Path.home() / ".openclaw" / "workspace" / "period_tracker" / "data.json"
TRACKER_SCRIPT = Path(__file__).parent / "period_tracker.py"
CRON_TAG = "# period-tracker-reminder"


def get_next_period_date() -> str:
    """调用 period_tracker 获取下次经期日期"""
    try:
        result = subprocess.run(
            [sys.executable, str(TRACKER_SCRIPT), "predict"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if "下次预测经期" in line:
                # 提取 YYYY-MM-DD
                import re
                dates = re.findall(r"\d{4}-\d{2}-\d{2}", line)
                if dates:
                    return dates[0]
    except Exception as e:
        print(f"⚠️  无法获取预测日期：{e}")
    return None


def list_reminders():
    """列出当前经期提醒 cron 任务"""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        lines = [l for l in result.stdout.splitlines() if CRON_TAG in l]
        if lines:
            print("📋 当前经期提醒：")
            for l in lines:
                print(f"  {l}")
        else:
            print("暂无经期提醒设置")
    except Exception as e:
        print(f"读取 cron 失败：{e}")


def add_reminder(days_before: int, hour: int = 9, minute: int = 0):
    """设置提前 N 天的经期提醒"""
    next_date = get_next_period_date()
    if not next_date:
        print("❌ 无法获取预测日期，请先添加至少一条经期记录")
        return

    from datetime import datetime
    remind_date = datetime.strptime(next_date, "%Y-%m-%d").date() - timedelta(days=days_before)
    today = date.today()

    if remind_date <= today:
        print(f"⚠️  提醒日期 {remind_date} 已过（预测经期 {next_date}，提前 {days_before} 天）")
        print("   建议减少提前天数，或等待下次经期记录后重新设置")
        return

    # cron 格式：minute hour day month *
    cron_line = (
        f"{minute} {hour} {remind_date.day} {remind_date.month} * "
        f'python3 {TRACKER_SCRIPT} today {CRON_TAG} days_before={days_before}'
    )

    # 读取现有 crontab
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    # 移除同类旧提醒
    lines = [l for l in existing.splitlines() if CRON_TAG not in l]
    lines.append(cron_line)
    new_crontab = "\n".join(lines) + "\n"

    proc = subprocess.run(["crontab", "-"], input=new_crontab, text=True, capture_output=True)
    if proc.returncode == 0:
        print(f"✅ 已设置经期提醒")
        print(f"   下次预测经期：{next_date}")
        print(f"   提醒时间：{remind_date} {hour:02d}:{minute:02d}（提前 {days_before} 天）")
    else:
        print(f"❌ 设置 cron 失败：{proc.stderr}")


def remove_reminders():
    """清除所有经期提醒"""
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        print("暂无 crontab")
        return
    lines = [l for l in result.stdout.splitlines() if CRON_TAG not in l]
    new_crontab = "\n".join(lines) + "\n"
    subprocess.run(["crontab", "-"], input=new_crontab, text=True)
    print("✅ 已清除所有经期提醒")


def main():
    parser = argparse.ArgumentParser(description="经期提醒设置")
    sub = parser.add_subparsers(dest="cmd")

    p_add = sub.add_parser("add", help="添加提醒")
    p_add.add_argument("--days", type=int, default=3, help="提前天数（默认3天）")
    p_add.add_argument("--hour", type=int, default=9, help="提醒小时（24h，默认9）")
    p_add.add_argument("--minute", type=int, default=0, help="提醒分钟（默认0）")

    sub.add_parser("list", help="列出提醒")
    sub.add_parser("remove", help="清除提醒")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    if args.cmd == "add":
        add_reminder(args.days, args.hour, args.minute)
    elif args.cmd == "list":
        list_reminders()
    elif args.cmd == "remove":
        remove_reminders()


if __name__ == "__main__":
    main()
