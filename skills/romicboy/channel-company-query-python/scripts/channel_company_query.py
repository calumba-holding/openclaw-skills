import argparse
import json
import os
import urllib.request
import urllib.error
API_BASE_URL = "https://apps.ddguanhuai.com/customize-php/lejian"
AUTH_TOKEN = os.environ.get("LEJIAN_AUTH_TOKEN", "")

def make_request(url, data=None):
    if not AUTH_TOKEN:
        print("错误：未配置环境变量 LEJIAN_AUTH_TOKEN，请先运行 openclaw config set env.vars.LEJIAN_AUTH_TOKEN <你的token>")
        return None
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
        error_body = e.read().decode("utf-8") if e.fp else ""
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Response body: {error_body}")
        return None
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def search_channel_companies(name):
    url = f"{API_BASE_URL}/channelCompany/search"
    data = {"name": name}
    return make_request(url, data)


def get_channel_company_detail(company_id):
    url = f"{API_BASE_URL}/channelCompany/detail?id={company_id}"
    data = {"id": company_id}
    return make_request(url, data)


def format_search_results(results):
    if not results or results.get("code") != 200:
        msg = results.get("message", "查询失败") if results else "请求失败"
        print(f"查询失败: {msg}")
        return []

    data = results.get("data", [])
    if not data:
        print("未找到匹配的渠道单位")
        return []

    if len(data) == 1:
        company_id = data[0].get('id')
        print(f"\n仅找到一个渠道单位，自动查询详情 (ID: {company_id})...")
        detail_result = get_channel_company_detail(company_id)
        format_company_detail(detail_result)
        return data

    print(f"\n找到 {len(data)} 个渠道单位:\n")
    print("-" * 70)
    print(f"{'序号':<6}{'ID':<12}{'名称':<40}{'组织ID':<10}")
    print("-" * 70)

    for i, item in enumerate(data, 1):
        print(f"{i:<6}{item.get('id', ''):<12}{item.get('name', ''):<40}{item.get('organization_id', ''):<10}")

    print("-" * 70)
    return data


def format_company_detail(result):
    if not result or result.get("code") != 200:
        msg = result.get("message", "查询失败") if result else "请求失败"
        print(f"查询失败: {msg}")
        return

    data = result.get("data", {})
    if not data:
        print("未找到渠道单位详情")
        return

    print("\n" + "=" * 50)
    print("           渠道单位详细信息           ")
    print("=" * 50)
    print(f"渠道单位ID: {data.get('id', 'N/A')}")
    print(f"渠道单位名称: {data.get('name', 'N/A')}")
    print(f"渠道ID: {data.get('channel_id', 'N/A')}")
    print(f"渠道名称: {data.get('channel_name', 'N/A')}")
    print(f"CRM手机号: {data.get('crm_mobile', 'N/A')}")
    print(f"CRM账号: {data.get('crm_account', 'N/A')}")
    print(f"关联站点ID: {data.get('site_id', 'N/A')}")
    print(f"关联站点标识: {data.get('site_identifier', 'N/A')}")

    env_urls = data.get("environment_urls", {})
    if env_urls:
        print("\n环境URL:")
        print("-" * 50)
        for env_name, env_url in env_urls.items():
            print(f"{env_name}: {env_url}")

    print("=" * 50)
    print("=== 查询完成 ===")


def main():
    parser = argparse.ArgumentParser(description="渠道单位查询工具")
    parser.add_argument("--name", help="渠道单位名称 (模糊搜索)")
    parser.add_argument("--detail", type=int, help="通过ID查询渠道单位详情")

    args = parser.parse_args()

    if args.detail:
        result = get_channel_company_detail(args.detail)
        format_company_detail(result)
        return

    if args.name:
        result = search_channel_companies(args.name)
        format_search_results(result)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
