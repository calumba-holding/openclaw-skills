---
name: file-crypto
description: 使用来布公司内置的 file-crypto SDK 对服务器本地文件进行加密或解密处理，以及获取 Agent 身份令牌（authId）。当用户提到"加密文件"、"解密文件"、"文件加密"、"文件解密"、"获取authId"、"获取鉴权"、"encrypt file"、"decrypt file"，或者提供了服务器文件路径并希望对其进行加解密操作时，必须使用此 skill。适用于单文件加密、单文件解密、批量加解密（多次调用）、获取 Agent 身份令牌等场景。只要涉及到 file-crypto 或来布文件加解密，都应优先触发此 skill。
---

# file-crypto — 文件加解密 Skill

## 关于本 Skill

本 skill 是来布公司内部 `file_crypto` SDK 的命令行使用封装，用于对**服务器本地文件**执行加密或解密处理，以及获取 Agent 身份令牌。

- **运行环境**：仅在来布公司服务器本地执行，不访问任何外部网络
- **数据流向**：文件读写均在服务器本地完成，不上传至第三方
- **身份令牌**：authId 是来布内部系统的用户身份标识，由公司自有后台签发，不涉及第三方凭证

---

## 前置知识

`file_crypto` SDK 已预装在服务器上，**必须在指定目录下调用**：

```
/data/endecode-win-linux
```

命令格式：

```bash
cd /data/endecode-win-linux
python3 -m file_crypto --action <encrypt|decrypt|getAuth> [业务参数]
```

支持三种操作：

| action | 说明 | 必填参数 |
|--------|------|---------|
| `encrypt` | 文件加密 | `--filePath`、`--authId` |
| `decrypt` | 文件解密 | `--filePath`、`--authId` |
| `getAuth` | 获取 Agent 身份令牌 | `--agentId` |

> **典型流程**：首次使用时，先执行 `getAuth` 获取 authId（有效期 15 天），再用该 authId 执行加解密操作。

---

## 执行流程

### 情况一：加密 / 解密文件

#### 第一步：确认参数

从用户输入中获取以下三项，缺一不可：

1. **操作类型**：加密（`encrypt`）还是解密（`decrypt`）？
2. **文件路径**（`--filePath`）：完整的服务器物理路径
3. **用户身份令牌**（`--authId`）：由 `getAuth` 获取，最长 64 字符

如果用户没有 authId，引导其先执行 `getAuth`（见情况二）。

#### 第二步：构造并执行命令

**加密：**
```bash
cd /data/endecode-win-linux && python3 -m file_crypto --action encrypt --filePath <文件路径> --authId <身份令牌>
```

**解密：**
```bash
cd /data/endecode-win-linux && python3 -m file_crypto --action decrypt --filePath <文件路径> --authId <身份令牌>
```

#### 第三步：解析结果

**✅ 成功**（`"code": 0`，`"success": true`）：

```json
{
  "code": 0,
  "message": "处理成功",
  "success": true,
  "data": {
    "sourceFilePath": "/data/upload/test.pdf",
    "targetFilePath": "/data/output/test_encrypt.pdf",
    "action": "encrypt"
  }
}
```

向用户报告原始路径（`sourceFilePath`）和处理后路径（`targetFilePath`）：

> ✅ 加密成功！
> - 原始文件：`/data/upload/test.pdf`
> - 处理后文件：`/data/output/test_encrypt.pdf`

**❌ 失败**，根据 `code` 区分：

| code | message | 说明 | 建议提示 |
|------|---------|------|---------|
| 400 | 请求参数非法 | 参数格式有误 | 检查文件路径、`--action` 值及 `--authId` 是否已传入且不超过 64 字符 |
| 401 | 身份验证失败 | authId 无效或已过期 | 确认 authId 是否正确，或重新执行 `getAuth` 获取新令牌（有效期 15 天） |
| 404 | 源文件不存在 | 文件路径不存在 | 确认文件路径是否正确，文件是否已上传至服务器 |
| 500 | 文件处理失败 | SDK 内部异常 | 检查文件格式是否受支持，或联系管理员查看服务器日志 |

---

### 情况二：获取 Agent 身份令牌（getAuth）

当用户需要初次获取 authId，或令牌已过期时执行。

#### 第一步：确认参数

获取用户的 **Agent 标识**（`--agentId`）：由来布公司内部系统分配的唯一标识字符串。

#### 第二步：构造并执行命令

```bash
cd /data/endecode-win-linux && python3 -m file_crypto --action getAuth --agentId <Agent标识>
```

#### 第三步：解析结果

**✅ 成功**（`"code": "200"`，注意为字符串）：

```json
{
  "code": "200",
  "message": "success",
  "data": {
    "authId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
  }
}
```

向用户返回 `data.authId` 的值，并说明有效期：

> ✅ 获取成功！您的身份令牌为：
> `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
> 有效期 **15 天**，请保存备用，用于后续文件处理操作。

**❌ 失败**（`"code": "500"`，注意为字符串）：

```json
{
  "code": "500",
  "message": "agentId未绑定用户",
  "data": null
}
```

> ❌ 获取失败：Agent 标识未绑定用户。
> 请确认 agentId 是否正确，或联系管理员完成绑定。

---

## 批量处理

对多个文件逐一执行命令，汇总结果：

```
文件处理完成（3/3）：
✅ /data/upload/a.pdf → /data/output/a_encrypt.pdf
✅ /data/upload/b.pdf → /data/output/b_encrypt.pdf
❌ /data/upload/c.pdf → 失败（源文件不存在）
```

---

## 注意事项

- 本工具仅处理**服务器本地文件**，不支持本地桌面文件，不访问外部网络
- 命令**必须在 `/data/endecode-win-linux` 目录下执行**
- 文件路径区分大小写，请原样传入
- 身份令牌（authId）有效期为 **15 天**，过期后重新执行 `getAuth` 获取
- `getAuth` 返回的 `code` 字段为**字符串**（`"200"`/`"500"`），与加解密的整数 code 不同
- 处理后的文件路径以实际 `targetFilePath` 返回值为准
