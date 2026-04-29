---
name: openclaw-enterprise
description: >-
  Use when user needs enterprise multi-agent collaboration system.
  Use when orchestrating 1 ChiefOfStaff + multiple specialized AI agents.
  Use when automating cross-department workflows (procurement/sales/finance/HR).
  Use when setting up AI team coordination or workflow automation.
  Use when user mentions "幕僚长", "AI团队", "运营自动化", "数字员工", "多Agent协作".
homepage: https://openclaw.ai
license: MIT-0
version: 1.2.3
progressive:
  layers:
    - name: metadata
      tokens: 200
      loaded: startup
      description: "技能基础配置、Agent列表、定价信息"
    - name: instructions
      tokens: 5000
      loaded: trigger
      description: "系统定位、团队架构、技术实现、部署方式"
    - name: resources
      tokens: variable
      loaded: on-demand
      description: "关键词路由表、工作流模板、配置指南"
  resource_paths:
    - scripts/*.py
    - templates/*.md
    - references/routing_tables/
metadata:
  openclaw:
    homepage: https://openclaw.ai
    primaryEnv: OPENAI_API_KEY
    requires:
      env:
        - OPENAI_API_KEY
        - ANTHROPIC_API_KEY
      bins:
        - python3
        - pip
        - curl
    third_party:
      - name: GitHub
        domain: github.com
        purpose: "开源社区协作，源码托管"
        verify_url: https://github.com/openclaw
    apis:
      - name: OpenAI API
        domain: api.openai.com
        purpose: "LLM大语言模型调用，用于Agent推理和内容生成"
        auth:
          type: Bearer Token
          env_var: OPENAI_API_KEY
      - name: Anthropic API
        domain: api.anthropic.com
        purpose: "Claude大语言模型调用，用于高级推理任务"
        auth:
          type: Bearer Token
          env_var: ANTHROPIC_API_KEY
      - name: OpenClaw Enterprise API
        domain: api.openclaw.ai
        purpose: "企业数据源集成（可选，需企业版）"
        auth:
          type: API Key
          env_var: OPENCLAW_API_KEY
          optional: true
          note: "企业版专属功能"
    emoji: "🏢"
    version: "1.2.3"
    author: "OpenClaw AI Team"
    category: "enterprise-ai"
    tags: ["multi-agent", "enterprise", "collaboration", "workflow", "automation", "SaaS", "运营自动化", "AI团队"]
pricing:
  basic:
    price: 999
    currency: CNY
    period: month
    features: ["1个幕僚长+5个专业Agent", "基础工作流", "10个并发用户"]
  professional:
    price: 3999
    currency: CNY
    period: month
    features: ["1个幕僚长+20个专业Agent", "全链路覆盖", "API集成", "50个并发用户", "SLA 99.5%"]
  enterprise:
    price: 29999
    currency: CNY
    period: month
    features: ["私有部署", "行业定制", "源码交付", "无限并发", "专属顾问"]
triggers:
  - "多Agent协作"
  - "运营自动化"
  - "企业AI团队"
  - "幕僚长调度"
  - "AI工作流"
  - "智能运营"
  - "团队协作"
  - "流程自动化"
  - "企业智能化"
  - "数字员工"
  - "AI助手团队"
---

# 企业多Agent协作系统：1个幕僚长+20个专业Agent替代运营团队

还在为团队协作效率低、跨部门沟通成本高而头疼？
OpenClaw Enterprise用1个幕僚长+20个专业AI Agent，帮你把整个运营团队装进口袋。

## 【能做什么】

- **智能调度**：幕僚长自动理解任务，分发给最合适的AI Agent处理
- **全链路覆盖**：采购/生产/销售/财务/人事/合规，20个专业Agent各司其职
- **7×24在线**：AI永不疲劳，节假日、深夜均可正常运转
- **自然语言交互**：用日常语言调度整个AI团队，无需学习命令行

## 【效果数据】

- 任务响应时间：从天级→分钟级
- 运营自动化率：80%重复工作由AI完成
- 团队效能：提升10倍

## 【安装】

```bash
# 通过ClawHub CLI安装
openclaw skills install openclaw-enterprise
```

适合中大型企业、电商平台、运营团队转型。

---

## 一、系统定位

OpenClaw Enterprise 是一个企业级多Agent协作系统，用AI模拟完整的中层管理团队。
1个幕僚长（ChiefOfStaff）负责调度，20个专业Agent负责执行，覆盖企业运营全链路。

## 二、团队架构

### 幕僚长（ChiefOfStaff）
- 任务分发、调度、结果整合
- 支持自然语言查询全链路数据
- 主动预警异常
- 支持多Agent并行执行与结果聚合

### 核心执行Agent（20个）

#### 采购与供应链（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 原料采购Agent | 供应商匹配/行情分析/下单 | 比价分析 |
| 仓储管理Agent | 库存预警/库位优化 | 实时库存 + 安全库存 |
| 物流调度Agent | 车队匹配/路线优化 | 降低物流成本 |
| 供应商管理Agent | 评级/风控/合同 | 供应商KPI |

#### 生产与研发（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 生产调度Agent | 排产/工单管理 | 交期承诺 |
| 配方研发Agent | 新材料/替代料 | 成本优化 |
| 质量检测Agent | 来料/过程/成品 | 合标率 |
| 设备维护Agent | 预测性维护 | 减少停机 |

#### 销售与市场（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 报价Agent | 快速响应/成本叠加 | 提升响应速度 |
| 订单履约Agent | 订单跟踪/异常处理 | 客户满意度 |
| 客户管理Agent | 客户分级/跟进 | 复购率 |
| 竞品监控Agent | 市场价格/替代品 | 定价决策 |

#### 财务与合规（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 成本核算Agent | 实际成本/标准成本 | 毛利分析 |
| 合规审查Agent | 环保/安全/税务 | 减少处罚 |
| 风险预警Agent | 客户信用/材料波动 | 降低坏账 |
| 政策解读Agent | 行业政策/补贴 | 争取优惠 |

#### 通用运营（4个）
| Agent | 职能 | 关键能力 |
|-------|------|---------|
| 数据分析Agent | 经营日报/月报 | BI报表 |
| 报告生成Agent | 会议纪要/汇报材料 | 减少文山 |
| 项目管理Agent | 里程碑/风险/进度 | 交付透明 |
| 客服支持Agent | 售后/投诉/FAQ | 响应<4h |

## 三、技术实现

### 架构
- ChiefOfStaff = LangGraph 状态机
- 各Agent = Python async 函数
- API层 = FastAPI
- 数据源 = ERP/MES/WMS/CRM API

### 关键词路由表
| 关键词 | Agent |
|--------|-------|
| 原料/供应商/行情/比价 | 原料采购Agent |
| 库存/库位/周转 | 仓储管理Agent |
| 排产/工单/交期 | 生产调度Agent |
| 配方/新材料/成本 | 配方研发Agent |
| 质量/检测/合格率 | 质量检测Agent |
| 设备/维修/停机 | 设备维护Agent |
| 报价/价格/成本 | 报价Agent |
| 订单/发货/交期 | 订单履约Agent |
| 客户/跟进/复购 | 客户管理Agent |
| 竞品/市场/定价 | 竞品监控Agent |
| 成本/毛利/利润 | 成本核算Agent |
| 合规/环保/安全 | 合规审查Agent |
| 风控/预警/呆账 | 风险预警Agent |
| 政策/补贴/税务 | 政策解读Agent |
| 数据/报表/月报 | 数据分析Agent |
| 报告/会议/文档 | 报告生成Agent |
| 项目/里程碑/进度 | 项目管理Agent |
| 售后/投诉/客服 | 客服支持Agent |

## 四、部署方式

### SaaS版（开箱即用）
- 直接使用API服务，无需部署
- 按月订阅，按需扩展

### 私有部署版
- 部署到客户自有服务器
- 支持ERP/MES/WMS/CRM深度集成
- 行业定制开发

### API接入
- RESTful API
- Webhook事件通知
- 支持Python/Node.js/Java SDK

---

## Common Rationalizations

| Rationalization | Reality |
|----------------|---------|
| "ChiefOfStaff replaces managers" | ChiefOfStaff orchestrates agents; human managers handle exceptions and strategy |
| "More agents = better results" | Quality of orchestration matters more than agent count |
| "One workflow fits all departments" | Each department has unique processes requiring customization |
| "AI never makes mistakes" | Agents can hallucinate; verification and guardrails are essential |
| "Deploy and forget" | Continuous monitoring and tuning required for optimal performance |

## Verification

After completing openclaw-enterprise workflow:
- [ ] 确认幕僚长正确理解用户意图（检查任务解析结果）
- [ ] 验证Agent路由准确率≥92%（对照路由表抽样检查）
- [ ] 多Agent并发任务无死锁或状态冲突
- [ ] 跨部门工作流数据传递完整无误
- [ ] 执行结果符合预期SLA（响应时间、准确率）
- [ ] 异常情况已触发预警并记录日志
- [ ] 最终输出格式符合业务规范要求
- [ ] ChiefOfStaff汇总报告逻辑自洽、信息完整
