#!/usr/bin/env python3
"""
period_tracker.py - Period Management / 经期管理核心脚本
支持：记录、查询、统计、预测、排卵期管理（受孕概率）、日历视图、导出
"""

import argparse
import json
import csv
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

DATA_PATH = Path.home() / ".openclaw" / "workspace" / "period_tracker" / "data.json"


def load_data() -> dict:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DATA_PATH.exists():
        empty = {"version": "1.1", "periods": [], "settings": {"avg_cycle": 28, "avg_duration": 5}}
        DATA_PATH.write_text(json.dumps(empty, ensure_ascii=False, indent=2))
        return empty
    return json.loads(DATA_PATH.read_text())


def save_data(data: dict):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def parse_date(s: str) -> date:
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"无法解析日期：{s}，请使用 YYYY-MM-DD 格式")


def date_str(d) -> str:
    if isinstance(d, str):
        return d
    return d.strftime("%Y-%m-%d")


def compute_avg_cycle(periods: list) -> Optional[float]:
    starts = sorted([parse_date(p["start_date"]) for p in periods])
    if len(starts) < 2:
        return None
    gaps = [(starts[i+1] - starts[i]).days for i in range(len(starts)-1)]
    return round(sum(gaps) / len(gaps), 1)


def compute_avg_duration(periods: list) -> Optional[float]:
    durations = []
    for p in periods:
        if p.get("end_date"):
            d = (parse_date(p["end_date"]) - parse_date(p["start_date"])).days + 1
            durations.append(d)
    if not durations:
        return None
    return round(sum(durations) / len(durations), 1)


def get_ovulation_info(last_start: date, avg_cycle: float, avg_duration: float):
    cycle = int(round(avg_cycle))
    duration = int(round(avg_duration))
    next_start = last_start + timedelta(days=cycle)
    ovulation_day = next_start - timedelta(days=14)
    fertile_start = ovulation_day - timedelta(days=5)
    fertile_end = ovulation_day + timedelta(days=4)
    return {
        "next_start": next_start,
        "next_end": next_start + timedelta(days=duration - 1),
        "ovulation_day": ovulation_day,
        "fertile_start": fertile_start,
        "fertile_end": fertile_end,
    }


def get_conception_probability(today: date, ovulation_day: date, fertile_start: date, fertile_end: date) -> dict:
    """受孕概率评估（基于标准医学周期算法）"""
    days_from_ovulation = (today - ovulation_day).days

    if not (fertile_start <= today <= fertile_end):
        return {"level": "极低", "percent": "< 3%", "emoji": "🟢", "desc": "安全期，受孕概率极低"}

    if days_from_ovulation == 0:
        return {"level": "最高", "percent": "25-30%", "emoji": "🔴",
                "desc": "排卵日！卵子存活12-24小时，黄金受孕窗口"}
    elif days_from_ovulation in (-1, -2):
        return {"level": "高", "percent": "20-25%", "emoji": "🟠",
                "desc": "排卵日前1-2天，精子可在输卵管存活3-5天"}
    elif days_from_ovulation in (-3, -4, -5):
        return {"level": "中", "percent": "10-15%", "emoji": "🟡",
                "desc": "排卵日前3-5天，精子提前等待，有一定受孕概率"}
    elif days_from_ovulation in (1, 2):
        return {"level": "低", "percent": "5-10%", "emoji": "🔵",
                "desc": "排卵日后1-2天，卵子存活窗口快关闭"}
    else:
        return {"level": "极低", "percent": "< 3%", "emoji": "🟢",
                "desc": "易孕期尾声，受孕概率极低"}


def cmd_add(args):
    data = load_data()
    start = parse_date(args.start)
    end = parse_date(args.end) if args.end else None

    for p in data["periods"]:
        if p["start_date"] == date_str(start):
            print(f"⚠️  已存在该开始日期的记录：{date_str(start)}，如需修改请使用 edit 命令")
            return

    record = {
        "id": int(datetime.now().timestamp() * 1000),
        "start_date": date_str(start),
        "end_date": date_str(end) if end else None,
        "duration": (end - start).days + 1 if end else None,
        "symptoms": {
            "pain_level": args.pain,
            "mood": args.mood,
            "flow": args.flow,
            "tags": args.tags.split(",") if args.tags else []
        },
        "notes": args.notes or "",
        "created_at": datetime.now().isoformat()
    }
    data["periods"].append(record)
    data["periods"].sort(key=lambda x: x["start_date"])

    avg_c = compute_avg_cycle(data["periods"])
    avg_d = compute_avg_duration(data["periods"])
    if avg_c:
        data["settings"]["avg_cycle"] = avg_c
    if avg_d:
        data["settings"]["avg_duration"] = avg_d

    save_data(data)
    print(f"✅ 已添加经期记录")
    print(f"   开始：{date_str(start)}")
    if end:
        print(f"   结束：{date_str(end)}，经期 {record['duration']} 天")
    if args.pain:
        print(f"   痛经程度：{'★' * args.pain}{'☆' * (5 - args.pain)} ({args.pain}/5)")
    if args.flow:
        print(f"   经血量：{args.flow}")


def cmd_list(args):
    data = load_data()
    periods = data["periods"]
    limit = args.limit or 10

    if not periods:
        print("暂无记录。使用 add 命令添加第一条记录。")
        return

    recent = sorted(periods, key=lambda x: x["start_date"], reverse=True)[:limit]
    print(f"📋 最近 {len(recent)} 条经期记录：\n")
    for p in recent:
        end_str = f" → {p['end_date']}" if p.get("end_date") else " → (进行中)"
        dur_str = f"，{p['duration']}天" if p.get("duration") else ""
        sym = p.get("symptoms", {})
        pain_str = f"，痛经{'★'*sym['pain_level']}{'☆'*(5-sym['pain_level'])}" if sym.get("pain_level") else ""
        flow_str = f"，经血量:{sym['flow']}" if sym.get("flow") else ""
        tags_str = f"，症状:[{','.join(sym['tags'])}]" if sym.get("tags") else ""
        print(f"  {p['start_date']}{end_str}{dur_str}{pain_str}{flow_str}{tags_str}")


def cmd_predict(args):
    data = load_data()
    periods = data["periods"]

    if not periods:
        print("⚠️  暂无历史数据，无法预测。请先添加至少一条记录。")
        return

    last = sorted(periods, key=lambda x: x["start_date"], reverse=True)[0]
    last_start = parse_date(last["start_date"])
    avg_cycle = compute_avg_cycle(periods) or data["settings"].get("avg_cycle", 28)
    avg_duration = compute_avg_duration(periods) or data["settings"].get("avg_duration", 5)

    ov = get_ovulation_info(last_start, avg_cycle, avg_duration)
    next_start = ov["next_start"]
    next_end = ov["next_end"]
    ovulation_day = ov["ovulation_day"]
    fertile_start = ov["fertile_start"]
    fertile_end = ov["fertile_end"]

    duration = int(round(avg_duration))
    cur_end = parse_date(last["end_date"]) if last.get("end_date") else last_start + timedelta(days=duration - 1)
    safe1_start = cur_end + timedelta(days=5)
    safe1_end = fertile_start - timedelta(days=1)
    safe2_start = fertile_end + timedelta(days=1)
    safe2_end = next_start - timedelta(days=5)

    today = date.today()
    days_until = (next_start - today).days

    print(f"\n🔮 Period Management / 经期管理 — 预测报告")
    print(f"   平均周期：{avg_cycle} 天 | 平均经期：{avg_duration} 天")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📅 最近一次经期：{last_start} ~ {date_str(cur_end)}")

    print(f"\n🩸 下次预测经期：{date_str(next_start)} ~ {date_str(next_end)}")
    if days_until > 0:
        print(f"   距今还有 {days_until} 天")
    elif days_until == 0:
        print(f"   ← 预计今天开始！")
    else:
        print(f"   已超期 {-days_until} 天（可能已开始或延迟）")

    print(f"\n🥚 排卵期")
    print(f"   排卵日：{date_str(ovulation_day)}  🔴 受孕概率最高（25-30%）")
    print(f"   易孕期：{date_str(fertile_start)} ~ {date_str(fertile_end)}（共10天）")

    print(f"\n🛡️  安全期：")
    if safe1_end >= safe1_start:
        print(f"   前安全期：{date_str(safe1_start)} ~ {date_str(safe1_end)}")
    if safe2_end >= safe2_start:
        print(f"   后安全期：{date_str(safe2_start)} ~ {date_str(safe2_end)}")

    print(f"\n📍 今日受孕概率：")
    prob = get_conception_probability(today, ovulation_day, fertile_start, fertile_end)
    print(f"   {prob['emoji']} {prob['level']}（{prob['percent']}）— {prob['desc']}")

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📌 受孕概率参考（标准医学周期算法）：")
    print(f"   🔴 排卵日         最高 25-30%")
    print(f"   🟠 排卵前1-2天    高   20-25%")
    print(f"   🟡 排卵前3-5天    中   10-15%")
    print(f"   🔵 排卵后1-2天    低   5-10%")
    print(f"   🟢 其他时间       极低 < 3%")
    print(f"\n⚠️  数据基于标准周期估算，个体差异因人而异，建议配合排卵试纸（LH试纸）。")


def cmd_ovulation(args):
    """排卵期管理 — 7天受孕概率日历"""
    data = load_data()
    periods = data["periods"]

    if not periods:
        print("⚠️  暂无历史数据，请先添加至少一条经期记录。")
        return

    last = sorted(periods, key=lambda x: x["start_date"], reverse=True)[0]
    last_start = parse_date(last["start_date"])
    avg_cycle = compute_avg_cycle(periods) or data["settings"].get("avg_cycle", 28)
    avg_duration = compute_avg_duration(periods) or data["settings"].get("avg_duration", 5)

    ov = get_ovulation_info(last_start, avg_cycle, avg_duration)
    today = date.today()
    ovulation_day = ov["ovulation_day"]
    fertile_start = ov["fertile_start"]
    fertile_end = ov["fertile_end"]
    days_to_ovulation = (ovulation_day - today).days

    print(f"\n🥚 排卵期管理 — Period Management / 经期管理")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 平均周期：{avg_cycle} 天 | 最近经期开始：{last_start}")
    print()
    print(f"🔴 排卵日：{date_str(ovulation_day)}", end="")
    if days_to_ovulation > 0:
        print(f"（还有 {days_to_ovulation} 天）")
    elif days_to_ovulation == 0:
        print(f" ← 今天！")
    else:
        print(f"（已过 {-days_to_ovulation} 天）")
    print(f"🌸 易孕期：{date_str(fertile_start)} ~ {date_str(fertile_end)}")
    print()

    # 7天受孕概率日历
    print(f"📆 未来7天受孕概率：")
    print(f"   日期           状态   受孕概率")
    print(f"   {'─'*40}")
    for i in range(7):
        d = today + timedelta(days=i)
        prob = get_conception_probability(d, ovulation_day, fertile_start, fertile_end)
        label = "（今天）" if i == 0 else f"（+{i}天） "
        print(f"   {date_str(d)} {label}  {prob['emoji']} {prob['level']:<4} {prob['percent']}")

    print()
    # 今日状态
    in_period = False
    for p in periods:
        s = parse_date(p["start_date"])
        dur = int(avg_duration)
        e = parse_date(p["end_date"]) if p.get("end_date") else s + timedelta(days=dur - 1)
        if s <= today <= e:
            in_period = True
            break

    print(f"📍 今日状态：", end="")
    if in_period:
        print("🩸 经期中")
    elif today == ovulation_day:
        print("🔴 排卵日！（受孕概率最高 25-30%）")
    elif fertile_start <= today <= fertile_end:
        prob = get_conception_probability(today, ovulation_day, fertile_start, fertile_end)
        print(f"🌸 易孕期 — 受孕概率{prob['level']}（{prob['percent']}）")
    else:
        print("🟢 安全期（受孕概率极低 < 3%）")

    print()
    print(f"💡 备孕建议：")
    if today == ovulation_day:
        print(f"   ★ 今天是排卵日，是备孕最佳时机！")
    elif 1 <= days_to_ovulation <= 3:
        print(f"   ★ 排卵日还有 {days_to_ovulation} 天，现在同房精子可提前等待卵子释放。")
    elif days_to_ovulation > 3:
        print(f"   → 排卵日还有 {days_to_ovulation} 天，建议排卵日前2-3天开始备孕。")
    else:
        print(f"   → 本次排卵窗口已过，等待下一个周期。")

    print(f"\n⚠️  本预测基于标准算法，实际排卵日因个体差异、压力、作息等会有偏差。")
    print(f"   建议配合 LH 排卵试纸监测，精准度更高。")


def cmd_today(args):
    data = load_data()
    periods = data["periods"]
    today = date.today()

    print(f"\n📍 今日状态 ({today}) — Period Management / 经期管理")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    if not periods:
        print("暂无记录，请先添加经期数据。")
        return

    avg_cycle = compute_avg_cycle(periods) or data["settings"].get("avg_cycle", 28)
    avg_duration = compute_avg_duration(periods) or data["settings"].get("avg_duration", 5)
    last = sorted(periods, key=lambda x: x["start_date"], reverse=True)[0]
    last_start = parse_date(last["start_date"])
    ov = get_ovulation_info(last_start, avg_cycle, avg_duration)
    ovulation_day = ov["ovulation_day"]
    fertile_start = ov["fertile_start"]
    fertile_end = ov["fertile_end"]

    in_period = False
    for p in periods:
        s = parse_date(p["start_date"])
        dur = int(avg_duration)
        e = parse_date(p["end_date"]) if p.get("end_date") else s + timedelta(days=dur - 1)
        if s <= today <= e:
            day_num = (today - s).days + 1
            print(f"🩸 经期第 {day_num} 天（{date_str(s)} 开始）")
            in_period = True
            break

    if not in_period:
        next_start = ov["next_start"]
        days_until = (next_start - today).days

        if today == ovulation_day:
            print(f"🔴 排卵日！受孕概率最高（25-30%）")
        elif fertile_start <= today <= fertile_end:
            prob = get_conception_probability(today, ovulation_day, fertile_start, fertile_end)
            days_to_ov = (ovulation_day - today).days
            if days_to_ov >= 0:
                print(f"🌸 易孕期中（距排卵日还有 {days_to_ov} 天）")
            else:
                print(f"🌸 易孕期中（排卵日已过 {-days_to_ov} 天）")
            print(f"   受孕概率：{prob['emoji']} {prob['level']}（{prob['percent']}）")
        else:
            print(f"🟢 安全期（受孕概率极低）")

        if days_until > 0:
            print(f"📅 下次预测经期：{date_str(next_start)}（还有 {days_until} 天）")
        elif days_until == 0:
            print(f"📅 预测今天经期开始！")
        else:
            print(f"📅 经期可能已迟到 {-days_until} 天，注意观察")


def cmd_stats(args):
    data = load_data()
    periods = data["periods"]

    if not periods:
        print("暂无数据。")
        return

    today = date.today()
    print(f"\n📊 健康统计 — Period Management / 经期管理")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"总记录：{len(periods)} 次")

    avg_c = compute_avg_cycle(periods)
    if avg_c:
        status = "✅ 正常" if 21 <= avg_c <= 35 else "⚠️ 偏短" if avg_c < 21 else "⚠️ 偏长"
        print(f"平均周期：{avg_c} 天 {status}")

    avg_d = compute_avg_duration(periods)
    if avg_d:
        status = "✅ 正常" if 3 <= avg_d <= 7 else "⚠️ 偏短" if avg_d < 3 else "⚠️ 偏长"
        print(f"平均经期：{avg_d} 天 {status}")

    starts = sorted([parse_date(p["start_date"]) for p in periods])
    if len(starts) >= 2:
        gaps = [(starts[i+1] - starts[i]).days for i in range(len(starts)-1)]
        regularity = max(gaps) - min(gaps)
        reg_str = "很规律 ✅" if regularity <= 3 else "较规律" if regularity <= 7 else "不规律 ⚠️"
        print(f"周期规律性：{reg_str}（最长{max(gaps)}天，最短{min(gaps)}天，波动{regularity}天）")

    pain_levels = [p["symptoms"]["pain_level"] for p in periods if p.get("symptoms", {}).get("pain_level")]
    if pain_levels:
        avg_pain = round(sum(pain_levels) / len(pain_levels), 1)
        print(f"平均痛经：{'★' * round(avg_pain)}{'☆' * (5 - round(avg_pain))} ({avg_pain}/5)")

    all_tags = []
    for p in periods:
        all_tags.extend(p.get("symptoms", {}).get("tags", []))
    if all_tags:
        from collections import Counter
        tag_counts = Counter(all_tags).most_common(5)
        print(f"常见症状：{', '.join([f'{t}({c}次)' for t, c in tag_counts])}")


def cmd_calendar(args):
    data = load_data()
    periods = data["periods"]
    year = args.year or date.today().year

    avg_cycle = compute_avg_cycle(periods) or data["settings"].get("avg_cycle", 28)
    avg_duration = compute_avg_duration(periods) or data["settings"].get("avg_duration", 5)

    period_days = set()
    ovulation_days = set()
    fertile_days = set()

    for p in periods:
        s = parse_date(p["start_date"])
        e = parse_date(p["end_date"]) if p.get("end_date") else s + timedelta(days=int(avg_duration) - 1)
        cur = s
        while cur <= e:
            if cur.year == year:
                period_days.add(cur)
            cur += timedelta(days=1)

    if periods:
        last = sorted(periods, key=lambda x: x["start_date"], reverse=True)[0]
        last_start = parse_date(last["start_date"])
        for _ in range(14):
            ov = get_ovulation_info(last_start, avg_cycle, avg_duration)
            if ov["ovulation_day"].year == year:
                ovulation_days.add(ov["ovulation_day"])
                cur = ov["fertile_start"]
                while cur <= ov["fertile_end"]:
                    if cur != ov["ovulation_day"]:
                        fertile_days.add(cur)
                    cur += timedelta(days=1)
            last_start = ov["next_start"]
            if last_start.year > year + 1:
                break

    month_names = ["一月","二月","三月","四月","五月","六月",
                   "七月","八月","九月","十月","十一月","十二月"]

    print(f"\n📅 {year} 年 日历 — Period Management / 经期管理")
    print(f"图例：🩸=经期  🔴=排卵日  🌸=易孕期\n")

    for month in range(1, 13):
        print(f"  ── {month_names[month-1]} ──")
        print(f"  日  一  二  三  四  五  六")

        first_day = date(year, month, 1)
        start_weekday = (first_day.weekday() + 1) % 7
        last_day = date(year, month + 1, 1) - timedelta(days=1) if month < 12 else date(year + 1, 1, 1) - timedelta(days=1)

        line = "  " + "    " * start_weekday
        cur = first_day
        weekday = start_weekday
        while cur <= last_day:
            if cur in period_days:
                line += f"[{cur.day:2d}]"
            elif cur in ovulation_days:
                line += f"*{cur.day:2d}*"
            elif cur in fertile_days:
                line += f"({cur.day:2d})"
            else:
                line += f" {cur.day:2d} "
            weekday += 1
            if weekday == 7:
                print(line)
                line = "  "
                weekday = 0
            cur += timedelta(days=1)
        if line.strip():
            print(line)
        print()
    print("图例：[日期]=经期  *日期*=排卵日  (日期)=易孕期")


def cmd_export(args):
    data = load_data()
    periods = data["periods"]
    fmt = args.format or "json"
    out_path = Path(args.output) if args.output else Path.home() / ".openclaw" / "workspace" / "period_tracker" / f"export.{fmt}"

    if fmt == "json":
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        print(f"✅ 已导出 JSON：{out_path}")
    elif fmt == "csv":
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["开始日期","结束日期","经期天数","痛经程度","情绪","经血量","症状标签","备注"])
            for p in sorted(periods, key=lambda x: x["start_date"]):
                sym = p.get("symptoms", {})
                writer.writerow([p["start_date"], p.get("end_date",""), p.get("duration",""),
                    sym.get("pain_level",""), sym.get("mood",""), sym.get("flow",""),
                    ",".join(sym.get("tags",[])), p.get("notes","")])
        print(f"✅ 已导出 CSV：{out_path}")


def cmd_edit(args):
    data = load_data()
    target_date = parse_date(args.start)
    for p in data["periods"]:
        if p["start_date"] == date_str(target_date):
            if args.end:
                e = parse_date(args.end)
                p["end_date"] = date_str(e)
                p["duration"] = (e - target_date).days + 1
            if args.pain is not None:
                p.setdefault("symptoms", {})["pain_level"] = args.pain
            if args.mood:
                p.setdefault("symptoms", {})["mood"] = args.mood
            if args.flow:
                p.setdefault("symptoms", {})["flow"] = args.flow
            if args.tags:
                p.setdefault("symptoms", {})["tags"] = args.tags.split(",")
            if args.notes:
                p["notes"] = args.notes
            save_data(data)
            print(f"✅ 已更新 {date_str(target_date)} 的记录")
            return
    print(f"❌ 未找到开始日期为 {date_str(target_date)} 的记录")


def cmd_delete(args):
    data = load_data()
    target_date = parse_date(args.start)
    before = len(data["periods"])
    data["periods"] = [p for p in data["periods"] if p["start_date"] != date_str(target_date)]
    if len(data["periods"]) < before:
        save_data(data)
        print(f"✅ 已删除 {date_str(target_date)} 的记录")
    else:
        print(f"❌ 未找到该记录")


def main():
    parser = argparse.ArgumentParser(description="Period Management / 经期管理工具")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="添加经期记录")
    p_add.add_argument("start", help="开始日期 YYYY-MM-DD")
    p_add.add_argument("--end", help="结束日期 YYYY-MM-DD")
    p_add.add_argument("--pain", type=int, choices=range(1, 6), help="痛经程度 1-5")
    p_add.add_argument("--mood", choices=["开心","平静","烦躁","低落","焦虑"], help="情绪状态")
    p_add.add_argument("--flow", choices=["少","中","多"], help="经血量")
    p_add.add_argument("--tags", help="症状标签，逗号分隔")
    p_add.add_argument("--notes", help="备注")

    p_list = sub.add_parser("list", help="列出记录")
    p_list.add_argument("--limit", type=int, default=10)

    sub.add_parser("predict", help="预测下次经期 + 排卵期")
    sub.add_parser("ovulation", help="排卵期管理（7天受孕概率日历）")
    sub.add_parser("today", help="今日状态")
    sub.add_parser("stats", help="健康统计")

    p_cal = sub.add_parser("calendar", help="年度日历")
    p_cal.add_argument("--year", type=int)

    p_exp = sub.add_parser("export", help="导出数据")
    p_exp.add_argument("--format", choices=["json","csv"], default="json")
    p_exp.add_argument("--output")

    p_edit = sub.add_parser("edit", help="编辑记录")
    p_edit.add_argument("start")
    p_edit.add_argument("--end")
    p_edit.add_argument("--pain", type=int, choices=range(1, 6))
    p_edit.add_argument("--mood", choices=["开心","平静","烦躁","低落","焦虑"])
    p_edit.add_argument("--flow", choices=["少","中","多"])
    p_edit.add_argument("--tags")
    p_edit.add_argument("--notes")

    p_del = sub.add_parser("delete", help="删除记录")
    p_del.add_argument("start")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    cmds = {
        "add": cmd_add, "list": cmd_list, "predict": cmd_predict,
        "ovulation": cmd_ovulation, "today": cmd_today,
        "stats": cmd_stats, "calendar": cmd_calendar,
        "export": cmd_export, "edit": cmd_edit, "delete": cmd_delete
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
