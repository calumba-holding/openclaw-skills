---
name: tutu-smart-control
description: |
  图图智控（TUTU Smart Control）— 远程控制 Android 手机，执行 GUI 自动化、系统管理和日常任务。当用户提到以下任何内容时使用此 skill：
  - 控制手机、操作手机、手机上做某事
  - 打开手机上的 App（微信、抖音、支付宝、淘宝等）
  - 手机截图、查看手机屏幕
  - 在手机上点击、输入、滑动
  - 手机自动化、GUI 自动化
  - 查看手机状态（电量、网络、内存等）
  - 发短信、打电话、读短信、通讯相关
  - 手机定位、获取位置
  - 查看手机通知
  - 手机震动、语音播报（TTS）
  - 手机文件管理（列目录、读写删文件、存储分析）
  - 执行手机 Shell 命令
  - 按文字/ID 点击 UI 元素、查找界面元素
  - 搜索手机媒体文件（图片、视频、音乐）
  - 微信自动回复、社交应用自动化
  - 手机定时任务、批量操作
  - 手机健康检查、系统巡检
version: 1.2.0
triggers:
  - 手机
  - 控制手机
  - 手机截图
  - 打开手机
  - 手机操作
  - phone
  - android
  - 手机上
  - 微信
  - 抖音
  - 支付宝
  - 淘宝
  - 京东
  - 手机屏幕
  - GUI
  - 电量
  - 手机信息
  - 设备信息
  - 发短信
  - 打电话
  - 短信
  - 定位
  - 位置
  - 通知
  - 文件管理
  - shell命令
  - 震动
  - 语音
  - TTS
  - 媒体
  - 存储
  - 截图
  - 自动化
  - 远程控制
  - remote control
  - 解锁
  - 签到
  - 巡检
  - 图图智控
  - TUTU
  - tutu
metadata: {"openclaw":{"emoji":"📱","homepage":"https://tutuai.me","primaryEnv":"TUTU_API_TOKEN","requires":{"env":["TUTU_API_TOKEN"]}}}
---

# 图图智控 TUTU Smart Control

通过图图智控（TUTU）硬件设备，无需安装 App，USB 即插即用，让 AI 像人一样远程操控你的 Android 手机 — 截图、点击、滑动、输入、发短信、文件管理等 30+ 种操作。

---

## ⚠️ 首次使用：Token 配置（必读）

**在执行任何操作之前，你必须先确认用户是否已提供 API Token。**

### Token 获取引导流程

请按以下步骤引导用户：

1. **询问用户**："要使用图图智控（TUTU）远程控制功能，需要提供您的 API Token。请问您是否已有 Token？"

2. **如果用户没有 Token**，告知：
   - "您可以在 https://tutuai.me 购买图图智控硬件并绑定设备后获取 Token。"
   - "图图智控是一款 USB 即插即用的 AI 硬件，插入 Android 手机即可实现远程控制。"
   - "Token 是一串加密字符串，由硬件设备自动生成，可在设备管理页面或扫描设备二维码获取。"
   - "每个 Token 对应一台设备，已包含设备身份信息，无需额外提供设备序列号。"

3. **用户提供 Token 后**，直接调用 `status` 接口验证设备在线状态。Token 中已加密包含设备信息，**不需要用户另外提供设备 SN**。

4. **验证成功后**即可开始执行操作。

**重要：**
- 在用户提供 Token 之前，不要执行任何 API 调用
- 将 Token 保存在当前会话中使用
- Token 已加密包含设备身份，无需明文传输设备序列号，更加安全

---

## 连接信息

- **API 地址**: `https://tutuai.me/api/phone_action.php`
- **鉴权方式**: `Authorization: Bearer <用户提供的Token>`
- **设备识别**: Token 已加密包含设备信息，无需在请求中传递 SN
- **硬件要求**: 图图智控 TUTU 硬件设备（USB-C 即插即用，无需安装 App）
- **屏幕分辨率**: 默认 1080 x 2400（宽 x 高），坐标使用绝对像素

---

## 调用方式

使用 `exec` / `Shell` / `run_shell` 等工具执行 `curl` 命令调用 API。所有请求都是 POST + JSON 格式。

### 基础 curl 模板

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"<ACTION>", ...其他参数}'
```

> Token 已加密包含设备信息，请求体中无需传递 SN 字段。

---

## 可用操作（完整列表 — 30 项）

### 一、基础 GUI 控制

#### 1. 截图 — 查看手机当前屏幕

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"screenshot"}'
```

返回：
```json
{
  "success": true,
  "action": "screenshot",
  "screenshot_url": "https://tutuai.me/screenshots/<SN>_xxx.jpg",
  "screenshot_base64": "data:image/jpeg;base64,...",
  "width": 1080,
  "height": 2400
}
```

**截图是最重要的操作！** 截图后用图像分析能力查看 `screenshot_url` 来理解屏幕内容，决定下一步操作。

#### 2. 点击 — 点击屏幕上的指定位置

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"click", "x":540, "y":1200}'
```

参数：`x`（横坐标 0-1080）、`y`（纵坐标 0-2400），绝对像素。

#### 3. 长按

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"long_press", "x":540, "y":1200}'
```

#### 4. 输入文本

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"type", "text":"你好世界", "x":540, "y":600}'
```

参数：
- `text`（必填）：要输入的文本。中文自动使用剪贴板粘贴。末尾加 `\n` 表示输入后按回车。
- `x`、`y`（可选）：输入框坐标，会先点击聚焦再输入。

#### 5. 滚动

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"scroll", "x":540, "y":1200, "direction":"down"}'
```

参数：
- `direction`：`up`、`down`、`left`、`right`
- `x`、`y`：滚动起始点（默认屏幕中心）

#### 6. 拖拽

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"drag", "x1":540, "y1":1800, "x2":540, "y2":600}'
```

#### 7. 打开应用

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"open_app", "app_name":"微信"}'
```

**支持中文应用名！** 常用应用名：微信、抖音、支付宝、淘宝、京东、设置、相机、电话、短信、浏览器、地图、日历、时钟、文件管理。也可以用包名（如 `com.tencent.mm`）。

#### 8. 按键操作

```bash
# 按 Home 键（回到桌面）
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"press_home"}'

# 按返回键
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"press_back"}'

# 按回车键
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"press_enter"}'
```

### 二、高级 UI 操作

#### 9. 获取 UI 节点树

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"get_ui_nodes"}'
```

返回当前屏幕的 UI 元素树（JSON 数组），每个元素包含 `cls`（类型）、`text`（文本）、`c`（中心坐标）等信息。

#### 10. 按文字点击 UI 元素

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"click_by_text", "text":"同意"}'
```

参数：`text`（必填）：要查找并点击的文字内容（模糊匹配）。比手动截图+估算坐标+click 更精准，**优先考虑使用**。

#### 11. 按资源 ID 点击 UI 元素

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"click_by_id", "id":"com.tencent.mm:id/btn_send"}'
```

#### 12. 查找 UI 元素

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"find_element", "text":"搜索", "className":"android.widget.EditText"}'
```

参数（至少一个）：`text`、`id`、`className`。返回元素列表含坐标信息。

### 三、系统信息与状态

#### 13. 获取设备信息 — 电量、网络、内存、屏幕等

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"get_device_info"}'
```

返回：电量（`battery.level`/`charging`）、WiFi/移动网络状态、存储/内存用量、屏幕方向、前台应用包名、亮度、设备型号、Android 版本等。

#### 14. 查询设备在线状态

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"status"}'
```

#### 15. 获取服务端版本信息

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"get_server_info"}'
```

### 四、通讯功能

#### 16. 发送短信

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"send_sms", "destination":"13800138000", "text":"你好"}'
```

#### 17. 读取短信

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"read_sms", "limit":10}'
```

参数：`limit`（默认20）、`box`（`inbox` 收件箱 / `sent` 发件箱，默认 `inbox`）

#### 18. 拨打电话

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"make_call", "number":"10086"}'
```

### 五、位置与通知

#### 19. 获取 GPS 位置

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"get_location"}'
```

返回：`latitude`、`longitude`、`accuracy`、`provider`。

#### 20. 读取系统通知

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"read_notifications", "limit":10}'
```

### 六、反馈输出

#### 21. 震动

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"vibrate", "duration":500}'
```

#### 22. 语音播报（TTS）

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"speak_tts", "text":"你好，世界"}'
```

### 七、文件管理

#### 23. 列出文件目录

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"list_files", "path":"/sdcard/DCIM"}'
```

#### 24. 读取文件

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"read_file", "path":"/sdcard/test.txt"}'
```

参数：`maxSize`（可选，最大读取字节数，默认 64KB）

#### 25. 写入文件

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"write_file", "path":"/sdcard/test.txt", "content":"Hello World"}'
```

参数：`append`（可选，`true` 为追加模式，默认覆盖）

#### 26. 删除文件

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"delete_file", "path":"/sdcard/test.txt"}'
```

#### 27. 存储分析

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"analyze_storage"}'
```

#### 28. 查找大文件

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"find_large_files", "path":"/sdcard", "minSize":10485760, "limit":20}'
```

### 八、媒体与 Shell

#### 29. 搜索媒体文件

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"search_media", "mediaType":"image", "keyword":"screenshot", "limit":10}'
```

参数：`mediaType`（`image`/`video`/`audio`，默认`image`）、`keyword`（可选）、`limit`（默认20）

#### 30. 执行 Shell 命令

```bash
curl -s -X POST https://tutuai.me/api/phone_action.php \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{"action":"execute_shell", "command":"ls /sdcard/"}'
```

参数：`command`（必填）、`timeout`（可选，默认30秒）。此接口超时为 35 秒。

---

## 操作流程（重要！）

执行手机任务时，严格遵循以下循环流程：

### 步骤 0：验证连接（首次必须）

1. 确认用户已提供 Token 和 SN
2. 调用 `status` 验证设备在线
3. 调用 `get_device_info` 了解设备基本情况（电量、网络、前台应用、屏幕方向）

### 步骤 1：先截图看屏幕

每次操作前必须先截图，了解当前屏幕状态。

### 步骤 2：分析截图

使用图像分析能力查看截图 URL，理解当前屏幕：
- 当前在什么应用/页面？
- 目标元素在哪里？坐标大概是多少？
- 屏幕是否锁定？
- 是否有弹窗/对话框需要处理？

### 步骤 3：执行操作

根据分析结果选择合适的操作（参考上方 30 项操作列表）。

**优先使用 `click_by_text` 而非手动坐标点击**，精准度更高。

### 步骤 4：等待 + 再截图验证

操作后等待 2-3 秒让手机响应，然后再次截图验证操作结果。

### 重复步骤 1-4 直到任务完成。

---

## 坐标参考

屏幕分辨率 1080 x 2400：

- 屏幕中心：(540, 1200)
- 状态栏高度约：0-80px
- 导航栏高度约：2300-2400px
- 顶部区域：y < 400
- 中部区域：400 < y < 1800
- 底部区域：y > 1800

---

## 场景示例

### 场景 1：打开微信并发送消息

```
1. open_app("微信") → 等 3 秒 → screenshot
2. 分析截图，找到目标联系人 → click 或 click_by_text
3. 等 2 秒 → screenshot → 确认进入聊天
4. type("你好", x=输入框x, y=输入框y)
5. click_by_text("发送") 或 click(发送按钮坐标)
6. screenshot → 确认消息已发送
```

### 场景 2：微信自动回复

```
1. read_notifications(limit=5) → 检查是否有微信新消息通知
2. 如果有新消息 → open_app("微信")
3. screenshot → 分析聊天列表，找到未读消息
4. click_by_text(联系人名) → 进入聊天
5. screenshot → 阅读对方发来的消息
6. type("收到，稍后回复") → click_by_text("发送")
7. screenshot → 确认发送成功
```

### 场景 3：App 签到/打卡

```
1. open_app("目标App") → 等 3 秒 → screenshot
2. 分析截图，找到签到入口
3. click_by_text("签到") 或 click(签到按钮坐标)
4. screenshot → 处理可能的弹窗（点击"确定"/"关闭"）
5. screenshot → 确认签到成功
```

### 场景 4：查看手机当前状态（综合巡检）

```
1. get_device_info → 获取电量、网络、内存、前台应用
2. analyze_storage → 查看存储空间
3. read_notifications(limit=10) → 查看未处理通知
4. screenshot → 查看当前屏幕
5. 向用户汇报完整的手机状态
```

### 场景 5：存储空间清理

```
1. analyze_storage → 了解总容量和可用空间
2. find_large_files(minSize=50MB) → 找到占空间的大文件
3. 向用户列出大文件，等待确认哪些可以删除
4. delete_file(path=用户确认的文件) → 逐个删除
5. analyze_storage → 再次确认清理效果
```

### 场景 6：发短信给某人

```
1. send_sms(destination="13800138000", text="明天下午开会")
2. 检查返回 success=true 确认发送成功
```

### 场景 7：查看最近收到的验证码

```
1. read_sms(limit=5, box="inbox") → 读取最近 5 条收件箱短信
2. 从短信内容中提取验证码数字
3. 向用户展示验证码
```

### 场景 8：获取手机位置

```
1. get_location → 获取 GPS 坐标
2. 向用户报告经纬度和大致位置描述
```

### 场景 9：解锁屏幕

如果截图显示锁屏：
```
1. click(540, 1200) → 唤醒屏幕
2. drag(540, 2000, 540, 800) → 上滑解锁（无密码锁屏）
3. screenshot → 确认已解锁
```

### 场景 10：手机找回/防丢失

```
1. get_location → 获取当前位置
2. vibrate(duration=3000) → 持续震动 3 秒
3. speak_tts("请注意，有人正在寻找这部手机") → 语音提示
4. screenshot → 截图记录当前屏幕状态
5. 向用户报告位置和操作结果
```

### 场景 11：批量处理通知

```
1. read_notifications(limit=20) → 获取所有通知
2. 按 App 分类整理通知内容
3. 向用户汇总：哪些是重要的、哪些可以忽略
4. 如用户要求，open_app 进入对应 App 处理
```

### 场景 12：手机上搜索和整理照片

```
1. search_media(mediaType="image", keyword="screenshot") → 搜索截图
2. 向用户列出找到的图片
3. 如需删除 → delete_file(path=图片路径) 逐个清理
```

### 场景 13：安装应用状态检查

```
1. execute_shell(command="pm list packages -3") → 列出所有第三方应用
2. 格式化展示已安装应用列表
3. 如用户要求，可通过 execute_shell 查看特定应用信息
```

### 场景 14：系统信息收集

```
1. get_device_info → 硬件信息
2. get_server_info → 服务端版本
3. execute_shell(command="getprop ro.build.display.id") → 系统版本
4. execute_shell(command="df -h") → 分区使用情况
5. 汇总为系统信息报告
```

### 场景 15：语音助手模式

```
1. 用户下达语音/文字指令
2. speak_tts("好的，正在为您执行") → 语音反馈
3. 执行对应操作（打开App、发短信、查信息等）
4. speak_tts("操作完成") → 语音通知结果
5. screenshot → 发送截图给用户确认
```

### 场景 16：社交应用内容浏览

```
1. open_app("抖音") → 等 3 秒 → screenshot
2. scroll(direction="up") → 上滑查看下一个视频
3. screenshot → 分析当前视频内容
4. 重复滑动浏览，或 click_by_text("关注"/"点赞")
```

### 场景 17：电商比价/下单辅助

```
1. open_app("淘宝") → 等 3 秒 → screenshot
2. find_element(className="android.widget.EditText") → 找到搜索框
3. click(搜索框坐标) → type("蓝牙耳机\n")
4. screenshot → 分析搜索结果，汇报价格和商品信息
5. 如用户要求，点击进入商品详情
```

---

## 注意事项

- **截图操作可能需要 3-5 秒**，这是正常的（需要通过图图智控服务端中转）
- **操作后一定要截图验证**，不要盲目连续操作
- **坐标是绝对像素**，不是百分比。屏幕宽 1080、高 2400
- **中文输入**会自动通过剪贴板粘贴，无需特殊处理
- 如果截图超时，先用 `status` 检查设备状态
- 每次操作后等待 2-3 秒再截图（`open_app` 等待 3 秒）
- 可通过 `get_device_info` 的 `foregroundApp` 字段确认当前前台应用
- 执行网络相关任务前，先检查 `network` 状态确认设备有网络连接
- `click_by_text` 比手动截图+估算坐标+click 更精准，优先使用
- `execute_shell` 超时为 35 秒，适合运行较长命令
- `find_large_files` 扫描大文件可能较慢（超时 30 秒）
- 发短信 `send_sms` 和打电话 `make_call` 依赖手机的 SIM 卡和信号
- 图图智控硬件通过 USB 连接手机，利用 ADB 协议控制，完全不影响手机日常使用
- **安全提示**：不要在日志或对话中明文展示用户 Token
