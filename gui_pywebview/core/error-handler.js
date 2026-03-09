/**
 * MechForge AI - 全局错误处理模块
 * 提供统一的错误捕获、日志记录和用户提示
 */

(function () {
  'use strict';

  // ==================== 错误类型 ====================
  const ErrorTypes = {
    NETWORK: 'NETWORK_ERROR',
    API: 'API_ERROR',
    VALIDATION: 'VALIDATION_ERROR',
    RUNTIME: 'RUNTIME_ERROR',
    UNKNOWN: 'UNKNOWN_ERROR'
  };

  // ==================== 错误处理器 ====================
  class ErrorHandler {
    constructor() {
      this.listeners = new Map();
      this.setupGlobalHandlers();
    }

    /**
     * 设置全局错误处理器
     */
    setupGlobalHandlers() {
      // 捕获未处理的 Promise 拒绝
      window.addEventListener('unhandledrejection', (event) => {
        console.error('[Unhandled Rejection]', event.reason);
        this.handleError(event.reason, ErrorTypes.RUNTIME);
        event.preventDefault();
      });

      // 捕获全局错误
      window.addEventListener('error', (event) => {
        console.error('[Global Error]', event.error);
        this.handleError(event.error, ErrorTypes.RUNTIME);
        event.preventDefault();
      });
    }

    /**
     * 处理错误
     * @param {Error|string} error - 错误对象或消息
     * @param {string} type - 错误类型
     * @param {Object} context - 上下文信息
     */
    handleError(error, type = ErrorTypes.UNKNOWN, context = {}) {
      const errorInfo = this.normalizeError(error, type, context);

      // 记录日志
      this.logError(errorInfo);

      // 触发监听器
      this.notifyListeners(errorInfo);

      // 显示用户提示
      this.showUserMessage(errorInfo);

      return errorInfo;
    }

    /**
     * 标准化错误信息
     */
    normalizeError(error, type, context) {
      if (error instanceof Error) {
        return {
          type,
          message: error.message,
          stack: error.stack,
          name: error.name,
          ...context,
          timestamp: new Date().toISOString()
        };
      }

      if (typeof error === 'object' && error !== null) {
        return {
          type,
          message: error.message || error.detail || JSON.stringify(error),
          ...context,
          timestamp: new Date().toISOString()
        };
      }

      return {
        type,
        message: String(error),
        ...context,
        timestamp: new Date().toISOString()
      };
    }

    /**
     * 记录错误日志
     */
    logError(errorInfo) {
      const prefix = `[${errorInfo.type}]`;
      console.error(prefix, errorInfo.message, errorInfo);
    }

    /**
     * 显示用户提示
     */
    showUserMessage(errorInfo) {
      // 根据错误类型决定是否显示
      const silentTypes = [ErrorTypes.VALIDATION];
      if (silentTypes.includes(errorInfo.type)) {
        return;
      }

      // 尝试使用 ChatUI 显示
      if (window.ChatUI && typeof ChatUI.addSystemMessage === 'function') {
        ChatUI.addSystemMessage(`⚠️ ${errorInfo.message}`);
        return;
      }

      // 降级到 alert
      console.warn('Error:', errorInfo.message);
    }

    /**
     * 订阅错误事件
     */
    onError(type, callback) {
      if (!this.listeners.has(type)) {
        this.listeners.set(type, []);
      }
      this.listeners.get(type).push(callback);
    }

    /**
     * 通知监听器
     */
    notifyListeners(errorInfo) {
      // 通知特定类型的监听器
      const typeListeners = this.listeners.get(errorInfo.type) || [];
      typeListeners.forEach(cb => {
        try {
          cb(errorInfo);
        } catch (e) {
          console.error('Error in error listener:', e);
        }
      });

      // 通知全局监听器
      const globalListeners = this.listeners.get('*') || [];
      globalListeners.forEach(cb => {
        try {
          cb(errorInfo);
        } catch (e) {
          console.error('Error in error listener:', e);
        }
      });
    }
  }

  // ==================== API 错误处理 ====================

  /**
   * 包装 API 调用，添加错误处理
   * @param {Function} fn - 异步函数
   * @param {Object} options - 选项
   */
  async function withErrorHandling(fn, options = {}) {
    const { 
      onError, 
      fallback = null, 
      retries = 0, 
      retryDelay = 1000 
    } = options;

    let lastError = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;

        // 如果还有重试机会
        if (attempt < retries) {
          console.warn(`Retry ${attempt + 1}/${retries} after error:`, error.message);
          await new Promise(resolve => setTimeout(resolve, retryDelay));
          continue;
        }

        // 处理错误
        const errorInfo = window.ErrorHandler?.handleError(error, ErrorTypes.API) || {
          message: error.message
        };

        if (onError) {
          return onError(errorInfo);
        }

        return fallback;
      }
    }

    return fallback;
  }

  // ==================== 创建全局实例 ====================
  const errorHandler = new ErrorHandler();

  // ==================== 导出 ====================
  window.ErrorHandler = errorHandler;
  window.ErrorTypes = ErrorTypes;
  window.withErrorHandling = withErrorHandling;

})();