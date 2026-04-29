---
name: Elastic Search
summary: 从日志搜索工具到'企业搜索层'——Elastic如何重新定义数据检索基础设施
read_when:
  - "研究开源软件的开源核心商业模式（open-core）"
  - "分析搜索和可观测性市场的竞争格局（vs Splunk vs Datadog）"
  - "了解企业级搜索的技术栈选型"
  - "探讨ELK Stack（Elasticsearch + Logstash + Kibana）的技术生态"
---

# Elastic Search

从日志搜索工具到'企业搜索层'——Elastic如何重新定义数据检索基础设施。

## 历史时间线

- 2010年：Shay Banon发布Elasticsearch 0.0.1，源于个人项目Compass的失败教训
- 2012年：成立Elastic NV公司，开始商业化
- 2015年：发布Elastic Stack（原ELK Stack），统一品牌
- 2018年10月：纽交所上市（ESTC），首日市值约56亿美元
- 2019年：修改开源许可证（从Apache 2.0改为SSPL/ELv2），回应云厂商搭便车问题
- 2021年：推出Elastic Cloud（托管服务），加速向SaaS转型
- 2023年：整合AI能力（Elastic AI Assistant），将LLM接入可观测性和安全工作流

## 商业模式

开源核心（open-core）模式。免费版：Elasticsearch核心搜索引擎。商业版：Elastic Stack X-Pack（安全、告警、机器学习、APM）+ Elastic Cloud（托管SaaS）。三大应用场景：可观测性（日志/指标/链路追踪，对标Splunk）、企业搜索（站点搜索/文档搜索）、安全（SIEM/终端安全）。订阅制收入占比超70%。

## 护城河分析

全文搜索领域的事实标准——几乎所有现代应用搜索都基于或兼容Elasticsearch；开源社区的开发者惯性——从学习阶段到生产部署的自然升级路径；开源许可证变更（SSPL）有效阻止了云厂商的免费搭车；在可观测性市场的早期布局形成客户锁定。

## 关键数据

2024财年营收约12亿美元，同比增长约18%；客户超18,000家（含75%的财富100强）；全球贡献者社区超3,000人；GitHub上Elasticsearch超67,000 stars；日均搜索查询量超万亿次。

## 有趣事实

- Shay Banon创建Elasticsearch的初衷是因为他妻子在做厨师求职网站时，他需要一个更好的搜索工具——结果这个'家庭项目'变成了百亿美元公司
- Netflix每天产生超1PB的日志数据，其中90%通过Elasticsearch处理——这是全球最大的Elasticsearch部署之一
