# TI-ONE 脚本参数参考

本文档列出各脚本支持的详细参数和过滤条件。

## 训练任务模块

### describe-training-tasks.sh

查询训练任务列表。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--region` | 地域 | 环境变量配置值 |
| `--limit` | 返回数量，最大 50 | 10 |
| `--offset` | 偏移量 | 0 |
| `--order` | 排序方向：ASC / DESC | DESC |
| `--order-field` | 排序字段：CreateTime / UpdateTime / StartTime | UpdateTime |
| `--filters` | 过滤条件 | - |
| `--tag-filters` | 标签过滤条件（JSON 数组） | - |

**Filters 支持的 Name 值：**

| Name | 说明 | 可选 Values |
|------|------|------------|
| Name | 按任务名称模糊匹配 | 任意字符串 |
| Id | 按任务 ID 过滤 | `train-xxx` |
| Status | 按状态过滤 | `SUBMITTING`, `PENDING`, `STARTING`, `RUNNING`, `STOPPING`, `STOPPED`, `FAILED`, `SUCCEED`, `SUBMIT_FAILED` |
| ResourceGroupId | 按资源组 ID 过滤 | `trsg-xxx` |
| Creator | 按创建者 uin 过滤 | UIN 数字 |
| ChargeType | 按计费类型过滤 | `PREPAID`(预付费), `POSTPAID_BY_HOUR`(后付费) |
| CHARGE_STATUS | 按计费状态过滤 | `NOT_BILLING`, `BILLING`, `ARREARS_STOP` |

### describe-training-task.sh

查询训练任务详情。

| 参数 | 说明 | 必填 |
|------|------|------|
| `--region` | 地域 | 否 |
| `--id` | 训练任务 ID | 是 |

### describe-training-task-pods.sh

查询训练任务 Pod 列表。

| 参数 | 说明 | 必填 |
|------|------|------|
| `--region` | 地域 | 否 |
| `--id` | 训练任务 ID | 是 |

## 在线服务模块

### describe-model-service-groups.sh

查询服务组列表。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--region` | 地域 | 环境变量配置值 |
| `--limit` | 返回数量，最大 100 | 20 |
| `--offset` | 偏移量 | 0 |
| `--order` | 排序方向：ASC / DESC | - |
| `--order-field` | 排序字段：CreateTime / UpdateTime | - |
| `--search-word` | 按名称搜索（转为 ServiceGroupName filter） | - |
| `--filters` | 过滤条件 | - |
| `--tag-filters` | 标签过滤条件（JSON 数组） | - |

**Filters 支持的 Name 值：**

| Name | 说明 |
|------|------|
| ClusterId | 按集群 ID 过滤 |
| ServiceId | 按服务 ID 过滤 |
| ServiceGroupName | 按服务组名称过滤 |
| ServiceGroupId | 按服务组 ID 过滤 |
| Status | 按状态过滤：`Waiting`, `Pending`, `Normal`, `Abnormal`, `Stopping` |
| CreatedBy | 按创建者 uin 过滤 |
| ModelVersionId | 按模型版本 ID 过滤 |

### describe-model-service-group.sh

查询单个服务组详情。

| 参数 | 说明 | 必填 |
|------|------|------|
| `--region` | 地域 | 否 |
| `--id` | 服务组 ID | 是 |

### describe-model-service.sh

查询单个服务详情。

| 参数 | 说明 | 必填 |
|------|------|------|
| `--region` | 地域 | 否 |
| `--service-id` | 服务 ID | 是 |
| `--service-group-id` | 服务组 ID | 否 |

### describe-model-service-callinfo.sh

查询服务调用信息。

| 参数 | 说明 | 必填 |
|------|------|------|
| `--region` | 地域 | 否 |
| `--service-group-id` | 服务组 ID | 是 |

## Notebook 模块

### describe-notebooks.sh

查询 Notebook 列表。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--region` | 地域 | 环境变量配置值 |
| `--limit` | 返回数量 | 10 |
| `--offset` | 偏移量 | 0 |
| `--order` | 排序方向：ASC / DESC | DESC |
| `--order-field` | 排序字段：CreateTime / UpdateTime | UpdateTime |
| `--filters` | 过滤条件 | - |
| `--tag-filters` | 标签过滤条件（JSON 数组） | - |

**Filters 支持的 Name 值：**

| Name | 说明 | 可选 Values |
|------|------|------------|
| Name | 按名称模糊匹配 | 任意字符串 |
| Id | 按 Notebook ID 过滤 | `nb-xxx` |
| Status | 按状态过滤 | `Starting`, `Submitting`, `Running`, `Stopping`, `Stopped`, `Failed`, `SubmitFailed` |
| Creator | 按创建者 uin 过滤 | UIN 数字 |
| ChargeType | 按计费类型过滤 | `PREPAID`, `POSTPAID_BY_HOUR` |
| ChargeStatus | 按计费状态过滤 | `NOT_BILLING`, `BILLING`, `BILLING_STORAGE`, `ARREARS_STOP` |
| DefaultCodeRepoId | 按默认代码仓库 ID 过滤 | `cr-xxx` |
| AdditionalCodeRepoId | 按关联代码仓库 ID 过滤 | `cr-xxx` |
| LifecycleScriptId | 按生命周期脚本 ID 过滤 | `ls-xxx` |

### describe-notebook.sh

查询 Notebook 详情。

| 参数 | 说明 | 必填 |
|------|------|------|
| `--region` | 地域 | 否 |
| `--id` | Notebook ID | 是 |

## 资源组模块

### describe-billing-resource-groups.sh

查询资源组列表。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--region` | 地域 | 环境变量配置值 |
| `--limit` | 返回数量 | 20 |
| `--offset` | 偏移量 | 0 |
| `--search-word` | 模糊查找资源组 ID 或名称 | - |
| `--filters` | 过滤条件 | - |

**Filters 支持的 Name 值：**

| Name | 说明 |
|------|------|
| ResourceGroupId | 按资源组 ID 过滤（Fuzzy=true 时支持模糊查询） |
| ResourceGroupName | 按资源组名称过滤（Fuzzy=true 时支持模糊查询） |
| AvailableNodeCount | 按可用节点数量过滤 |

### describe-billing-resource-group.sh

查询资源组节点列表。

| 参数 | 说明 | 必填/默认值 |
|------|------|------------|
| `--region` | 地域 | 否 |
| `--resource-group-id` | 资源组 ID | 是 |
| `--limit` | 返回数量 | 20 |
| `--offset` | 偏移量 | 0 |
| `--order` | 排序方向：ASC / DESC | DESC |
| `--order-field` | 排序字段：CreateTime / ExpireTime | CreateTime |
| `--filters` | 过滤条件 | - |

**Filters 支持的 Name 值：**

| Name | 说明 |
|------|------|
| InstanceId | 按节点 ID 过滤（Fuzzy=true 时支持模糊查询） |
| InstanceStatus | 按节点状态过滤（如 `RUNNING`） |

## 模型仓库模块

### describe-training-model-versions.sh

查询模型版本列表。

| 参数 | 说明 | 必填 |
|------|------|------|
| `--region` | 地域 | 否 |
| `--training-model-id` | 模型 ID | 是 |
| `--filters` | 过滤条件 | 否 |

**Filters 支持的 Name 值：**

| Name | 说明 | 可选 Values |
|------|------|------------|
| TrainingModelVersionId | 按模型版本 ID 过滤 | `mv-xxx` |
| ModelVersionType | 按版本类型过滤 | `NORMAL`(通用), `ACCELERATE`(加速) |
| ModelFormat | 按模型格式过滤 | `TORCH_SCRIPT`, `PYTORCH`, `DETECTRON2`, `SAVED_MODEL`, `FROZEN_GRAPH`, `PMML` |
| AlgorithmFramework | 按算法框架过滤 | `TENSORFLOW`, `PYTORCH`, `DETECTRON2` |

### describe-training-model-version.sh

查询模型版本详情。

| 参数 | 说明 | 必填 |
|------|------|------|
| `--region` | 地域 | 否 |
| `--training-model-version-id` | 模型版本 ID | 是 |

## 数据集模块

### describe-datasets.sh

查询数据集列表。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--region` | 地域 | 环境变量配置值 |
| `--limit` | 返回数量，最大 200 | 20 |
| `--offset` | 偏移量 | 0 |
| `--order` | 排序值：Asc / Desc | Desc |
| `--order-field` | 排序字段：CreateTime / UpdateTime | CreateTime |
| `--filters` | 过滤条件 | - |
| `--dataset-ids` | 数据集 ID 列表 | - |

**Filters 支持的 Name 值：**

| Name | 说明 | 可选 Values |
|------|------|------------|
| DatasetName | 按数据集名称过滤 | 任意字符串 |
| DatasetScope | 按范围过滤 | `SCOPE_DATASET_PRIVATE`(私有), `SCOPE_DATASET_PUBLIC`(公共) |

## 日志模块

### describe-logs.sh

查询日志。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--region` | 地域 | 环境变量配置值 |
| `--service` | 服务类型：TRAIN / NOTEBOOK / INFER / BATCH | 必填 |
| `--service-id` | 服务实例 ID（注意：须用实例级 ID） | 必填 |
| `--pod-name` | Pod 名称（支持尾部通配符 *） | - |
| `--start-time` | 开始时间（RFC3339 格式） | 当前时间前一小时 |
| `--end-time` | 结束时间（RFC3339 格式） | 当前时间 |
| `--limit` | 返回条数，最大 1000 | 100 |
| `--offset` | 偏移量 | 0 |
| `--order` | 排序方向：ASC / DESC | DESC |
| `--filters` | 过滤条件 | - |

**Filters 支持的 Name 值：**

| Name | 说明 |
|------|------|
| Key | 按关键字过滤日志（多值时表示同时满足） |

## 事件模块

### describe-events.sh

查询事件。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--region` | 地域 | 环境变量配置值 |
| `--service` | 服务类型：TRAIN / NOTEBOOK / INFER / BATCH | 必填 |
| `--service-id` | 服务实例 ID | - |
| `--start-time` | 最早发生时间（RFC3339 格式） | 前一天 |
| `--end-time` | 最晚发生时间（RFC3339 格式） | 当前时间 |
| `--limit` | 返回条数，最大 100 | 100 |
| `--offset` | 偏移量 | 0 |
| `--order` | 排序方向：ASC / DESC | DESC |
| `--order-field` | 排序字段：FirstTimestamp / LastTimestamp | LastTimestamp |
| `--filters` | 过滤条件 | - |

**Filters 支持的 Name 值：**

| Name | 说明 | 可选 Values |
|------|------|------------|
| ResourceKind | 按资源类型过滤 | `Deployment`, `Replicaset`, `Pod` 等 |
| Type | 按事件类型过滤 | `Normal`, `Warning` |

## 控制台链接工具

### generate-console-url.sh

生成控制台详情页 URL。

| 参数 | 说明 | 必填/默认值 |
|------|------|------------|
| `--type` | 资源类型：training / notebook / service / resource-group | 是 |
| `--id` | 资源 ID | 是 |
| `--region` | 地域 | 默认值 |
| `--workspace-id` | 工作空间 ID | 0 |
