/**
 * Logger - 前端日志系统模块
 * 提供统一的日志记录、过滤和输出功能
 */

(function () {
  'use strict';

  // ==================== 日志级别 ====================
  const LogLevel = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3,
    NONE: 4
  };

  // ==================== 配置 ====================
  const config = {
    level: LogLevel.INFO,
    prefix: '[MechForge]',
    timestamp: true,
    colorize: true,
    persist: false, // 是否持久化到 localStorage
    maxPersistLogs: 100
  };

  // ==================== 颜色映射 ====================
  const colors = {
    DEBUG: '#888888',
    INFO: '#00e5ff',
    WARN: '#ffa502',
    ERROR: '#ff4757'
  };

  // ==================== 日志存储 ====================
  const logBuffer = [];

  // ==================== 格式化 ====================

  /**
   * 获取时间戳
   * @returns {string}
   */
  function getTimestamp() {
    const now = new Date();
    return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}:${String(now.getSeconds()).padStart(2, '0')}.${String(now.getMilliseconds()).padStart(3, '0')}`;
  }

  /**
   * 格式化日志消息
   * @param {string} level - 日志级别
   * @param {string} module - 模块名
   * @param {string} message - 消息
   * @param {Array} args - 额外参数
   * @returns {string}
   */
  function formatMessage(level, module, message, args) {
    let formatted = '';
    
    if (config.timestamp) {
      formatted += `[${getTimestamp()}] `;
    }
    
    formatted += `${config.prefix} `;
    formatted += `[${level}] `;
    
    if (module) {
      formatted += `[${module}] `;
    }
    
    formatted += message;
    
    return formatted;
  }

  // ==================== 日志函数 ====================

  /**
   * 通用日志函数
   * @param {string} levelName - 日志级别名称
   * @param {number} level - 日志级别值
   * @param {string} module - 模块名
   * @param {string} message - 消息
   * @param {Array} args - 额外参数
   */
  function log(levelName, level, module, message, args) {
    if (level < config.level) return;

    const formatted = formatMessage(levelName, module, message, args);
    const color = config.colorize ? colors[levelName] : undefined;

    // 控制台输出
    const consoleMethod = levelName.toLowerCase();
    const style = color ? `color: ${color}; font-weight: bold;` : '';

    if (style) {
      console[consoleMethod](`%c${formatted}`, style, ...args);
    } else {
      console[consoleMethod](formatted, ...args);
    }

    // 存储到缓冲区
    const logEntry = {
      timestamp: Date.now(),
      level: levelName,
      module,
      message,
      args: args.length > 0 ? args : undefined
    };

    logBuffer.push(logEntry);

    // 限制缓冲区大小
    if (logBuffer.length > 1000) {
      logBuffer.shift();
    }

    // 持久化
    if (config.persist) {
      persistLog(logEntry);
    }
  }

  /**
   * 持久化日志
   * @param {Object} entry - 日志条目
   */
  function persistLog(entry) {
    try {
      const key = 'mechforge_logs';
      let logs = JSON.parse(localStorage.getItem(key) || '[]');
      logs.push(entry);
      
      // 限制数量
      if (logs.length > config.maxPersistLogs) {
        logs = logs.slice(-config.maxPersistLogs);
      }
      
      localStorage.setItem(key, JSON.stringify(logs));
    } catch (e) {
      // 忽略存储错误
    }
  }

  // ==================== 公共 API ====================

  const Logger = {
    /**
     * 设置日志级别
     * @param {number} level - LogLevel 值
     */
    setLevel(level) {
      config.level = level;
    },

    /**
     * 设置配置
     * @param {Object} options - 配置选项
     */
    configure(options) {
      Object.assign(config, options);
    },

    /**
     * 创建模块日志器
     * @param {string} module - 模块名
     * @returns {Object}
     */
    module(module) {
      return {
        debug: (msg, ...args) => log('DEBUG', LogLevel.DEBUG, module, msg, args),
        info: (msg, ...args) => log('INFO', LogLevel.INFO, module, msg, args),
        warn: (msg, ...args) => log('WARN', LogLevel.WARN, module, msg, args),
        error: (msg, ...args) => log('ERROR', LogLevel.ERROR, module, msg, args)
      };
    },

    /**
     * 获取日志缓冲区
     * @returns {Array}
     */
    getBuffer() {
      return [...logBuffer];
    },

    /**
     * 清空日志缓冲区
     */
    clearBuffer() {
      logBuffer.length = 0;
    },

    /**
     * 导出日志
     * @param {string} format - 导出格式 ('json' | 'text')
     * @returns {string}
     */
    export(format = 'text') {
      if (format === 'json') {
        return JSON.stringify(logBuffer, null, 2);
      }

      return logBuffer.map(entry => {
        const date = new Date(entry.timestamp);
        const time = date.toTimeString().split(' ')[0];
        return `[${time}] [${entry.level}] ${entry.module ? `[${entry.module}] ` : ''}${entry.message}`;
      }).join('\n');
    },

    // 快捷方法
    debug: (msg, ...args) => log('DEBUG', LogLevel.DEBUG, null, msg, args),
    info: (msg, ...args) => log('INFO', LogLevel.INFO, null, msg, args),
    warn: (msg, ...args) => log('WARN', LogLevel.WARN, null, msg, args),
    error: (msg, ...args) => log('ERROR', LogLevel.ERROR, null, msg, args)
  };

  // 导出
  window.Logger = Logger;
  window.LogLevel = LogLevel;

})();