# tsinghua-learn skill

清华网络学堂（learn.tsinghua.edu.cn）自动化助手——从登录、查看待办、下载课件到提交作业，一切均可对话完成。

---

## 如果你是人类，首次使用请务必阅读以下说明

本 skill 为清华网络学堂打造全自动助手——从登录、查看待办、下载课件到提交作业，一切均可对话完成。首次使用仅需提供学号和密码，之后完全无人值守。

**它能做什么：**

- **查看待办**：自动拉取本学期所有课程未读消息（作业/公告/课件/讨论/答疑/问卷），按截止时间和课程排序显示，再也不用手动一个个点开看
- **下载课件**：指定课程名称，课件自动发送到当前对话，下载后本地临时文件精准清除，不留痕迹
- **提交作业**：直接把作业文件发给机器人，它自动按指定格式（如姓名+学号）命名并提交，省去繁琐的网页上传流程
- **批量标记已读**：所有课程的未读课件，一键全部标记为已读

**运行原理：**

首次运行需手动完成一次浏览器验证（点击"是的，我信任浏览器"），之后所有凭证和浏览器指纹会保存到本地。之后所有操作由机器人自动完成，无需重复验证。

---

## 零、驻地规范（铁律）

所有网络学堂相关脚本必须写在 `skills/tsinghua-learn/` 目录下，禁止散落到任何其他位置。

禁止位置：workspace 根目录、buffer/、其他 skill 目录。

---

## 一、文件结构

```
skills/tsinghua-learn/
├── SKILL.md                        ← 本文档
├── credentials.json               ← 账号密码（机器人自动创建，用户无需手动操作）
│
├── scripts/
│   ├── _config.py                  ← 凭证和路径加载器（所有脚本共享）
│   ├── learn_api.py                ← 所有 HTTP API 封装（详见文件内注释）
│   ├── login_supervised.py         ← 有人值守：首次建立 Profile + 2FA
│   ├── login_auto.py               ← 无人值守：日常调用，Session 失效自动续期
│   ├── todos_api.py                ← 查看待办：默认版（纯 API，并行请求）
│   ├── todos_dom.py                ← 查看待办：备用版（Playwright DOM）
│   ├── download_and_send_kj.py     ← 下载课件 + 发送 + 精准删除
│   ├── mark_kj_read.py             ← 批量标记课件已读
│   └── install_playwright.py        ← Chromium 浏览器安装
│
├── sessions/
│   └── learn_session.json          ← Session 文件（JSESSIONID + CSRF）
│
└── profiles/
    └── learn_profile/              ← 固定浏览器 Profile（cookies 持久化）
```

---

## 二、账号配置（首次使用）

机器人会主动询问用户的学号和密码，配置好后自动写入 `credentials.json`，之后所有脚本自动读取，无需重复操作。

---

## 三、双脚本登录架构

### 3.1 有人值守（supervised）

首次配置 / Session 彻底失效时使用。弹出浏览器窗口，若触发 2FA（企业微信/短信）需人工验证。

### 3.2 无人值守（auto）— 默认

日常调用。Session 有效时直接返回（<100ms），失效时自动用固定 Profile 续期，无需人工介入。

---

## 四、降级策略

```
todos_api.py / todos_dom.py
  → Session 无效 → login_auto.py（自动续期）
  → Profile 丢失 → login_supervised.py（手动 2FA）
  → Chromium 未装 → install_playwright.py

login_auto.py
  → Session 无效 → login_supervised.py
```

---

## 五、未读/未处理判断标准

| 模块 | API 字段 | 过滤条件 |
|------|---------|---------|
| 作业 | `zt` | `zt == "未交"` → 待提交 |
| 公告 | `sfyd` | `sfyd == "否"` → 未读（"是"=已读）|
| 课件 | `isNew` | `isNew == 1` → 未读 |
| 讨论/答疑 | `htsl` | `htsl > 0` → 有新回复 |
| 问卷 | — | 全局 API `pageListWks` 返回未做问卷数量 |

---

*最后更新：2026-04-26*