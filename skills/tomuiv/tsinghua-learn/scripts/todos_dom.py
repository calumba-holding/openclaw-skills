#!/usr/bin/env python3
"""
todos.py
清华网络学堂代办总览脚本
================================
【流程】
  1. 检查 Session 是否有效
  2. 无效 → 自动调 login_auto.py 续期
  3. Playwright 打开主页读 DOM（权威未读数）
  4. API 获取作业详情（截止时间）
  5. 汇总输出

【性能】
  Session 有效：纯 API → 1-2s
  Session 需续期：Playwright re-login + API → 15-25s
"""
import json, requests, sys, time, shutil, tempfile, re, os
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

# ====== 路径 + 账号配置（从 credentials.json 统一加载）=======
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _config import get_state_file, get_profile_dir, get_fp_file

STATE_FILE = get_state_file()
PROFILE_DIR = get_profile_dir()
FINGERPRINT_FILE = get_fp_file()
COURSE_NAME = {
    "2025-2026-2151368648": "大学物理A(1)",
    "2025-2026-2151369314": "概率论与数理统计",
    "2025-2026-2151369343": "英语听说交流(A)",
    "2025-2026-2151368819": "写作与沟通",
    "2025-2026-2151368584": "微积分A(2)",
}
# ======================


def check_session(state):
    """Session 有效性检查（毫秒级）"""
    if not state.get("learn_jsession") or not state.get("csrf"):
        return False
    h = {
        "Accept": "application/json, */*",
        "Referer": "https://learn.tsinghua.edu.cn/f/wlxt/index/course/student/",
        "X-XSRF-TOKEN": state["csrf"],
        "Cookie": f"JSESSIONID={state['learn_jsession']}; XSRF-TOKEN={state['csrf']}",
    }
    try:
        r = requests.get(
            "https://learn.tsinghua.edu.cn/b/wlxt/kczy/zy/student/index/zyListWj?wlkcid=&size=1",
            headers=h, timeout=10
        )
        return not ("location.href" in r.text and r.status_code == 200)
    except:
        return False


def auto_relogin():
    """调 login_auto.py 续期 Session"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    auto_script = os.path.join(script_dir, "login_auto.py")
    print("Session 失效，自动续期中...")
    import subprocess
    result = subprocess.run([sys.executable, auto_script],
                             capture_output=True, text=True)
    if result.returncode != 0:
        print("auto login 失败:", result.stderr)
        sys.exit(1)
    print(result.stdout)
    return json.load(open(STATE_FILE, encoding="utf-8"))


def api_get(path, csrf, learn_j):
    url = f"https://learn.tsinghua.edu.cn{path}&_csrf={csrf}" if "?" in path \
          else f"https://learn.tsinghua.edu.cn{path}?_csrf={csrf}"
    return requests.get(url, headers={
        "Accept": "application/json, */*",
        "Referer": "https://learn.tsinghua.edu.cn/f/wlxt/index/course/student/",
        "X-XSRF-TOKEN": csrf,
        "Cookie": f"JSESSIONID={learn_j}; XSRF-TOKEN={csrf}",
    }, timeout=15).json()


# ====== 主流程 ======
# 1. 读取 Session
state = json.load(open(STATE_FILE, encoding="utf-8"))
age_h = (time.time() - state.get("timestamp", 0)) / 3600
print(f"Session age={age_h:.1f}h")

# 2. 检查并续期
if not check_session(state):
    print("⚠️ Session 无效")
    state = auto_relogin()
else:
    print("✅ Session 有效")

csrf = state["csrf"]
learn_j = state["learn_jsession"]

# 3. Playwright 读主页 DOM（权威未读数）
TMP = tempfile.mkdtemp(prefix="todos_")
PROFILE_TMP = os.path.join(TMP, "profile")
os.makedirs(PROFILE_TMP)

pw = sync_playwright().start()
ctx = None
try:
    ctx = pw.chromium.launch_persistent_context(
        PROFILE_TMP, headless=True,
        viewport={"width": 1280, "height": 900},
        ignore_https_errors=True,
        args=["--no-sandbox", "--disable-dev-shm-usage"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    ctx.add_cookies([
        {"name": "JSESSIONID", "value": learn_j, "domain": ".learn.tsinghua.edu.cn", "path": "/"},
        {"name": "XSRF-TOKEN", "value": csrf, "domain": ".learn.tsinghua.edu.cn", "path": "/"},
    ])
    page.goto(
        "https://learn.tsinghua.edu.cn/f/wlxt/index/course/student/",
        timeout=30000, wait_until="networkidle"
    )
    time.sleep(3)
    body_text = page.inner_text("body")
finally:
    if ctx: ctx.close()
    pw.stop()
    shutil.rmtree(TMP, ignore_errors=True)

# 4. 解析主页 DOM
COURSE_CODE = {
    "大学物理A(1)": "10430934",
    "概率论": "10880012",
    "写作与沟通": "10691342",
    "微积分": "2151368584",
}

def parse_courses(text):
    results = {}
    for cname, code in COURSE_CODE.items():
        idx = text.find(cname)
        if idx < 0: continue
        end_idx = len(text)
        for _, other_code in COURSE_CODE.items():
            if other_code == code: continue
            other_pos = text.find(other_code, idx + len(cname))
            if other_pos > idx: end_idx = min(end_idx, other_pos)
        chunk = text[idx:end_idx]
        def get_count(pat):
            m = re.search(pat, chunk)
            return int(m.group(1)) if m else 0
        results[cname] = {
            "gg": get_count(r"公告\s*(\d+)"),
            "kj": get_count(r"课件\s*(\d+)"),
            "zy": get_count(r"作业\s*(\d+)"),
            "tl": get_count(r"讨论\s*(\d+)\s*我参与"),
            "dy": get_count(r"答疑\s*(\d+)"),
            "wj": get_count(r"问卷\s*(\d+)"),
        }
    return results

course_todos = parse_courses(body_text)

# 英语听说交流(A) - 单独处理
eng_idx = body_text.find("英语听说交流")
if eng_idx >= 0:
    eng_chunk = body_text[eng_idx:eng_idx + 800]
    def eng_count(pat):
        m = re.search(pat, eng_chunk)
        return int(m.group(1)) if m else 0
    course_todos["英语听说交流(A)"] = {
        "gg": eng_count(r"公告\s*(\d+)"),
        "kj": eng_count(r"课件\s*(\d+)"),
        "zy": eng_count(r"作业\s*(\d+)"),
        "tl": eng_count(r"讨论\s*(\d+)"),
        "dy": eng_count(r"答疑\s*(\d+)"),
        "wj": eng_count(r"问卷\s*(\d+)"),
    }
else:
    course_todos["英语听说交流(A)"] = {"gg": 0, "kj": 0, "zy": 0, "tl": 0, "dy": 0, "wj": 0}

# 5. API 获取作业详情
def fetch_all_homework():
    results = []
    for wlkcid in COURSE_NAME.keys():
        d = api_get(f"/b/wlxt/kczy/zy/student/index/zyListWj?wlkcid={wlkcid}&size=100", csrf, learn_j)
        items = d.get("object", {}).get("aaData", [])
        for x in items:
            if x.get("zt") == "未交":
                results.append({
                    "wlkcid": wlkcid,
                    "bt": x.get("bt", ""),
                    "jzsjStr": x.get("jzsjStr", ""),
                })
    return results

# 6. 汇总输出
print("\n=== 网络学堂代办总览 ===\n")
total = 0
for cname, todos in course_todos.items():
    print(f"【{cname}】")
    has_todo = False
    for cat, label in [
        ("zy", "作业未提交"), ("gg", "公告未浏览"), ("kj", "课件未浏览"),
        ("tl", "讨论我参与"), ("dy", "答疑已回答"), ("wj", "问卷未提交"),
    ]:
        count = todos[cat]
        if count > 0:
            print(f"  ⚠️ {label}: {count} 项")
            total += count
            has_todo = True
    if not has_todo:
        print(f"  ✅ 无待处理")

# 作业详情
has_zy = any(todos["zy"] > 0 for todos in course_todos.values())
if has_zy:
    print("\n--- 作业详情 ---")
    hw_list = fetch_all_homework()
    for x in sorted(hw_list, key=lambda x: x.get("jzsjStr", "")):
        name2 = COURSE_NAME.get(x["wlkcid"], x["wlkcid"])
        print(f"  {name2} | {x['bt']} | 截止:{x['jzsjStr']}")

print(f"\n待办总计: {total} 项")
