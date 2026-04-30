const ProjectManager = require('./project');
const CostEstimator = require('./estimator');
const ChangeDetector = require('./change-detector');
const Setup = require('./setup');

class Dispatch {
  constructor(dataDir) {
    this.dataDir = dataDir || `${process.env.HOME}/.openclaw/workspace/.dispatch`;
    this.projectManager = new ProjectManager(this.dataDir);
    this.estimator = new CostEstimator();
    this.changeDetector = new ChangeDetector(this.dataDir);
  }

  // Project management
  async createProject(name, description) {
    const phases = this.projectManager.suggestPhases(this.detectType(description));
    
    return {
      preview: true,
      name,
      description,
      suggested_phases: phases,
      message: 'Review and approve these phases, or request edits'
    };
  }

  async confirmProject(name, description, phases) {
    const { id, meta } = this.projectManager.createProject(name, description, phases);
    
    return {
      created: true,
      id,
      name: meta.name,
      phases: meta.phases.length,
      data_path: `${this.dataDir}/projects/${id}`,
      message: `Project created. Start with: "Estimate phase ${meta.phases[0].name}"`
    };
  }

  detectType(description) {
    const d = description.toLowerCase();
    if (d.includes('api')) return 'api';
    if (d.includes('web') || d.includes('app')) return 'web-app';
    if (d.includes('research') || d.includes('analyze')) return 'research';
    return 'default';
  }

  async estimatePhase(projectId, phaseName, taskDescription) {
    const estimate = this.estimator.estimate(taskDescription);
    
    return {
      phase: phaseName,
      tasks: estimate.tasks.length,
      total_estimate: estimate.total_estimate,
      breakdown: estimate.tasks,
      message: 'Approve this estimate to proceed?'
    };
  }

  listProjects() {
    return this.projectManager.listProjects();
  }

  getProjectStatus(projectId) {
    const project = this.projectManager.getProject(projectId);
    if (!project) return { error: 'Project not found' };
    
    return {
      id: project.id,
      name: project.name,
      status: project.status,
      active_phase: project.active_phase,
      phases: project.phases.map(p => ({
        name: p.name,
        status: p.status,
        estimate: p.estimate,
        actual: p.actual
      }))
    };
  }

  // Model management
  async checkForNewModels() {
    return await this.changeDetector.checkForChanges();
  }

  // Setup
  async setup() {
    const setup = new Setup();
    await setup.run();
  }
}

module.exports = Dispatch;
