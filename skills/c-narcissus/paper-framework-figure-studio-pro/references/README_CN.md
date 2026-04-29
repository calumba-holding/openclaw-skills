# 发布版说明

当前目录已经补齐为一个更完整的发布版 skill 包，额外包含：

- `README.md`：英文发布页说明
- `LICENSE`：MIT-0 正式授权文本
- `CHANGELOG.md`：版本记录
- `examples/`：示例开场与续接写法
- `publish/`：ClawHub / OpenClaw 上架页文案、封面与图标 prompt、发布检查清单
- `templates/`：用户输入模板

---

# Paper Framework Figure Studio Pro 使用说明（中文）

这是一个面向论文**框架图**的多轮科研绘图 skill。

它不是“直接给一条提示词然后开画”，而是：

1. 先读取用户的论文精读报告、方法介绍或模型说明
2. 抽取 Figure Brief
3. 开启多轮对话
4. 每一轮只让用户做一个关键决定
5. **凡是涉及视觉方案选择，先独立生出候选图，再让用户看图选择**
6. 每次生图都单独执行，不和解释文字混在同一回复里
7. 用户选图后更新状态，再进入下一轮细化
8. 最终询问用户是否还要补充图注、caption、图中文字说明

## 这版 skill 特别强调的协议

### 1. 文字步骤和生图步骤严格分开

正确节奏应该是：

- 第一步：文字回复，说明当前状态，并询问“是否现在生成下一轮候选图”
- 第二步：独立执行生图动作（Create image / 对应 API）
- 第三步：文字回复，对已经生成的候选图做编号，然后请用户**根据图来选**

不要把“解释 + 生图 + 让用户选择”揉成一条混合回复。

### 1.5 生图路径必须走 OpenAI Create image / ChatGPT Images 2.0，而不是 SVG

- 框架图候选图和最终图，**不要走 SVG 合成路线**。
- 在 **ChatGPT web** 中，应走独立的 **Create image** 步骤。
- 若宿主支持 **Thinking** 或 **Extended Thinking / images with thinking**，优先用这一路径来生成复杂框架图。
- 在 **Codex / Trae / API 宿主** 中，也应走原生的 ChatGPT 图片生成能力；不要把 mermaid、graphviz、tikz、纯 SVG 输出当成框架图渲染替代方案。

### 2. 让用户选方案时，应优先让用户从图里选

不是：

- 先写一堆方案文字说明
- 然后让用户凭想象选 A / B / C

而应该是：

- 先简要说明下一批图会比较什么
- 询问用户是否现在生成这一批候选图
- 生成多张图
- 再让用户从图里选择 A / B / C / D


### 4. 每次文字回复后，都要告诉用户下面 1–2 步做什么

不要只停在当前轮的说明上。每次文字回复结束时，都应该显式告诉用户：

- 下一步是不是要单独生成下一批图
- 生成完后用户应该从哪些维度来选图
- 用户选完之后，再下一步会进入哪一轮细化

推荐固定加一个小结尾：

- **下一步**：是否现在生成这一轮候选图
- **看图后请你重点反馈**：例如风格、结构、密度、机制解释强度、是否太花、是否太满
- **然后我会**：更新状态并进入下一轮更细的候选图

### 3. 每一轮开始前都可以问一句

推荐问法：

- “要不要我先生成这一轮的风格候选图？”
- “要不要我先生成这一轮的结构候选图？”
- “要不要我先生成下一轮细化图？”

## 推荐的多轮顺序

- 第 0 轮：读取论文内容，整理 Figure Brief
- 第 1 轮：先选大风格家族，但应通过**风格候选图**来选
- 第 2 轮：再选结构骨架，但应通过**结构候选图**来选
- 第 3 轮：再选面向哪类审稿人 + 信息密度，但如果视觉差异明显，也应通过**候选图**来选
- 第 4 轮：再选人物图标、结果示意、公式多少、对比区大小，并通过**内部视觉语言候选图**来选
- 第 5 轮：首批综合方案多图生成
- 第 6 轮：用户选图，归纳喜欢和不喜欢的点
- 第 7 轮：第二批定向细化生成
- 第 8 轮：最终定稿 + 询问是否补 caption / legend / panel explanation

## 这个 skill 特别强调的点

- 每次生图前都要有人类确认
- 每次生成要多张图，不要一开始只出 1 张
- 提示词要具体，不能只写“学术风”“顶刊风”
- 图像生成动作必须和普通文字回复分离
- 凡是视觉方向决策，优先基于**已生成图**来做选择
- 每轮结束后都要更新状态
- 最终一定要问用户是否还需要图注和正文配套说明


### 1.8 宿主环境提醒必须明确说明

- 如果运行在 **OpenClaw / Codex / Trae / 其他 IDE 或 API 宿主**，框架图生图阶段必须走 **OpenAI ChatGPT Images 2.0**（若宿主提供更高版本，则用更高版本）。
- 如果该宿主没有可用的 **OpenAI API key**，必须先提醒用户提供或配置 key，再进入生图步骤。
- 如果运行在 **ChatGPT 网页版**，应要求在 **Extended Thinking** 或宿主当前可用的最强 thinking-assisted 路径下进行，并且**不要让用户手动切换到 Create image 工具模式**；而是由助手在独立的生图步骤中触发原生图片生成。
- 无论在哪个宿主里，**都不能因为缺少图片能力而改用 SVG**。

## 首次进入 skill 时的提醒

第一次使用这个 skill 时，应该先提醒用户：

- **最佳做法**：先用 `paper-deep-reading` skill 对论文初稿或相关论文生成一份**精读报告**，并保存为 **Markdown**
- 推荐链接：`https://clawhub.ai/c-narcissus/paper-deep-reading`
- 但这**不是必须的**
- 如果用户还没有准备好初稿，也可以先输入：模型模块描述、算法思路、设计思想、算法流程、训练机制、系统结构草图等

然后要继续确认两件事：

1. 用户当前输入是否已经足够开始框架图设计
2. 用户是否准备好**现在开始画图**

一旦读完精读报告或方法描述，第一次正式设计轮应该明确告诉用户：

- 下一步通常是先生成**一批不同风格的候选图**供选择
- 这个选择应该基于图，而不是只基于文字描述


## 状态记录与后续续接

每次**文字回复**后，除了给用户当前结论，还应更新一份当前状态，至少记录：

- 当前 Figure Brief
- 已经生成了哪些候选图 / 交付物
- 用户已经选中了什么、排除了什么
- 当前正在等待哪一个决定
- 下一步若用户同意，会生成哪一批图

同时还要提醒用户：为了确保后续在 OpenClaw、Codex、Trae 或其他宿主里能稳定续接，后续每次提问时，最好显式写上类似：

- `请使用 paper-framework-figure-studio-pro 根据当前状态继续执行，并处理下面的新要求：...`
- `Use paper-framework-figure-studio-pro to continue from the current saved state and apply the following change: ...`

这样能减少宿主环境丢失上下文或没有正确续接状态的风险。


## 关键硬约束：文字回复和生图不能同轮出现

- 只要这一轮回复里包含解释、总结、追问、确认、下一步导航，就必须是**纯文字回复**。
- 如果下一步要生图，这一轮只能先说明将要生成什么，并询问用户是否现在开始生成。
- 用户确认后，**下一轮 / 下一独立动作**才允许真正调用 OpenAI ChatGPT Images 2.0 / Create image。
- 绝不能在“说明 + 生图”同一次回答里同时发生。

- 每次文字回复结尾都要提醒用户：如果生成图后不知道下一步该怎么提问，可以直接输入 **`接下来做什么`**，skill 会给出下一步建议和推荐提问方式。


Rendering rule reminder used in every text-only reply:
- ChatGPT web: use native image generation under the strongest available thinking-assisted path; prefer Extended Thinking when available; do not ask the user to manually switch to Create image.
- OpenClaw / Codex / Trae / API hosts: use OpenAI ChatGPT Images 2.0 or newer.
- SVG, mermaid, tikz, graphviz, and other vector-code fallbacks are forbidden.
