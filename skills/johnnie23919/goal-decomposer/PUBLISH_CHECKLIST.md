# Goal Decomposer 发布清单

**发布目标**：ClawHub Skill Store  
**发布日期**：2026-04-26  
**作者**：筱龙虾

---

## ✅ 发布材料检查清单

### 核心文件（必需）

- [x] **SKILL.md** - 技能定义文件
  - 路径：`skills/goal-decomposer/SKILL.md`
  - 包含：name, version, description, metadata
  - 状态：已完善（添加tags字段）

- [x] **README.md** - 用户文档
  - 路径：`skills/goal-decomposer/README.md`
  - 包含：安装指南、使用示例、设计原理、常见坑
  - 状态：已完成（3966字节）

- [x] **scripts/decompose.py** - 核心实现脚本
  - 路径：`skills/goal-decomposer/scripts/decompose.py`
  - 功能：目标分类、模板填充、MECE验证
  - 状态：已存在（2452字节）

### 示例文件（推荐）

- [x] **examples/product-research.json** - 产品调研示例
  - 展示research类型目标拆解
  - 包含完整输入输出结构

- [x] **examples/development-task.json** - 开发任务示例
  - 展示create类型目标拆解
  - 包含依赖关系和spawn_hint

- [x] **examples/community-operation.json** - 社区运营示例
  - 展示manage类型目标拆解
  - 包含KPI指标

---

## 📋 发布命令

### 前置准备

```bash
# 1. 登录ClawHub（如未登录）
clawhub login

# 2. 验证登录状态
clawhub whoami
```

### 发布执行

```bash
# 发布到ClawHub
clawhub publish ./skills/goal-decomposer \
  --slug goal-decomposer \
  --name "Goal Decomposer" \
  --version 1.0.0 \
  --changelog "初始版本：支持research/create/manage三类目标拆解，MECE验证，优先级自动标注" \
  --tags "task-management,planning,mece"
```

### 发布后验证

```bash
# 搜索验证
clawhub search "goal decomposer"

# 检查详情
clawhub inspect goal-decomposer

# 安装测试
clawhub install goal-decomposer --dir /tmp/test-install
```

---

## 📦 发布包结构

```
goal-decomposer/
├── SKILL.md                    # 技能定义（必需）
├── README.md                   # 用户文档（必需）
├── scripts/
│   └── decompose.py            # 核心实现（必需）
└── examples/
    ├── product-research.json   # 示例1
    ├── development-task.json   # 示例2
    └── community-operation.json # 示例3
```

**总大小**：约10KB（压缩后）

---

## 🎯 目标用户

1. **Agent开发者** - 需要将模糊目标转为可执行任务
2. **项目经理** - 需要快速拆解复杂项目
3. **产品经理** - 需要调研、分析类任务拆解
4. **运营人员** - 需要运营计划结构化

---

## 🔍 竞品分析

ClawHub已有相关技能：
- `goal-agent` (3.309分) - 目标优化agent
- `goal-setter` (3.294分) - 目标设定
- `goal-clarifier` (3.290分) - 目标澄清

**差异化定位**：
- goal-decomposer专注**任务拆解**而非目标优化
- 提供结构化输出（JSON格式）
- 支持spawn_hint指导子任务执行
- MECE验证确保拆解质量

---

## 📊 预期指标

| 指标 | 目标 |
|------|------|
| 首周下载量 | ≥ 50 |
| 用户评分 | ≥ 4.0 |
| Issue反馈 | ≤ 5个 |
| 复装率 | ≥ 30% |

---

## 🚀 后续迭代计划

### v1.1.0（计划）
- [ ] 支持自定义拆解模板
- [ ] 添加时间估算字段
- [ ] 集成更多spawn_hint建议

### v1.2.0（计划）
- [ ] 依赖关系可视化
- [ ] 任务进度跟踪
- [ ] 与workflow-engine深度集成

---

## ⚠️ 发布注意事项

1. **版本号**：首次发布使用1.0.0
2. **Slug命名**：使用kebab-case（goal-decomposer）
3. **Changelog**：简洁明了，突出核心功能
4. **Tags**：选择3-5个相关标签，便于搜索

---

## ✅ 发布前最终检查

- [x] SKILL.md格式正确
- [x] README.md包含完整安装使用说明
- [x] 示例文件可运行
- [x] 版本号符合semver规范
- [x] 作者信息正确
- [x] 无敏感信息泄露

**状态**：✅ 准备就绪，可立即发布

---

**发布负责人**：筱龙虾  
**审核状态**：待发布  
**预计发布时间**：2026-04-26 15:00
