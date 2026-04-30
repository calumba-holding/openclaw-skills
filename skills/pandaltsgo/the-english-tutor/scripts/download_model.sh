#!/usr/bin/env bash
#
# 下载 SenseVoice Small 模型到本地
# 用法: bash download_model.sh [目标目录]
#
# 目标目录可通过环境变量配置：
#   SENSE_VOICE_MODEL_DIR=~/.local/share/sense-voice-model
# 或通过第一个参数传入
#
set -e

DEST="${SENSE_VOICE_MODEL_DIR:-${1:-"$HOME/.local/share/sense-voice-model"}}"
BASE_URL="https://modelscope.cn/api/v1/models/xiaowangge/sherpa-onnx-sense-voice-small/resolve/master"

mkdir -p "$DEST"
echo "📦 下载到: $DEST"
echo "   （可通过环境变量 SENSE_VOICE_MODEL_DIR 自定义路径）"
echo

echo "⬇️  tokens.txt (~309KB)..."
curl -L "$BASE_URL/tokens.txt" -o "$DEST/tokens.txt"
echo "✅ tokens.txt done"

echo ""
echo "⬇️  model.onnx (~895MB，这可能需要几分钟)..."
curl -L "$BASE_URL/model.onnx" -o "$DEST/model.onnx"
echo "✅ model.onnx done"

SIZE=$(du -sh "$DEST" | cut -f1)
echo ""
echo "🎉 下载完成！总计: $SIZE"
echo ""
echo "📝 下一步：配置环境变量"
echo "   export SENSE_VOICE_MODEL_DIR=\"$DEST\""
echo "   然后运行: python3 scripts/check_env.py"
