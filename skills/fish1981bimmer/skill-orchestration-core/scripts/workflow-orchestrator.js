#!/usr/bin/env node

/**
 * 流程编排器
 * 
 * 基于 DESIGN.md 的流程编排
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class WorkflowOrchestrator {
  constructor(designPath) {
    this.designPath = designPath;
    this.projectPath = path.dirname(designPath);
    this.orchestrationDir = path.join(this.projectPath, '.orchestration');
    this.stateFile = path.join(this.orchestrationDir, 'state.json');
    this.checkpointsDir = path.join(this.orchestrationDir, 'checkpoints');
    
    // 初始化状态
    this.state = {
      currentStage: null,
      completedStages: [],
      progress: 0,
      startTime: null,
      paused: false,
      checkpoints: []
    };
    
    // 确保目录存在
    this._ensureDirectories();
  }
  
  /**
   * 解析 DESIGN.md
   */
  parseDesign() {
    const content = fs.readFileSync(this.designPath, 'utf8');
    
    // 提取 frontmatter
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (frontmatterMatch) {
      this.frontmatter = yaml.load(frontmatterMatch[1]);
    }
    
    // 解析工作流程
    this.workflow = this._parseWorkflow(content);
    
    // 解析上下文传递
    this.contextFlow = this._parseContextFlow(content);
    
    // 解析质量验证
    this.validation = this._parseValidation(content);
    
    // 解析状态管理
    this.stateManagement = this._parseStateManagement(content);
    
    return {
      frontmatter: this.frontmatter,
      workflow: this.workflow,
      contextFlow: this.contextFlow,
      validation: this.validation,
      stateManagement: this.stateManagement
    };
  }
  
  /**
   * 执行流程
   */
  async execute() {
    console.log('Starting workflow execution...');
    
    // 解析 DESIGN.md
    this.parseDesign();
    
    // 初始化状态
    this.state.startTime = Date.now();
    this.state.paused = false;
    
    // 执行每个阶段
    for (const stage of this.workflow) {
      if (this.state.paused) {
        console.log('Workflow paused');
        break;
      }
      
      console.log(`\nExecuting stage: ${stage.name}`);
      
      // 执行阶段
      await this._executeStage(stage);
      
      // 标记完成
      this.state.completedStages.push(stage.name);
      this.state.currentStage = stage.name;
      this.state.progress = this._calculateProgress();
      
      // 保存状态
      this._saveState();
      
      // 检查是否需要设置检查点
      if (this._shouldSetCheckpoint(stage.name)) {
        this.setCheckpoint(`checkpoint-${stage.name}`);
      }
    }
    
    console.log('\nWorkflow execution completed');
  }
  
  /**
   * 暂停
   */
  pause() {
    this.state.paused = true;
    this._saveState();
    console.log('Workflow paused');
  }
  
  /**
   * 恢复
   */
  async resume() {
    console.log('Resuming workflow...');
    
    // 加载状态
    this._loadState();
    
    // 解析 DESIGN.md
    this.parseDesign();
    
    // 找到当前阶段
    const currentIndex = this.workflow.findIndex(
      stage => stage.name === this.state.currentStage
    );
    
    if (currentIndex === -1) {
      console.log('No current stage found, starting from beginning');
      this.state.paused = false;
      await this.execute();
      return;
    }
    
    // 从当前阶段继续执行
    this.state.paused = false;
    for (let i = currentIndex; i < this.workflow.length; i++) {
      const stage = this.workflow[i];
      
      if (this.state.paused) {
        console.log('Workflow paused');
        break;
      }
      
      console.log(`\nExecuting stage: ${stage.name}`);
      
      // 执行阶段
      await this._executeStage(stage);
      
      // 标记完成
      if (!this.state.completedStages.includes(stage.name)) {
        this.state.completedStages.push(stage.name);
      }
      this.state.currentStage = stage.name;
      this.state.progress = this._calculateProgress();
      
      // 保存状态
      this._saveState();
      
      // 检查是否需要设置检查点
      if (this._shouldSetCheckpoint(stage.name)) {
        this.setCheckpoint(`checkpoint-${stage.name}`);
      }
    }
    
    console.log('\nWorkflow execution completed');
  }
  
  /**
   * 跳到指定阶段
   */
  async jumpTo(stageName) {
    console.log(`Jumping to stage: ${stageName}`);
    
    // 解析 DESIGN.md
    this.parseDesign();
    
    // 查找阶段
    const stage = this.workflow.find(s => s.name === stageName);
    if (!stage) {
      console.error(`Stage not found: ${stageName}`);
      return;
    }
    
    // 执行阶段
    await this._executeStage(stage);
    
    // 更新状态
    if (!this.state.completedStages.includes(stageName)) {
      this.state.completedStages.push(stageName);
    }
    this.state.currentStage = stageName;
    this.state.progress = this._calculateProgress();
    
    // 保存状态
    this._saveState();
  }
  
  /**
   * 获取状态
   */
  getStatus() {
    this._loadState();
    return {
      currentStage: this.state.currentStage,
      completedStages: this.state.completedStages,
      progress: this.state.progress,
      startTime: this.state.startTime,
      paused: this.state.paused,
      elapsed: this.state.startTime ? Date.now() - this.state.startTime : 0
    };
  }
  
  /**
   * 获取进度
   */
  getProgress() {
    this._loadState();
    return this.state.progress;
  }
  
  /**
   * 设置检查点
   */
  setCheckpoint(name) {
    const checkpoint = {
      name: name,
      timestamp: Date.now(),
      state: JSON.parse(JSON.stringify(this.state)),
      context: this._getContextSnapshot()
    };
    
    const checkpointFile = path.join(this.checkpointsDir, `${name}.json`);
    fs.writeFileSync(checkpointFile, JSON.stringify(checkpoint, null, 2));
    
    this.state.checkpoints.push(name);
    this._saveState();
    
    console.log(`Checkpoint set: ${name}`);
  }
  
  /**
   * 恢复到检查点
   */
  restoreCheckpoint(name) {
    const checkpointFile = path.join(this.checkpointsDir, `${name}.json`);
    
    if (!fs.existsSync(checkpointFile)) {
      console.error(`Checkpoint not found: ${name}`);
      return;
    }
    
    const checkpoint = JSON.parse(fs.readFileSync(checkpointFile, 'utf8'));
    this.state = checkpoint.state;
    this._saveState();
    
    console.log(`Restored to checkpoint: ${name}`);
  }
  
  /**
   * 获取所有检查点
   */
  getCheckpoints() {
    if (!fs.existsSync(this.checkpointsDir)) {
      return [];
    }
    
    const files = fs.readdirSync(this.checkpointsDir);
    return files.map(file => {
      const content = fs.readFileSync(path.join(this.checkpointsDir, file), 'utf8');
      return JSON.parse(content);
    });
  }
  
  // 私有方法
  
  _ensureDirectories() {
    if (!fs.existsSync(this.orchestrationDir)) {
      fs.mkdirSync(this.orchestrationDir, { recursive: true });
    }
    if (!fs.existsSync(this.checkpointsDir)) {
      fs.mkdirSync(this.checkpointsDir, { recursive: true });
    }
  }
  
  _parseWorkflow(content) {
    const stages = [];
    const stageRegex = /###\s+阶段\s+(\d+):\s*(.+?)(?=\n###|$)/g;
    let match;
    
    while ((match = stageRegex.exec(content)) !== null) {
      const stageNumber = match[1];
      const stageName = match[2].trim();
      
      // 提取阶段内容
      const stageStart = match.index;
      const nextStageStart = content.indexOf('###', stageStart + 1);
      const stageContent = nextStageStart === -1 
        ? content.slice(stageStart)
        : content.slice(stageStart, nextStageStart);
      
      // 解析技能
      const skills = this._extractSkills(stageContent);
      
      // 解析任务
      const tasks = this._extractTasks(stageContent);
      
      // 解析输出
      const outputs = this._extractOutputs(stageContent);
      
      stages.push({
        number: parseInt(stageNumber),
        name: stageName,
        skills: skills,
        tasks: tasks,
        outputs: outputs
      });
    }
    
    return stages;
  }
  
  _extractSkills(content) {
    const skills = [];
    const skillsMatch = content.match(/\*\*使用的 Skills\*\*:\s*([\s\S]*?)(?=\n\*\*|$)/);
    
    if (skillsMatch) {
      const lines = skillsMatch[1].trim().split('\n');
      lines.forEach(line => {
        const skillMatch = line.match(/-\s*(.+)/);
        if (skillMatch) {
          skills.push(skillMatch[1].trim());
        }
      });
    }
    
    return skills;
  }
  
  _extractTasks(content) {
    const tasks = [];
    const tasksMatch = content.match(/\*\*任务\*\*:\s*([\s\S]*?)(?=\n\*\*|$)/);
    
    if (tasksMatch) {
      const lines = tasksMatch[1].trim().split('\n');
      lines.forEach(line => {
        const taskMatch = line.match(/-\s*(.+)/);
        if (taskMatch) {
          tasks.push(taskMatch[1].trim());
        }
      });
    }
    
    return tasks;
  }
  
  _extractOutputs(content) {
    const outputs = [];
    const outputsMatch = content.match(/\*\*输出\*\*:\s*([\s\S]*?)(?=\n\*\*|$)/);
    
    if (outputsMatch) {
      const lines = outputsMatch[1].trim().split('\n');
      lines.forEach(line => {
        const outputMatch = line.match(/-\s*(.+)/);
        if (outputMatch) {
          outputs.push(outputMatch[1].trim());
        }
      });
    }
    
    return outputs;
  }
  
  _parseContextFlow(content) {
    // 解析上下文传递配置
    const contextMatch = content.match(/##\s+上下文传递\s*([\s\S]*?)(?=\n##|$)/);
    
    if (contextMatch) {
      try {
        return yaml.load(contextMatch[1]);
      } catch (e) {
        console.warn('Failed to parse context flow:', e.message);
      }
    }
    
    return {};
  }
  
  _parseValidation(content) {
    // 解析质量验证配置
    const validationMatch = content.match(/##\s+质量验证\s*([\s\S]*?)(?=\n##|$)/);
    
    if (validationMatch) {
      try {
        return yaml.load(validationMatch[1]);
      } catch (e) {
        console.warn('Failed to parse validation:', e.message);
      }
    }
    
    return {};
  }
  
  _parseStateManagement(content) {
    // 解析状态管理配置
    const stateMatch = content.match(/##\s+状态管理\s*([\s\S]*?)(?=\n##|$)/);
    
    if (stateMatch) {
      try {
        return yaml.load(stateMatch[1]);
      } catch (e) {
        console.warn('Failed to parse state management:', e.message);
      }
    }
    
    return {};
  }
  
  async _executeStage(stage) {
    console.log(`  Skills: ${stage.skills.join(', ')}`);
    console.log(`  Tasks: ${stage.tasks.length} tasks`);
    console.log(`  Outputs: ${stage.outputs.join(', ')}`);
    
    // 这里应该实际调用 skill
    // 目前只是模拟
    console.log('  Executing...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('  Completed');
  }
  
  _calculateProgress() {
    if (this.workflow.length === 0) return 0;
    return (this.state.completedStages.length / this.workflow.length) * 100;
  }
  
  _shouldSetCheckpoint(stageName) {
    if (!this.stateManagement || !this.stateManagement.checkpoints) {
      return false;
    }
    
    return this.stateManagement.checkpoints.some(
      cp => cp.after === stageName
    );
  }
  
  _saveState() {
    fs.writeFileSync(this.stateFile, JSON.stringify(this.state, null, 2));
  }
  
  _loadState() {
    if (fs.existsSync(this.stateFile)) {
      const content = fs.readFileSync(this.stateFile, 'utf8');
      this.state = JSON.parse(content);
    }
  }
  
  _getContextSnapshot() {
    // 获取上下文快照
    const contextFile = path.join(this.orchestrationDir, 'context.json');
    if (fs.existsSync(contextFile)) {
      return JSON.parse(fs.readFileSync(contextFile, 'utf8'));
    }
    return null;
  }
}

// 导出
module.exports = WorkflowOrchestrator;

// 如果直接运行，提供 CLI 接口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const designPath = args[1];
  
  if (!designPath && command !== 'help') {
    console.error('Please provide DESIGN.md path');
    process.exit(1);
  }
  
  if (command === 'help') {
    console.log('Usage:');
    console.log('  workflow execute <DESIGN.md>        - Execute workflow');
    console.log('  workflow pause <DESIGN.md>           - Pause workflow');
    console.log('  workflow resume <DESIGN.md>          - Resume workflow');
    console.log('  workflow jump <DESIGN.md> <stage>    - Jump to stage');
    console.log('  workflow status <DESIGN.md>          - Show status');
    console.log('  workflow progress <DESIGN.md>         - Show progress');
    console.log('  workflow checkpoint <DESIGN.md> <name> - Set checkpoint');
    console.log('  workflow restore <DESIGN.md> <name>  - Restore checkpoint');
    console.log('  workflow checkpoints <DESIGN.md>     - List checkpoints');
    console.log('  workflow parse <DESIGN.md>            - Parse DESIGN.md');
    process.exit(0);
  }
  
  const orchestrator = new WorkflowOrchestrator(designPath);
  
  switch (command) {
    case 'execute':
      orchestrator.execute().catch(console.error);
      break;
      
    case 'pause':
      orchestrator.pause();
      break;
      
    case 'resume':
      orchestrator.resume().catch(console.error);
      break;
      
    case 'jump':
      const stageName = args[2];
      if (!stageName) {
        console.error('Please provide stage name');
        process.exit(1);
      }
      orchestrator.jumpTo(stageName).catch(console.error);
      break;
      
    case 'status':
      const status = orchestrator.getStatus();
      console.log(JSON.stringify(status, null, 2));
      break;
      
    case 'progress':
      console.log(`Progress: ${orchestrator.getProgress()}%`);
      break;
      
    case 'checkpoint':
      const cpName = args[2];
      if (!cpName) {
        console.error('Please provide checkpoint name');
        process.exit(1);
      }
      orchestrator.setCheckpoint(cpName);
      break;
      
    case 'restore':
      const restoreName = args[2];
      if (!restoreName) {
        console.error('Please provide checkpoint name');
        process.exit(1);
      }
      orchestrator.restoreCheckpoint(restoreName);
      break;
      
    case 'checkpoints':
      const checkpoints = orchestrator.getCheckpoints();
      console.log(JSON.stringify(checkpoints, null, 2));
      break;
      
    case 'parse':
      const parsed = orchestrator.parseDesign();
      console.log(JSON.stringify(parsed, null, 2));
      break;
      
    default:
      console.log('Usage:');
      console.log('  workflow execute <DESIGN.md>        - Execute workflow');
      console.log('  workflow pause <DESIGN.md>           - Pause workflow');
      console.log('  workflow resume <DESIGN.md>          - Resume workflow');
      console.log('  workflow jump <DESIGN.md> <stage>    - Jump to stage');
      console.log('  workflow status <DESIGN.md>          - Show status');
      console.log('  workflow progress <DESIGN.md>         - Show progress');
      console.log('  workflow checkpoint <DESIGN.md> <name> - Set checkpoint');
      console.log('  workflow restore <DESIGN.md> <name>  - Restore checkpoint');
      console.log('  workflow checkpoints <DESIGN.md>     - List checkpoints');
      console.log('  workflow parse <DESIGN.md>            - Parse DESIGN.md');
  }
}
