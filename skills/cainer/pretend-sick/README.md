# Pretend-Sick 🤒 — 帮请病假

> AI推测合理病症 → 生成请假话术 → 指导开证明 → 管理生病状态

生病了只想躺着，请假还要想理由、写话术、找证明？让AI帮你搞定。

## 一句话介绍

告诉AI你想请几天假、哪里不舒服，它帮你推测合理的病症、生成请假消息、告诉去哪开证明。

## 功能

### 🎯 症状推测 + 天数匹配
- 你说"想请3天"，AI推荐病程3天的合理病症
- 1天=轻微不适，3天=中等严重，5天+=需要休养
- 结合你所在城市的季节和疫情，推测更准确

### 📝 请假话术生成
- 根据你的公司/学校生成不同风格的话术
- 支持钉钉、飞书、企微、纸质请假
- 正式版、随意版、带交接版，一键复制

### 🏥 开证明指导
- 优先推荐社区医院（快、便宜、好开）
- 线上问诊备选（微医、好大夫、丁香医生）
- 告诉你要带什么、证明长什么样、盖什么章

### 📊 生病状态管理
- 每日状态记录和追踪
- 提醒可能出现的症状（"明天可能会开始咳嗽，正常"）
- 恢复进度判断

### 📸 图片识别
- 拍照识别喉咙红肿、皮肤红疹、体温计、药品
- 帮你更准确描述症状

## 使用

跟AI对话就行，比如：

```
你：我头疼，想请3天假
AI：[推测病症 + 请假话术 + 开证明方案]
```

```
你：嗓子疼+低烧，在杭州，公司用飞书
AI：[针对性的请假方案 + 附近社区医院 + 飞书请假流程]
```

CLI工具：
```bash
sick-buddy start 感冒        # 建档
sick-buddy symptoms 嗓子疼   # 添加症状
sick-buddy set city 杭州     # 设置城市
sick-buddy set workplace 阿里 # 设置公司
sick-buddy status            # 查看状态
sick-buddy log 今天好多了     # 记录状态
sick-buddy history           # 历史记录
```

## 安装

```bash
# ClawHub安装（推荐）
clawhub install pretend-sick

# 手动安装
git clone https://github.com/Cainer/pretend-sick.git
cp -r pretend-sick ~/.openclaw/workspace/skills/
```

## 适用场景

- 🤒 真的病了，但不知道怎么请假
- 😩 身体不舒服需要休息，想请个合理的假
- 📋 公司要求病假证明，不知道去哪开
- 🤔 不确定自己的症状该请几天

## 文件结构

```
pretend-sick/
├── SKILL.md              # AI行为指南
├── sick-buddy            # CLI工具
├── knowledge/
│   ├── diseases.md       # 常见疾病知识库
│   └── leave-templates.md # 请假话术模板
├── package.json
├── LICENSE
└── README.md
```

## ⚠️ 声明

本工具仅供合理请假参考，不提供医疗诊断。**真的病了请及时就医。**

## License

MIT
