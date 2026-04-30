#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag

EXTRACTOR = Path(__file__).resolve().with_name('extract.js')
SKILL_DIR = EXTRACTOR.parent.parent
IMA_BASE = 'https://ima.qq.com/openapi/note/v1'


def load_local_env():
    env_path = SKILL_DIR / '.env'
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[len('export '):].strip()
        if '=' not in line:
            continue
        key, value = line.split('=', 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_local_env()


def fail(msg, code=1):
    print(json.dumps({'ok': False, 'error': msg}, ensure_ascii=False))
    raise SystemExit(code)


def check_env():
    missing = [k for k in ['IMA_OPENAPI_CLIENTID', 'IMA_OPENAPI_APIKEY'] if not os.environ.get(k)]
    if missing:
        fail(f"missing env: {', '.join(missing)}", 2)
    if not EXTRACTOR.exists():
        fail(f'extractor not found in skill: {EXTRACTOR}', 3)


def run_extract(url: str):
    js = f"""
const fs = require('fs');
const {{ extract }} = require('{EXTRACTOR.as_posix()}');
(async () => {{
  const result = await extract({json.dumps(url)}, {{
    shouldReturnContent: true,
    shouldReturnRawMeta: false,
    shouldFollowTransferLink: true,
    shouldExtractMpLinks: true,
    shouldExtractTags: true,
    shouldExtractRepostMeta: true,
  }});
  process.stdout.write(JSON.stringify(result));
}})().catch(err => {{
  console.error(err);
  process.exit(1);
}});
"""
    res = subprocess.run(['node', '-e', js], capture_output=True, text=True)
    if res.returncode != 0:
        fail(res.stderr.strip() or 'extract failed', 4)
    try:
        obj = json.loads(res.stdout)
    except Exception as e:
        fail(f'invalid extractor output: {e}', 5)
    if not obj.get('done'):
        fail(obj.get('msg') or f"extract failed code={obj.get('code')}", 6)
    return obj['data']


def text_of(node):
    return ' '.join(node.stripped_strings).strip()


def code_text_of(node):
    # Preserve code/newline structure instead of collapsing whitespace.
    return node.get_text('\n', strip=False).strip('\n')


def is_code_block(node):
    if not isinstance(node, Tag):
        return False
    name = node.name.lower()
    classes = ' '.join(node.get('class') or []).lower()
    style = (node.get('style') or '').lower()
    return (
        name in ['pre', 'code']
        or 'code' in classes
        or 'code-snippet' in classes
        or 'monospace' in style
        or 'font-family: monospace' in style
    )


def append_code_block(lines, node):
    code = code_text_of(node)
    if code:
        lines += ['```', code, '```', '']
    return lines


def build_markdown(data: dict):
    html = data.get('msg_content') or ''
    soup = BeautifulSoup(html, 'html.parser')
    lines = [
        f"# {data.get('msg_title', '未命名文章')}",
        '',
        f"> **作者**: {data.get('msg_author') or '未知'}  ",
        f"> **公众号**: {data.get('account_name') or '未知'}  ",
        f"> **发布时间**: {data.get('msg_publish_time_str') or '未知'}  ",
        f"> **原文链接**: {data.get('msg_link') or ''}",
        '',
        '---',
        ''
    ]

    body_img_count = 0
    seen = set()

    for node in soup.children:
        if isinstance(node, NavigableString):
            t = str(node).strip()
            if t:
                lines += [t, '']
            continue
        if not isinstance(node, Tag):
            continue
        name = node.name.lower()
        if is_code_block(node):
            append_code_block(lines, node)
            continue
        if name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            title = text_of(node)
            if title:
                lines += ['#' * int(name[1]) + ' ' + title, '']
            continue
        if name in ['p', 'section', 'div']:
            # Preserve nested code blocks before collapsing normal prose text.
            code_nodes = [c for c in node.find_all(['pre', 'code'], recursive=True) if is_code_block(c)]
            for c in code_nodes:
                append_code_block(lines, c)
                c.decompose()
            txt = text_of(node)
            if txt:
                lines += [txt, '']
            for img in node.find_all('img', recursive=True):
                src = img.get('data-src') or img.get('src')
                if src and src not in seen:
                    seen.add(src)
                    body_img_count += 1
                    lines += [f'![]({src})', '']
            for a in node.find_all('a', recursive=True):
                href = a.get('href')
                title = text_of(a)
                if href and title and title != txt:
                    lines += [f'- [{title}]({href})', '']
            continue
        if name == 'img':
            src = node.get('data-src') or node.get('src')
            if src and src not in seen:
                seen.add(src)
                body_img_count += 1
                lines += [f'![]({src})', '']
            continue
        if name == 'a':
            href = node.get('href')
            title = text_of(node)
            if href and title:
                lines += [f'- [{title}]({href})', '']

    cover = data.get('msg_cover')
    cover_used = False
    if body_img_count == 0 and cover:
        cover_used = True
        lines = lines[:9] + [f'![]({cover})', ''] + lines[9:]

    cleaned = []
    blank = False
    for line in lines:
        if line == '':
            if not blank:
                cleaned.append(line)
            blank = True
        else:
            cleaned.append(line)
            blank = False
    md = '\n'.join(cleaned).strip() + '\n'
    return md, body_img_count, cover_used


def ima_post(endpoint: str, payload: dict):
    req = urllib.request.Request(
        f'{IMA_BASE}/{endpoint}',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'ima-openapi-clientid': os.environ['IMA_OPENAPI_CLIENTID'],
            'ima-openapi-apikey': os.environ['IMA_OPENAPI_APIKEY'],
            'Content-Type': 'application/json',
        },
        method='POST'
    )
    with urllib.request.urlopen(req) as resp:
        raw = resp.read().decode('utf-8')
    obj = json.loads(raw)
    if obj.get('code') != 0:
        fail(f"IMA {endpoint} failed: {obj.get('msg')}", 7)
    return obj


def main():
    if len(sys.argv) != 2:
        fail('usage: save_wechat_to_ima.py <mp.weixin.qq.com url>', 9)
    url = sys.argv[1].strip()
    check_env()
    data = run_extract(url)
    md, body_img_count, cover_used = build_markdown(data)
    safe = data.get('msg_sn') or 'wechat_article'
    md_path = Path(tempfile.gettempdir()) / f'wechat_{safe}_inline.md'
    md_path.write_text(md, encoding='utf-8')

    imported = ima_post('import_doc', {'content_format': 1, 'content': md})
    note_id = imported['data']['note_id']
    readback = ima_post('get_doc_content', {'doc_id': note_id, 'target_content_format': 0})
    content = readback.get('data', {}).get('content', '')

    print(json.dumps({
        'ok': True,
        'title': data.get('msg_title'),
        'account': data.get('account_name'),
        'author': data.get('msg_author'),
        'publish_time': data.get('msg_publish_time_str'),
        'body_img_count': body_img_count,
        'cover_used': cover_used,
        'markdown_path': str(md_path),
        'note_id': note_id,
        'readback_ok': bool(content.strip()),
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
