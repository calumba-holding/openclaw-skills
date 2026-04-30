---
name: "channel-company-query-python"
description: "查询渠道单位信息（Python3实现）。通过名称模糊搜索获取列表，或通过ID查询详情。包括CRM账号、站点标识和环境URL。"
metadata:
  {"openclaw": {"requires": {"env": ["LEJIAN_AUTH_TOKEN"]}}}
---

# Channel Company Query (Python3)

## 功能

- **搜索**：按名称模糊搜索渠道单位
- **详情**：通过ID查询渠道单位完整信息
- **格式化**：输出搜索列表和详情信息

## 首次配置

使用前需要配置 API Token：

```bash
openclaw config set env.vars.LEJIAN_AUTH_TOKEN <你的token>
```

重启 gateway 后生效。

## 环境变量校验

```bash
python3 scripts/channel_company_query.py --help
```

## LLM 调用流程

### 步骤1：搜索渠道单位
```bash
python3 scripts/channel_company_query.py --name "示例公司"
```
- 多个结果：返回列表(含序号、ID、名称)，提示用户选择
- 单个结果：自动查详情并返回

### 步骤2：根据用户选择的序号，用对应ID查询详情
```bash
python3 scripts/channel_company_query.py --detail 1234567
```

## 技术要求

- Python 3.x
- 标准库 urllib
- 有效的 Authorization token（配置在 `LEJIAN_AUTH_TOKEN` 环境变量中）