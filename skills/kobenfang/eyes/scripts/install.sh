#!/bin/bash
# Eyes Skill 安装脚本（简化版）
#
# 用途：创建安装标记文件。
#       注册 cron 定时器由 agent 动态完成（推荐方式：回复「帮我安装」）。
#       此脚本仅用于手动安装场景。
#
# 用法：bash install.sh
# 注意：推荐直接回复「帮我安装」由 AI 自动完成配置，无需手动运行此脚本。

WORKDIR="${WORKDIR:-$(cd "$(dirname "$0")/.." && pwd)}"
MARKER_FILE="$WORKDIR/workspace/memory/eyes-installed"

echo "==> Eyes 安装脚本..."

INSTALL_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
mkdir -p "$(dirname "$MARKER_FILE")"
cat > "$MARKER_FILE" <<EOF
# Eyes skill 安装确认
安装时间：$INSTALL_TIME
EOF

echo "    ✓ 标记文件已创建：$MARKER_FILE"
echo ""
echo "==> 注意：推荐直接回复「帮我安装」由 AI 完成定时器注册。"
echo "    如需手动注册，请运行 openclaw cron add 命令（参考 SKILL.md）。"
