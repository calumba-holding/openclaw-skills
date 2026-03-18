/**
 * new-robot-setup 技能测试用例
 * 测试状态管理和日志脱敏功能
 */

const StateManager = require('./state-manager');
const { sanitizeLog, sanitizeObject, SENSITIVE_PATTERNS } = require('../utils/logger');
const fs = require('fs');
const path = require('path');
const assert = require('assert');

// 测试目录
const TEST_DIR = path.join(__dirname, 'test-data');

console.log('🧪 开始运行测试用例...\n');

// ========== 测试状态管理器 ==========
console.log('=== 测试状态管理器 ===\n');

// 测试 1: 创建状态管理器
console.log('测试 1: 创建状态管理器');
try {
  const stateManager = new StateManager(TEST_DIR);
  console.log('✅ 状态管理器创建成功\n');
} catch (error) {
  console.log('❌ 状态管理器创建失败:', error.message, '\n');
}

// 测试 2: 创建新状态
console.log('测试 2: 创建新状态');
try {
  const stateManager = new StateManager(TEST_DIR);
  const testUserId = 'test_user_001';
  const state = stateManager.createState(testUserId);
  
  assert(state.session_id, '应该有 session_id');
  assert(state.user_id === testUserId, 'user_id 应该匹配');
  assert(state.current_step === 0, '初始步骤应该是 0（从功能介绍开始）');
  assert(state.step_data, '应该有 step_data');
  assert(state.created_at, '应该有 created_at');
  assert(state.updated_at, '应该有 updated_at');
  
  console.log('✅ 状态创建成功');
  console.log('   Session ID:', state.session_id);
  console.log('   初始步骤:', state.current_step, '\n');
} catch (error) {
  console.log('❌ 状态创建失败:', error.message, '\n');
}

// 测试 3: 保存和加载状态
console.log('测试 3: 保存和加载状态');
try {
  const stateManager = new StateManager(TEST_DIR);
  const testUserId = 'test_user_002';
  
  const initialState = stateManager.createState(testUserId);
  stateManager.saveState(testUserId, initialState);
  
  const loadedState = stateManager.loadState(testUserId);
  
  assert(loadedState, '应该能加载状态');
  assert(loadedState.session_id === initialState.session_id, 'session_id 应该匹配');
  assert(loadedState.user_id === testUserId, 'user_id 应该匹配');
  
  console.log('✅ 保存和加载状态成功\n');
} catch (error) {
  console.log('❌ 保存和加载状态失败:', error.message, '\n');
}

// 测试 4: 回退功能
console.log('测试 4: 回退功能 (goBack)');
try {
  const stateManager = new StateManager(TEST_DIR);
  const testUserId = 'test_user_003';
  
  // 创建状态并前进到第 5 步
  const state = stateManager.createState(testUserId);
  state.current_step = 5;
  stateManager.saveState(testUserId, state);
  
  // 测试回退
  const result1 = stateManager.goBack(testUserId);
  assert(result1.success === true, '回退应该成功');
  assert(result1.step === 4, '应该回退到第 4 步');
  
  const result2 = stateManager.goBack(testUserId);
  assert(result2.success === true, '再次回退应该成功');
  assert(result2.step === 3, '应该回退到第 3 步');
  
  // 回退到第 0 步后继续回退
  stateManager.updateStep(testUserId, 0);
  const result3 = stateManager.goBack(testUserId);
  assert(result3.success === false, '第 0 步回退应该失败');
  assert(result3.message, '应该有错误消息');
  
  console.log('✅ 回退功能测试成功');
  console.log('   从第 5 步回退到第 4 步：成功');
  console.log('   从第 4 步回退到第 3 步：成功');
  console.log('   从第 0 步回退：正确失败\n');
} catch (error) {
  console.log('❌ 回退功能测试失败:', error.message, '\n');
}

// 测试 5: 前进功能
console.log('测试 5: 前进功能 (goNext)');
try {
  const stateManager = new StateManager(TEST_DIR);
  const testUserId = 'test_user_004';
  
  const state = stateManager.createState(testUserId);
  stateManager.saveState(testUserId, state);
  
  const result1 = stateManager.goNext(testUserId);
  assert(result1.success === true, '前进应该成功');
  assert(result1.step === 1, '应该前进到第 1 步');
  
  // 前进到第 10 步（从 0 开始，需要前进 10 次）
  for (let i = 0; i < 9; i++) {
    stateManager.goNext(testUserId);
  }
  
  const result2 = stateManager.goNext(testUserId);
  assert(result2.success === false, '第 10 步前进应该失败');
  
  console.log('✅ 前进功能测试成功\n');
} catch (error) {
  console.log('❌ 前进功能测试失败:', error.message, '\n');
}

// 测试 6: 步骤数据保存
console.log('测试 6: 步骤数据保存');
try {
  const stateManager = new StateManager(TEST_DIR);
  const testUserId = 'test_user_005';
  
  stateManager.getOrCreateState(testUserId);
  
  const stepData = {
    streaming: true,
    memory: 'enhanced',
    receipt: true
  };
  
  stateManager.saveStepData(testUserId, 1, stepData);
  
  const loadedData = stateManager.getStepData(testUserId, 1);
  assert(loadedData, '应该能加载步骤数据');
  assert(loadedData.streaming === true, 'streaming 应该匹配');
  assert(loadedData.memory === 'enhanced', 'memory 应该匹配');
  
  console.log('✅ 步骤数据保存成功\n');
} catch (error) {
  console.log('❌ 步骤数据保存失败:', error.message, '\n');
}

// 测试 7: 清除状态
console.log('测试 7: 清除状态');
try {
  const stateManager = new StateManager(TEST_DIR);
  const testUserId = 'test_user_006';
  
  stateManager.getOrCreateState(testUserId);
  const result = stateManager.clearState(testUserId);
  
  assert(result === true, '清除应该成功');
  
  const loadedState = stateManager.loadState(testUserId);
  assert(loadedState === null, '清除后应该返回 null');
  
  console.log('✅ 清除状态成功\n');
} catch (error) {
  console.log('❌ 清除状态失败:', error.message, '\n');
}

// ========== 测试日志脱敏 ==========
console.log('=== 测试日志脱敏 ===\n');

// 测试 8: 邮箱脱敏
console.log('测试 8: 邮箱脱敏');
try {
  const testCases = [
    { input: '联系邮箱：test@example.com', expected: '联系邮箱：[EMAIL]' },
    { input: '邮箱 user.name+tag@domain.co.uk 已验证', expected: '邮箱 [EMAIL] 已验证' }
  ];
  
  for (const testCase of testCases) {
    const result = sanitizeLog(testCase.input);
    assert(result.includes('[EMAIL]'), `应该脱敏邮箱：${testCase.input}`);
  }
  
  console.log('✅ 邮箱脱敏测试通过\n');
} catch (error) {
  console.log('❌ 邮箱脱敏测试失败:', error.message, '\n');
}

// 测试 9: 手机号脱敏
console.log('测试 9: 手机号脱敏');
try {
  const testCases = [
    { input: '手机号：13812345678', expected: '手机号：[PHONE]' },
    { input: '电话 19912345678 已联系', expected: '电话 [PHONE] 已联系' }
  ];
  
  for (const testCase of testCases) {
    const result = sanitizeLog(testCase.input);
    assert(result.includes('[PHONE]'), `应该脱敏手机号：${testCase.input}`);
  }
  
  console.log('✅ 手机号脱敏测试通过\n');
} catch (error) {
  console.log('❌ 手机号脱敏测试失败:', error.message, '\n');
}

// 测试 10: API Key 脱敏
console.log('测试 10: API Key 脱敏');
try {
  const testCases = [
    { input: 'API Key: abcdef1234567890abcdef1234567890', expected: 'API Key: [API_KEY]' },
    { input: '密钥 xyzXYZ123456789012345678901234 已生成', expected: '密钥 [API_KEY] 已生成' }
  ];
  
  for (const testCase of testCases) {
    const result = sanitizeLog(testCase.input);
    assert(result.includes('[API_KEY]'), `应该脱敏 API Key: ${testCase.input}`);
  }
  
  console.log('✅ API Key 脱敏测试通过\n');
} catch (error) {
  console.log('❌ API Key 脱敏测试失败:', error.message, '\n');
}

// 测试 11: 密码脱敏
console.log('测试 11: 密码脱敏');
try {
  const testCases = [
    { input: 'password: secret123', expected: 'password: [REDACTED]' },
    { input: "password = 'mysecret'", expected: 'password: [REDACTED]' },
    { input: 'Secret: topsecret456', expected: 'secret: [REDACTED]' },
    { input: 'Token: abc123xyz', expected: 'token: [REDACTED]' }
  ];
  
  for (const testCase of testCases) {
    const result = sanitizeLog(testCase.input);
    assert(result.includes('[REDACTED]'), `应该脱敏敏感信息：${testCase.input}`);
  }
  
  console.log('✅ 密码脱敏测试通过\n');
} catch (error) {
  console.log('❌ 密码脱敏测试失败:', error.message, '\n');
}

// 测试 12: 对象脱敏
console.log('测试 12: 对象脱敏');
try {
  const testObj = {
    username: '张三',
    email: 'zhangsan@example.com',
    phone: '13812345678',
    password: 'secret123',
    config: {
      api_key: 'abcdef1234567890abcdef1234567890',
      enabled: true
    }
  };
  
  const sanitized = sanitizeObject(testObj);
  
  assert(sanitized.email === '[EMAIL]', '邮箱应该被脱敏');
  assert(sanitized.phone === '[PHONE]', '手机号应该被脱敏');
  assert(sanitized.password === '[REDACTED]', '密码应该被脱敏');
  assert(sanitized.config.api_key === '[REDACTED]', 'API Key 应该被脱敏');
  assert(sanitized.username === '张三', '普通字段不应该被脱敏');
  assert(sanitized.config.enabled === true, '布尔值不应该被脱敏');
  
  console.log('✅ 对象脱敏测试通过');
  console.log('   原始对象:', JSON.stringify(testObj, null, 2));
  console.log('   脱敏后:', JSON.stringify(sanitized, null, 2), '\n');
} catch (error) {
  console.log('❌ 对象脱敏测试失败:', error.message, '\n');
}

// 测试 13: 获取所有会话
console.log('测试 13: 获取所有会话');
try {
  const stateManager = new StateManager(TEST_DIR);
  
  // 创建几个测试会话
  for (let i = 10; i < 13; i++) {
    const userId = `test_user_0${i}`;
    stateManager.getOrCreateState(userId);
  }
  
  const sessions = stateManager.getAllSessions();
  assert(sessions.length >= 3, '应该至少有 3 个会话');
  
  console.log(`✅ 获取所有会话成功，共 ${sessions.length} 个会话\n`);
} catch (error) {
  console.log('❌ 获取所有会话失败:', error.message, '\n');
}

// 清理测试数据
console.log('清理测试数据...');
try {
  if (fs.existsSync(TEST_DIR)) {
    fs.rmSync(TEST_DIR, { recursive: true, force: true });
    console.log('✅ 测试数据已清理\n');
  }
} catch (error) {
  console.log('⚠️ 清理测试数据失败:', error.message, '\n');
}

// ========== 测试总结 ==========
console.log('=================================');
console.log('✅ 所有测试用例执行完成！');
console.log('=================================\n');

console.log('📊 测试覆盖：');
console.log('   - 状态管理器：7 个测试');
console.log('   - 日志脱敏：6 个测试');
console.log('   - 总计：13 个测试用例\n');

console.log('💡 提示：');
console.log('   - 状态管理支持保存、加载、回退、前进、清除等功能');
console.log('   - 日志脱敏支持邮箱、手机号、身份证、API Key、密码等敏感信息');
console.log('   - 所有 console.log/error/warn 都已自动包装，确保日志安全\n');
