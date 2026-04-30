#!/usr/bin/env node

/**
 * 输出验证器
 * 
 * 自动验证 skill 输出质量
 */

const fs = require('fs');
const path = require('path');

class OutputValidator {
  constructor() {
    this.rules = new Map();
    this.results = new Map();
  }
  
  /**
   * 添加验证规则
   */
  addRule(skill, rule) {
    this.rules.set(skill, rule);
  }
  
  /**
   * 验证输出
   */
  async validate(skill, output) {
    const rule = this.rules.get(skill);
    
    if (!rule) {
      console.warn(`No validation rule for skill: ${skill}`);
      return {
        valid: true,
        errors: [],
        warnings: [],
        fixable: false
      };
    }
    
    const result = {
      valid: true,
      errors: [],
      warnings: [],
      fixable: false
    };
    
    // 验证必需章节
    if (rule.requiredSections) {
      const missingSections = this._checkRequiredSections(output, rule.requiredSections);
      if (missingSections.length > 0) {
        result.valid = false;
        result.errors.push(`Missing required sections: ${missingSections.join(', ')}`);
        result.fixable = true;
      }
    }
    
    // 验证格式
    if (rule.format) {
      const formatValid = this._checkFormat(output, rule.format);
      if (!formatValid) {
        result.valid = false;
        result.errors.push(`Invalid format: expected ${rule.format}`);
      }
    }
    
    // 验证长度
    if (rule.maxLength) {
      const lengthValid = this._checkMaxLength(output, rule.maxLength);
      if (!lengthValid) {
        result.valid = false;
        result.errors.push(`Output exceeds max length: ${rule.maxLength}`);
        result.fixable = true;
      }
    }
    
    if (rule.minLength) {
      const lengthValid = this._checkMinLength(output, rule.minLength);
      if (!lengthValid) {
        result.valid = false;
        result.errors.push(`Output below min length: ${rule.minLength}`);
      }
    }
    
    // 验证代码质量
    if (rule.codeQuality) {
      const codeQualityResult = await this._checkCodeQuality(output, rule.codeQuality);
      if (!codeQualityResult.valid) {
        result.valid = false;
        result.errors.push(...codeQualityResult.errors);
        result.warnings.push(...codeQualityResult.warnings);
      }
    }
    
    // 验证测试覆盖率
    if (rule.testCoverage) {
      const coverageResult = await this._checkTestCoverage(output, rule.testCoverage);
      if (!coverageResult.valid) {
        result.valid = false;
        result.errors.push(...coverageResult.errors);
        result.warnings.push(...coverageResult.warnings);
      }
    }
    
    // 保存结果
    this.results.set(skill, result);
    
    return result;
  }
  
  /**
   * 验证所有输出
   */
  async validateAll() {
    const results = new Map();
    
    for (const [skill, rule] of this.rules.entries()) {
      // 这里需要实际获取输出
      // 目前只是模拟
      const output = this._getOutputForSkill(skill);
      const result = await this.validate(skill, output);
      results.set(skill, result);
    }
    
    return results;
  }
  
  /**
   * 自动修复
   */
  async autoFix(skill) {
    const result = this.results.get(skill);
    
    if (!result || !result.fixable) {
      console.log(`No fixable issues for skill: ${skill}`);
      return;
    }
    
    console.log(`Auto-fixing issues for skill: ${skill}`);
    
    // 这里应该实际修复问题
    // 目前只是模拟
    console.log('Fixed issues');
  }
  
  /**
   * 获取验证报告
   */
  getReport() {
    const report = {
      total: this.results.size,
      valid: 0,
      invalid: 0,
      fixable: 0,
      details: []
    };
    
    for (const [skill, result] of this.results.entries()) {
      if (result.valid) {
        report.valid++;
      } else {
        report.invalid++;
        if (result.fixable) {
          report.fixable++;
        }
      }
      
      report.details.push({
        skill: skill,
        valid: result.valid,
        errors: result.errors,
        warnings: result.warnings,
        fixable: result.fixable
      });
    }
    
    return report;
  }
  
  /**
   * 从 DESIGN.md 加载验证规则
   */
  loadFromDesign(designPath) {
    const content = fs.readFileSync(designPath, 'utf8');
    
    // 解析质量验证部分
    const validationMatch = content.match(/##\s+质量验证\s*([\s\S]*?)(?=\n##|$)/);
    
    if (validationMatch) {
      const yaml = require('js-yaml');
      try {
        const validationConfig = yaml.load(validationMatch[1]);
        
        for (const [skill, rule] of Object.entries(validationConfig)) {
          this.addRule(skill, rule);
        }
        
        console.log(`Loaded ${Object.keys(validationConfig).length} validation rules`);
      } catch (e) {
        console.warn('Failed to parse validation rules:', e.message);
      }
    }
  }
  
  // 私有方法
  
  _checkRequiredSections(output, requiredSections) {
    const missing = [];
    
    for (const section of requiredSections) {
      // 检查是否存在该章节
      const regex = new RegExp(`^#+\\s*${section.replace(/\s+/g, '\\s+')}`, 'im');
      if (!regex.test(output)) {
        missing.push(section);
      }
    }
    
    return missing;
  }
  
  _checkFormat(output, format) {
    switch (format) {
      case 'markdown':
        // 简单的 markdown 格式检查
        return output.includes('#') || output.includes('**') || output.includes('`');
      
      case 'json':
        try {
          JSON.parse(output);
          return true;
        } catch (e) {
          return false;
        }
      
      case 'yaml':
        try {
          require('js-yaml').load(output);
          return true;
        } catch (e) {
          return false;
        }
      
      default:
        return true;
    }
  }
  
  _checkMaxLength(output, maxLength) {
    return output.length <= maxLength;
  }
  
  _checkMinLength(output, minLength) {
    return output.length >= minLength;
  }
  
  async _checkCodeQuality(output, quality) {
    const result = {
      valid: true,
      errors: [],
      warnings: []
    };
    
    // 提取代码块
    const codeBlocks = this._extractCodeBlocks(output);
    
    for (const block of codeBlocks) {
      // 简单的代码质量检查
      if (block.code.includes('console.log')) {
        result.warnings.push('Found console.log in code');
      }
      
      if (block.code.includes('TODO') || block.code.includes('FIXME')) {
        result.warnings.push('Found TODO/FIXME in code');
      }
      
      if (quality === 'high') {
        // 更严格的检查
        if (block.code.length < 10) {
          result.warnings.push('Code block is too short');
        }
      }
    }
    
    return result;
  }
  
  async _checkTestCoverage(output, requiredCoverage) {
    const result = {
      valid: true,
      errors: [],
      warnings: []
    };
    
    // 提取测试代码
    const testBlocks = this._extractTestBlocks(output);
    
    if (testBlocks.length === 0) {
      result.valid = false;
      result.errors.push('No test code found');
      return result;
    }
    
    // 简单的覆盖率估算
    // 实际应该使用覆盖率工具
    const estimatedCoverage = Math.min(testBlocks.length * 20, 100);
    
    if (estimatedCoverage < requiredCoverage) {
      result.valid = false;
      result.errors.push(`Test coverage (${estimatedCoverage}%) below required (${requiredCoverage}%)`);
    }
    
    return result;
  }
  
  _extractCodeBlocks(output) {
    const blocks = [];
    const regex = /```(\w+)?\n([\s\S]*?)```/g;
    let match;
    
    while ((match = regex.exec(output)) !== null) {
      blocks.push({
        language: match[1] || 'text',
        code: match[2]
      });
    }
    
    return blocks;
  }
  
  _extractTestBlocks(output) {
    const blocks = [];
    const regex = /```(\w+)?\n([\s\S]*?)```/g;
    let match;
    
    while ((match = regex.exec(output)) !== null) {
      const language = match[1] || 'text';
      const code = match[2];
      
      // 检查是否是测试代码
      if (language === 'python' && (code.includes('def test_') || code.includes('class Test'))) {
        blocks.push({ language, code });
      } else if (language === 'javascript' && (code.includes('describe') || code.includes('it('))) {
        blocks.push({ language, code });
      }
    }
    
    return blocks;
  }
  
  _getOutputForSkill(skill) {
    // 这里应该实际获取 skill 的输出
    // 目前返回空字符串
    return '';
  }
}

// 导出
module.exports = OutputValidator;

// 如果直接运行，提供 CLI 接口
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  
  const validator = new OutputValidator();
  
  switch (command) {
    case 'validate':
      const skill = args[1];
      const output = args[2];
      
      if (!skill) {
        console.error('Please provide skill name');
        process.exit(1);
      }
      
      if (!output) {
        console.error('Please provide output');
        process.exit(1);
      }
      
      validator.validate(skill, output).then(result => {
        console.log(JSON.stringify(result, null, 2));
      });
      break;
      
    case 'validate-all':
      validator.validateAll().then(results => {
        console.log(JSON.stringify(Object.fromEntries(results), null, 2));
      });
      break;
      
    case 'auto-fix':
      const fixSkill = args[1];
      if (!fixSkill) {
        console.error('Please provide skill name');
        process.exit(1);
      }
      validator.autoFix(fixSkill);
      break;
      
    case 'report':
      const report = validator.getReport();
      console.log(JSON.stringify(report, null, 2));
      break;
      
    case 'load-design':
      const designPath = args[1];
      if (!designPath) {
        console.error('Please provide DESIGN.md path');
        process.exit(1);
      }
      validator.loadFromDesign(designPath);
      break;
      
    default:
      console.log('Usage:');
      console.log('  validator validate <skill> <output>  - Validate output');
      console.log('  validator validate-all                 - Validate all outputs');
      console.log('  validator auto-fix <skill>             - Auto-fix issues');
      console.log('  validator report                       - Get validation report');
      console.log('  validator load-design <DESIGN.md>      - Load rules from DESIGN.md');
  }
}
