#!/bin/bash
# 統一備份腳本
TIMESTAMP=$(date +%Y%m%d%H%M)
BACKUP_ROOT="$HOME/openclaw_backups"
TARGET_DIR="$BACKUP_ROOT/$TIMESTAMP"

echo "正在開始備份到: $TARGET_DIR"

mkdir -p "$TARGET_DIR"

# 備份設定檔
if [ -d "$HOME/.openclaw" ]; then
    cp -R "$HOME/.openclaw" "$TARGET_DIR/.openclaw"
    echo "- 已備份 .openclaw"
else
    echo "- 警告: 找不到 $HOME/.openclaw"
fi

# 備份工作區
if [ -d "$HOME/clawd" ]; then
    cp -R "$HOME/clawd" "$TARGET_DIR/clawd"
    echo "- 已備份 clawd"
else
    echo "- 警告: 找不到 $HOME/clawd"
fi

echo "備份完成！路徑: $TARGET_DIR"
