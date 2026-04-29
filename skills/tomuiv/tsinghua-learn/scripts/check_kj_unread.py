import json, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

state = json.load(open(r'C:\Users\TOM\.openclaw\workspace\skills\tsinghua-learn\sessions\learn_session.json', encoding='utf-8'))
csrf = state['csrf']; js = state['learn_jsession']
h = {'Accept': 'application/json, */*', 'X-XSRF-TOKEN': csrf, 'Cookie': 'JSESSIONID=' + js + '; XSRF-TOKEN=' + csrf}

wlkcid = '2025-2026-2151369343'

r = requests.get(f'https://learn.tsinghua.edu.cn/b/wlxt/kj/wlkc_kjxxb/student/kjxxbByWlkcidAndSizeForStudent?wlkcid={wlkcid}&size=100&_csrf={csrf}', headers=h, timeout=15)
d = r.json()

obj = d.get('object', d)
if isinstance(obj, list):
    items = obj
elif isinstance(obj, dict):
    items = obj.get('aaData', [])
else:
    items = []

print(f'课件总数: {len(items)}')
new_items = [x for x in items if str(x.get('isNew','')) == '1']
old_items = [x for x in items if str(x.get('isNew','')) != '1']
print(f'  isNew=1（未读）: {len(new_items)}')
print(f'  isNew=0（已读）: {len(old_items)}')
if old_items:
    print(f'  已读课件示例: {old_items[0].get("bt","?")[:40]}')
if new_items:
    print(f'  未读课件示例: {new_items[0].get("bt","?")[:40]}')