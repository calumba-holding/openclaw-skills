const fs = require('fs');
const path = require('path');

class ProjectManager {
  constructor(dataDir) {
    this.dataDir = dataDir || process.env.DISPATCH_DATA || `${process.env.HOME}/.openclaw/workspace/.dispatch`;
    this.config = this.loadConfig();
    this.outputDir = this.config.output_dir || `${process.env.HOME}/.openclaw/workspace/dispatch`;
  }

  loadConfig() {
    try {
      const configPath = path.join(this.dataDir, 'config.json');
      if (fs.existsSync(configPath)) {
        return JSON.parse(fs.readFileSync(configPath, 'utf8'));
      }
    } catch (err) {
      // Silently fail, use defaults
    }
    return {};
  }

  generateId(name) {
    const sanitized = name.toLowerCase().replace(/[^a-z0-9]/g, '-');
    const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    return `${timestamp}-${sanitized}`;
  }

  suggestPhases(projectType) {
    const templates = {
      'api': ['Discovery', 'Design', 'Implementation', 'Testing', 'Documentation'],
      'web-app': ['Research', 'UI/UX Design', 'Frontend', 'Backend', 'Integration', 'Deploy'],
      'research': ['Literature Review', 'Analysis', 'Synthesis', 'Report'],
      'default': ['Discovery', 'Planning', 'Execution', 'Review']
    };
    
    return templates[projectType] || templates.default;
  }

  suggestAgentForPhase(phaseName) {
    const phaseLower = phaseName.toLowerCase();
    const defaults = this.config.phase_defaults || {};
    
    // Find matching phase default
    for (const [key, config] of Object.entries(defaults)) {
      if (phaseLower.includes(key)) {
        // Return first available agent from suggested list
        return config.suggested.find(id => this.config.agents[id]) || 'echo';
      }
    }
    
    return 'echo'; // Default fallback
  }

  getFileNamingConvention(phaseName, phaseIndex) {
    const phaseLower = phaseName.toLowerCase();
    const paddedIndex = String(phaseIndex + 1).padStart(2, '0');
    
    if (phaseLower.includes('research') || phaseLower.includes('discovery')) {
      return {
        primary: `${paddedIndex}-${phaseName.toLowerCase().replace(/\s+/g, '-')}_report.html`,
        summary: 'RESEARCH_SUMMARY.md',
        assets: 'assets/'
      };
    } else if (phaseLower.includes('design')) {
      return {
        primary: `${paddedIndex}-${phaseName.toLowerCase().replace(/\s+/g, '-')}_report.html`,
        technical: 'TECHNICAL_SPEC.md',
        diagram: 'architecture.png'
      };
    } else if (phaseLower.includes('implementation') || phaseLower.includes('build')) {
      return {
        primary: `${paddedIndex}-implementation_report.html`,
        code: 'src/',
        tests: 'tests/',
        readme: 'README.md'
      };
    } else {
      return {
        primary: `${paddedIndex}-${phaseName.toLowerCase().replace(/\s+/g, '-')}_deliverables.html`
      };
    }
  }

  createProject(name, description, phases) {
    const id = this.generateId(name);
    const projectDir = path.join(this.dataDir, 'projects', id);
    const outputProjectDir = path.join(this.outputDir, id);
    
    // Create internal project directory (metadata, costs, etc.)
    fs.mkdirSync(projectDir, { recursive: true });
    
    // Create output project directory (deliverables, reports)
    fs.mkdirSync(outputProjectDir, { recursive: true });
    
    const meta = {
      id,
      name,
      description,
      status: 'active',
      created: new Date().toISOString(),
      captain: this.config.captain,
      output_path: outputProjectDir,
      phases: phases.map((p, i) => ({
        name: typeof p === 'string' ? p : p.name,
        order: i + 1,
        status: i === 0 ? 'active' : 'pending',
        estimate: 0,
        actual: 0,
        assigned_agent: this.suggestAgentForPhase(typeof p === 'string' ? p : p.name),
        files: this.getFileNamingConvention(typeof p === 'string' ? p : p.name, i)
      })),
      active_phase: phases[0]?.name || phases[0]
    };
    
    fs.writeFileSync(
      path.join(projectDir, 'meta.json'),
      JSON.stringify(meta, null, 2)
    );
    
    // Create phase directories in both locations
    for (let i = 0; i < phases.length; i++) {
      const phaseName = typeof phases[i] === 'string' ? phases[i] : phases[i].name;
      const phaseSlug = `${String(i + 1).padStart(2, '0')}-${phaseName.toLowerCase().replace(/\s+/g, '-')}`;
      
      // Internal phase metadata
      const phaseDir = path.join(projectDir, 'phases', phaseSlug);
      fs.mkdirSync(path.join(phaseDir, 'tasks'), { recursive: true });
      
      fs.writeFileSync(
        path.join(phaseDir, 'meta.json'),
        JSON.stringify({
          name: phaseName,
          order: i + 1,
          status: i === 0 ? 'active' : 'pending',
          estimate: 0,
          actual: 0,
          tasks_count: 0,
          completed_tasks: 0
        }, null, 2)
      );
      
      // Output phase directory for deliverables
      const outputPhaseDir = path.join(outputProjectDir, phaseSlug);
      fs.mkdirSync(outputPhaseDir, { recursive: true });
      
      // Create task brief for the assigned agent
      const assignedAgent = meta.phases[i].assigned_agent;
      const fileConventions = meta.phases[i].files;
      const outputPath = outputPhaseDir;
      
      fs.writeFileSync(
        path.join(outputPhaseDir, 'TASK_BRIEF.md'),
        `# Task Brief: ${phaseName}

**For:** ${assignedAgent}
**From:** Captain (${this.config.captain})
**Project:** ${name} (${id})
**Phase:** ${paddedIndex} of ${phases.length}

## Your Task
Complete the "${phaseName}" phase for this project.

## Output Requirements

**Save Location:**
\`${outputPath}/\`

**Deliverables:**
${Object.entries(fileConventions).map(([key, value]) => `- ${key}: \`${value}\``).join('\n')}

## Instructions
1. Do the work for this phase
2. Save all output files to the location above
3. Use the exact filenames specified
4. Report back to Captain when complete

## Notes
- Do not save files to your personal workspace
- Use the exact paths and filenames provided
- Ask the Captain if anything is unclear
`
    }
    
    // Initialize costs (internal only)
    fs.writeFileSync(
      path.join(projectDir, 'costs.json'),
      JSON.stringify({
        project_estimate: 0,
        project_actual: 0,
        phases: {},
        tasks: []
      }, null, 2)
    );
    
    return { id, meta, output_path: outputProjectDir };
  }

  getProject(id) {
    const projectDir = path.join(this.dataDir, 'projects', id);
    const metaPath = path.join(projectDir, 'meta.json');
    
    if (!fs.existsSync(metaPath)) return null;
    
    return JSON.parse(fs.readFileSync(metaPath, 'utf8'));
  }

  listProjects() {
    const projectsDir = path.join(this.dataDir, 'projects');
    if (!fs.existsSync(projectsDir)) return [];
    
    return fs.readdirSync(projectsDir)
      .map(id => this.getProject(id))
      .filter(Boolean);
  }

  updatePhaseStatus(projectId, phaseName, status) {
    const project = this.getProject(projectId);
    if (!project) return false;
    
    const phase = project.phases.find(p => p.name === phaseName);
    if (phase) {
      phase.status = status;
      
      const metaPath = path.join(this.dataDir, 'projects', projectId, 'meta.json');
      fs.writeFileSync(metaPath, JSON.stringify(project, null, 2));
      
      return true;
    }
    
    return false;
  }
}

module.exports = ProjectManager;
