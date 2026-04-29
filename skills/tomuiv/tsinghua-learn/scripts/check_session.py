import json, requests

f = r'C:\Users\TOM\.openclaw\workspace\skills\tsinghua-learn\sessions\learn_session.json'
s = json.load(open(f, encoding='utf-8'))
print('csrf:', s['csrf'])

h = {
    'Accept': 'application/json, */*',
    'Referer': 'https://learn.tsinghua.edu.cn/f/wlxt/index/course/student/',
    'X-XSRF-TOKEN': s['csrf'],
    'Cookie': 'JSESSIONID=' + s['learn_jsession'] + '; XSRF-TOKEN=' + s['csrf'],
}
r = requests.get('https://learn.tsinghua.edu.cn/b/wlxt/kczy/zy/student/index/zyListWj?wlkcid=&size=1', headers=h, timeout=10)
print('status:', r.status_code)
print('has location.href:', 'location.href' in r.text)
print('body[:300]:', r.text[:300])