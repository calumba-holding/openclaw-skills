/**
 * SSH连接池管理器
 *
 * 提供SSH连接的复用、超时管理和并发控制
 */
import { Client } from 'ssh2';
/**
 * SSH连接池
 */
export class SSHConnectionPool {
    connections = new Map();
    maxConnections = 10;
    connectionTimeout = 300000; // 5分钟
    maxRetries = 3;
    retryDelay = 1000;
    constructor(maxConnections = 10) {
        this.maxConnections = maxConnections;
        // 定期清理过期连接
        setInterval(() => this.cleanup(), 60000);
    }
    /**
     * 获取连接键
     */
    getConnectionKey(config) {
        return `${config.user || 'default'}@${config.host}:${config.port || 22}`;
    }
    /**
     * 创建SSH连接
     */
    async createConnection(config) {
        return new Promise((resolve, reject) => {
            const client = new Client();
            const connConfig = {
                host: config.host,
                port: config.port || 22,
                username: config.user || 'root',
                readyTimeout: config.connectTimeout || 15000,
                algorithms: {
                    kex: ['curve25519-sha256', 'ecdh-sha2-nistp256', 'diffie-hellman-group14-sha256'],
                    cipher: ['aes256-gcm@openssh.com', 'aes128-gcm@openssh.com', 'aes256-ctr'],
                    serverHostKey: ['ssh-ed25519', 'ecdsa-sha2-nistp256', 'rsa-sha2-512']
                }
            };
            // 优先使用密钥认证
            if (config.keyFile) {
                connConfig.privateKey = require('fs').readFileSync(config.keyFile);
            }
            else if (config.password) {
                connConfig.password = config.password;
            }
            else {
                // 尝试使用默认密钥
                try {
                    const defaultKey = require('fs').readFileSync(require('os').homedir() + '/.ssh/id_rsa');
                    connConfig.privateKey = defaultKey;
                }
                catch (e) {
                    // 忽略错误，可能使用密码认证
                }
            }
            client.on('ready', () => {
                resolve(client);
            });
            client.on('error', (err) => {
                reject(err);
            });
            client.connect(connConfig);
        });
    }
    /**
     * 获取或创建连接
     */
    async getConnection(config) {
        const key = this.getConnectionKey(config);
        const existing = this.connections.get(key);
        // 检查现有连接是否可用
        if (existing && existing.isActive) {
            existing.lastUsed = Date.now();
            return existing.client;
        }
        // 清理旧连接
        if (existing) {
            try {
                existing.client.end();
            }
            catch (e) {
                // 忽略错误
            }
            this.connections.delete(key);
        }
        // 检查连接池是否已满
        if (this.connections.size >= this.maxConnections) {
            await this.cleanup();
        }
        // 创建新连接
        const client = await this.createConnection(config);
        this.connections.set(key, {
            client,
            config,
            lastUsed: Date.now(),
            isActive: true
        });
        return client;
    }
    /**
     * 执行命令（带重试）
     */
    async executeCommand(config, command) {
        const maxRetries = config.maxRetries || this.maxRetries;
        const retryDelay = config.retryDelay || this.retryDelay;
        let lastError = null;
        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                const client = await this.getConnection(config);
                return new Promise((resolve, reject) => {
                    let stdout = '';
                    let stderr = '';
                    client.exec(command, (err, stream) => {
                        if (err) {
                            reject(err);
                            return;
                        }
                        stream.on('data', (data) => {
                            stdout += data.toString();
                        });
                        stream.stderr.on('data', (data) => {
                            stderr += data.toString();
                        });
                        stream.on('close', (code) => {
                            resolve({ stdout, stderr, exitCode: code || 0 });
                        });
                        stream.on('error', (err) => {
                            reject(err);
                        });
                    });
                });
            }
            catch (error) {
                lastError = error;
                if (attempt < maxRetries) {
                    // 指数退避
                    const delay = retryDelay * Math.pow(2, attempt);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
            }
        }
        throw lastError || new Error('SSH command execution failed');
    }
    /**
     * 清理过期连接
     */
    async cleanup() {
        const now = Date.now();
        const keysToDelete = [];
        for (const [key, conn] of this.connections.entries()) {
            if (now - conn.lastUsed > this.connectionTimeout) {
                keysToDelete.push(key);
                try {
                    conn.client.end();
                }
                catch (e) {
                    // 忽略错误
                }
            }
        }
        for (const key of keysToDelete) {
            this.connections.delete(key);
        }
    }
    /**
     * 关闭所有连接
     */
    async closeAll() {
        for (const [key, conn] of this.connections.entries()) {
            try {
                conn.client.end();
            }
            catch (e) {
                // 忽略错误
            }
        }
        this.connections.clear();
    }
    /**
     * 获取连接池状态
     */
    getStatus() {
        let active = 0;
        for (const conn of this.connections.values()) {
            if (conn.isActive)
                active++;
        }
        return {
            total: this.connections.size,
            active
        };
    }
}
// 全局连接池实例
let globalPool = null;
/**
 * 获取全局连接池
 */
export function getSSHPool(maxConnections = 10) {
    if (!globalPool) {
        globalPool = new SSHConnectionPool(maxConnections);
    }
    return globalPool;
}
/**
 * 关闭全局连接池
 */
export async function closeGlobalPool() {
    if (globalPool) {
        await globalPool.closeAll();
        globalPool = null;
    }
}
//# sourceMappingURL=ssh-pool.js.map