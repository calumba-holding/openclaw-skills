# cn-emoji-translator

Emoji 翻译器。文本转 emoji 表情，emoji 转文字描述。

## 功能

- 文本 → Emoji 表情（关键词替换）
- Emoji → 文字描述
- 支持中英文混合
- 纯本地处理，无需API

## 安装要求

- Python 3.6+
- 无外部依赖（使用内置 emoji 库或自定义映射）

## 使用方法

```
千策，把这段翻译成emoji：今天天气真好
千策，这个emoji是什么意思：🎉
```

## 参数

- `text`: 要翻译的文本
- `direction`: 翻译方向 (text2emoji / emoji2text)，默认 text2emoji

## 示例

输入：
```
千策，把这段转成emoji：我爱吃苹果
```

输出：
```
我❤️🍎
```

## 分类

趣味

## 关键词

emoji, 表情, 翻译, emoji translator, 表情包
