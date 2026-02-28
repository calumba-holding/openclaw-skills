#!/usr/bin/env python3
"""SSL连接辅助模块 - 139邮箱兼容模式"""

import ssl

def create_ssl_context():
    """
    创建SSL上下文（139邮箱兼容模式）
    
    由于139邮箱服务器使用较旧版本的TLS协议，需要使用兼容模式连接。
    注意：此模式降低了SSL安全性，建议仅在受信任网络中使用。
    
    Returns:
        SSL上下文对象
    """
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.set_ciphers('DEFAULT:@SECLEVEL=1')
    return context
