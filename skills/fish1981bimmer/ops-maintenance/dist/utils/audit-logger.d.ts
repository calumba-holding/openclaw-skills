/**
 * 审计日志工具
 *
 * 记录所有运维操作，用于审计和问题排查
 */
export interface AuditLogEntry {
    timestamp: string;
    operation: string;
    server: string;
    user?: string;
    command?: string;
    status: 'success' | 'failure' | 'partial';
    duration?: number;
    error?: string;
    metadata?: Record<string, any>;
}
/**
 * 审计日志管理器
 */
export declare class AuditLogger {
    private logDir;
    private logFile;
    constructor(logDir?: string);
    /**
     * 记录操作
     */
    log(entry: AuditLogEntry): void;
    /**
     * 记录成功操作
     */
    logSuccess(operation: string, server: string, command?: string, duration?: number, metadata?: Record<string, any>): void;
    /**
     * 记录失败操作
     */
    logFailure(operation: string, server: string, error: string, command?: string, metadata?: Record<string, any>): void;
    /**
     * 记录部分成功操作
     */
    logPartial(operation: string, server: string, error: string, command?: string, duration?: number, metadata?: Record<string, any>): void;
    /**
     * 查询日志
     */
    queryLogs(filter?: {
        operation?: string;
        server?: string;
        status?: string;
        startTime?: Date;
        endTime?: Date;
    }): AuditLogEntry[];
    /**
     * 获取统计信息
     */
    getStats(): {
        total: number;
        success: number;
        failure: number;
        partial: number;
        byOperation: Record<string, number>;
        byServer: Record<string, number>;
    };
}
/**
 * 获取全局审计日志
 */
export declare function getAuditLogger(): AuditLogger;
//# sourceMappingURL=audit-logger.d.ts.map