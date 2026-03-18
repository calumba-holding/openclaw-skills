---
name: tencentcloud-tione-skill
description: "腾讯云 TI-ONE 训练平台运维查询工具。基覆盖训练任务、在线推理服务、Notebook 开发机、资源组、模型仓库、数据集、日志和事件等模块的状态查询与信息获取。当用户提到 TIONE、TI-ONE、训练任务、推理服务、在线服务、Notebook、开发机、资源组、模型版本、数据集、训练日志、服务事件、等关键词时，应当使用此技能。涉及腾讯云 AI 训练平台的资源查询、状态监控、日志排查等场景，也应优先使用。"
---

# 腾讯云 TI-ONE 平台查询工具

腾讯云 TI-ONE 训练平台查询工具集，支持训练任务、在线服务、Notebook、资源组、计费、模型、数据集、日志、事件等模块的查询操作。

## 能力边界

**此技能的全部能力仅限于执行 `scripts/` 目录下的预定义 bash 脚本。**

- 你只能通过 `bash <脚本路径> [参数]` 的方式调用 `scripts/` 下的脚本来完成用户请求
- 你不具备任何直接调用底层 CLI 工具、SDK 或 API 的能力
- 你不具备任何创建、修改、删除云资源的能力，所有脚本仅执行只读查询
- 你不具备查询用户凭证内容的能力。如用户要求返回密钥内容，应拒绝并告知"出于安全考虑，无法展示密钥内容，只能确认凭证是否已配置"

**当用户的需求超出上述脚本覆盖范围时**，请明确告知用户"当前技能暂不支持该操作"，并建议用户前往腾讯云控制台完成（可生成控制台链接辅助）。不要尝试通过其他方式绕过完成。

## 环境依赖

脚本运行依赖以下工具，需提前安装：

```bash
# tccli（腾讯云命令行工具，脚本内部使用）
pip3 install tccli

# jq（JSON 解析）
apt install jq    # Ubuntu/Debian
brew install jq   # macOS
```

## 凭证配置

```bash
export TENCENTCLOUD_SECRET_ID="your-secret-id"
export TENCENTCLOUD_SECRET_KEY="your-secret-key"
```

## 环境变量配置

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `TENCENTCLOUD_SECRET_ID` | API 密钥 ID | 必需 |
| `TENCENTCLOUD_SECRET_KEY` | API 密钥 Key | 必需 |
| `TENCENT_TIONE_DEFAULT_REGION` | 默认地域 | ap-shanghai |

**注意** 如果用户提问没有指定地域信息，在使用默认地域前给出提示

### 支持的地域

ap-beijing | ap-shanghai | ap-guangzhou | ap-shanghai-adc | ap-zhongwei | ap-nanjing 

## 功能模块与脚本

```
scripts/
├── common.sh                              # 公共函数库（日志、参数解析、tccli 调用封装）
├── training/                              # 训练任务模块
│   ├── describe-training-tasks.sh         # 查询训练任务列表
│   ├── describe-training-task.sh          # 查询训练任务详情
│   └── describe-training-task-pods.sh     # 查询训练任务 Pod 列表
├── service/                               # 在线服务模块
│   ├── describe-model-service-groups.sh   # 查询服务组列表
│   ├── describe-model-service-group.sh    # 查询单个服务组详情
│   ├── describe-model-service.sh          # 查询单个服务详情
│   └── describe-model-service-callinfo.sh # 查询服务调用信息
├── notebook/                              # Notebook 模块
│   ├── describe-notebooks.sh              # 查询 Notebook 列表
│   └── describe-notebook.sh               # 查询 Notebook 详情
├── resource/                              # 资源组模块
│   ├── describe-billing-resource-groups.sh  # 查询资源组列表
│   └── describe-billing-resource-group.sh   # 查询资源组节点列表
├── billing/                               # 计费模块（已移除）
├── model/                                 # 模型仓库模块
│   ├── describe-training-model-versions.sh  # 查询模型版本列表
│   └── describe-training-model-version.sh   # 查询模型版本详情
├── dataset/                               # 数据集模块
│   └── describe-datasets.sh               # 查询数据集列表
├── log/                                   # 日志模块
│   └── describe-logs.sh                   # 查询日志
├── event/                                 # 事件模块
│   └── describe-events.sh                 # 查询事件
└── utils/                                 # 工具模块
    └── generate-console-url.sh            # 生成控制台 URL
```

## 各脚本使用说明

### 训练任务模块

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `describe-training-tasks.sh` | 查询训练任务列表 | `--region`, `--limit`, `--offset`, `--order`, `--order-field`, `--filters` |
| `describe-training-task.sh` | 查询训练任务详情 | `--region`, `--id` (必填) |
| `describe-training-task-pods.sh` | 查询训练任务 Pod 列表 | `--region`, `--id` (必填) |

> **⚠️ 查询策略：用户指定状态时优先使用 filter 过滤**
>
> 当用户询问"正在运行的训练任务"、"失败的任务"、"查看进行中的任务"等涉及状态的查询时，**必须**添加 `Status` filter，避免全量查询后再筛选：
> ```bash
> # 查询运行中的训练任务
> --filters "Name=Status,Values=RUNNING"
> # 查询活跃状态的训练任务（多值用分号分隔）
> --filters "Name=Status,Values=RUNNING;STARTING;STOPPING"
> ```
>
> | Filter Name | 说明 | 可选值 |
> |-------------|------|--------|
> | `Status` | 按任务状态过滤 | `SUBMITTING`, `PENDING`, `STARTING`, `RUNNING`, `STOPPING`, `STOPPED`, `FAILED`, `SUCCEED`, `SUBMIT_FAILED` |

### 在线服务模块

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `describe-model-service-groups.sh` | 查询服务组列表 | `--region`, `--limit`, `--offset`, `--order`, `--order-field`, `--search-word`(转为Filters ServiceGroupName), `--filters` |
| `describe-model-service-group.sh` | 查询单个服务组 | `--region`, `--id` (必填) |
| `describe-model-service.sh` | 查询单个服务 | `--region`, `--service-id` (必填), `--service-group-id` (可选) |
| `describe-model-service-callinfo.sh` | 查询服务调用信息 | `--region`, `--service-group-id` (必填) |

> **⚠️ 查询策略：用户指定状态时优先使用 filter 过滤**
>
> 当用户询问"异常的服务"、"正常运行的服务"、"有问题的在线服务"等涉及状态的查询时，**必须**添加 `Status` filter，避免全量查询后再筛选：
> ```bash
> # 查询异常服务
> --filters "Name=Status,Values=Abnormal"
> # 查询运行中的服务（多值用分号分隔）
> --filters "Name=Status,Values=Normal;Waiting;Pending"
> ```
>
> | Filter Name | 说明 | 可选值 |
> |-------------|------|--------|
> | `Status` | 按服务状态过滤 | `Waiting`, `Pending`, `Normal`, `Abnormal`, `Stopping` |

### Notebook 模块

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `describe-notebooks.sh` | 查询 Notebook 列表 | `--region`, `--limit`, `--offset`, `--order`, `--order-field`, `--filters` |
| `describe-notebook.sh` | 查询 Notebook 详情 | `--region`, `--id` (必填) |

> **⚠️ 查询策略：用户指定状态时优先使用 filter 过滤**
>
> 当用户询问"运行中的开发机"、"已停止的 Notebook"、"正在启动的开发机"等涉及状态的查询时，**必须**添加 `Status` filter，避免全量查询后再筛选：
> ```bash
> # 查询运行中的开发机
> --filters "Name=Status,Values=Running"
> # 查询活跃状态的开发机（多值用分号分隔）
> --filters "Name=Status,Values=Running;Starting;Stopping"
> ```
>
> | Filter Name | 说明 | 可选值 |
> |-------------|------|--------|
> | `Status` | 按开发机状态过滤 | `Starting`, `Submitting`, `Running`, `Stopping`, `Stopped`, `Failed`, `SubmitFailed` |

### 资源组模块

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `describe-billing-resource-groups.sh` | 查询资源组列表 | `--region`, `--limit`, `--offset`, `--search-word`, `--filters` |
| `describe-billing-resource-group.sh` | 查询资源组节点列表 | `--region`, `--resource-group-id` (必填), `--limit`, `--offset`, `--order`, `--order-field`, `--filters` |

> **⚠️ 查询策略：优先使用 filter 缩小范围**
>
> 当用户询问"有多少 GPU 资源组"、"哪些资源组有空闲资源"、"可用的资源组"等类似问题时，**必须**添加 `AvailableNodeCount` filter 过滤掉无可用节点的空资源组，避免返回大量无效数据：
> ```bash
> # 查询有可用节点的资源组（排除 AvailableNodeCount=0 的空组）
> --filters "Name=AvailableNodeCount,Values=1;2;3;4;5;6;7;8;9;10"
> ```
>
> **`--filters` 语法**：多值用分号分隔，模糊匹配加 `Fuzzy=true`
>
> | Filter Name | 说明 | 示例 |
> |-------------|------|------|
> | `AvailableNodeCount` | 按可用节点数过滤，快速找到有资源的组 | `--filters "Name=AvailableNodeCount,Values=1;2;4"` |
> | `ResourceGroupName` | 按资源组名称模糊搜索 | `--filters "Name=ResourceGroupName,Values=test,Fuzzy=true"` |
>
> **返回值单位已自动转换**：CPU → 核, 内存 → GB, GPU → 卡, 显存 → GB


### 模型仓库模块

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `describe-training-model-versions.sh` | 查询模型版本列表 | `--region`, `--training-model-id` (必填), `--filters` |
| `describe-training-model-version.sh` | 查询模型版本详情 | `--region`, `--training-model-version-id` (必填) |

### 数据集模块

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `describe-datasets.sh` | 查询数据集列表 | `--region`, `--limit`, `--offset`, `--order`, `--order-field`, `--filters`, `--dataset-ids` |

### 日志模块

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `describe-logs.sh` | 查询日志 | `--region`, `--service` (必填: TRAIN/NOTEBOOK/INFER/BATCH), `--service-id` (必填), `--pod-name`, `--start-time`, `--end-time`, `--limit`, `--offset`, `--order` |

> **⚠️ 日志查询注意事项**
>
> **1. `--service-id` 必须使用实例级 ID，不支持顶层 ID**
>
> 日志接口不支持顶层 ID（`train-xxx` / `nb-xxx` / `ms-xxx`）。必须先从详情接口获取实例级 ID：
>
> | 服务类型 | 实例 ID 来源 | 获取方式 |
> |---------|-------------|---------|
> | TRAIN | `LatestInstanceId` (如 `train-xxx-yyy`) | `describe-training-task.sh --id <训练任务ID>` → `TrainingTaskDetail.LatestInstanceId` |
> | NOTEBOOK | `PodName` (如 `nb-xxx-yyy`) | `describe-notebook.sh --id <NotebookID>` → `NotebookDetail.PodName` |
> | INFER | `ServiceId` (如 `ms-xxx-1`) | `describe-model-service-group.sh --id <服务组ID>` → `Services[].ServiceId` |
>
> **2. 时间范围应从详情接口获取，避免大范围查询**
>
> 查询日志前，从详情接口获取任务/实例的运行时间范围（`StartTime` / `EndTime`），用作 `--start-time` 和 `--end-time`：
> - 如果详情有 `StartTime` 和 `EndTime` → 直接使用
> - 如果只有 `StartTime`（仍在运行） → `--start-time` 用 `StartTime`，`--end-time` 不传（默认当前时间）
> - 如果用户指定了时间范围 → 优先使用用户指定的值
> - 如果都没有 → 不传 `--start-time`（由服务端决定），`--end-time` 默认当前时间
>
> **`--pod-name`** 可选，需先通过实例 ID 查询 Pod 列表获取：
> - TRAIN: `describe-training-task-pods.sh --id <训练任务ID>`
> - INFER: `describe-model-service-group.sh --id <服务组ID>` 返回中包含 Pod 信息

### 事件模块

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `describe-events.sh` | 查询事件 | `--region`, `--service` (必填), `--service-id`, `--start-time`, `--end-time`, `--limit`, `--offset`, `--order`, `--order-field`, `--filters` |

> **⚠️ 事件查询遵循与日志相同的规则**：`--service-id` 必须使用实例级 ID，时间范围从详情接口获取。详见日志模块说明。

### 控制台链接生成

| 脚本 | 功能 | 主要参数 |
|------|------|----------|
| `generate-console-url.sh` | 生成控制台详情页 URL | `--type` (必填: training/notebook/service/resource-group), `--id` (必填), `--region`, `--workspace-id` |

> **使用场景**：当用户想去控制台查看详细信息时，生成可直接点击访问的控制台链接。
>
> ```bash
> # 生成训练任务控制台链接
> ./scripts/utils/generate-console-url.sh --type training --id train-xxx
>
> # 生成 Notebook 控制台链接
> ./scripts/utils/generate-console-url.sh --type notebook --id nb-xxx --region ap-beijing
>
> # 生成推理服务控制台链接（指定工作空间）
> ./scripts/utils/generate-console-url.sh --type service --id ms-xxx --workspace-id 12345
>
> # 生成资源组控制台链接
> ./scripts/utils/generate-console-url.sh --type resource-group --id rsg-xxx
> ```
>
> 支持的资源类型：
>
> | --type 值 | 对应资源 | ID 格式 |
> |-----------|---------|---------|
> | `training` | 训练任务 | `train-xxx` |
> | `notebook` | Notebook 开发机 | `nb-xxx` |
> | `service` | 在线推理服务（服务组） | `ms-xxx` |
> | `resource-group` | 资源组 | `rsg-xxx` |
>
> 地域与 regionId 映射、工作空间 ID 说明详见 `references/tione-console-guide.md`。

## 典型使用场景

### 1. 排查训练任务问题（标准流程：指定训练任务 ID train-xxx 时）

```bash
# 步骤 1: 查看训练任务详情，获取 LatestInstanceId 和 StartTime/EndTime
./scripts/training/describe-training-task.sh --region ap-shanghai --id train-xxx
# 从返回中获取:
#   LatestInstanceId (如 train-xxx-yyy) — 日志/事件查询必需
#   StartTime / EndTime — 用作日志时间范围

# 步骤 2: 使用 LatestInstanceId + 时间范围查询日志
./scripts/log/describe-logs.sh --region ap-shanghai --service TRAIN \
  --service-id train-xxx-yyy \
  --start-time "2026-03-10T02:50:56Z" --end-time "2026-03-10T03:30:00Z" --limit 50

# 步骤 3: 如需查看指定 Pod 日志，先获取 Pod 列表
./scripts/training/describe-training-task-pods.sh --region ap-shanghai --id train-xxx
# 从返回结果获取 Pod 名称

# 步骤 4: 使用 Pod 名称查询指定 Pod 日志
./scripts/log/describe-logs.sh --region ap-shanghai --service TRAIN \
  --service-id train-xxx-yyy --pod-name <pod-name> --limit 50

# 查看训练事件
./scripts/event/describe-events.sh --region ap-shanghai --service TRAIN \
  --service-id train-xxx-yyy --start-time "2026-03-10T02:50:56Z"
```

### 1.1 按状态查询训练任务

```bash
# ⚠️ 查询运行中的训练任务 → 优先用 Status filter
./scripts/training/describe-training-tasks.sh --region ap-shanghai --filters "Name=Status,Values=RUNNING"

# 查询失败的任务
./scripts/training/describe-training-tasks.sh --region ap-shanghai --filters "Name=Status,Values=FAILED"

# 查询活跃状态的任务（运行中+启动中+停止中）
./scripts/training/describe-training-tasks.sh --region ap-shanghai --filters "Name=Status,Values=RUNNING;STARTING;STOPPING"
```

### 2. 排查在线服务问题（标准流程：指定服务组 ID ms-xxx 时）

```bash
# 步骤 1: 查看服务组详情，获取服务实例 ID 和 Pod 名称
./scripts/service/describe-model-service-group.sh --region ap-shanghai --id ms-xxx
# 从 Services[].ServiceId 获取实例 ID，如 ms-xxx-1, ms-xxx-2

# 步骤 2: 使用服务实例 ID 查询日志
./scripts/log/describe-logs.sh --region ap-shanghai --service INFER --service-id ms-xxx-1 --limit 100

# 步骤 3: 如需指定 Pod，从步骤 1 返回中获取 Pod 名称
./scripts/log/describe-logs.sh --region ap-shanghai --service INFER --service-id ms-xxx-1 --pod-name <pod-name>

# 查看单个服务实例详情
./scripts/service/describe-model-service.sh --region ap-shanghai --service-id ms-xxx-1

# 查看服务调用信息
./scripts/service/describe-model-service-callinfo.sh --region ap-shanghai --service-group-id ms-xxx

# 查看推理事件
./scripts/event/describe-events.sh --region ap-shanghai --service INFER --service-id ms-xxx-1
```

### 2.1 按状态查询在线服务

```bash
# ⚠️ 查询异常服务 → 优先用 Status filter
./scripts/service/describe-model-service-groups.sh --region ap-shanghai --filters "Name=Status,Values=Abnormal"

# 查询正常运行的服务
./scripts/service/describe-model-service-groups.sh --region ap-shanghai --filters "Name=Status,Values=Normal"

# 查询活跃状态的服务
./scripts/service/describe-model-service-groups.sh --region ap-shanghai --filters "Name=Status,Values=Normal;Waiting;Pending"
```

### 3. 查看 Notebook 状态

```bash
# 查看 Notebook 列表
./scripts/notebook/describe-notebooks.sh --region ap-shanghai

# 查看某个 Notebook 详情
./scripts/notebook/describe-notebook.sh --region ap-shanghai --id nb-xxx
```

### 3.1 排查 Notebook 日志（标准流程）

```bash
# 步骤 1: 查看 Notebook 详情，获取 PodName 和 StartTime
./scripts/notebook/describe-notebook.sh --region ap-shanghai --id nb-xxx
# 从 NotebookDetail 获取:
#   PodName (如 nb-xxx-yyy) — 日志查询必需
#   StartTime — 用作日志时间范围起点

# 步骤 2: 使用 PodName + 时间范围查询日志
./scripts/log/describe-logs.sh --region ap-shanghai --service NOTEBOOK \
  --service-id nb-xxx-yyy --start-time "2026-03-17T19:23:21Z" --limit 50

# 查看 Notebook 事件
./scripts/event/describe-events.sh --region ap-shanghai --service NOTEBOOK \
  --service-id nb-xxx-yyy --start-time "2026-03-17T19:23:21Z"
```

### 3.1 按状态查询开发机

```bash
# ⚠️ 查询运行中的开发机 → 优先用 Status filter
./scripts/notebook/describe-notebooks.sh --region ap-shanghai --filters "Name=Status,Values=Running"

# 查询已停止的开发机
./scripts/notebook/describe-notebooks.sh --region ap-shanghai --filters "Name=Status,Values=Stopped"

# 查询活跃状态的开发机（运行中+启动中+停止中）
./scripts/notebook/describe-notebooks.sh --region ap-shanghai --filters "Name=Status,Values=Running;Starting;Stopping"
```

### 4. 查看资源与计费

```bash
# 查看所有资源组
./scripts/resource/describe-billing-resource-groups.sh --region ap-shanghai

# ⚠️ 查询有多少 GPU 资源组 / 哪些资源组有空闲资源 → 优先用 filter 排除空组
./scripts/resource/describe-billing-resource-groups.sh --region ap-shanghai --filters "Name=AvailableNodeCount,Values=1;2;3;4;5;6;7;8;9;10"

# 按名称模糊搜索资源组
./scripts/resource/describe-billing-resource-groups.sh --region ap-shanghai --filters "Name=ResourceGroupName,Values=test,Fuzzy=true"

# 查看资源组节点
./scripts/resource/describe-billing-resource-group.sh --region ap-shanghai --resource-group-id rg-xxx
```

## 参考资料

- 脚本参数详细说明与过滤条件：`references/tccli-tione-reference.md`
- 控制台 URL 格式、地域 ID 映射、工作空间说明：`references/tione-console-guide.md`
