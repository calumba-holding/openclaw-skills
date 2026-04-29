# CLAWHUB_PUBLISH.md

## 发布信息

| 字段 | 值 |
|------|-----|
| **Slug** | multi-find-skills |
| **名称** | Multi Find Skills（技能搜索全能版） |
| **版本** | 2.6.0 |
| **作者** | wagnzairong |
| **标签** | search, skill, finder, clawhub, skills-sh, openclaw, multi-source |
| **分类** | utilities |

## 描述（ClawHub 展示用）

中文：同时支持 ClawHub 和 skills.sh 两大生态的技能搜索工具，具备质量核验、安装验证和完整生命周期管理功能。支持6个搜索来源。

English: All-in-One Skill Finder for ClawHub and skills.sh ecosystems with quality checks, install verification, and full lifecycle management. Supports 6 search sources.

## 中国区说明

本技能在中国区使用 clawhub mirror 安装：

```bash
clawhub install multi-find-skills --registry https://cn.clawhub-mirror.com
```

或设置默认镜像：

```bash
clawhub config set registry https://cn.clawhub-mirror.com
```

## 依赖说明

本技能依赖以下 CLI 工具：

| 工具 | 安装方式 | 必选 |
|------|---------|------|
| `clawhub` | `npm i -g clawhub` | ✅ |
| `npx` | Node.js 内置 | ✅ |

如在中国区安装 clawhub 遇到问题，请使用镜像站。

## 质量门槛说明

本技能文档中的安装量门槛（≥100 / ≥1,000）和 Stars 门槛（≥5）是经验性指导值，非平台强制校验。实际选择时请结合具体 skill 的更新时间、社区反馈等因素综合判断。

## 功能特性

- **双生态搜索**：ClawHub + skills.sh 6个来源并行
- **质量核验**：安装量门槛 + Stars + 来源声誉
- **安装验证**：安装后自动验证文件存在性
- **安全重跑**：幂等设计，支持 --force 安全重试
- **生命周期管理**：update / uninstall / list
- **输入验证**：关键词长度+危险字符校验

## 支持

- **GitHub Issues**: https://github.com/wangzairong/skills
- **Discord**: https://discord.com/invite/clawd
- **ClawHub**: https://clawhub.ai/skills/multi-find-skills

## 更新日志

### v2.6.0
- 优化：quick-reference.md 全面升级（新增热门技能速查、3个新分类、扩展关键词）
- 优化：匹配 quick-reference.md 关键词移至第1步（理解需求时同步匹配），未匹配则跳过
- 优化：术语统一（搜索词 → 关键词），全流程一致
- 优化：搜索命令速查体现搜索顺序（1️⃣2️⃣3️⃣标注）
- 新增：输出格式中 skills.sh 新增"总安装量/24h安装量/排名"三字段
- 新增：输出格式新增 GitHub 渠道格式（owner/repo + Stars + 安装命令）
- 优化：LobeHub 输出格式改用安装命令替代链接
- 精简：整合 skills.sh 排名机制到推荐优先级判断
- 迁移：搜索技巧、安装命令语法、安装量字段说明移至 sources.md
- 更新：SKILL.md 正文只保留快速参考，详细内容引导至 sources.md

### v2.0.0
- 优化token成本：正文精简，详细内容移至 references/
- 新增生命周期管理：update/uninstall/list 指令
- 新增安全重跑机制：幂等性说明 + --force 安全重跑
- 新增输入验证：关键词长度+危险字符校验
- 触发词扩展到 frontmatter description
- 保留原始完整触发词、工作流、全6来源输出格式
- 补回搜索策略（按功能/提供商/热度）+ 查看详情 Step 3
- 补回核心/集成/Agent技能分类推荐列表
- 补回最佳实践（5条指导原则）

### v1.2.0
- 扩充搜索来源为 6 个独立来源
- 新增"搜索策略"章节（按功能/提供商/热度）
- 新增"最佳实践"、"安装提示"章节

### v1.1.0
- 统一安装路径为 `~/.openclaw/skills/`
- 添加质量门槛标注（可灵活调整）

### v1.0.0
- 双生态搜索（ClawHub + skills.sh）
- 质量核验流程
- 安装验证机制
- 整合自 eaton/find-skills-v2 + fangkelvin/find-skills-skill + guohongbin-git/skill-finder-cn

---

*本文件为 ClawHub 发布专用补充文档，不影响技能核心功能。*
