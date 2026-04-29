#!/usr/bin/env python3
"""
learn_api.py — 清华网络学堂 HTTP API 封装
无需浏览器，直接操作网络学堂 API
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os, json, time, ssl, base64
import requests
from urllib.parse import urlencode

# ========== 配置 ==========
SESSION_FILE = r"D:\testclaw\learn_session.json"
FINGERPRINT_FILE = r"D:\testclaw\learn_fingerprint.json"
DOWNLOAD_DIR = r"D:\testclaw\learn_downloads"
LEARN_BASE = "https://learn.tsinghua.edu.cn"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Referer": LEARN_BASE + "/",
}

AJAX_HEADERS = {
    **DEFAULT_HEADERS,
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
}

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def escape_filename(s):
    """转义文件名非法字符"""
    for ch in [' ', '\t', '?', '/', "'", '"', '<', '>', '#', ';', '*', '|', '\\']:
        s = s.replace(ch, '_')
    return s


class LearnAPI:
    def __init__(self, session_file=None):
        self.session_file = session_file or SESSION_FILE
        self.session = None
        self.valid = False
        self.fingerprint = None
        self.session_data = None
        self.cookies = {}
        self.xsrf_token = None
        self._ensure_download_dir()

    # ====== 内部方法 ======

    def _ensure_download_dir(self):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    def _update_headers(self):
        """更新 session headers"""
        if self.xsrf_token:
            self.session.headers.update({"X-XSRF-TOKEN": self.xsrf_token})

    def _post(self, path, data=None, use_ajax=True):
        """POST 请求"""
        url = LEARN_BASE + path
        headers = AJAX_HEADERS if use_ajax else DEFAULT_HEADERS
        kwargs = {"headers": headers}
        if data:
            if isinstance(data, dict):
                kwargs["data"] = urlencode(data, encoding='utf-8')
                kwargs["headers"]["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                kwargs["data"] = data
        r = self.session.post(url, **kwargs, verify=False, timeout=15)
        try:
            return r.json()
        except Exception:
            return r.text

    def _get(self, path, params=None, use_ajax=False):
        """GET 请求"""
        url = LEARN_BASE + path
        headers = AJAX_HEADERS if use_ajax else DEFAULT_HEADERS
        kwargs = {"headers": headers, "params": params}
        r = self.session.get(url, **kwargs, verify=False, timeout=15)
        return r

    def _build_url(self, path):
        return LEARN_BASE + path

    # ====== Session 管理 ======

    def reload_session(self):
        """从文件加载 session 并验证"""
        if not os.path.exists(self.session_file):
            self.valid = False
            return False

        with open(self.session_file, 'r', encoding='utf-8') as f:
            self.session_data = json.load(f)

        self.cookies = self.session_data.get('cookies', {})
        self.fingerprint = self.session_data.get('fingerprint', {})

        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

        # 设置 cookies
        for name, value in self.cookies.items():
            if value is None:
                continue
            for domain in ['.tsinghua.edu.cn', 'learn.tsinghua.edu.cn', 'id.tsinghua.edu.cn']:
                self.session.cookies.set(name, value, domain=domain, path='/', secure=False)

        # 设置 XSRF token
        self.xsrf_token = self.cookies.get('XSRF-TOKEN') or self.cookies.get('xsrf-token')
        if self.xsrf_token:
            self.session.headers.update({"X-XSRF-TOKEN": self.xsrf_token})

        return self._check_valid()

    def _check_valid(self):
        """验证 session 是否有效"""
        if not self.session:
            self.valid = False
            return False
        try:
            ts = str(int(time.time() * 1000))
            url = f"{LEARN_BASE}/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/2025-2026-2/zh_CN?timestamp={ts}"
            r = self.session.get(url, verify=False, timeout=8,
                                headers={**AJAX_HEADERS, "X-XSRF-TOKEN": self.xsrf_token} if self.xsrf_token else AJAX_HEADERS)
            result = r.json()
            courses = result.get('resultList', [])
            if courses:
                self.valid = True
                return True
        except Exception:
            pass
        self.valid = False
        return False

    def login(self):
        """
        尝试纯 API 登录。
        成功返回 True；失败返回 False（需使用浏览器版脚本）。
        """
        # 尝试从已有 fingerprint + session 重新认证
        # 当前纯 API 登录受限于 localStorage，暂时返回 False
        return False

    def save_session(self):
        """保存当前 session 到文件"""
        if not self.session or not self.cookies:
            return
        # 从 credentials.json 读取用户名（不在此处写死）
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))
            from _config import load_credentials
            username = load_credentials()[0]
        except Exception:
            username = 'unknown'
        self.session_data = {
            'username': username,
            'cookies': self.cookies,
            'fingerprint': self.fingerprint,
            'timestamp': time.time(),
        }
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, ensure_ascii=False, indent=2)

    # ====== 课程 API ======

    def get_current_semester(self):
        """获取当前学期和下学期信息"""
        data = self._post("/b/kc/zhjw_v_code_xnxq/getCurrentAndNextSemester", use_ajax=True)
        return data.get('result', {}).get('xnxq', [])

    def get_semesters(self):
        """获取所有学期列表"""
        data = self._post("/b/wlxt/kc/v_wlkc_xs_xktjb_coassb/queryxnxq", use_ajax=True)
        return [x for x in data if x is not None]

    def get_courses(self, semester=None):
        """获取课程列表

        Args:
            semester: str 学期ID，默认当前学期。格式 "2025-2026-2"

        Returns:
            List[dict] 课程列表，每项含 kcm(已转义课名), wlkcid, jsm(教师), kch, kxh, xf, xs, jslx
        """
        if semester is None:
            semesters = self.get_current_semester()
            semester = semesters[0] if semesters else '2025-2026-2'

        courses = []
        # 学生选课
        try:
            data = self._get(
                f"/b/wlxt/kc/v_wlkc_xs_xkb_kcb_extend/student/loadCourseBySemesterId/{semester}/zh_CN",
                use_ajax=True
            ).json()
            for c in data.get('resultList', []):
                c['jslx'] = '3'
                courses.append(c)
        except Exception:
            pass

        # 助教课程
        try:
            data2 = self._post(f"/b/kc/v_wlkc_kcb/queryAsorCoCourseList/{semester}/0", use_ajax=True)
            for c in data2.get('resultList', []):
                c['jslx'] = '0'
                courses.append(c)
        except Exception:
            pass

        # 转义课名
        for c in courses:
            c['kcm_escaped'] = escape_filename(c.get('kcm', ''))

        return courses

    def get_course_type(self, jslx):
        """根据 jslx 返回课程类型字符串"""
        return {'3': 'student', '0': 'teacher'}.get(str(jslx), 'student')

    # ====== 公告 API ======

    def get_announcements(self, wlkcid):
        """获取课程公告列表"""
        data = self._post(
            "/b/wlxt/kcgg/wlkc_ggb/student/pageListXs",
            {"aoData": [{"name": "wlkcid", "value": wlkcid}]},
            use_ajax=True
        )
        return data.get('object', {}).get('aaData', [])

    # ====== 课件 API ======

    def get_files(self, wlkcid):
        """获取课件文件列表"""
        data = self._get(
            f"/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent",
            params={"wlkcid": wlkcid, "size": 0},
            use_ajax=True
        )
        return data.json().get('object', [])

    def get_file_categories(self, wlkcid, type_='student'):
        """获取课件分类列表"""
        data = self._get(
            f"/b/wlxt/kj/wlkc_kjflb/{type_}/pageList",
            params={"wlkcid": wlkcid},
            use_ajax=True
        )
        return json.loads(data.text).get('object', {}).get('rows', [])

    def download_file(self, wlkcid, wjid, type_='student', filename=None, save_dir=None):
        """
        下载课件文件。

        Returns:
            str 保存的完整路径，失败返回 None
        """
        save_dir = save_dir or DOWNLOAD_DIR
        os.makedirs(save_dir, exist_ok=True)

        url = f"{LEARN_BASE}/b/wlxt/kj/wlkc_kjxxb/{type_}/downloadFile"
        params = {"sfgk": 0, "wjid": wjid}

        self._update_headers()
        headers = {**DEFAULT_HEADERS, "X-XSRF-TOKEN": self.xsrf_token} if self.xsrf_token else DEFAULT_HEADERS

        r = self.session.get(url, params=params, headers=headers, verify=False, stream=True, timeout=30)

        if r.status_code != 200:
            return None

        # 从 Content-Disposition 提取文件名
        cd = r.headers.get('Content-Disposition', '')
        if filename is None:
            import re
            m = re.search(r'filename[^;]*=([^;]+)', cd)
            if m:
                fname = m.group(1).strip().strip('"').strip("'")
                # decode URI encoding
                import urllib.parse
                filename = urllib.parse.unquote(fname)
            else:
                filename = f"file_{wjid}"

        filename = escape_filename(filename)
        filepath = os.path.join(save_dir, filename)

        try:
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return filepath
        except Exception:
            return None

    # ====== 作业 API ======

    def get_homeworks(self, wlkcid):
        """获取作业列表（含未提交/已提交/已批改）"""
        hws = []
        data = {"aoData": [{"name": "wlkcid", "value": wlkcid}]}
        for endpoint in ['zyListWj', 'zyListYjwg', 'zyListYpg']:
            try:
                d = self._post(f"/b/wlxt/kczy/zy/student/{endpoint}", data, use_ajax=True)
                hws.extend(d.get('object', {}).get('aaData', []))
            except Exception:
                continue
        return hws

    def get_homework_detail(self, wlkcid, zyid, xszyid='', type_='student'):
        """获取作业详情（含说明、附件、截止日期）"""
        url = f"/f/wlxt/kczy/zy/{type_}/viewZy"
        params = {
            "wlkcid": wlkcid,
            "sfgq": "0",
            "zyid": zyid,
            "xszyid": xszyid,
        }
        r = self._get(url, params=params, use_ajax=False)
        html = r.text if isinstance(r, requests.Response) else r

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        info = {}

        for item in soup.find_all('div', class_='list'):
            left = item.find('div', class_='left')
            right = item.find('div', class_='right')
            if not left or not right:
                continue
            key = left.get_text(strip=True)
            val = right.get_text(strip=True)
            if '标题' in key:
                info['title'] = val
            elif '说明' in key:
                info['description'] = val
            elif '截止' in key:
                info['deadline'] = val
            elif '补交' in key:
                info['makeup_deadline'] = val

        # 附件
        attachments = []
        for fj in soup.find_all('div', class_='fujian'):
            left = fj.find('div', class_='left')
            links = fj.find_all('a')
            if left and links:
                key = left.get_text(strip=True)
                for link in links:
                    href = link.get('href', '')
                    name = link.get_text(strip=True)
                    if href and name:
                        if '作业' in key:
                            attachments.append({'name': name, 'href': href})
        info['attachments'] = attachments
        return info

    # ====== 讨论 API ======

    def get_discussions(self, wlkcid, type_='student'):
        """获取讨论帖列表"""
        data = self._get(
            f"/b/wlxt/bbs/bbs_tltb/{type_}/kctlList",
            params={"wlkcid": wlkcid},
            use_ajax=True
        )
        try:
            return json.loads(data.text).get('object', {}).get('resultsList', [])
        except Exception:
            return []

    def get_discussion_detail(self, wlkcid, id_, bqid, type_='student'):
        """获取讨论帖详情"""
        url = f"/f/wlxt/bbs/bbs_tltb/{type_}/viewTlById"
        params = {"wlkcid": wlkcid, "id": id_, "tabbh": "2", "bqid": bqid}
        r = self._get(url, params=params, use_ajax=False)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        detail = soup.find('div', class_='detail')
        return detail.get_text(strip=True) if detail else ""


# ====== 命令行接口 ======
if __name__ == '__main__':
    import argparse, pprint

    parser = argparse.ArgumentParser(description='清华网络学堂 API')
    parser.add_argument('--session', default=SESSION_FILE)
    parser.add_argument('--semester', default=None)
    parser.add_argument('--course', default=None, help='课名（部分匹配）')
    parser.add_argument('--action', default='courses',
                        choices=['courses', 'announcements', 'files', 'homeworks', 'discussions', 'semesters'])
    args = parser.parse_args()

    api = LearnAPI(session_file=args.session)
    api.reload_session()

    if not api.valid:
        print("❌ Session 无效，请先运行:")
        print('   python "D:\\testclaw\\learn_login_v2.py"')
        exit(1)

    courses = api.get_courses(semester=args.semester)
    if args.course:
        courses = [c for c in courses if args.course in c.get('kcm', '')]

    if args.action == 'semesters':
        semesters = api.get_semesters()
        print("所有学期:", semesters)
    elif args.action == 'courses':
        for c in courses:
            print(f"[{c.get('jslx')}] {c.get('kcm')} | {c.get('jsm')} | wlkcid={c.get('wlkcid')}")
    elif args.action == 'announcements':
        for c in courses:
            ads = api.get_announcements(c['wlkcid'])
            if ads:
                print(f"\n=== {c['kcm']} 公告 ===")
                for a in ads:
                    print(f"  [{a.get('fbsjStr','')}] {a.get('bt','')}")
    elif args.action == 'files':
        for c in courses:
            files = api.get_files(c['wlkcid'])
            if files:
                print(f"\n=== {c['kcm']} 课件 ===")
                for f in files:
                    print(f"  {f.get('bt','?')}.{f.get('wjlx','?')}")
    elif args.action == 'homeworks':
        for c in courses:
            hws = api.get_homeworks(c['wlkcid'])
            if hws:
                print(f"\n=== {c['kcm']} 作业 ===")
                for h in hws:
                    print(f"  [{h.get('zt','?')}] {h.get('bt','?')} 截止:{h.get('scsjStr','?')}")
    elif args.action == 'discussions':
        for c in courses:
            disc = api.get_discussions(c['wlkcid'])
            if disc:
                print(f"\n=== {c['kcm']} 讨论 ===")
                for d in disc:
                    print(f"  {d.get('bt','?')} by {d.get('fbrxm','?')}")
