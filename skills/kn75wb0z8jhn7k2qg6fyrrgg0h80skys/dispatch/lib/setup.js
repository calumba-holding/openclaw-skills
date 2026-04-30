const fs = require('fs');
const path = require('path');
const readline = require('readline');

const DATA_DIR = process.env.DISPATCH_DATA || `${process.env.HOME}/.openclaw/workspace/.dispatch`;
const CONFIG_DIR = path.join(__dirname, '..', 'config');
const OPENCLAW_CONFIG = `${process.env.HOME}/.openclaw/openclaw.json`;

class Setup {
  constructor(options = {}) {
    this.autoMode = options.auto || false;
    this.config = {
      providers: {},
      trust: { trusted: [], untrusted: [] },
      model_tiers: { fast: [], capable: [], powerful: [] },
      auto_check: 'weekly',
      captain: null,
      agents: {}
    };
    this.detectedProviders = [];
    this.detectedAgents = [];
    this.suggestions = {};
  }

  async run() {
    console.log('🚀 Dispatch Setup\n');
    
    // First, detect everything
    this.detectProviders();
    this.detectAgents();
    
    if (this.autoMode) {
      // Auto mode: apply defaults without interaction
      console.log('\n⚙️  Running in auto mode with detected defaults...\n');
      this.generateSuggestions();
      this.applyDefaults();
      this.saveConfig();
      this.createDirectories();
      
      console.log('\n✓ Setup complete!');
      console.log(`Captain: ${this.config.captain}`);
      console.log(`Providers: ${Object.keys(this.config.providers).join(', ')}`);
      console.log(`Trusted: ${this.config.trust.trusted.join(', ') || 'none'}`);
      console.log(`Internal data: ${this.config.data_dir || DATA_DIR}`);
      console.log(`Output directory: ${this.config.output_dir || this.suggestions.outputDir}`);
      console.log(`Auto-check: ${this.config.auto_check}`);
    } else {
      // Interactive mode: show menu
      this.generateSuggestions();
      
      let done = false;
      while (!done) {
        this.showSummary();
        const choice = await this.question('\nEnter number to change, or 0 to accept and continue: ');
        
        switch (choice.trim()) {
          case '0':
            done = true;
            break;
          case '1':
            await this.changeProviders();
            break;
          case '2':
            await this.changeCaptain();
            break;
          case '3':
            await this.changeTrustLevels();
            break;
          case '4':
            await this.changeDataDir();
            break;
          case '5':
            await this.changeOutputDir();
            break;
          case '6':
            await this.changeAutoCheck();
            break;
          default:
            console.log('   Invalid option');
        }
      }
      
      this.saveConfig();
      this.createDirectories();
      
      console.log('\n✓ Setup complete!');
      console.log(`Captain: ${this.config.captain}`);
      console.log(`Internal data: ${this.config.data_dir || DATA_DIR}`);
      console.log(`Output directory: ${this.config.output_dir || this.suggestions.outputDir}`);
      console.log('\nTry: "Start project My Project"');
    }
  }

  detectProviders() {
    const providers = new Set();
    
    try {
      if (fs.existsSync(OPENCLAW_CONFIG)) {
        const openclawConfig = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
        const models = openclawConfig.agents?.defaults?.models || {};
        
        for (const modelId of Object.keys(models)) {
          const provider = modelId.includes('/') 
            ? modelId.split('/')[0] 
            : this.inferProvider(modelId);
          
          if (provider) {
            providers.add(provider);
          }
        }
      }
    } catch (err) {
      // Silent fail - will use empty detection
    }
    
    this.detectedProviders = Array.from(providers);
    
    // Pre-populate config with detected providers
    for (const provider of this.detectedProviders) {
      this.config.providers[provider] = { enabled: true, models: [] };
      this.config.trust.trusted.push(provider);
    }
  }

  inferProvider(model) {
    const patterns = {
      'gemini': 'google',
      'claude': 'anthropic',
      'gpt': 'openai',
      'kimi': 'kimi',
      'k2': 'kimi'
    };
    
    const lowerModel = model.toLowerCase();
    for (const [pattern, provider] of Object.entries(patterns)) {
      if (lowerModel.includes(pattern)) return provider;
    }
    return null;
  }

  detectAgents() {
    try {
      if (fs.existsSync(OPENCLAW_CONFIG)) {
        const openclawConfig = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
        const agents = openclawConfig.agents?.list || [];
        
        for (const agent of agents) {
          const agentConfig = {
            id: agent.id,
            name: agent.name || agent.id,
            workspace: agent.workspace,
            subagents: agent.subagents?.allowAgents || []
          };
          
          this.config.agents[agent.id] = agentConfig;
          this.detectedAgents.push(agentConfig);
        }
        
        // Default captain to echo
        const echo = this.detectedAgents.find(a => a.id === 'echo');
        this.config.captain = echo?.id || this.detectedAgents[0]?.id;
      }
    } catch (err) {
      // Silent fail
    }
  }

  generateSuggestions() {
    this.suggestions = {
      providers: this.detectedProviders.length > 0 
        ? this.detectedProviders.join(', ') 
        : 'none detected - will need manual entry',
      captain: this.config.captain || 'none detected',
      trusted: this.config.trust.trusted.join(', ') || 'none',
      dataDir: DATA_DIR,
      outputDir: `${process.env.HOME}/.openclaw/workspace/dispatch`,
      autoCheck: 'weekly'
    };
  }

  applyDefaults() {
    // In auto mode: trust all detected providers, use default paths
    this.config.output_dir = this.suggestions.outputDir;
    this.config.auto_check = 'weekly';
  }

  showSummary() {
    console.log('\n📋 Suggested Configuration:\n');
    console.log(`  1. Providers:     ${this.suggestions.providers}`);
    console.log(`  2. Captain:       ${this.config.captain || this.suggestions.captain}`);
    console.log(`  3. Trusted:       ${this.config.trust.trusted.join(', ') || this.suggestions.trusted}`);
    console.log(`  4. Data directory: ${this.config.data_dir || this.suggestions.dataDir}`);
    console.log(`  5. Output directory: ${this.config.output_dir || this.suggestions.outputDir}`);
    console.log(`  6. Auto-check:    ${this.config.auto_check}`);
    console.log('\n  0. ✓ Accept and continue');
  }

  async changeProviders() {
    console.log('\n   Current providers:', Object.keys(this.config.providers).join(', ') || 'none');
    console.log('   Available: google, openrouter, anthropic, kimi, openai');
    
    const input = await this.question('   Enter providers (comma-separated): ');
    const selected = input.split(',').map(s => s.trim()).filter(Boolean);
    
    // Reset and re-add
    this.config.providers = {};
    for (const provider of selected) {
      this.config.providers[provider] = { enabled: true, models: [] };
    }
    
    // Reset trust and ask again
    this.config.trust = { trusted: [], untrusted: [] };
    console.log('\n   Now setting trust levels for new providers...');
    for (const provider of selected) {
      const trust = await this.question(`   ${provider} - Trusted for sensitive data? (yes/no): `);
      if (trust.toLowerCase().startsWith('y')) {
        this.config.trust.trusted.push(provider);
      } else {
        this.config.trust.untrusted.push(provider);
      }
    }
  }

  async changeCaptain() {
    console.log('\n   Available agents:');
    for (const agent of this.detectedAgents) {
      const canSpawn = agent.subagents.length > 0 ? ' [can spawn agents]' : '';
      console.log(`     • ${agent.id} (${agent.name})${canSpawn}`);
    }
    
    const captainId = await this.question(`\n   Captain agent ID: `);
    const selected = this.detectedAgents.find(a => a.id === captainId.trim());
    
    if (selected) {
      this.config.captain = selected.id;
      console.log(`   ✓ Captain set to: ${selected.name}`);
    } else {
      console.log('   ⚠ Unknown agent, keeping current');
    }
  }

  async changeTrustLevels() {
    const providers = Object.keys(this.config.providers);
    if (providers.length === 0) {
      console.log('\n   No providers configured. Set providers first (option 1).');
      return;
    }
    
    console.log('\n   Classify providers for sensitive tasks:');
    this.config.trust = { trusted: [], untrusted: [] };
    
    for (const provider of providers) {
      const trust = await this.question(`   ${provider} - Trusted? (yes/no): `);
      if (trust.toLowerCase().startsWith('y')) {
        this.config.trust.trusted.push(provider);
      } else {
        this.config.trust.untrusted.push(provider);
      }
    }
  }

  async changeDataDir() {
    console.log(`\n   Current: ${this.config.data_dir || DATA_DIR}`);
    const custom = await this.question('   New path (Enter to keep): ');
    if (custom.trim()) {
      this.config.data_dir = custom.trim();
    }
  }

  async changeOutputDir() {
    const current = this.config.output_dir || this.suggestions.outputDir;
    console.log(`\n   Current: ${current}`);
    const custom = await this.question('   New path (Enter to keep): ');
    if (custom.trim()) {
      this.config.output_dir = custom.trim();
    }
  }

  async changeAutoCheck() {
    console.log(`\n   Current: ${this.config.auto_check}`);
    console.log('   Options: daily, weekly, never');
    const check = await this.question('   Frequency (Enter to keep): ');
    if (check.trim() && ['daily', 'weekly', 'never'].includes(check)) {
      this.config.auto_check = check;
    }
  }

  saveConfig() {
    const dataDir = this.config.data_dir || DATA_DIR;
    const configPath = path.join(dataDir, 'config.json');
    fs.mkdirSync(dataDir, { recursive: true });
    fs.writeFileSync(configPath, JSON.stringify(this.config, null, 2));
    
    // Also save default pricing
    const pricingPath = path.join(CONFIG_DIR, 'pricing.json');
    const defaultPricing = this.getDefaultPricing();
    fs.writeFileSync(pricingPath, JSON.stringify(defaultPricing, null, 2));
  }

  createDirectories() {
    // Create internal data directories
    const dataDir = this.config.data_dir || DATA_DIR;
    const internalDirs = ['projects', 'templates', 'logs'];
    for (const dir of internalDirs) {
      fs.mkdirSync(path.join(dataDir, dir), { recursive: true });
    }
    
    // Create output directory for deliverables
    if (this.config.output_dir) {
      fs.mkdirSync(this.config.output_dir, { recursive: true });
    }
  }

  getDefaultPricing() {
    return {
      providers: {
        google: {
          models: {
            'gemini-flash': { input: 0.35, output: 1.05, tier: 'fast' },
            'gemini-pro': { input: 3.50, output: 10.50, tier: 'capable' }
          }
        },
        openrouter: {
          models: {
            'anthropic/claude-3.5-sonnet': { input: 3.00, output: 15.00, tier: 'capable' },
            'anthropic/claude-3-opus': { input: 15.00, output: 75.00, tier: 'powerful' }
          }
        }
      }
    };
  }

  question(prompt) {
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    return new Promise(resolve => {
      rl.question(prompt, answer => {
        rl.close();
        resolve(answer);
      });
    });
  }
}

// Run if called directly
if (require.main === module) {
  const autoMode = process.argv.includes('--auto');
  const setup = new Setup({ auto: autoMode });
  setup.run().catch(console.error);
}

module.exports = Setup;
