import json, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

state = json.load(open(r'C:\Users\TOM\.openclaw\workspace\skills\tsinghua-learn\sessions\learn_session.json', encoding='utf-8'))
csrf = state['csrf']; js = state['learn_jsession']
h = {'Accept': 'application/json, */*', 'X-XSRF-TOKEN': csrf, 'Cookie': 'JSESSIONID=' + js + '; XSRF-TOKEN=' + csrf}

# 测试问卷 API（POST，Form Data 格式）
# pageListWks = 未做问卷，pageListWys = 已做问卷
import urllib.parse

# 未做问卷
params = {
    'aoData[0][name]': 'iDisplayStart',
    'aoData[0][value]': 0,
    'aoData[1][name]': 'iDisplayLength',
    'aoData[1][value]': 100,
}
body = urllib.parse.urlencode(params)
r1 = requests.post(
    'https://learn.tsinghua.edu.cn/b/wlxt/kcwj/wlkc_wjb/student/pageListWks?_csrf=' + csrf,
    headers={**h, 'Content-Type': 'application/x-www-form-urlencoded'},
    data=body, timeout=15
)
print('=== 未做问卷 ===')
print('status:', r1.status_code)
d1 = r1.json()
obj1 = d1.get('object', d1)
if isinstance(obj1, dict):
    items1 = obj1.get('aaData', [])
elif isinstance(obj1, list):
    items1 = obj1
else:
    items1 = []
print(f'未做问卷总数: {len(items1)}')
for x in items1[:3]:
    print(f'  {x.get("bt","?")[:40]} | wjid={x.get("wjid","?")[:20]}')

# 已做问卷
r2 = requests.post(
    'https://learn.tsinghua.edu.cn/b/wlxt/kcwj/wlkc_wjb/student/pageListWys?_csrf=' + csrf,
    headers={**h, 'Content-Type': 'application/x-www-form-urlencoded'},
    data=body, timeout=15
)
print('\n=== 已做问卷 ===')
print('status:', r2.status_code)
d2 = r2.json()
obj2 = d2.get('object', d2)
if isinstance(obj2, dict):
    items2 = obj2.get('aaData', [])
elif isinstance(obj2, list):
    items2 = obj2
else:
    items2 = []
print(f'已做问卷总数: {len(items2)}')
for x in items2[:3]:
    print(f'  {x.get("bt","?")[:40]} | wjid={x.get("wjid","?")[:20]}')

# 也测试下对每门课程分别查问卷
print('\n=== 各课程的问卷情况 ===')
courses = {
    '2025-2026-2151368648': '大学物理A(1)',
    '2025-2026-2151369314': '概率论',
    '2025-2026-2151369343': '英语听说交流(A)',
    '2025-2026-2151368819': '写作与沟通',
    '2025-2026-2151368584': '微积分A(2)',
}
for wlkcid, name in courses.items():
    r = requests.get(
        f'https://learn.tsinghua.edu.cn/b/wlxt/kcwj/wlkc_wjb/student/pageListWks?wlkcid={wlkcid}&size=20&_csrf={csrf}',
        headers=h, timeout=10
    )
    try:
        d = r.json()
        obj = d.get('object', d)
        items = (obj.get('aaData', []) if isinstance(obj, dict) else (obj if isinstance(obj, list) else []))
        print(f'  {name} 未做: {len(items)} 项')
    except:
        print(f'  {name} API 无响应或格式异常')