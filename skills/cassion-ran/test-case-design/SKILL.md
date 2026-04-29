---
name: test-case-design
description: This skill should be used when generating test cases, writing test cases, designing test cases, supplementing exception scenarios and boundary values, designing complex interaction test cases, outputting standardized test cases, compatibility testing, adaptation testing, API testing, security testing, UI visual testing, mobile/App/mini-program/H5/desktop/PC Web testing, linkage testing, or routing testing. Only focuses on writing test cases, does not involve test plans, test strategies, or test automation scripts.
---

## 加载指引

> **逐步披露原则**：先读 SKILL.md 获取全貌，再按场景关键词加载对应 references 文件。无需一次加载全部。

## 设计顺序

功能（正向+边界+异常）→ 接口 → 安全 → 平台专项

## 输出

- 默认 Markdown 表格，如需 Excel 调用 xlsx Skill
- 未指明平台 → 仅通用用例；指明平台 → 通用 + 平台专项
- 结构：编号 | 标题 | 类型 | 模块 | 级别 | 预置条件 | 步骤 | 预期结果

## 能力边界
✅ 可生成：功能测试、边界值、异常场景、接口、安全意识、UI视觉用例、性能体验用例（响应时间、加载速度）
❌ 不可生成：测试方案、测试策略、测试计划、渗透测试执行、漏洞扫描、性能压测（并发、压力、负载测试）、自动化脚本

## 指令映射表

| 关键词触发 | 加载文件 | 精确定位 |
|-----------|---------|---------|
| "测试用例"、"写用例"、"设计用例"（通用） | `references/core-capabilities/common-testing.md` + `references/templates/common-rules.md` | common-testing.md 全文加载 |
| "移动端测试"、"App 测试" | `references/core-capabilities/common-testing.md` + `references/platform/mobile-app.md` + `references/templates/common-rules.md` | platform/mobile-app.md：专项测试点 |
| "小程序测试" | `references/core-capabilities/common-testing.md` + `references/platform/mini-program.md` + `references/templates/common-rules.md` | platform/mini-program.md：专项测试点 |
| "移动 Web 测试"、"H5 测试" | `references/core-capabilities/common-testing.md` + `references/platform/mobile-web.md` + `references/templates/common-rules.md` | platform/mobile-web.md：专项测试点 |
| "桌面端测试"、"桌面应用测试" | `references/core-capabilities/common-testing.md` + `references/platform/desktop.md` + `references/templates/common-rules.md` | platform/desktop.md：专项测试点 |
| "PC Web 测试"、"Web 端测试" | `references/core-capabilities/common-testing.md` + `references/platform/pc-web.md` + `references/templates/common-rules.md` | platform/pc-web.md：专项测试点 |
| "联动测试" | `references/core-capabilities/common-testing.md` | 行116-159：第三部分 联动测试 |
| "路由测试"、"跳转测试" | `references/core-capabilities/common-testing.md` | 行160-214：第四部分 路由测试 |
| "UI 测试"、"视觉测试"、"界面测试" | `references/core-capabilities/common-testing.md` | 行215-300：第五部分 UI视觉测试 |
| "接口测试"、"API 测试" | `references/core-capabilities/common-testing.md` | 行301-375：第六部分 接口测试 |
| "安全测试" | `references/core-capabilities/common-testing.md` | 行376-443：第七部分 安全测试 |
| "边界值"、"异常场景" | `references/core-capabilities/common-testing.md` | 行22-86：第一部分 测试用例设计方法 |
| "兼容性测试"、"适配测试" | `references/core-capabilities/common-testing.md` | 按平台加载对应 platform/ 文件 |
| "可访问性测试" | `references/platform/mobile-app.md` + `references/checklists/mobile-app-checklist.md` | platform/mobile-app.md 六、设备兼容 |
| "功能测试" | `references/core-capabilities/common-testing.md` + `references/templates/common-rules.md` + `references/examples/common.md` | examples/common.md 行20-294：一、功能测试 |
| 检查清单（通用） | `references/checklists/common-checklist.md` | |
| 检查清单（平台专项） | `references/checklists/mobile-app-checklist.md` / `mobile-web-checklist.md` / `pc-web-checklist.md` / `desktop-checklist.md` / `mini-program-checklist.md` | |
| 示例参考 | `references/examples/common.md` + `references/examples/{platform}.md` | examples/common.md 含目录 |

## 文件结构

> **注意**：本 skill 无 scripts/ 和 assets/ 目录，所有内容均通过 references/ 提供。

```
references/
├── templates/               # 模板规则
│   └── common-rules.md       # 用例模板+测试类型+优先级+编号
├── core-capabilities/       # 通用测试能力
│   └── common-testing.md    # 所有通用测试能力（含目录）
├── platform/               # 平台专项测试点
│   ├── mobile-app.md        # 移动端App：手势/中断/网络/权限/推送/兼容/性能
│   ├── mobile-web.md        # 移动端Web：响应式/触摸/浏览器/视口/登录支付/H5/SEO
│   ├── pc-web.md           # PC Web：浏览器/布局/键盘/表单/会话/多窗口/路由/联动/拖拽/富文本/国际化/深色/打印
│   ├── desktop.md          # 桌面端：窗口/快捷键/文件/系统集成/多显示器/安装更新/兼容
│   └── mini-program.md     # 小程序：生命周期/授权/分享/支付/跳转/订阅/平台差异
├── checklists/             # 用例设计检查清单
│   ├── common-checklist.md # 通用检查清单（含目录）
│   ├── mobile-app-checklist.md
│   ├── mobile-web-checklist.md
│   ├── pc-web-checklist.md
│   ├── desktop-checklist.md
│   └── mini-program-checklist.md
└── examples/              # 示例参考
    ├── common.md          # 通用测试示例（含目录）
    ├── mobile-app.md      # 移动端App示例
    ├── mobile-web.md      # 移动端Web示例
    ├── pc-web.md         # PC Web示例
    ├── desktop.md        # 桌面端示例
    └── mini-program.md   # 小程序示例
```
