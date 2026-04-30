import argparse
import json
import os
import re
import urllib.request
import urllib.error

API_BASE_URL = "https://apps.ddguanhuai.com/customize-php/lejian"

# Token 配置：从环境变量 SMS_AUTH_TOKEN 读取
def get_token():
    return os.environ.get("SMS_AUTH_TOKEN", "")

AUTH_TOKEN = get_token()

def make_request(url, data=None):
    if not AUTH_TOKEN:
        return {"code": 400, "message": "未配置环境变量 SMS_AUTH_TOKEN，请先运行 openclaw config set env.vars.SMS_AUTH_TOKEN <你的token>"}

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }

    try:
        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
        else:
            req = urllib.request.Request(url, headers=headers, method="GET")

        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            error_data = json.loads(e.read().decode("utf-8"))
            return error_data
        except:
            return {"code": e.code, "message": f"HTTP错误: {e.code}"}
    except urllib.error.URLError as e:
        return {"code": 500, "message": f"网络错误: {str(e)}"}
    except Exception as e:
        return {"code": 500, "message": f"未知错误: {str(e)}"}

def get_verify_code(mobile, debug=False):
    url = f"{API_BASE_URL}/SmsRecord/verifyCode"
    data = {"mobile": mobile}
    
    if debug:
        print(f"[DEBUG] 请求URL: {url}")
        print(f"[DEBUG] 请求手机号: {mobile[:4]}****{mobile[-4:]}")
    
    result = make_request(url, data)
    
    if debug:
        print(f"[DEBUG] 响应状态: {result.get('code', 'N/A')}")
    
    return result

def format_verify_code_result(result):
    if result.get("code") != 200:
        print(f"查询失败: {result.get('message', '未知错误')}")
        return False
    
    data = result.get("data", {})
    
    # 优先用 verify_code 字段，若为空则从短信内容中提取
    verify_code = data.get('verify_code')
    if not verify_code:
        sms_content = data.get('sms_content', '')
        code_match = re.search(r'验证码[是为：:]*(\d{4,8})', sms_content)
        verify_code = code_match.group(1) if code_match else 'N/A'
    
    print("========================================")
    print("           短信验证码查询结果              ")
    print("========================================")
    print(f"手机号: {data.get('mobile', 'N/A')}")
    print(f"验证码: {verify_code}")
    print(f"短信内容: {data.get('sms_content', 'N/A')}")
    print(f"发送时间: {data.get('insert_time', 'N/A')}")
    print("========================================")
    print("=== 查询完成 ===")
    return True

def main():
    parser = argparse.ArgumentParser(description="短信验证码查询工具")
    parser.add_argument("mobile", help="手机号")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    print(f"查询手机号: {args.mobile}")
    
    if args.debug:
        print("启用调试模式...")
    
    result = get_verify_code(args.mobile, args.debug)
    format_verify_code_result(result)

if __name__ == "__main__":
    main()
