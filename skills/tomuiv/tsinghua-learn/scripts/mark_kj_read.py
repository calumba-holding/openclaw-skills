#!/usr/bin/env python3
"""
mark_kj_read.py
批量标记所有课程未读课件为已读
使用 savePlayRecord 接口（isNew=1 → 0）

用法：python mark_kj_read.py
"""
import json, requests, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# 统一路径
_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.path.join(_SKILL_DIR, "sessions", "learn_session.json")
state = json.load(open(STATE_FILE, encoding="utf-8"))
learn_j = state["learn_jsession"]
csrf = state["csrf"]

headers = {
    "Accept": "application/json, */*",
    "Referer": "https://learn.tsinghua.edu.cn/f/wlxt/kj/wlkc_kjxxb/student/beforePageList",
    "X-XSRF-TOKEN": csrf,
    "Cookie": f"JSESSIONID={learn_j}; XSRF-TOKEN={csrf}",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

BASE_URL = "https://learn.tsinghua.edu.cn"

def mark_read(wjid):
    r = requests.post(
        f"{BASE_URL}/b/wlxt/kj/wlkc_kjfwb/student/savePlayRecord?_csrf={csrf}",
        headers=headers, data=f"wjid={wjid}&sfgk=0", timeout=10
    )
    return r.status_code == 200 and "success" in r.text

# 获取全部课程
r = requests.get(
    f"{BASE_URL}/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/2025-2026-2/zh?_csrf={csrf}",
    headers={k: v for k, v in headers.items() if k != "Content-Type"},
    timeout=15
)
courses = r.json().get("resultList", [])
print(f"共 {len(courses)} 门课程")

total_unread = 0
total_marked = 0

for course in courses:
    wlkcid = course.get("wlkcid", "")
    kcm = course.get("kcm", "?")
    if not wlkcid:
        continue

    r2 = requests.get(
        f"{BASE_URL}/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent?wlkcid={wlkcid}&size=100&_csrf={csrf}",
        headers={k: v for k, v in headers.items() if k != "Content-Type"},
        timeout=15
    )
    d = r2.json()
    obj = d.get("object", d)
    items = obj.get("aaData", []) if isinstance(obj, dict) else obj
    unread = [x for x in items if x.get("isNew") == 1]
    if not unread:
        continue

    total_unread += len(unread)
    marked = 0
    for item in unread:
        wjid = item.get("wjid", "")
        bt = item.get("bt", "?")
        if not wjid:
            continue
        if mark_read(wjid):
            marked += 1
        else:
            print(f"  ⚠️ 失败: {bt}")

    print(f"【{kcm}】{len(unread)} 项未读 → 标记 {marked} 项")
    total_marked += marked

print(f"\n总计：{total_unread} 项未读 → 标记已读 {total_marked} 项")
print("完成！")
