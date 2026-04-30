const fs = require('fs');
const path = require('path');

class CostEstimator {
  constructor(pricingConfig) {
    this.pricing = pricingConfig || this.loadPricing();
  }

  loadPricing() {
    const configPath = path.join(__dirname, '..', 'config', 'pricing.json');
    if (fs.existsSync(configPath)) {
      return JSON.parse(fs.readFileSync(configPath, 'utf8'));
    }
    return { providers: {} };
  }

  estimate(request, tier = 'auto') {
    // Break request into sub-tasks
    const tasks = this.breakIntoTasks(request);
    
    // Assign models and calculate costs
    const estimates = tasks.map(task => {
      const model = this.selectModel(task, tier);
      const tokens = this.estimateTokens(task);
      const cost = this.calculateCost(model, tokens);
      
      return {
        description: task,
        model: model.id,
        provider: model.provider,
        tokens_in: tokens.input,
        tokens_out: tokens.output,
        cost_usd: cost,
        tier: model.tier
      };
    });
    
    const total = estimates.reduce((sum, e) => sum + e.cost_usd, 0);
    
    return {
      tasks: estimates,
      total_estimate: Math.round(total * 100) / 100,
      currency: 'USD'
    };
  }

  breakIntoTasks(request) {
    // Simple heuristic-based task breaking
    const tasks = [];
    const lower = request.toLowerCase();
    
    if (lower.includes('research') || lower.includes('find')) {
      tasks.push('Search for relevant information');
      tasks.push('Analyze and summarize findings');
    }
    
    if (lower.includes('compare')) {
      tasks.push('Identify options to compare');
      tasks.push('Evaluate each option');
      tasks.push('Generate comparison summary');
    }
    
    if (lower.includes('write') || lower.includes('create')) {
      tasks.push('Plan structure and approach');
      tasks.push('Generate content');
      tasks.push('Review and refine');
    }
    
    if (tasks.length === 0) {
      tasks.push(request);
    }
    
    return tasks;
  }

  selectModel(task, requestedTier) {
    const tiers = ['fast', 'capable', 'powerful'];
    const taskLower = task.toLowerCase();
    
    // Determine tier
    let tier = requestedTier;
    if (tier === 'auto') {
      if (taskLower.includes('research') || taskLower.includes('search') || taskLower.includes('find')) {
        tier = 'fast';
      } else if (taskLower.includes('design') || taskLower.includes('architecture') || taskLower.includes('code')) {
        tier = 'capable';
      } else if (taskLower.includes('analyze') || taskLower.includes('optimize') || taskLower.includes('complex')) {
        tier = 'powerful';
      } else {
        tier = 'capable';
      }
    }
    
    // Find cheapest model in tier
    let selected = null;
    let minPrice = Infinity;
    
    for (const [provider, data] of Object.entries(this.pricing.providers)) {
      for (const [modelId, pricing] of Object.entries(data.models || {})) {
        if (pricing.tier === tier) {
          const avgPrice = (pricing.input + pricing.output) / 2;
          if (avgPrice < minPrice) {
            minPrice = avgPrice;
            selected = { id: modelId, provider, tier, pricing };
          }
        }
      }
    }
    
    // Fallback to any available model
    if (!selected) {
      for (const [provider, data] of Object.entries(this.pricing.providers)) {
        const models = Object.entries(data.models || {});
        if (models.length > 0) {
          const [modelId, pricing] = models[0];
          selected = { id: modelId, provider, tier: pricing.tier || 'unknown', pricing };
          break;
        }
      }
    }
    
    return selected;
  }

  estimateTokens(task) {
    // Rough estimation based on task description length
    const words = task.split(/\s+/).length;
    
    return {
      input: Math.min(4000, Math.max(500, words * 10)),
      output: Math.min(2000, Math.max(200, words * 5))
    };
  }

  calculateCost(model, tokens) {
    if (!model || !model.pricing) return 0;
    
    const inputCost = (tokens.input / 1000000) * model.pricing.input;
    const outputCost = (tokens.output / 1000000) * model.pricing.output;
    
    return Math.round((inputCost + outputCost) * 100) / 100;
  }
}

module.exports = CostEstimator;
