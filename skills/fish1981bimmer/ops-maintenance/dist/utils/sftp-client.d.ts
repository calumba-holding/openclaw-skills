/**
 * SFTP文件传输工具
 *
 * 提供文件上传、下载、目录操作等功能
 */
import { ConnectionConfig } from './ssh-pool.js';
export interface FileTransferOptions {
    localPath: string;
    remotePath: string;
    mode?: 'upload' | 'download';
}
export interface DirectoryOptions {
    path: string;
    recursive?: boolean;
}
/**
 * SFTP客户端封装
 */
export declare class SFTPManager {
    private pool;
    constructor();
    /**
     * 获取SFTP客户端
     */
    private getSFTPClient;
    /**
     * 上传文件
     */
    uploadFile(config: ConnectionConfig, localPath: string, remotePath: string): Promise<void>;
    /**
     * 下载文件
     */
    downloadFile(config: ConnectionConfig, remotePath: string, localPath: string): Promise<void>;
    /**
     * 列出目录
     */
    listDirectory(config: ConnectionConfig, remotePath: string): Promise<any[]>;
    /**
     * 创建目录
     */
    createDirectory(config: ConnectionConfig, remotePath: string, recursive?: boolean): Promise<void>;
    /**
     * 删除文件
     */
    deleteFile(config: ConnectionConfig, remotePath: string): Promise<void>;
    /**
     * 删除目录
     */
    deleteDirectory(config: ConnectionConfig, remotePath: string, recursive?: boolean): Promise<void>;
    /**
     * 检查文件是否存在
     */
    fileExists(config: ConnectionConfig, remotePath: string): Promise<boolean>;
    /**
     * 获取文件信息
     */
    getFileInfo(config: ConnectionConfig, remotePath: string): Promise<any>;
}
/**
 * 获取全局SFTP管理器
 */
export declare function getSFTPManager(): SFTPManager;
//# sourceMappingURL=sftp-client.d.ts.map