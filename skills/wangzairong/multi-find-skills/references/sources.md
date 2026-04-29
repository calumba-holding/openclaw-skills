# 搜索来源详细说明

## 1. ClawHub（官方生态）

```bash
# 搜索 skills（向量搜索）
clawhub search "<关键词>"

# 浏览热门技能（支持排序）
clawhub explore --sort installs --limit 20   # 按安装量
clawhub explore --sort rating --limit 20     # 按评分
clawhub explore --sort trending --limit 20   # 按趋势

# 查看详情
clawhub inspect <skill-name>
```

**特点**：官方生态，质控严格，SKILL.md 格式规范

## 2. skills.sh（Vercel 生态，高质量首选）

### 基础命令

```bash
# 搜索 skills
npx skills find "<关键词>"

# 浏览所有可用技能
npx skills add vercel-labs/agent-skills --list
```

### 高级用法

| 命令 | 说明 |
|------|------|
| `npx skills find "<关键词>"` | 搜索 skills |
| `npx skills add owner/repo --list` | 预览可用技能（不安装） |
| `npx skills list` | 查看已安装 |
| `npx skills list -g` | 查看全局安装 |
| `npx skills find "popular"` | 浏览热门技能 |

### 排行榜分类

| 分类 | 说明 | 适用场景 |
|------|------|---------|
| **All Time** | 总安装量排名 | 发现经过时间验证的成熟技能 |
| **Trending (24h)** | 24小时内安装量 | 发现最新热门趋势 |
| **Hot** | 实时热度 | 追逐最新潮流 |

**访问** https://skills.sh 查看完整排行榜

### 排名机制

skills.sh 安装量基于 **匿名遥测数据**（用户安装时自动上报，聚合统计，不追踪个人信息）：

- ≥100K → 顶级 | ≥10K → 热门
- 官方技能（vercel-labs、anthropics、microsoft）有例行安全审计

**特点**：Vercel 出品，社区活跃，更新频繁

## 3. LobeHub（社区市场）

```bash
# 搜索 skills
npx -y @lobehub/market-cli skills search --q "<关键词>"
```

**特点**：社区贡献，市场丰富，适合发现创新/实验性技能

## 4. OpenClaw Directory

- 网站：https://www.openclawdirectory.dev/skills
- 支持按分类、人气或关键词搜索
- 可直接访问详情页查看安装量、描述

## 5. GitHub（补充来源）

```bash
# 网页搜索
site:github.com "openclaw skill"
site:github.com "SKILL.md"
```

**推荐来源**：
- `vercel-labs/agent-skills` - Vercel 官方
- `anthropics/` - Anthropic 相关
- `microsoft/` - Microsoft 相关
- `openclaw/` - OpenClaw 官方

## 6. 社区论坛

- SitePoint：https://www.sitepoint.com/community/
- Discord：https://discord.com/invite/clawd

## 搜索技巧

1. **使用具体关键词**：`"react testing"` 比单独 `"testing"` 效果更好
2. **尝试替代术语**：如果 `"deploy"` 没结果，试试 `"deployment"`
3. **检查热门来源**：vercel-labs、anthropics、microsoft、openclaw
4. **中文关键词翻译**：先用中文理解需求，再翻译成英文搜索
5. **搜索顺序**：skills.sh（首选）→ ClawHub → LobeHub → GitHub
6. **超时处理**：单个来源超时 → 继续其他来源；所有超时 → 建议手动访问网站

---

## 附录：输出格式字段说明

### skills.sh 安装量字段

| 字段 | 说明 |
|------|------|
| 总安装量 | All Time 累计安装量（越大越成熟） |
| 24h 安装量 | Trending 24h 新增安装（越大越热门） |
| 排名 | 当前在 skills.sh 排行榜的位置 |

### 安装命令语法

```bash
# 安装特定 skill
npx skills add owner/repo@skill-name -g -y

# 安装整个技能库
npx skills add owner/repo -g -y

# 参数说明
# -g：全局安装（用户级）
# -y：跳过确认提示
# @skill-name：指定特定 skill（不指定则安装整个仓库）
```

### LobeHub 安装命令

```bash
npx -y @lobehub/market-cli skills install <skill-name> --agent open-claw
```