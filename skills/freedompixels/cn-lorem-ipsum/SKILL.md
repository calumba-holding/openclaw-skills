# cn-lorem-ipsum - 随机文本生成器

纯 Python 标准库实现的 Lorem Ipsum 随机文本生成工具。

## 功能

- **单词生成**：生成指定数量的随机单词
- **句子生成**：生成指定数量的完整句子
- **段落生成**：生成指定数量的段落
- **固定种子**：支持 `secrets` 模块随机种子（安全随机）

## 使用方式

```bash
# 生成 10 个随机单词
python3 cn_lorem_ipsum.py words 10

# 生成 5 个完整句子
python3 cn_lorem_ipsum.py sentences 5

# 生成 3 个段落
python3 cn_lorem_ipsum.py paragraphs 3

# 指定种子（可复现）
python3 cn_lorem_ipsum.py words 20 --seed 42

# 指定最小/最大单词数
python3 cn_lorem_ipsum.py words 50 --min 3 --max 12

# 中文模式（中文占位文本）
python3 cn_lorem_ipsum.py words 10 --lang zh
```

## 技术说明

- 纯 Python 标准库（`secrets`、`argparse`、`random`）
- 默认使用 `secrets.choice` 作为随机源（安全随机）
- 可选 `random` 配合种子实现可复现结果
- 支持中英文占位文本
