/**
 * Validator - 数据验证器
 * 提供各种数据验证规则和表单验证功能
 */

(function () {
  'use strict';

  // ==================== 验证规则 ====================
  const rules = {
    // 必填
    required: (value) => {
      if (value === null || value === undefined) return false;
      if (typeof value === 'string') return value.trim().length > 0;
      if (Array.isArray(value)) return value.length > 0;
      if (typeof value === 'object') return Object.keys(value).length > 0;
      return true;
    },

    // 邮箱
    email: (value) => {
      if (!value) return true;
      const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return regex.test(value);
    },

    // URL
    url: (value) => {
      if (!value) return true;
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    },

    // 手机号（中国大陆）
    phone: (value) => {
      if (!value) return true;
      const regex = /^1[3-9]\d{9}$/;
      return regex.test(value);
    },

    // 身份证
    idCard: (value) => {
      if (!value) return true;
      const regex = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;
      return regex.test(value);
    },

    // 最小长度
    minLength: (value, length) => {
      if (!value) return true;
      return String(value).length >= length;
    },

    // 最大长度
    maxLength: (value, length) => {
      if (!value) return true;
      return String(value).length <= length;
    },

    // 长度范围
    length: (value, min, max) => {
      if (!value) return true;
      const len = String(value).length;
      return len >= min && len <= max;
    },

    // 最小值
    min: (value, min) => {
      if (!value && value !== 0) return true;
      return Number(value) >= min;
    },

    // 最大值
    max: (value, max) => {
      if (!value && value !== 0) return true;
      return Number(value) <= max;
    },

    // 范围
    range: (value, min, max) => {
      if (!value && value !== 0) return true;
      const num = Number(value);
      return num >= min && num <= max;
    },

    // 数字
    numeric: (value) => {
      if (!value && value !== 0) return true;
      return !isNaN(Number(value));
    },

    // 整数
    integer: (value) => {
      if (!value && value !== 0) return true;
      return Number.isInteger(Number(value));
    },

    // 正整数
    positive: (value) => {
      if (!value && value !== 0) return true;
      return Number(value) > 0;
    },

    // 非负整数
    nonNegative: (value) => {
      if (!value && value !== 0) return true;
      return Number(value) >= 0;
    },

    // 字母
    alpha: (value) => {
      if (!value) return true;
      return /^[a-zA-Z]+$/.test(value);
    },

    // 字母数字
    alphaNum: (value) => {
      if (!value) return true;
      return /^[a-zA-Z0-9]+$/.test(value);
    },

    // 字母数字下划线
    alphaNumUnderscore: (value) => {
      if (!value) return true;
      return /^[a-zA-Z0-9_]+$/.test(value);
    },

    // 中文
    chinese: (value) => {
      if (!value) return true;
      return /^[\u4e00-\u9fa5]+$/.test(value);
    },

    // 匹配正则
    pattern: (value, regex) => {
      if (!value) return true;
      if (typeof regex === 'string') {
        regex = new RegExp(regex);
      }
      return regex.test(value);
    },

    // 等于
    equals: (value, target) => {
      return value === target;
    },

    // 不等于
    notEquals: (value, target) => {
      return value !== target;
    },

    // 包含
    contains: (value, target) => {
      if (!value) return true;
      return String(value).includes(target);
    },

    // 不包含
    notContains: (value, target) => {
      if (!value) return true;
      return !String(value).includes(target);
    },

    // 以...开头
    startsWith: (value, target) => {
      if (!value) return true;
      return String(value).startsWith(target);
    },

    // 以...结尾
    endsWith: (value, target) => {
      if (!value) return true;
      return String(value).endsWith(target);
    },

    // 日期
    date: (value) => {
      if (!value) return true;
      const date = new Date(value);
      return !isNaN(date.getTime());
    },

    // 日期在范围内
    dateRange: (value, start, end) => {
      if (!value) return true;
      const date = new Date(value);
      const startDate = new Date(start);
      const endDate = new Date(end);
      return date >= startDate && date <= endDate;
    },

    // 文件类型
    fileType: (value, types) => {
      if (!value) return true;
      const typeList = Array.isArray(types) ? types : [types];
      const ext = value.split('.').pop().toLowerCase();
      return typeList.includes(ext);
    },

    // 文件大小
    fileSize: (value, maxSize) => {
      if (!value || !value.size) return true;
      return value.size <= maxSize;
    },

    // 自定义验证
    custom: (value, validator) => {
      return validator(value);
    }
  };

  // ==================== 错误消息 ====================
  const messages = {
    required: '此字段为必填项',
    email: '请输入有效的邮箱地址',
    url: '请输入有效的URL',
    phone: '请输入有效的手机号',
    idCard: '请输入有效的身份证号',
    minLength: '长度不能少于 {0} 个字符',
    maxLength: '长度不能超过 {0} 个字符',
    length: '长度必须在 {0} 到 {1} 个字符之间',
    min: '不能小于 {0}',
    max: '不能大于 {0}',
    range: '必须在 {0} 到 {1} 之间',
    numeric: '必须是数字',
    integer: '必须是整数',
    positive: '必须是正数',
    nonNegative: '必须是非负数',
    alpha: '只能包含字母',
    alphaNum: '只能包含字母和数字',
    alphaNumUnderscore: '只能包含字母、数字和下划线',
    chinese: '只能包含中文',
    pattern: '格式不正确',
    equals: '必须等于 {0}',
    notEquals: '不能等于 {0}',
    contains: '必须包含 {0}',
    notContains: '不能包含 {0}',
    startsWith: '必须以 {0} 开头',
    endsWith: '必须以 {0} 结尾',
    date: '必须是有效的日期',
    dateRange: '日期必须在 {0} 到 {1} 之间',
    fileType: '文件类型必须是 {0}',
    fileSize: '文件大小不能超过 {0}',
    custom: '验证失败'
  };

  // ==================== 验证函数 ====================

  /**
   * 验证单个值
   * @param {*} value - 要验证的值
   * @param {string|Object} rule - 验证规则
   * @param {*} params - 规则参数
   * @returns {Object}
   */
  function validate(value, rule, params) {
    // 字符串规则
    if (typeof rule === 'string') {
      const validator = rules[rule];
      if (!validator) {
        return { valid: false, error: `未知规则: ${rule}` };
      }
      const valid = validator(value, params);
      return {
        valid,
        error: valid ? null : formatMessage(rule, params)
      };
    }

    // 对象规则
    if (typeof rule === 'object') {
      const results = [];
      for (const [key, val] of Object.entries(rule)) {
        const result = validate(value, key, val);
        results.push(result);
        if (!result.valid) {
          return result;
        }
      }
      return { valid: true, error: null };
    }

    // 自定义验证函数
    if (typeof rule === 'function') {
      const valid = rule(value);
      return {
        valid,
        error: valid ? null : messages.custom
      };
    }

    return { valid: false, error: '无效的验证规则' };
  }

  /**
   * 验证多个规则
   * @param {*} value - 要验证的值
   * @param {Array} rulesList - 规则列表
   * @returns {Object}
   */
  function validateAll(value, rulesList) {
    for (const rule of rulesList) {
      const result = validate(value, rule.rule, rule.params);
      if (!result.valid) {
        return {
          valid: false,
          error: rule.message || result.error,
          rule: rule.rule
        };
      }
    }
    return { valid: true, error: null };
  }

  /**
   * 验证表单
   * @param {Object} data - 表单数据
   * @param {Object} schema - 验证模式
   * @returns {Object}
   */
  function validateForm(data, schema) {
    const errors = {};
    let isValid = true;

    for (const [field, rules] of Object.entries(schema)) {
      const value = data[field];
      const result = validateAll(value, Array.isArray(rules) ? rules : [rules]);

      if (!result.valid) {
        errors[field] = result.error;
        isValid = false;
      }
    }

    return {
      valid: isValid,
      errors,
      data
    };
  }

  /**
   * 格式化错误消息
   * @param {string} rule - 规则名
   * @param {*} params - 参数
   * @returns {string}
   */
  function formatMessage(rule, params) {
    const message = messages[rule] || '验证失败';
    if (!params) return message;

    const args = Array.isArray(params) ? params : [params];
    return message.replace(/\{(\d+)\}/g, (match, index) => {
      return args[index] !== undefined ? args[index] : match;
    });
  }

  /**
   * 添加自定义规则
   * @param {string} name - 规则名
   * @param {Function} validator - 验证函数
   * @param {string} message - 错误消息
   */
  function addRule(name, validator, message) {
    rules[name] = validator;
    if (message) {
      messages[name] = message;
    }
  }

  /**
   * 设置错误消息
   * @param {string} rule - 规则名
   * @param {string} message - 消息
   */
  function setMessage(rule, message) {
    messages[rule] = message;
  }

  // ==================== 快捷验证方法 ====================

  function isEmail(value) {
    return rules.email(value);
  }

  function isPhone(value) {
    return rules.phone(value);
  }

  function isUrl(value) {
    return rules.url(value);
  }

  function isNumeric(value) {
    return rules.numeric(value);
  }

  function isInteger(value) {
    return rules.integer(value);
  }

  function isEmpty(value) {
    return !rules.required(value);
  }

  function isRequired(value) {
    return rules.required(value);
  }

  // ==================== 导出 ====================
  window.Validator = {
    rules,
    messages,
    validate,
    validateAll,
    validateForm,
    addRule,
    setMessage,
    formatMessage,
    isEmail,
    isPhone,
    isUrl,
    isNumeric,
    isInteger,
    isEmpty,
    isRequired
  };

})();
