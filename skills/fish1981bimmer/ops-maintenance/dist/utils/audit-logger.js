/**
 * 审计日志工具
 *
 * 记录所有运维操作，用于审计和问题排查
 */
import { join } from 'path';
import { existsSync, mkdirSync, appendFileSync, readFileSync } from 'fs';
/**
 * 审计日志管理器
 */
export class AuditLogger {
    logDir;
    logFile;
    constructor(logDir) {
        this.logDir = logDir || join(process.env.HOME || '~', '.config/ops-maintenance/logs');
        this.logFile = join(this.logDir, 'audit.log');
        // 确保日志目录存在
        if (!existsSync(this.logDir)) {
            mkdirSync(this.logDir, { recursive: true });
        }
    }
    /**
     * 记录操作
     */
    log(entry) {
        const logLine = JSON.stringify(entry) + '\n';
        appendFileSync(this.logFile, logLine);
    }
    /**
     * 记录成功操作
     */
    logSuccess(operation, server, command, duration, metadata) {
        this.log({
            timestamp: new Date().toISOString(),
            operation,
            server,
            command,
            status: 'success',
            duration,
            metadata
        });
    }
    /**
     * 记录失败操作
     */
    logFailure(operation, server, error, command, metadata) {
        this.log({
            timestamp: new Date().toISOString(),
            operation,
            server,
            command,
            status: 'failure',
            error,
            metadata
        });
    }
    /**
     * 记录部分成功操作
     */
    logPartial(operation, server, error, command, duration, metadata) {
        this.log({
            timestamp: new Date().toISOString(),
            operation,
            server,
            command,
            status: 'partial',
            duration,
            error,
            metadata
        });
    }
    /**
     * 查询日志
     */
    queryLogs(filter) {
        if (!existsSync(this.logFile)) {
            return [];
        }
        const content = readFileSync(this.logFile, 'utf-8');
        const lines = content.trim().split('\n');
        const logs = [];
        for (const line of lines) {
            try {
                const entry = JSON.parse(line);
                // 应用过滤条件
                if (filter) {
                    if (filter.operation && entry.operation !== filter.operation)
                        continue;
                    if (filter.server && entry.server !== filter.server)
                        continue;
                    if (filter.status && entry.status !== filter.status)
                        continue;
                    if (filter.startTime || filter.endTime) {
                        const entryTime = new Date(entry.timestamp);
                        if (filter.startTime && entryTime < filter.startTime)
                            continue;
                        if (filter.endTime && entryTime > filter.endTime)
                            continue;
                    }
                }
                logs.push(entry);
            }
            catch (e) {
                // 忽略解析错误
            }
        }
        return logs;
    }
    /**
     * 获取统计信息
     */
    getStats() {
        const logs = this.queryLogs();
        const stats = {
            total: logs.length,
            success: 0,
            failure: 0,
            partial: 0,
            byOperation: {},
            byServer: {}
        };
        for (const log of logs) {
            stats[log.status]++;
            if (log.operation) {
                stats.byOperation[log.operation] = (stats.byOperation[log.operation] || 0) + 1;
            }
            if (log.server) {
                stats.byServer[log.server] = (stats.byServer[log.server] || 0) + 1;
            }
        }
        return stats;
    }
}
// 全局审计日志实例
let globalAuditLogger = null;
/**
 * 获取全局审计日志
 */
export function getAuditLogger() {
    if (!globalAuditLogger) {
        globalAuditLogger = new AuditLogger();
    }
    return globalAuditLogger;
}
//# sourceMappingURL=audit-logger.js.map