---
name: spin-sales
description: The ultimate professional skill for mastering SPIN selling. Use when the user requires a structured, multi-stage consultation to deeply diagnose customer needs. The skill must guide the user through a rigorous process: 1. Opening/Rapport building (scripts/opening.py), 2. Situation (S) -> Problem (P) -> Implication (I) -> Need-Payoff (N)，并包含专门的 [References/Objection_Handling.md] 模块，以应对对话中的各种异议。
---

# 🚀 终极版 SPIN 销售法专家系统 (Ultimate SPIN Selling Expert System)

## 🎯 技能目标
提供一个从**开场、到挖掘、再到促成**的全周期、可操作的销售对话脚本框架。它要求用户或AI必须按照流程化的顺序进行提问和引导，模拟一次完整的销售咨询过程。

## 📜 流程与模块（Workflow & Modules）

本技能由以下相互关联的子模块构成，使用时**必须按顺序执行**：

1.  **[开场] 破冰脚本**: 总是从这里开始。使用 `scripts/opening.py` 来确保初次接触的专业性和亲和力。
2.  **[流程核心] S-P-I-N 循环**:
    *   **Situation (S)**: 参考 `references/s-questions.md` 收集背景事实。
    *   **Problem (P)**: 参考 `references/p-questions.md` 挖掘痛点。
    *   **Implication (I)**: 参考 `references/i-questions.md` 放大痛点影响。
    *   **Need-Payoff (N)**: 参考 `references/n-questions.md` 引导价值确认。
3.  **[防御机制] 异议处理**: 随时准备。如果客户提出质疑，必须转入该模式，参考 `references/objections.md` 进行专业的回应和引导，避免在压力下偏离主线。

## 💡 关键指导原则
*   **线性流程与灵活补充**: 遵循 S-P-I-N 的核心流程，但必须将“异议处理”视为任何阶段都可以插入的**中断和修正机制**。
*   **必须以脚本启动**: 始终从 `scripts/opening.py` 开始，确保开场专业化。

## 🧩 脚本执行指南
使用 `scripts/demo_interview.py` 来管理整个流程的状态和状态切换。此脚本内置了流程的状态机，用于指导您的提问。

## 📚 知识库与参考（References）
所有深度的知识点和高阶问题均已分离到 `references/` 目录下，以保持 `SKILL.md` 的简洁性。
*   **`references/s-questions.md`**: 现状问题（Facts）。
*   **`references/p-questions.md`**: 痛点挖掘（Pain）。
*   **`references/i-questions.md`**: 影响放大（Impact）。
*   **`references/n-questions.md`**: 价值确认（Value）。
*   **`references/objections.md`**: 应对异议（Objections）。
*   **`assets/opening_scripts.md`**: 用于学习开场白的专业脚本。

**👉 使用建议**: 每次使用时，请先运行 `scripts/demo_interview.py`，让脚本引导您进入流程，并根据需要随时参考 `references/objections.md` 来处理突发状况。