"""
下载课件 + 自动标已读 + 发送给用户 + 精准删除
用法：python download_and_send_kj.py < COURSE_ID > < WJID > < 课程名 >
示例：python download_and_send_kj.py 2025-2026-2151368584 2005990081_KJ_xxx 微积分
"""
import json, requests, sys, os
sys.stdout.reconfigure(encoding='utf-8')

# 统一 session 路径
import os as _os
_SKILL_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
STATE_FILE = _os.path.join(_SKILL_DIR, "sessions", "learn_session.json")
state = json.load(open(STATE_FILE, encoding="utf-8"))
learn_j = state['learn_jsession']; csrf = state['csrf']

headers = {
    'Accept': 'application/json, */*',
    'Referer': 'https://learn.tsinghua.edu.cn/f/wlxt/index/course/student/',
    'X-XSRF-TOKEN': csrf,
    'Cookie': f'JSESSIONID={learn_j}; XSRF-TOKEN={csrf}',
}
headers_post = {
    'Accept': 'application/json, */*',
    'Referer': 'https://learn.tsinghua.edu.cn/f/wlxt/kj/wlkc_kjxxb/student/beforePageList',
    'X-XSRF-TOKEN': csrf,
    'Cookie': f'JSESSIONID={learn_j}; XSRF-TOKEN={csrf}',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
}

def mark_kj_read(wjid):
    r = requests.post(
        f'https://learn.tsinghua.edu.cn/b/wlxt/kj/wlkc_kjfwb/student/savePlayRecord?_csrf={csrf}',
        headers=headers_post, data=f'wjid={wjid}&sfgk=0', timeout=10
    )
    return r.status_code == 200 and 'success' in r.text

def download_and_send(wlkcid, wjid, wjlx, save_dir):
    os.makedirs(save_dir, exist_ok=True)
    fname = None

    # 下载
    dl_url = f'https://learn.tsinghua.edu.cn/b/wlxt/kj/wlkc_kjxxb/student/downloadFile?wlkcid={wlkcid}&wjid={wjid}&sfgk=0'
    r = requests.get(dl_url, headers=headers, timeout=60)

    # 取文件名（从bt字段，wjlx传进来）
    # 构造输出路径
    out_path = os.path.join(save_dir, f'temp_kj.{wjlx}')

    if r.status_code == 200 and len(r.content) > 10000:
        with open(out_path, 'wb') as fp:
            fp.write(r.content)
        print(f'下载完成: {len(r.content):,} bytes')

        # 标记已读
        if mark_kj_read(wjid):
            print('已标记已读')
        else:
            print('标记失败（继续）')

        # 打印 <qqmedia> 标签（供 AI 直接回复用户）
        print(f'\n<qqmedia>{out_path}</qqmedia>')

        # 精准删除
        if os.path.exists(out_path):
            os.remove(out_path)
            print(f'已删除: {out_path}')
    else:
        print(f'下载失败: {r.status_code}')

if __name__ == '__main__':
    # 命令行参数：wlkcid wjid wjlx save_dir
    if len(sys.argv) >= 5:
        wlkc_id = sys.argv[1]
        wjid = sys.argv[2]
        wjlx = sys.argv[3]
        save_dir = sys.argv[4]
        download_and_send(wlkc_id, wjid, wjlx, save_dir)
    else:
        print('用法: python download_and_send_kj.py <wlkcid> <wjid> <wjlx> <save_dir>')