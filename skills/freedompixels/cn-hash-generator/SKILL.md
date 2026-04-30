---
slug: cn-hash-generator
name: Hash生成器
description: "Hash生成器工具。支持MD5/SHA-1/SHA-256/SHA-512/BLAKE2b哈希、Base64编解码、UUID生成、HMAC签名。纯Python标准库，无需API Key。"
keywords: hash, MD5, SHA256, Base64, UUID, HMAC, 哈希, 校验, 签名
version: "1.0.0"
author: 千策
---

# Hash生成器

多功能Hash工具，支持哈希生成、Base64编解码、UUID生成、HMAC签名。纯Python标准库实现，无需API Key。

## 功能

- **哈希生成**：MD5、SHA-1、SHA-256、SHA-512、BLAKE2b
- **Base64**：编码和解码
- **UUID**：随机UUID生成
- **HMAC签名**：密钥+消息签名
- 纯标准库（hashlib + uuid + base64），零依赖

## 使用示例

```
计算"Hello World"的SHA256
生成一个UUID
Base64编码"你好"
HMAC签名 消息"test" 密钥"key"
```

## 技术实现

调用 `scripts/cn_hash_generator.py`，支持参数：
- `--algo`：算法选择（md5/sha1/sha256/sha512/blake2）
- `--encode64`：Base64编码
- `--decode`：Base64解码
- `--uuid`：生成UUID
- `--hmac KEY`：HMAC签名
- `--upper`：输出大写
- `--count N`：UUID生成数量

## 注意事项

- Hash是单向的，不可逆
- MD5和SHA-1不建议用于安全场景
- 密码存储建议使用bcrypt而非简单Hash
