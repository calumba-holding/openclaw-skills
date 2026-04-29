#!/usr/bin/env python3
"""
todos_api.py
清华网络学堂代办总览 — 纯API版本（默认版本）
==============================================
【流程】
  1. 检查 Session 有效性
  2. 无效 → 自动调 login_auto.py 续期
  3. 并行发出 5 个课程 × 5 个模块 = 25 个请求
  4. 汇总输出

【性能】Session 有效时约 2-3 秒（纯 HTTP，无 Playwright）
【默认运行】python todos.py 时优先调用本文件
"""
import json, requests, sys, time, os, concurrent.futures
sys.stdout.reconfigure(encoding='utf-8')

# ====== 路径 + 账号配置（从 credentials.json 统一加载）=======
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import load_credentials, get_state_file

STATE_FILE = get_state_file()
# ======================

# TOM 的 5 门课程
COURSE_NAME = {
    "2025-2026-2151368648": "大学物理A(1)",
    "2025-2026-2151369314": "概率论与数理统计",
    "2025-2026-2151369343": "英语听说交流(A)",
    "2025-2026-2151368819": "写作与沟通",
    "2025-2026-2151368584": "微积分A(2)",
}

BASE = "https://learn.tsinghua.edu.cn"

HEADERS = {
    "Accept": "application/json, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": BASE + "/f/wlxt/index/course/student/",
}


def check_session(state):
    if not state.get("learn_jsession") or not state.get("csrf"):
        return False
    h = {**HEADERS, "X-XSRF-TOKEN": state["csrf"],
         "Cookie": f"JSESSIONID={state['learn_jsession']}; XSRF-TOKEN={state['csrf']}"}
    try:
        r = requests.get(BASE + "/b/wlxt/kczy/zy/student/index/zyListWj?wlkcid=&size=1",
                         headers=h, timeout=10)
        return not ("location.href" in r.text and r.status_code == 200)
    except:
        return False


def auto_relogin():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    auto_script = os.path.join(script_dir, "login_auto.py")
    print("Session 失效，自动续期中...")
    import subprocess
    result = subprocess.run([sys.executable, auto_script],
                             capture_output=True, text=True)
    if result.returncode != 0:
        print("auto login 失败:", result.stderr)
        sys.exit(1)
    return json.load(open(STATE_FILE, encoding="utf-8"))


def api_get(path, csrf, jsession):
    url = (BASE + path) if "?" in path else (BASE + path + "?_csrf=" + csrf)
    if "?" in path:
        url = BASE + path + "&_csrf=" + csrf
    else:
        url = BASE + path + "?_csrf=" + csrf
    h = {**HEADERS, "X-XSRF-TOKEN": csrf,
         "Cookie": f"JSESSIONID={jsession}; XSRF-TOKEN={csrf}"}
    try:
        r = requests.get(url, headers=h, timeout=15)
        return r.json()
    except Exception as e:
        return {}


def fetch_course(wlkcid, csrf, jsession):
    """并行抓一门课的全部代办，返回 dict"""
    d_gg = api_get(f"/b/wlxt/kcgg/wlkc_ggb/student/kcggListXs?wlkcid={wlkcid}&size=20", csrf, jsession)
    d_kj = api_get(f"/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent?wlkcid={wlkcid}&size=100", csrf, jsession)
    d_zy = api_get(f"/b/wlxt/kczy/zy/student/index/zyListWj?wlkcid={wlkcid}&size=100", csrf, jsession)
    d_tl = api_get(f"/b/wlxt/bbs/bbs_tltb/student/kctlList?wlkcid={wlkcid}&size=20", csrf, jsession)
    d_dy = api_get(f"/b/wlxt/bbs/bbs_tltb/student/kcdyList?wlkcid={wlkcid}&size=20", csrf, jsession)

    def count_unread(data, field, value):
        if isinstance(data, dict):
            obj = data.get("object", data)
            if isinstance(obj, dict):
                items = obj.get("aaData", [])
            elif isinstance(obj, list):
                items = obj
            else:
                items = []
        elif isinstance(data, list):
            items = data
        else:
            return 0
        return sum(1 for x in items if str(x.get(field, "")).strip('"') == str(value))

    def get_items(data):
        if isinstance(data, dict):
            obj = data.get("object", data)
            if isinstance(obj, list):
                return obj
            elif isinstance(obj, dict):
                return obj.get("aaData", [])
        elif isinstance(data, list):
            return data
        return []

    return {
        "gg": count_unread(d_gg, "sfyd", "否"),
        "kj": count_unread(d_kj, "isNew", "1"),
        "zy": count_unread(d_zy, "zt", "未交"),
        "tl": count_unread(d_tl, "htsl", ""),
        "dy": count_unread(d_dy, "htsl", ""),
        "zy_items": [x for x in get_items(d_zy) if str(x.get("zt", "")).strip('"') == "未交"],
    }


# ====== 主流程 ======
state = json.load(open(STATE_FILE, encoding="utf-8"))
age_h = (time.time() - state.get("timestamp", 0)) / 3600
print(f"Session age={age_h:.1f}h")

if not check_session(state):
    print("⚠️ Session 无效")
    state = auto_relogin()
else:
    print("✅ Session 有效")

csrf = state["csrf"]
jsession = state["learn_jsession"]

# 并行抓所有课程
print("\n并行获取 5 门课程代办数据...")
results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    futures = {ex.submit(fetch_course, wlkcid, csrf, jsession): wlkcid
               for wlkcid in COURSE_NAME.keys()}
    for f in concurrent.futures.as_completed(futures):
        wlkcid = futures[f]
        results[wlkcid] = f.result()

# 汇总输出
print("\n=== 网络学堂代办总览（纯API）===\n")
total = 0
for wlkcid, todos in results.items():
    cname = COURSE_NAME[wlkcid]
    print(f"【{cname}】")
    has = False
    for cat, label in [
        ("zy", "作业未提交"),
        ("gg", "公告未浏览"),
        ("kj", "课件未浏览"),
        ("tl", "讨论我参与"),
        ("dy", "答疑已回答"),
    ]:
        cnt = todos[cat]
        if cnt > 0:
            print(f"  ⚠️ {label}: {cnt} 项")
            total += cnt
            has = True
    if not has:
        print(f"  ✅ 无待处理")

# 作业详情
any_zy = any(todos["zy"] > 0 for todos in results.values())
if any_zy:
    print("\n--- 作业详情 ---")
    for wlkcid, todos in results.items():
        for x in sorted(todos["zy_items"], key=lambda t: t.get("jzsjStr", "")):
            cname = COURSE_NAME[wlkcid]
            print(f"  {cname} | {x.get('bt','?')} | 截止:{x.get('jzsjStr','?')}")

print(f"\n待办总计: {total} 项")