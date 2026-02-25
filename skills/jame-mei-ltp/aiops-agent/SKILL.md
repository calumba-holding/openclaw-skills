# AIOps Agent - AI驱动的智能运维系统

> 将传统被动告警升级为主动预测、智能诊断和自动化治理的新一代AIOps平台

---

## 📋 概述

**AIOps Agent**是一个基于AI的智能运维代理系统，通过多维度数据采集、智能分析和自动化执行，实现：

- ⚡ **主动预警** - 提前1-3小时发现潜在风险
- 🔍 **智能诊断** - 自动化根因分析，减少70%+排查时间
- 🌙 **风险前置** - 减少80%+凌晨告警
- 🤖 **自动化治理** - 支持自动修复和半自动化运维

---

## 🚀 快速开始

### 1. 环境要求

```bash
# 必需
- Python 3.11+
- Docker & Docker Compose
- Kubernetes 集群（可选）

# 依赖服务
- Prometheus（指标）
- Loki（日志）
- PostgreSQL（存储）
- Redis（缓存）
```

### 2. 本地启动

```bash
# 克隆项目
git clone <your-repo-url>
cd sre-agent

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入必要配置

# 启动所有服务（Docker Compose）
make up

# 或手动启动
docker-compose up -d

# 查看日志
docker-compose logs -f sre-agent
```

### 3. 访问服务

```
API:      http://localhost:8000
文档:     http://localhost:8000/docs
健康检查: http://localhost:8000/health
```

---

## 🎯 核心功能

### 1. 多维度数据采集

```yaml
# config/config.yaml
data_sources:
  prometheus:
    url: "http://prometheus:9090"
    metrics:
      - cpu_usage
      - memory_usage
      - disk_io
      - network_traffic
  
  loki:
    url: "http://loki:3100"
    query: '{namespace="production"}'
  
  kubernetes:
    enabled: true
    events: true
```

### 2. AI驱动分析

**异常检测:**
```python
# 使用多算法检测异常
from src.cognition.anomaly_detector import AnomalyDetector

detector = AnomalyDetector()
anomalies = detector.detect(
    metric_name="cpu_usage",
    values=cpu_data,
    sensitivity=0.95
)
```

**趋势预测:**
```python
# 预测未来1-6小时走势
from src.cognition.predictor import Predictor

predictor = Predictor()
forecast = predictor.predict(
    metric_name="memory_usage",
    horizon_hours=3
)
```

**根因分析:**
```python
# LLM驱动的智能根因分析
from src.cognition.rca_engine import RCAEngine

rca = RCAEngine()
analysis = rca.analyze(
    anomaly=anomaly_event,
    context={
        'metrics': related_metrics,
        'logs': error_logs,
        'events': k8s_events
    }
)
```

### 3. 智能决策

```python
# 风险评估
from src.decision.risk_assessment import RiskAssessor

assessor = RiskAssessor()
risk = assessor.evaluate(
    anomaly=anomaly,
    impact_analysis=impact,
    historical_cases=similar_cases
)

# 风险等级: CRITICAL / HIGH / MEDIUM / LOW
```

### 4. 自动化执行

```python
# 自动修复
from src.action.executor import ActionExecutor

executor = ActionExecutor()
result = executor.execute(
    action_type="restart_pod",
    target="production/nginx-deployment",
    approval_required=True
)
```

---

## 📊 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                   SRE Agent 系统架构                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │  Perception  │──▶│  Cognition   │──▶│  Decision   │ │
│  │  (感知层)     │   │  (认知层)     │   │  (决策层)    │ │
│  └──────────────┘   └──────────────┘   └─────────────┘ │
│         │                   │                   │       │
│         ▼                   ▼                   ▼       │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Action (行动层)                     │   │
│  └─────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘

数据源: Prometheus, Loki, Kubernetes, Jaeger
AI引擎: Baseline, Anomaly Detection, Prediction, RCA
执行器: Kubernetes API, Shell, Playbooks
```

### 核心组件

1. **Perception (感知层)**
   - 指标采集器
   - 日志聚合器
   - 事件监听器

2. **Cognition (认知层)**
   - 基线引擎
   - 异常检测器
   - 趋势预测器
   - 根因分析引擎

3. **Decision (决策层)**
   - 风险评估器
   - 行动规划器
   - 知识库

4. **Action (行动层)**
   - 执行引擎
   - 审批流程
   - 反馈循环

---

## 🛠️ 使用场景

### 场景1: CPU使用率异常预警

```python
# 1. 系统检测到CPU使用率异常上升
anomaly = {
    'metric': 'cpu_usage',
    'current_value': 85.2,
    'baseline': 45.3,
    'deviation': 3.5  # 标准差
}

# 2. 预测趋势
forecast = predictor.predict('cpu_usage', hours=2)
# 预测结果: 2小时后将达到95%

# 3. 根因分析
root_cause = rca.analyze(anomaly)
# 可能原因: 某个Pod内存泄漏导致频繁GC

# 4. 生成行动方案
actions = planner.generate_actions(root_cause)
# 建议: 重启问题Pod

# 5. 发送告警（提前预警）
alert.send(
    level='WARNING',
    message='预测2小时后CPU将达到95%，建议立即处理',
    actions=actions
)
```

### 场景2: 内存泄漏自动诊断

```python
# 1. 检测到内存持续上升
anomaly = detector.detect_trend(
    metric='memory_usage',
    pattern='monotonic_increase'
)

# 2. 关联分析
context = correlator.analyze({
    'metrics': ['heap_usage', 'gc_time'],
    'logs': loki.query('{app="backend"} |= "OutOfMemory"'),
    'events': k8s.get_pod_events('backend-pod')
})

# 3. LLM分析
diagnosis = llm.analyze(f"""
根据以下信息诊断内存泄漏:
- 内存使用率: {anomaly}
- 堆内存: {context['heap_usage']}
- GC时间: {context['gc_time']}
- 错误日志: {context['logs']}
""")

# 4. 自动执行修复
if diagnosis.confidence > 0.8:
    executor.restart_pod('backend-pod')
```

### 场景3: 磁盘空间预测性扩容

```python
# 1. 预测磁盘使用
forecast = predictor.predict('disk_usage', days=7)

# 2. 风险评估
if forecast.max_value > 80:
    risk = assessor.evaluate(
        metric='disk_usage',
        forecast=forecast,
        impact='HIGH'  # 磁盘满会导致服务不可用
    )
    
    # 3. 生成扩容方案
    plan = planner.create_scaling_plan(
        resource='disk',
        current_size='100Gi',
        target_size='200Gi',
        urgency=risk.level
    )
    
    # 4. 提交审批（关键操作）
    approval = workflow.submit_for_approval(plan)
```

---

## 📚 配置说明

### 基础配置 (config/config.yaml)

```yaml
# AI引擎配置
ai:
  llm:
    provider: "openai"  # openai / azure / local
    model: "gpt-4"
    temperature: 0.3
  
  anomaly_detection:
    algorithms:
      - statistical  # 统计方法
      - isolation_forest  # 孤立森林
      - prophet  # Facebook Prophet
    sensitivity: 0.95
  
  prediction:
    model: "prophet"  # prophet / lstm / arima
    horizon_hours: 6

# 告警配置
alerting:
  channels:
    - type: "slack"
      webhook_url: "${SLACK_WEBHOOK}"
    - type: "email"
      smtp_server: "smtp.gmail.com"
      recipients: ["oncall@example.com"]
  
  rules:
    - name: "高风险立即通知"
      condition: "risk_level == 'CRITICAL'"
      channels: ["slack", "email", "phone"]
    
    - name: "中风险白天通知"
      condition: "risk_level == 'HIGH' and 8 <= hour <= 20"
      channels: ["slack"]

# 自动化配置
automation:
  approval_required:
    - "scale_deployment"
    - "delete_resource"
    - "rollback_deployment"
  
  auto_approve:
    - "restart_pod"
    - "clear_cache"
```

### Prometheus查询 (config/promql_queries.yaml)

```yaml
cpu_usage:
  query: "rate(container_cpu_usage_seconds_total[5m])"
  threshold: 0.8

memory_usage:
  query: "container_memory_usage_bytes / container_spec_memory_limit_bytes"
  threshold: 0.85

disk_io:
  query: "rate(container_fs_reads_bytes_total[5m]) + rate(container_fs_writes_bytes_total[5m])"
  threshold: 100000000  # 100MB/s
```

---

## 🔧 开发指南

### 添加新的异常检测算法

```python
# src/cognition/anomaly_detector.py

from src.cognition.base import BaseDetector

class MyCustomDetector(BaseDetector):
    """自定义异常检测器"""
    
    def detect(self, data, **kwargs):
        # 实现检测逻辑
        threshold = kwargs.get('threshold', 0.95)
        
        # 你的算法
        anomalies = []
        for point in data:
            if self._is_anomaly(point, threshold):
                anomalies.append(point)
        
        return anomalies
    
    def _is_anomaly(self, point, threshold):
        # 判断逻辑
        pass

# 注册到系统
from src.cognition import register_detector
register_detector('my_custom', MyCustomDetector)
```

### 添加新的执行器

```python
# src/action/executors/my_executor.py

from src.action.base import BaseExecutor

class MyExecutor(BaseExecutor):
    """自定义执行器"""
    
    def execute(self, action, context):
        # 实现执行逻辑
        target = action['target']
        params = action['params']
        
        # 执行操作
        result = self._do_action(target, params)
        
        return {
            'success': True,
            'result': result,
            'timestamp': datetime.now()
        }
```

---

## 📈 监控与告警

### Grafana 仪表盘

系统提供预配置的Grafana仪表盘：

```
http://localhost:3000

仪表盘:
- AIOps Overview: 系统总览
- Anomaly Detection: 异常检测
- Risk Assessment: 风险评估
- Action History: 执行历史
```

### 告警通道

支持多种告警方式：

| 通道 | 用途 | 配置 |
|------|------|------|
| Slack | 日常通知 | SLACK_WEBHOOK |
| Email | 重要告警 | SMTP配置 |
| 企业微信 | 中国团队 | WECHAT_WEBHOOK |
| PagerDuty | 值班轮换 | PAGERDUTY_KEY |

---

## 🐛 故障排查

### 常见问题

**Q: 异常检测误报率高？**

A: 调整敏感度参数：
```yaml
ai:
  anomaly_detection:
    sensitivity: 0.9  # 降低到0.9（默认0.95）
```

**Q: LLM响应慢？**

A: 使用本地模型或增加超时：
```yaml
ai:
  llm:
    timeout: 30  # 增加到30秒
    cache_enabled: true  # 启用缓存
```

**Q: Kubernetes权限不足？**

A: 检查RBAC配置：
```bash
kubectl apply -f k8s/rbac.yaml
```

---

## 🧪 测试

```bash
# 运行所有测试
make test

# 单独测试模块
pytest tests/test_anomaly_detector.py -v

# 覆盖率报告
make coverage
```

---

## 📦 部署

### Docker部署

```bash
# 构建镜像
make build

# 推送到仓库
docker push your-registry/sre-agent:v1.0

# 运行
docker run -d \
  -p 8000:8000 \
  -e PROMETHEUS_URL=http://prometheus:9090 \
  your-registry/sre-agent:v1.0
```

### Kubernetes部署

```bash
# 应用配置
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 检查状态
kubectl get pods -n aiops
```

---

## 🤝 贡献

欢迎贡献代码、提交Issue或功能建议！

---

## 📄 许可证

MIT License

---

## 👥 作者

**James Mei**
- 📧 Email: meijinmeng@126.com
- 📝 Blog: https://www.cnblogs.com/Jame-mei
- 🐙 GitHub: [Your GitHub]

---

## 🔗 相关资源

- [README.md](./README.md) - 完整文档
- [QUICKSTART.md](./docs/QUICKSTART.md) - 快速开始
- [CONFIGURATION.md](./docs/CONFIGURATION.md) - 配置指南
- [IMPLEMENTATION.md](./docs/IMPLEMENTATION.md) - 实现细节

---

_让AI为运维赋能！🚀_
