---
name: backup-system
description: 備份系統關鍵設定與工作區資料。當用戶要求「備份系統」、「backup system」或需要手動保存當前狀態時使用。
---

# 備份系統 (Backup System)

此技能用於統一備份 OpenClaw 的設定檔 (`~/.openclaw`) 以及工作區資料 (`~/clawd`)。

## 使用方法

1. 執行 `scripts/backup.sh` 腳本。
2. 該腳本會自動在 `~/openclaw_backups/` 目錄下建立一個以當前時間命名的資料夾（格式：`yyyymmddhhmm`）。
3. 備份完成後，向用戶回報備份的路徑。

## 腳本說明

- **位置**: `scripts/backup.sh`
- **行為**: 建立目錄並使用 `cp -R` 進行遞歸複製。
