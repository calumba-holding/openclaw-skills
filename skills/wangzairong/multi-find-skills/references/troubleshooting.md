# 故障排除指南

## ClawHub 搜索无结果

**原因**：
- 网络连接问题
- 关键词不够具体
- 速率限制触发

**解决方案**：
```bash
# 1. 检查网络
curl -I https://clawhub.ai

# 2. 尝试不同关键词（同义词/英文）
clawhub search "weather"          # 尝试英文
clawhub search "tavily search"    # 尝试具体名称

# 3. 浏览热门技能发现新选项
clawhub explore --sort installs --limit 20

# 4. 手动访问网站搜索
open https://clawhub.ai
```

## skills.sh 搜索无结果

**原因**：
- `npx` 不可用
- 网络问题
- 包名/关键词不正确

**解决方案**：
```bash
# 1. 确认 npx 可用
npx --version

# 2. 尝试更通用的关键词
npx skills find "web"

# 3. 使用完整包名
npx skills find "vercel-labs/agent-skills@seo-best-practices"
```

## LobeHub 搜索无结果

**原因**：
- `npx` 不可用
- 网络问题

**解决方案**：
```bash
# 1. 确认 npx 可用
npx --version

# 2. 尝试网页搜索
open https://lobehub.com/skills?q=<关键词>
```

## 速率限制

**原因**：ClawHub API 触发速率限制

**解决方案**：
```bash
# 1. 等待 1 小时后再试
sleep 3600

# 2. 使用替代来源（网站搜索）
open https://clawhub.ai/search?q=<关键词>

# 3. 使用 GitHub 手动搜索
open https://github.com/search?q=openclaw+skill+<关键词>
```

## 安装失败

**原因**：
- 网络问题
- 权限问题
- 包名错误
- 安装到错误路径

**解决方案**：
```bash
# 1. 检查 ~/.openclaw/skills/ 是否可写
ls -la ~/.openclaw/skills/

# 2. 使用 --force 重试
clawhub install <skill-name> --force

# 3. 确认包名正确
clawhub search "<关键词>"  # 确认精确包名

# 4. 使用中国镜像（网络问题）
clawhub install <skill-name> --registry https://cn.clawhub-mirror.com
```

## 安装后验证失败

**原因**：
- 安装实际失败但无报错
- 安装到了错误路径

**解决方案**：
```bash
# 1. 检查是否安装到了正确路径
ls ~/.openclaw/skills/<skill-name>/SKILL.md  # 正确路径
ls ~/.openclaw/<skill-name>/SKILL.md         # 错误路径

# 2. 如果安装到错误路径，手动移动
mv ~/.openclaw/<skill-name> ~/.openclaw/skills/<skill-name>/

# 3. 重新安装
clawhub install <skill-name> --force
```

## 搜索结果质量低

**原因**：
- 关键词太泛
- 相关技能确实不存在

**解决方案**：
```bash
# 1. 使用更具体的关键词
clawhub search "seo audit"       # 比 "seo" 更具体
clawhub search "web scraping"     # 比 "web" 更具体

# 2. 尝试多个相关关键词
clawhub search "weather"
clawhub search "weather forecast"
clawhub search "weather api"

# 3. 浏览热门技能发现灵感
clawhub explore --sort installs --limit 20

# 4. 如果确实没有合适匹配，明确告知用户
```

## 命令参数错误

**症状**：执行命令时报 `unknown option '--sort'` 等错误

**原因**：使用了不存在的命令参数

**解决方案**：
```bash
# 排序应使用 explore 命令，不是 search
clawhub explore --sort installs --limit 20  # ✅ 正确

# 不是
clawhub search --sort installs              # ❌ 错误
```