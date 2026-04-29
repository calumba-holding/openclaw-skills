/**
 * 运维助手 Skill 实现 (v2.0)
 *
 * 本模块提供运维检查功能，供 AI 助手调用
 *
 * 主要改进：
 * - 使用ssh2库替代child_process.exec
 * - 添加连接池管理
 * - 增强安全性（移除StrictHostKeyChecking=no）
 * - 添加重试机制和错误处理
 * - 添加审计日志
 * - 支持SFTP文件传输
 * - 添加并发控制
 */
/**
 * SSH 配置
 */
export interface SSHConfig {
    host: string;
    port?: number;
    user?: string;
    keyFile?: string;
    password?: string;
    name?: string;
    tags?: string[];
}
/**
 * 服务器集群配置
 */
export interface ClusterConfig {
    name: string;
    servers: SSHConfig[];
}
/**
 * 保存服务器列表
 */
export declare function saveServers(servers: SSHConfig[]): Promise<void>;
/**
 * 加载服务器列表
 */
export declare function loadServers(): Promise<SSHConfig[]>;
/**
 * 添加服务器
 */
export declare function addServer(config: SSHConfig): Promise<void>;
/**
 * 移除服务器
 */
export declare function removeServer(host: string): Promise<void>;
/**
 * 按标签筛选服务器
 */
export declare function getServersByTag(tag: string): Promise<SSHConfig[]>;
/**
 * 批量检查所有服务器健康状态
 */
export declare function checkAllServersHealth(tags?: string[]): Promise<{
    server: string;
    status: string;
    details: string;
}[]>;
/**
 * 批量执行命令到所有服务器
 */
export declare function executeOnAllServers(command: string, tags?: string[]): Promise<{
    server: string;
    output: string;
}[]>;
/**
 * 批量添加服务器 (支持 IP:Port 格式)
 */
export declare function batchAddServers(servers: string[]): Promise<{
    success: number;
    failed: number;
    details: string[];
}>;
/**
 * 从 CSV/JSON 批量导入
 */
export declare function importServersFromText(text: string): Promise<{
    success: number;
    failed: number;
    servers: SSHConfig[];
}>;
/**
 * 服务器状态摘要
 */
export declare function getClusterSummary(): Promise<string>;
/**
 * 通过 SSH 执行远程命令
 */
export declare function runRemoteCommand(config: SSHConfig, command: string): Promise<string>;
/**
 * 执行系统命令并返回结果
 */
export declare function runCommand(cmd: string, timeout?: number): Promise<string>;
/**
 * 系统健康检查
 */
export declare function checkHealth(): Promise<string>;
/**
 * 日志分析
 */
export declare function analyzeLogs(pattern?: string, lines?: number): Promise<string>;
/**
 * 性能监控
 */
export declare function checkPerformance(): Promise<string>;
/**
 * 端口检查
 */
export declare function checkPort(port?: number): Promise<string>;
/**
 * 进程检查
 */
export declare function checkProcess(name?: string): Promise<string>;
/**
 * 磁盘使用
 */
export declare function checkDisk(): Promise<string>;
/**
 * 远程服务器健康检查
 */
export declare function checkRemoteHealth(config: SSHConfig, services?: string[]): Promise<string>;
/**
 * 远程服务器端口检查
 */
export declare function checkRemotePort(config: SSHConfig, port?: number): Promise<string>;
/**
 * 远程服务器进程检查
 */
export declare function checkRemoteProcess(config: SSHConfig, name?: string): Promise<string>;
/**
 * 远程服务器磁盘检查
 */
export declare function checkRemoteDisk(config: SSHConfig): Promise<string>;
/**
 * 远程服务器日志检查
 */
export declare function checkRemoteLogs(config: SSHConfig, pattern?: string, lines?: number): Promise<string>;
/**
 * 运维操作执行入口
 */
export type OpsAction = 'health' | 'logs' | 'perf' | 'ports' | 'process' | 'disk';
/**
 * 本地运维操作
 */
export declare function executeOp(action: string, arg?: string): Promise<string>;
/**
 * 远程运维操作
 */
export declare function executeRemoteOp(action: string, config: SSHConfig, arg?: string): Promise<string>;
/**
 * SFTP文件操作
 */
export declare function uploadFile(config: SSHConfig, localPath: string, remotePath: string): Promise<string>;
export declare function downloadFile(config: SSHConfig, remotePath: string, localPath: string): Promise<string>;
export declare function listRemoteDirectory(config: SSHConfig, remotePath: string): Promise<string>;
/**
 * 获取审计日志统计
 */
export declare function getAuditStats(): Promise<string>;
/**
 * 清理资源
 */
export declare function cleanup(): Promise<void>;
//# sourceMappingURL=index.d.ts.map