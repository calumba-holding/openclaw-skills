/**
 * SSH连接池管理器
 *
 * 提供SSH连接的复用、超时管理和并发控制
 */
import { Client } from 'ssh2';
export interface SSHConfig {
    host: string;
    port?: number;
    user?: string;
    keyFile?: string;
    password?: string;
    name?: string;
    tags?: string[];
}
export interface ConnectionConfig extends SSHConfig {
    maxRetries?: number;
    retryDelay?: number;
    connectTimeout?: number;
}
export interface SSHConnection {
    client: Client;
    config: ConnectionConfig;
    lastUsed: number;
    isActive: boolean;
}
/**
 * SSH连接池
 */
export declare class SSHConnectionPool {
    private connections;
    private maxConnections;
    private connectionTimeout;
    private maxRetries;
    private retryDelay;
    constructor(maxConnections?: number);
    /**
     * 获取连接键
     */
    private getConnectionKey;
    /**
     * 创建SSH连接
     */
    private createConnection;
    /**
     * 获取或创建连接
     */
    getConnection(config: ConnectionConfig): Promise<Client>;
    /**
     * 执行命令（带重试）
     */
    executeCommand(config: ConnectionConfig, command: string): Promise<{
        stdout: string;
        stderr: string;
        exitCode: number;
    }>;
    /**
     * 清理过期连接
     */
    private cleanup;
    /**
     * 关闭所有连接
     */
    closeAll(): Promise<void>;
    /**
     * 获取连接池状态
     */
    getStatus(): {
        total: number;
        active: number;
    };
}
/**
 * 获取全局连接池
 */
export declare function getSSHPool(maxConnections?: number): SSHConnectionPool;
/**
 * 关闭全局连接池
 */
export declare function closeGlobalPool(): Promise<void>;
//# sourceMappingURL=ssh-pool.d.ts.map