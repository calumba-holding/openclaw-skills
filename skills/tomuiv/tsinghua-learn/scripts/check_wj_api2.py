import json, requests, sys
sys.stdout.reconfigure(encoding='utf-8')

state = json.load(open(r'C:\Users\TOM\.openclaw\workspace\skills\tsinghua-learn\sessions\learn_session.json', encoding='utf-8'))
csrf = state['csrf']; js = state['learn_jsession']
h = {'Accept': 'application/json, */*', 'X-XSRF-TOKEN': csrf, 'Cookie': 'JSESSIONID=' + js + '; XSRF-TOKEN=' + csrf}

# DataTables 格式的 aoData 参数
body = 'aoData=%5B%7B%22name%22%3A%22iDisplayStart%22%2C%22value%22%3A0%7D%2C%7B%22name%22%3A%22iDisplayLength%22%2C%22value%22%3A100%7D%5D'

# 未做问卷
r1 = requests.post(
    'https://learn.tsinghua.edu.cn/b/wlxt/kcwj/wlkc_wjb/student/pageListWks?_csrf=' + csrf,
    headers={**h, 'Content-Type': 'application/x-www-form-urlencoded'},
    data=body, timeout=15
)
print('=== 未做问卷 ===')
print('status:', r1.status_code)
print('body[:200]:', r1.text[:200])

# 已做问卷
r2 = requests.post(
    'https://learn.tsinghua.edu.cn/b/wlxt/kcwj/wlkc_wjb/student/pageListWys?_csrf=' + csrf,
    headers={**h, 'Content-Type': 'application/x-www-form-urlencoded'},
    data=body, timeout=15
)
print('\n=== 已做问卷 ===')
print('status:', r2.status_code)
print('body[:200]:', r2.text[:200])