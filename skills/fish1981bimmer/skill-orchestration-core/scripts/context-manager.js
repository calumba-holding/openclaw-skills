#!/usr/bin/env node

/**
 * 上下文管理器
 * 
 * 管理 skill 之间的上下文传递和共享
 */

const fs = require('fs');
const path = require('path');
const zlib = require('zlib');

class ContextManager {
  constructor(projectPath) {
    this.projectPath = projectPath;
    this.orchestrationDir = path.join(projectPath, '.orchestration');
    this.contextFile = path.join(this.orchestrationDir, 'context.json');
    
    // 初始化上下文
    this.context = {
      project: {
        name: path.basename(projectPath),
        path: projectPath,
        description: ''
      },
      state: {
        currentSkill: null,
        progress: 0,
        completedSkills: [],
        startTime: Date.now()
      },
      data: {},
      config: {
        contextCompression: true,
        maxContextSize: 100000
      }
    };
    
    // 确保目录存在
    this._ensureDirectories();
  }
  
  /**
   * 保存数据
   */
  set(key, value) {
    this.context.data[key] = value;
    this._checkSize();
  }
  
  /**
   * 获取数据
   */
  get(key) {
    return this.context.data[key];
  }
  
  /**
   * 删除数据
   */
  delete(key) {
    delete this.context.data[key];
  }
  
  /**
   * 检查是否存在
   */
  has(key) {
    return key in this.context.data;
  }
  
  /**
   * 压缩上下文
   */
  compress() {
    const json = JSON.stringify(this.context);
    const compressed = zlib.gzipSync(json);
    return {
      version: '1.0',
      compressed: true,
      data: compressed.toString('base64'),
      timestamp: Date.now()
    };
  }
  
  /**
   * 恢复上下文
   */
  restore(compressed) {
    if (compressed.compressed) {
      const buffer = Buffer.from(compressed.data, 'base64');
      const json = zlib.gunzipSync(buffer).toString();
      this.context = JSON.parse(json);
    } else {
      this.context = compressed;
    }
  }
  
  /**
   * 传递给下一个 skill
   */
  passTo(skill) {
    this.context.state.currentSkill = skill;
    this.context.state.progress = this._calculateProgress(skill);
    this.save();
  }
  
  /**
   * 保存到文件
   */
  save() {
    fs.writeFileSync(this.contextFile, JSON.stringify(this.context, null, 2));
  }
  
  /**
   * 从文件加载
   */
  load() {
    if (fs.existsSync(this.contextFile)) {
      const content = fs.readFileSync(this.contextFile, 'utf8');
      this.context = JSON.parse(content);
      return true;
    }
    return false;
  }
  
  /**
   * 清理
   */
  clear() {
    this.context.data = {};
    this.context.state = {
      currentSkill: null,
      progress: 0,
      completedSkills: [],
      startTime: Date.now()
    };
    this.save();
  }
  
  /**
   * 获取上下文大小
   */
  getSize() {
    return JSON.stringify(this.context).length;
  }
  
  /**
   * 获取项目信息
   */
  getProjectInfo() {
    return this.context.project;
  }
  
  /**
   * 获取状态
   */
  getState() {
    return this.context.state;
  }
  
  /**
   * 获取所有数据
   */
  getAllData() {
    return this.context.data;
  }
  
  /**
   * 设置项目信息
   */
  setProjectInfo(info) {
    this.context.project = { ...this.context.project, ...info };
  }
  
  /**
   * 标记 skill 完成
   */
  markSkillCompleted(skill) {
    if (!this.context.state.completedSkills.includes(skill)) {
      this.context.state.completedSkills.push(skill);
    }
  }
  
  /**
   * 检查 skill 是否完成
   */
  isSkillCompleted(skill) {
    return this.context.state.completedSkills.includes(skill);
  }
  
  /**
   * 获取进度
   */
  getProgress() {
    return this.context.state.progress;
  }
  
  /**
   * 设置进度
   */
  setProgress(progress) {
    this.context.state.progress = progress;
  }
  
  // 私有方法
  
  _ensureDirectories() {
    if (!fs.existsSync(this.orchestrationDir)) {
      fs.mkdirSync(this.orchestrationDir, { recursive: true });
    }
  }
  
  _checkSize() {
    const size = this.getSize();
    if (size > this.context.config.maxContextSize) {
      console.warn(`Context size (${size}) exceeds max size (${this.context.config.maxContextSize})`);
      if (this.context.config.contextCompression) {
        console.warn('Consider compressing context or removing unnecessary data');
      }
    }
  }
  
  _calculateProgress(skill) {
    // 简单的进度计算，可以根据实际需求调整
    const totalSkills = this.context.state.completedSkills.length + 1;
    return (this.context.state.completedSkills.length / totalSkills) * 100;
  }
}

// 导出
module.exports = ContextManager;

// 如果直接运行，提供 CLI 接口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  // 对于 set 和 get 命令，不需要 projectPath
  let projectPath = process.cwd();
  let key, value;
  
  if (command === 'set' || command === 'get') {
    key = args[1];
    value = args.slice(2).join(' ');
  } else {
    projectPath = args[1] || process.cwd();
  }
  
  const context = new ContextManager(projectPath);
  
  switch (command) {
    case 'show':
      context.load();
      console.log(JSON.stringify(context.context, null, 2));
      break;
      
    case 'save':
      context.save();
      console.log('Context saved');
      break;
      
    case 'load':
      if (context.load()) {
        console.log('Context loaded');
      } else {
        console.log('No context found');
      }
      break;
      
    case 'clear':
      context.clear();
      console.log('Context cleared');
      break;
      
    case 'get':
      context.load();
      if (key) {
        console.log(JSON.stringify(context.get(key), null, 2));
      } else {
        console.error('Please provide a key');
        process.exit(1);
      }
      break;
      
    case 'set':
      context.load();
      if (key && value) {
        try {
          context.set(key, JSON.parse(value));
          context.save();
          console.log(`Set ${key}`);
        } catch (e) {
          context.set(key, value);
          context.save();
          console.log(`Set ${key}`);
        }
      } else {
        console.error('Please provide key and value');
        process.exit(1);
      }
      break;
      
    default:
      console.log('Usage:');
      console.log('  context show [path]           - Show context');
      console.log('  context save [path]           - Save context');
      console.log('  context load [path]           - Load context');
      console.log('  context clear [path]          - Clear context');
      console.log('  context get <key> [path]      - Get value');
      console.log('  context set <key> <value> [path] - Set value');
  }
}
