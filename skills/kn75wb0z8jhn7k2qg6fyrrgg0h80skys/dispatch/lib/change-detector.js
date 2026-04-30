const fs = require('fs');
const path = require('path');

class ChangeDetector {
  constructor(dataDir) {
    this.dataDir = dataDir || `${process.env.HOME}/.openclaw/workspace/.dispatch`;
    this.configPath = path.join(this.dataDir, 'change-detection.json');
  }

  getLastCheck() {
    if (!fs.existsSync(this.configPath)) {
      return { last_check: null, openclaw_models: 0, configured_models: 0 };
    }
    return JSON.parse(fs.readFileSync(this.configPath, 'utf8'));
  }

  saveCheck(data) {
    fs.mkdirSync(this.dataDir, { recursive: true });
    fs.writeFileSync(this.configPath, JSON.stringify(data, null, 2));
  }

  async checkForChanges() {
    // This would integrate with OpenClaw's model list
    // For now, placeholder that reads from config
    const pricingPath = path.join(__dirname, '..', 'config', 'pricing.json');
    
    let configuredModels = 0;
    if (fs.existsSync(pricingPath)) {
      const pricing = JSON.parse(fs.readFileSync(pricingPath, 'utf8'));
      for (const provider of Object.values(pricing.providers || {})) {
        configuredModels += Object.keys(provider.models || {}).length;
      }
    }
    
    const lastCheck = this.getLastCheck();
    
    return {
      last_check: lastCheck.last_check,
      configured_models: configuredModels,
      has_changes: false, // Would compare to OpenClaw's actual model list
      new_models: [],
      message: configuredModels > lastCheck.configured_models 
        ? 'New models detected in config' 
        : 'No changes detected'
    };
  }

  markChecked(newModels = []) {
    const pricingPath = path.join(__dirname, '..', 'config', 'pricing.json');
    let configuredModels = 0;
    
    if (fs.existsSync(pricingPath)) {
      const pricing = JSON.parse(fs.readFileSync(pricingPath, 'utf8'));
      for (const provider of Object.values(pricing.providers || {})) {
        configuredModels += Object.keys(provider.models || {}).length;
      }
    }
    
    this.saveCheck({
      last_check: new Date().toISOString(),
      configured_models: configuredModels,
      new_models: newModels,
      status: newModels.length > 0 ? 'new_models_found' : 'up_to_date'
    });
  }
}

module.exports = ChangeDetector;
