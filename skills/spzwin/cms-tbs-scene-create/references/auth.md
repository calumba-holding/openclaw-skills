### cms-auth-skills：access-token 获取与注入（强制）

这份规则用于约束 Agent：任何需要执行本 Skill 真实写接口的链路，access-token 获取必须通过依赖 Skill `cms-auth-skills` 完成。

#### 必须做
- 只要确定要进入真实写接口链路（如知识检查/创建/最终落库），在调用目标脚本之前，**必须先调用** `cms-auth-skills` 获取 access-token。
- 将 `cms-auth-skills` 返回的 access-token **以 `--access-token`** 注入到后续执行命令：
  - `python3 scripts/<name>.py ... --access-token "<ACCESS_TOKEN>"`
- 最终落库统一使用：
  - `python3 scripts/tbs-scene-finalize-from-session.py --session-dir "<sessionDir>" --user-confirmation 确认 --access-token "<ACCESS_TOKEN>"`

#### 必须禁止
- 禁止自行从环境变量读取 access-token（例如 `TBS_ACCESS_TOKEN` 等）。
- 禁止按某种“自动解析逻辑”（如从 sender_id/account_id、上下文字段等推断）去获取 access-token。
- 禁止向用户索要 access-token（不要问“把 token 发我/让我用哪个 token”这类话）。
- 禁止在 `cms-auth-skills` 未返回可用 access-token 时继续调用真实写接口。

#### 失败处理
- `cms-auth-skills` 获取失败或无可用 access-token：必须停止当前链路，并引导用户重新完成授权/登录；然后再重新尝试进入执行链路。
