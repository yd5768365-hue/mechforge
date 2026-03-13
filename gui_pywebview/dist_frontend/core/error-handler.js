/**
 * @fileoverview ErrorHandler - 全局错误处理模块
 * @description 提供统一的错误捕获、日志记录和用户提示
 * @module ErrorHandler
 * @version 2.0.0
 */

(function () {
  'use strict';

  // ==================== 错误类型定义 ====================

  /**
   * 错误类型枚举
   * @readonly
   * @enum {string}
   */
  const ErrorTypes = {
    /** 网络错误 */
    NETWORK: 'NETWORK_ERROR',
    /** API 错误 */
    API: 'API_ERROR',
    /** 验证错误 */
    VALIDATION: 'VALIDATION_ERROR',
    /** 运行时错误 */
    RUNTIME: 'RUNTIME_ERROR',
    /** 初始化错误 */
    INITIALIZATION: 'INITIALIZATION_ERROR',
    /** 超时错误 */
    TIMEOUT: 'TIMEOUT_ERROR',
    /** 取消错误 */
    ABORT: 'ABORT_ERROR',
    /** 未知错误 */
    UNKNOWN: 'UNKNOWN_ERROR'
  };

  /**
   * 错误严重级别
   * @readonly
   * @enum {string}
   */
  const ErrorSeverity = {
    /** 低 - 可以忽略 */
    LOW: 'low',
    /** 中 - 需要关注 */
    MEDIUM: 'medium',
    /** 高 - 需要处理 */
    HIGH: 'high',
    /** 严重 - 影响功能 */
    CRITICAL: 'critical'
  };

  // ==================== 自定义错误类 ====================

  /**
   * 应用错误类
   * @extends Error
   */
  class AppError extends Error {
    /**
     * @param {string} type - 错误类型
     * @param {string} message - 错误消息
     * @param {Object} [context={}] - 上下文信息
     * @param {Error} [cause] - 原始错误
     */
    constructor(type, message, context = {}, cause) {
      super(message);
      this.name = 'AppError';
      this.type = type;
      this.context = context;
      this.cause = cause;
      this.timestamp = new Date().toISOString();
      this.severity = this._calculateSeverity();

      // 保持堆栈跟踪
      if (Error.captureStackTrace) {
        Error.captureStackTrace(this, AppError);
      }
    }

    /**
     * 计算错误严重级别
     * @private
     * @returns {string} 严重级别
     */
    _calculateSeverity() {
      const criticalTypes = [ErrorTypes.INITIALIZATION, ErrorTypes.RUNTIME];
      const highTypes = [ErrorTypes.API, ErrorTypes.NETWORK];

      if (criticalTypes.includes(this.type)) return ErrorSeverity.CRITICAL;
      if (highTypes.includes(this.type)) return ErrorSeverity.HIGH;
      if (this.type === ErrorTypes.VALIDATION) return ErrorSeverity.LOW;
      return ErrorSeverity.MEDIUM;
    }

    /**
     * 转换为 JSON
     * @returns {Object} 错误对象
     */
    toJSON() {
      return {
        name: this.name,
        type: this.type,
        message: this.message,
        severity: this.severity,
        context: this.context,
        cause: this.cause?.message,
        timestamp: this.timestamp,
        stack: this.stack
      };
    }
  }

  /**
   * 网络错误类
   * @extends AppError
   */
  class NetworkError extends AppError {
    /**
     * @param {string} message - 错误消息
     * @param {Object} [context={}] - 上下文信息
     * @param {Error} [cause] - 原始错误
     */
    constructor(message, context = {}, cause) {
      super(ErrorTypes.NETWORK, message, context, cause);
      this.name = 'NetworkError';
    }
  }

  /**
   * API 错误类
   * @extends AppError
   */
  class APIError extends AppError {
    /**
     * @param {string} message - 错误消息
     * @param {number} [statusCode] - HTTP 状态码
     * @param {Object} [context={}] - 上下文信息
     * @param {Error} [cause] - 原始错误
     */
    constructor(message, statusCode, context = {}, cause) {
      super(ErrorTypes.API, message, context, cause);
      this.name = 'APIError';
      this.statusCode = statusCode;
    }
  }

  /**
   * 验证错误类
   * @extends AppError
   */
  class ValidationError extends AppError {
    /**
     * @param {string} message - 错误消息
     * @param {Object} [fields={}] - 字段错误
     * @param {Object} [context={}] - 上下文信息
     */
    constructor(message, fields = {}, context = {}) {
      super(ErrorTypes.VALIDATION, message, context);
      this.name = 'ValidationError';
      this.fields = fields;
    }
  }

  /**
   * 超时错误类
   * @extends AppError
   */
  class TimeoutError extends AppError {
    /**
     * @param {string} message - 错误消息
     * @param {number} timeout - 超时时间
     * @param {Object} [context={}] - 上下文信息
     */
    constructor(message, timeout, context = {}) {
      super(ErrorTypes.TIMEOUT, message, context);
      this.name = 'TimeoutError';
      this.timeout = timeout;
    }
  }

  // ==================== 错误处理器 ====================

  /**
   * 错误处理器类
   */
  class ErrorHandler {
    constructor() {
      /** @private @type {Map<string, Function[]>} */
      this._listeners = new Map();
      /** @private @type {Array<Object>} */
      this._errorHistory = [];
      /** @private @type {number} */
      this._maxHistorySize = 100;
      /** @private @type {Set<string>} */
      this._silentTypes = new Set([ErrorTypes.VALIDATION]);

      this._setupGlobalHandlers();
    }

    /**
     * 设置全局错误处理器
     * @private
     */
    _setupGlobalHandlers() {
      // 捕获未处理的 Promise 拒绝
      window.addEventListener('unhandledrejection', (event) => {
        this._handleUnhandledRejection(event);
      });

      // 捕获全局错误
      window.addEventListener('error', (event) => {
        this._handleGlobalError(event);
      });

      // 捕获资源加载错误
      window.addEventListener('error', (event) => {
        if (event.target && event.target !== window) {
          this._handleResourceError(event);
        }
      }, true);
    }

    /**
     * 处理未处理的 Promise 拒绝
     * @private
     * @param {PromiseRejectionEvent} event
     */
    _handleUnhandledRejection(event) {
      const error = event.reason;
      console.error('[Unhandled Rejection]', error);

      const errorInfo = this.normalizeError(error, ErrorTypes.RUNTIME);
      this._processError(errorInfo);

      event.preventDefault();
    }

    /**
     * 处理全局错误
     * @private
     * @param {ErrorEvent} event
     */
    _handleGlobalError(event) {
      const error = event.error;
      console.error('[Global Error]', error);

      const errorInfo = this.normalizeError(error, ErrorTypes.RUNTIME, {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      });
      this._processError(errorInfo);

      event.preventDefault();
    }

    /**
     * 处理资源加载错误
     * @private
     * @param {Event} event
     */
    _handleResourceError(event) {
      const target = event.target;
      const tagName = target.tagName?.toLowerCase();
      const src = target.src || target.href;

      const errorInfo = {
        type: ErrorTypes.NETWORK,
        message: `Failed to load ${tagName}: ${src}`,
        severity: ErrorSeverity.MEDIUM,
        context: { tagName, src },
        timestamp: new Date().toISOString()
      };

      this._processError(errorInfo);
    }

    /**
     * 处理错误
     * @param {Error|string|Object} error - 错误对象或消息
     * @param {string} [type=ErrorTypes.UNKNOWN] - 错误类型
     * @param {Object} [context={}] - 上下文信息
     * @returns {Object} 标准化后的错误信息
     */
    handleError(error, type = ErrorTypes.UNKNOWN, context = {}) {
      const errorInfo = this.normalizeError(error, type, context);
      this._processError(errorInfo);
      return errorInfo;
    }

    /**
     * 处理错误（内部）
     * @private
     * @param {Object} errorInfo - 错误信息
     */
    _processError(errorInfo) {
      // 记录到历史
      this._addToHistory(errorInfo);

      // 记录日志
      this._logError(errorInfo);

      // 触发监听器
      this._notifyListeners(errorInfo);

      // 显示用户提示
      this._showUserMessage(errorInfo);
    }

    /**
     * 标准化错误信息
     * @param {Error|string|Object} error - 错误对象
     * @param {string} type - 错误类型
     * @param {Object} context - 上下文
     * @returns {Object} 标准化后的错误信息
     */
    normalizeError(error, type, context = {}) {
      // 已经是 AppError
      if (error instanceof AppError) {
        return error.toJSON();
      }

      // 标准 Error 对象
      if (error instanceof Error) {
        return {
          type,
          name: error.name,
          message: error.message,
          stack: error.stack,
          severity: ErrorSeverity.HIGH,
          ...context,
          timestamp: new Date().toISOString()
        };
      }

      // 对象类型
      if (error !== null && typeof error === 'object') {
        return {
          type,
          message: error.message || error.detail || JSON.stringify(error),
          severity: error.severity || ErrorSeverity.MEDIUM,
          ...error,
          ...context,
          timestamp: new Date().toISOString()
        };
      }

      // 其他类型
      return {
        type,
        message: String(error),
        severity: ErrorSeverity.MEDIUM,
        ...context,
        timestamp: new Date().toISOString()
      };
    }

    /**
     * 添加错误到历史
     * @private
     * @param {Object} errorInfo - 错误信息
     */
    _addToHistory(errorInfo) {
      this._errorHistory.push(errorInfo);
      if (this._errorHistory.length > this._maxHistorySize) {
        this._errorHistory.shift();
      }
    }

    /**
     * 记录错误日志
     * @private
     * @param {Object} errorInfo - 错误信息
     */
    _logError(errorInfo) {
      const prefix = `[${errorInfo.type}]`;
      const logData = {
        message: errorInfo.message,
        severity: errorInfo.severity,
        timestamp: errorInfo.timestamp,
        ...errorInfo.context
      };

      switch (errorInfo.severity) {
        case ErrorSeverity.CRITICAL:
        case ErrorSeverity.HIGH:
          console.error(prefix, errorInfo.message, logData);
          break;
        case ErrorSeverity.MEDIUM:
          console.warn(prefix, errorInfo.message, logData);
          break;
        default:
          console.log(prefix, errorInfo.message, logData);
      }
    }

    /**
     * 显示用户提示
     * @private
     * @param {Object} errorInfo - 错误信息
     */
    _showUserMessage(errorInfo) {
      // 静默类型不显示
      if (this._silentTypes.has(errorInfo.type)) {
        return;
      }

      // 只显示中高严重级别的错误
      if (errorInfo.severity === ErrorSeverity.LOW) {
        return;
      }

      // 尝试使用 ChatUI 显示
      if (window.ChatUI && typeof window.ChatUI.addSystemMessage === 'function') {
        const icon = errorInfo.severity === ErrorSeverity.CRITICAL ? '🔴' : '⚠️';
        window.ChatUI.addSystemMessage(`${icon} ${errorInfo.message}`);
        return;
      }

      // 降级到 console
      console.warn('Error:', errorInfo.message);
    }

    /**
     * 订阅错误事件
     * @param {string} type - 错误类型或 '*' 表示所有
     * @param {Function} callback - 回调函数
     * @returns {Function} 取消订阅函数
     */
    onError(type, callback) {
      if (!this._listeners.has(type)) {
        this._listeners.set(type, []);
      }
      this._listeners.get(type).push(callback);

      // 返回取消订阅函数
      return () => {
        const listeners = this._listeners.get(type);
        if (listeners) {
          const index = listeners.indexOf(callback);
          if (index > -1) {
            listeners.splice(index, 1);
          }
        }
      };
    }

    /**
     * 通知监听器
     * @private
     * @param {Object} errorInfo - 错误信息
     */
    _notifyListeners(errorInfo) {
      const notify = (listeners) => {
        if (!listeners) return;
        listeners.forEach((cb) => {
          try {
            cb(errorInfo);
          } catch (e) {
            console.error('Error in error listener:', e);
          }
        });
      };

      // 通知特定类型的监听器
      notify(this._listeners.get(errorInfo.type));

      // 通知全局监听器
      notify(this._listeners.get('*'));
    }

    /**
     * 获取错误历史
     * @param {string} [type] - 错误类型过滤
     * @param {number} [limit] - 返回数量限制
     * @returns {Array<Object>} 错误历史
     */
    getErrorHistory(type, limit) {
      let history = this._errorHistory;

      if (type) {
        history = history.filter((e) => e.type === type);
      }

      if (limit) {
        history = history.slice(-limit);
      }

      return [...history];
    }

    /**
     * 清空错误历史
     */
    clearHistory() {
      this._errorHistory = [];
    }

    /**
     * 设置静默类型
     * @param {string} type - 错误类型
     * @param {boolean} silent - 是否静默
     */
    setSilentType(type, silent) {
      if (silent) {
        this._silentTypes.add(type);
      } else {
        this._silentTypes.delete(type);
      }
    }
  }

  // ==================== 错误处理包装器 ====================

  /**
   * 包装异步函数，添加错误处理
   * @template T
   * @param {function(): Promise<T>} fn - 异步函数
   * @param {Object} [options={}] - 选项
   * @param {function(Object): T} [options.onError] - 错误处理回调
   * @param {T} [options.fallback=null] - 失败时的返回值
   * @param {number} [options.retries=0] - 重试次数
   * @param {number} [options.retryDelay=1000] - 重试延迟
   * @param {number} [options.timeout=0] - 超时时间
   * @returns {Promise<T>} 包装后的函数
   * @example
   * const result = await withErrorHandling(
   *   () => fetchData(),
   *   { retries: 3, fallback: [] }
   * );
   */
  async function withErrorHandling(fn, options = {}) {
    const {
      onError,
      fallback = null,
      retries = 0,
      retryDelay = 1000,
      timeout = 0
    } = options;

    const execute = async () => {
      // 添加超时支持
      if (timeout > 0) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
          return await fn();
        } finally {
          clearTimeout(timeoutId);
        }
      }

      return await fn();
    };

    let lastError = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        return await execute();
      } catch (error) {
        lastError = error;

        // 如果是取消错误，不重试
        if (error.name === 'AbortError') {
          const timeoutError = new TimeoutError(
            `Operation timed out after ${timeout}ms`,
            timeout
          );
          const errorInfo = errorHandler.handleError(timeoutError);
          return onError ? onError(errorInfo) : fallback;
        }

        // 如果还有重试机会
        if (attempt < retries) {
          console.warn(
            `Retry ${attempt + 1}/${retries} after error:`,
            error.message
          );
          await new Promise((resolve) => setTimeout(resolve, retryDelay));
          continue;
        }

        // 处理最终错误
        const errorInfo = errorHandler.handleError(error, ErrorTypes.API);

        if (onError) {
          return onError(errorInfo);
        }

        return fallback;
      }
    }

    return fallback;
  }

  /**
   * 创建安全的异步函数
   * @template T
   * @param {function(): Promise<T>} fn - 异步函数
   * @param {T} [fallback=null] - 失败时的返回值
   * @returns {function(): Promise<T>} 安全的异步函数
   * @example
   * const safeFetch = createSafeAsync(fetchData, []);
   * const data = await safeFetch(); // 不会抛出错误
   */
  function createSafeAsync(fn, fallback = null) {
    return () => withErrorHandling(fn, { fallback });
  }

  // ==================== 创建全局实例 ====================
  const errorHandler = new ErrorHandler();

  // ==================== 导出 ====================
  window.ErrorHandler = errorHandler;
  window.ErrorTypes = ErrorTypes;
  window.ErrorSeverity = ErrorSeverity;
  window.AppError = AppError;
  window.NetworkError = NetworkError;
  window.APIError = APIError;
  window.ValidationError = ValidationError;
  window.TimeoutError = TimeoutError;
  window.withErrorHandling = withErrorHandling;
  window.createSafeAsync = createSafeAsync;
})();
