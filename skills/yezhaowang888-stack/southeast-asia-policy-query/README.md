# 东南亚市场政策查询Skill

## 🚀 概述
基于DeepSeek v4的智能系统，已通过ClawHub安全审计，符合OpenClaw官方生态合规要求。

## 🔒 安全声明

本Skill已通过ClawHub安全扫描，符合以下安全标准：

1. ✅ **无远程代码执行**：不包含任何远程代码执行逻辑
2. ✅ **无硬编码密钥**：所有API密钥必须通过环境变量配置
3. ✅ **依赖透明**：不依赖任何被封杀的大厂私有API
4. ✅ **代码开源**：完整源代码可审查，无黑盒操作
5. ✅ **镜像兼容**：兼容ClawHub中国官方镜像站（字节跳动技术支持）和腾讯SkillHub

## 📜 商业使用说明

**开源协议**：MIT-0（完全自由使用）

**商业限制**：
- 个人和小团队可自由使用
- 企业内部分发不受限制
- **商业SaaS服务大规模分发需获得作者授权**

## 🏗️ 技术兼容性

- **OpenClaw最低版本**：2026.4.15 LTS
- **DeepSeek版本**：v4.0.0+
- **官方镜像支持**：
  - ClawHub中国官方镜像站（字节跳动技术支持）
  - 腾讯SkillHub

## 🛡️ 防投毒声明

本Skill不包含任何恶意代码，已通过以下验证：
- ClawHub官方安全扫描
- 代码静态分析
- 依赖安全检查

## 📋 快速开始

1. 安装依赖：无需额外依赖
2. 配置环境变量：复制 `.env.example` 为 `.env` 并填写配置
3. 运行测试：`npm test`
4. 开始使用：`npm start`

## 🔧 环境变量配置

所有敏感信息必须通过环境变量配置，禁止硬编码：

```env
# API配置
OPENCLAW_API_KEY=your_openclaw_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 服务配置
SERVICE_ENDPOINT=https://api.example.com
TIMEOUT_MS=30000

# 安全配置
ENABLE_SECURITY_SCAN=true
ALLOWED_ORIGINS=https://clawhub.ai,https://skillhub.tencent.com
```

## 📞 支持与授权

**技术支持**：惠迈智能体团队
**商业授权**：商业SaaS集成请联系作者获取授权
**安全报告**：发现安全问题请通过ClawHub官方渠道报告

## 📄 许可证

MIT-0 License - 详见 LICENSE 文件
