---
name: multi-find-skills
description: |
  技能搜索全能版 | Multi Find Skills
  触发场景：用户询问"有什么技能可以帮我..."、"找一个能做X的技能"、"有没有技能可以..."、"帮我搜一下XXX相关的技能"、"search for skill"、"找技能"
  功能：三生态(ClawHub+LobeHub+skills.sh)搜索+质量核验+安装验证+生命周期管理
  触发禁用：安装skill用clawhub install、管理已安装用openclaw skills list、创建新skill用skill-creator
author: "wagnzairong (https://github.com/wangzairong)"
evolution:
  created_at: "2026-04-23"
  version: "2.6.0"
  domain: "#engineering"
  success_rate: 0
  parent_skill: ""
  last_used: ""
  use_count: 0
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins: [clawhub]
---

# 🔍 Multi Find Skills（技能搜索全能版）v2.6.0

> 同步支持 **ClawHub**、**LobeHub**、**skills.sh** 三大生态的技能搜索工具，具备质量核验、安装验证与完整生命周期管理。

---

## 触发词

当用户说以下内容时，激活此技能：

- "有什么技能可以帮我..."
- "有没有技能可以..."
- "找一个能做 X 的技能"
- "有没有 X 相关的技能"
- "我需要一个能...的技能"
- "帮我搜一下 XXX 相关的技能"
- "X 有什么技能吗"
- "search for skill"

## 触发判断

### When to Use ✅

- 用户询问"有什么 技能 可以帮我做 X"
- 用户说"找一个能做 Y 的技能"
- 用户询问某个功能是否已有现成的技能
- 用户表示希望扩展能力（如设计、测试、部署等）

### When NOT to Use ❌

- 安装已知名称的技能 → 直接用 `clawhub install <skill-name>`
- 管理已安装的技能 → 用 `openclaw skills list`
- 创建新技能 → 用 `skill-creator`
- 单纯执行与技能搜索无关的任务 → 直接执行

---

## 核心功能

1. **三生态搜索** — ClawHub + LobeHub + skills.sh 多来源
2. **质量核验** — 安装量门槛 + Stars + 来源声誉
3. **安装验证** — 安装后自动验证文件存在性
4. **安全重跑** — 幂等设计，支持 --force 重试
5. **生命周期管理** — update / uninstall / list

---

## 工作流程

### 快速流程

```
用户需求 → 提取关键词 → 全源搜索 → 质量筛选 → 排序输出 → 展示结果 → 提供安装命令 → 安装验证
```

### 详细流程（8步）

```
第1步：理解用户需求
  ├─ 识别领域（React/测试/设计/部署）
  ├─ 识别具体任务（写测试/创建动画/PR审查）
  ├─ 匹配 quick-reference.md 关键词（识别领域关键字，未匹配则跳过）
  └─ 判断是否适合搜索技能

第2步：关键词处理
  ├─ 合并领域 + 具体任务 → 关键词
  └─ 中文 → 翻译成英文

第3步：全源并行搜索
  ├─ skills.sh：npx skills find "<关键词>"
  ├─ ClawHub：clawhub search "<关键词>"
  ├─ LobeHub：npx -y @lobehub/market-cli skills search --q "<关键词>"
  └─ 并行执行，汇总结果

第4步：质量筛选
  ├─ 安装量 <100 → ⚠️
  ├─ Stars < 5 且来源不明 → ⚠️
  └─ 官方/知名厂商 → 🌟 优先

第5步：排序输出
  └─ 按安装量降序

第6步：展示结果（中文格式）
  └─ 名称 + 描述 + 安装量 + 安装命令 + ✅/❌

第7步：提供安装命令
  └─ 根据来源提供对应命令

第8步：安装后验证
  └─ ls ~/.openclaw/skills/<skill-name>/SKILL.md
```

---

## 搜索命令速查

| 来源 | 命令 | 说明 |
|------|------|------|
| skills.sh | `npx skills find "<关键词>"` | 1️⃣ 首选，质量高更新快 |
| ClawHub | `clawhub search "<关键词>"` | 2️⃣ 次选，官方生态质控严 |
| ClawHub 热门 | `clawhub explore --sort installs --limit 20` | 按安装量浏览热门 |
| LobeHub | `npx -y @lobehub/market-cli skills search --q "<关键词>"` | 3️⃣ 补充，社区贡献丰富 |
| OpenClaw Directory | https://www.openclawdirectory.dev/skills | 网页分类浏览 |
| GitHub | 网页搜索 `site:github.com "openclaw skill"` | 补充来源，手动筛选 |

**搜索顺序**：skills.sh → ClawHub → LobeHub → GitHub

**超时处理**：单个来源超时 → 继续其他来源；所有超时 → 建议手动访问网站。

详见 `references/sources.md`（含搜索技巧、skills.sh 详细说明）

---

## 质量核验

### 安装量门槛

| 等级 | 安装量 | 说明 |
|------|--------|------|
| 🌟 优先推荐 | ≥1,000 | 成熟度高，社区验证充分 |
| ✅ 最低门槛 | ≥100 | 可用，需提示风险 |
| ⚠️ 谨慎使用 | <100 | 社区验证有限 |

**硬性门槛**：Stars ≥ 5，有明确作者/来源

### 推荐优先级

1. 🌟 官方/知名厂商 + 高安装量（≥100K 顶级，≥10K 热门）
   - vercel-labs、anthropics、microsoft、openclaw 有例行安全审计
2. ✅ 社区技能，安装量 ≥1K，有明确作者
3. ⚠️ 安装量 <100 或来源不明，慎用

> skills.sh 安装量基于匿名遥测数据（用户安装时自动上报），详见 `references/sources.md`

---

## 安装命令

| 来源 | 命令 |
|------|------|
| **ClawHub** | `clawhub install <skill-name>` |
| **LobeHub** | `npx -y @lobehub/market-cli skills install <skill-name> --agent open-claw` |
| **skills.sh** | `npx skills add <owner/repo@skill> -g -y` |
| **GitHub** | `npx skills add <owner/repo> -g -y` |

详见 `references/sources.md`（含单个 skill vs 仓库安装说明）

### 中国镜像（ClawHub 安装失败时）

```bash
clawhub config set registry https://cn.clawhub-mirror.com
clawhub install <skill-name> --registry https://cn.clawhub-mirror.com
```

---

## 安装验证

```bash
ls ~/.openclaw/skills/<skill-name>/SKILL.md
# 文件存在 = 安装成功
```

- 文件存在 → ✅ 安装成功
- 文件不存在 → ❌ 安装失败，尝试 `clawhub install <skill-name> --force`

---

## 生命周期管理

### 更新技能

```bash
clawhub install <skill-name> --force
npx skills add <owner/repo@skill> -g -y --force
```

### 卸载技能

```bash
rm -rf ~/.openclaw/skills/<skill-name>/
# 验证：ls ~/.openclaw/skills/<skill-name>/SKILL.md  # 应返回空
```

### 查看已安装

```bash
openclaw skills list
ls ~/.openclaw/skills/
```

---

## 输出格式

```
🔍 "【需求关键词】" 搜索结果（共 X 个来源）：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 skills.sh（高质量首选）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 【skill-name】
   总安装量：XXX,XXX | 24h 安装量：X,XXX ↑ | 排名：#XX
   安装命令：npx skills add owner/repo@skill -g -y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📦 ClawHub（官方生态）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 【skill-name】
   下载：X,XXX | Stars: XX | ✅ 已安装 / ❌ 未安装
   安装命令：clawhub install skill-name

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 LobeHub（社区市场）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 【skill-name】
   安装量：XX,XXX
   安装命令：npx -y @lobehub/market-cli skills install <skill-name> --agent open-claw

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐙 GitHub（补充来源）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 【owner/repo】
   描述：【描述】
   Stars: XX | 安装：npx skills add owner/repo -g -y

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 推荐：【最推荐的技能】，理由：【一句话】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**说明**：
- 总安装量：All Time 累计安装量（越大越成熟）
- 24h 安装量：Trending 24h 新增安装（越大越热门）
- 排名：当前在 skills.sh 排行榜的位置

详见 `references/sources.md`（含安装量字段说明、安装命令语法）

---

## 安全机制

### 输入验证

```bash
# 最大长度 100 字符
[[ ${#keyword} -gt 100 ]] && echo "关键词过长" && exit 1

# 禁止危险字符（防止注入）
[[ "$keyword" =~ [[:space:]]*[\;\|\`\"\'\\] ]] && echo "包含非法字符" && exit 1

# 最小长度 2 字符
[[ ${#keyword} -lt 2 ]] && echo "关键词至少2个字符" && exit 1
```

### 幂等性 & 安全重跑

| 操作 | 幂等性 | 安全重跑 |
|------|--------|---------|
| 搜索 | ✅ 天然幂等 | ✅ 安全，可重复 |
| 安装 | ✅ 幂等（--force） | ✅ 支持，使用--force |
| 验证 | ✅ 幂等 | ✅ 安全，只读 |

---

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| ClawHub 无结果 | 检查网络，尝试英文关键词，用 `clawhub explore` 浏览热门 |
| skills.sh 无结果 | 确认 `npx` 可用，检查关键词拼写 |
| 速率限制 | 等待1小时，使用替代来源 |
| 安装失败 | 检查路径，确认 `~/.openclaw/skills/` 可写 |
| 验证失败 | 重新安装：`clawhub install <skill-name> --force` |

详细方案见 `references/troubleshooting.md`

---

## 找不到合适技能时

```
我搜索了 "【关键词】" 相关的 skills，但没有找到合适的匹配。

我仍然可以直接帮你完成这个任务！要我试试吗？

如果经常需要这个功能，可以考虑创建自定义 skill：
npx skills init my-custom-skill
```

---

## 相关技能

- `clawhub` - ClawHub CLI 工具
- `skill-creator` - 创建新技能
- `healthcheck` - 系统健康检查

---

*🔍 技能搜索全能版 v2.6.0*