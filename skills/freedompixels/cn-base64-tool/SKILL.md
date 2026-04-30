# cn-base64-tool - Base64 编解码工具

纯 Python 标准库实现的 Base64 编解码工具。

## 功能

- **编码**：将字符串或文件内容编码为 Base64
- **解码**：将 Base64 字符串还原为原始内容
- **文件支持**：支持对文件进行 Base64 编码/解码

## 使用方式

```bash
# 编码字符串
python3 cn_base64_tool.py encode "Hello World"

# 解码 Base64 字符串
python3 cn_base64_tool.py decode "SGVsbG8gV29ybGQ="

# 编码文件
python3 cn_base64_tool.py encode_file input.png

# 解码文件
python3 cn_base64_tool.py decode_file output.b64 output.png

# 批量编码（目录）
python3 cn_base64_tool.py encode_dir ./my_folder
```

## 技术说明

- 纯 Python 标准库（`base64`、`argparse`）
- 无外部依赖
- 支持 UTF-8 字符串
