import os
import re
import socket
import logging
import subprocess
import tempfile
from pathlib import Path, PurePath
from urllib.parse import urlparse
from ipaddress import ip_address, ip_network, IPv6Address

logger = logging.getLogger(__name__)

_PRIVATE_IP_RANGES = (
    '0.0.0.0/8',
    '10.0.0.0/8',
    '127.0.0.0/8',
    '169.254.0.0/16',
    '172.16.0.0/12',
    '192.168.0.0/16',
)

def _is_private_ip(ip_str: str) -> bool:
    try:
        ip = ip_address(ip_str)
        if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_unspecified:
            return True
        if isinstance(ip, IPv6Address):
            if ip.ipv4_mapped and _is_private_ip(str(ip.ipv4_mapped)):
                return True
            if ip in ip_network('::ffff:0:0/96'):
                return True
            if ip in ip_network('64:ff9b::/96'):
                return True
        for cidr in _PRIVATE_IP_RANGES:
            if ip in ip_network(cidr):
                return True
    except ValueError:
        pass
    except TypeError:
        pass
    return False


def validate_video_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"禁止的协议: '{parsed.scheme}'，仅允许 http/https")

    host = parsed.hostname
    if not host:
        raise ValueError(f"无效的 URL，缺少主机名: {url[:80]}")
    if host.startswith('[') and host.endswith(']'):
        host = host[1:-1]

    raw_host = host
    host = host.lower()

    if any(ord(c) > 127 for c in raw_host):
        raise ValueError(f"禁止使用非 ASCII 字符的域名 (IDN 同形字攻击): {raw_host}")
    if 'xn--' in host:
        raise ValueError(f"禁止使用 Punycode 编码的域名: {raw_host}")

    try:
        ip = ip_address(host)
        if _is_private_ip(str(ip)):
            raise ValueError(f"禁止访问私有/内网 IP 地址: {host}")
        return
    except ValueError as e:
        if '禁止' in str(e):
            raise
        pass

    if re.match(r'^127\.\d+\.\d+\.\d+$', host):
        raise ValueError(f"禁止访问回环地址: {host}")
    if re.match(r'^10\.\d+\.\d+\.\d+$', host):
        raise ValueError(f"禁止访问内网地址: {host}")
    if re.match(r'^172\.(1[6-9]|2\d|3[01])\.\d+\.\d+$', host):
        raise ValueError(f"禁止访问内网地址: {host}")
    if re.match(r'^192\.168\.\d+\.\d+$', host):
        raise ValueError(f"禁止访问内网地址: {host}")
    if re.match(r'^169\.254\.\d+\.\d+$', host):
        raise ValueError(f"禁止访问链路本地地址: {host}")

    try:
        addrs = socket.getaddrinfo(host, 80, type=socket.SOCK_STREAM)
        seen = set()
        for addr in addrs:
            ip_str = addr[4][0]
            if ip_str in seen:
                continue
            seen.add(ip_str)
            if _is_private_ip(ip_str):
                raise ValueError(f"DNS 解析到私有/内网 IP: {host} -> {ip_str}")
    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"DNS 解析失败，无法验证目标地址安全性: {e}")

_FORBIDDEN_OUTPUT_NAMES = frozenset({
    'CON', 'PRN', 'AUX', 'NUL',
    'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
    'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
})

def sanitize_output_path(output_path: str, default_dir: str = '.') -> str:
    p = Path(output_path)
    parts = p.parts
    if any(part == '..' for part in parts):
        raise ValueError(f"禁止路径穿越 (..): {output_path}")
    stem = PurePath(p).name
    name_without_ext = Path(stem).stem.upper()
    if name_without_ext in _FORBIDDEN_OUTPUT_NAMES:
        raise ValueError(f"禁止使用系统保留文件名: {stem}")
    resolved = p.resolve()
    cwd = Path(default_dir).resolve()
    if not str(resolved).startswith(str(cwd)):
        raise ValueError(f"输出路径超出工作目录: {output_path}")
    return str(resolved)

def get_file_size_mb(path: str) -> float:
    return Path(path).stat().st_size / (1024 * 1024)

def download_video_to_temp(url: str, timeout: int = 300) -> str:
    validate_video_url(url)
    import requests
    temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
    temp_path = temp_file.name
    temp_file.close()
    
    response = requests.get(url, stream=True, timeout=timeout)
    with open(temp_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return temp_path

def cleanup_temp_file(path: str):
    """清理临时文件"""
    if path and os.path.exists(path):
        os.unlink(path)