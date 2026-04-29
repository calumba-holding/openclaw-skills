import json, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

state = json.load(open(r'C:\Users\TOM\.openclaw\workspace\skills\tsinghua-learn\sessions\learn_session.json', encoding='utf-8'))
csrf = state['csrf']; js = state['learn_jsession']
h = {'Accept': 'application/json, */*', 'X-XSRF-TOKEN': csrf, 'Cookie': 'JSESSIONID=' + js + '; XSRF-TOKEN=' + csrf}

# 未做问卷（全局，不是按课程）
body = 'aoData=%5B%7B%22name%22%3A%22iDisplayStart%22%2C%22value%22%3A0%7D%2C%7B%22name%22%3A%22iDisplayLength%22%2C%22value%22%3A100%7D%5D'

r = requests.post(
    'https://learn.tsinghua.edu.cn/b/wlxt/kcwj/wlkc_wjb/student/pageListWks?_csrf=' + csrf,
    headers={**h, 'Content-Type': 'application/x-www-form-urlencoded'},
    data=body, timeout=15
)
d = r.json()
obj = d.get('object', d)
items = obj.get('aaData', []) if isinstance(obj, dict) else []
print(f'未做问卷总数: {len(items)}')
for x in items:
    wlkcid = x.get('wlkcid', '')
    wjbt = x.get('bt', '?')
    wjsj = x.get('jzsjStr', '')
    print(f'  [{wlkcid}] {wjbt[:40]} | 截止:{wjsj}')

print()
# 看看有没有 wlkcid 字段可以区分课程
if items:
    print('字段列表:', list(items[0].keys()))
    print('wlkcid 示例:', items[0].get('wlkcid'))