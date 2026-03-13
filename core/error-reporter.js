/**
 * ErrorReporter - 错误报告器
 * 捕获和报告应用错误
 */

(function () {
  'use strict';

  // 配置
  const config = {
    enabled: true,
    endpoint: '/api/errors',
    maxErrors: 100,
    sampleRate: 1.0,
    ignorePatterns: [
      /^Script error\.?$/,
      /^ResizeObserver loop limit exceeded/,
      /^Network error$/
    ],
    ignoreUrls: [
      /extensions\//i,
      /^chrome:\/\//i
    ]
  };

  // 错误队列
  const errorQueue = [];
  let isReporting = false;

  /**
   * 初始化错误报告
   */
  function init(options = {}) {
    Object.assign(config, options);

    if (!config.enabled) return;

    // 全局错误捕获
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleRejection);

    // 重写 console.error
    const originalError = console.error;
    console.error = function(...args) {
      originalError.apply(console, args);
      reportConsoleError(args);
    };

    console.log('[ErrorReporter] Initialized');
  }

  /**
   * 处理错误
   */
  function handleError(event) {
    const { message, filename, lineno, colno, error } = event;

    // 检查是否应该忽略
    if (shouldIgnore(message, filename)) return;

    const errorInfo = {
      type: 'javascript',
      message,
      filename,
      lineno,
      colno,
      stack: error?.stack || '',
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    report(errorInfo);
  }

  /**
   * 处理 Promise 拒绝
   */
  function handleRejection(event) {
    const error = event.reason;

    const errorInfo = {
      type: 'promise',
      message: error?.message || String(error),
      stack: error?.stack || '',
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    report(errorInfo);
  }

  /**
   * 报告 console.error
   */
  function reportConsoleError(args) {
    const message = args.map(arg =>
      typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
    ).join(' ');

    if (shouldIgnore(message)) return;

    report({
      type: 'console',
      message,
      timestamp: Date.now(),
      url: window.location.href
    });
  }

  /**
   * 手动报告错误
   */
  function reportError(error, context = {}) {
    if (!config.enabled) return;

    const errorInfo = {
      type: 'manual',
      message: error.message || String(error),
      stack: error.stack || '',
      context,
      timestamp: Date.now(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };

    report(errorInfo);
  }

  /**
   * 报告信息
   */
  function report(info) {
    // 采样
    if (Math.random() > config.sampleRate) return;

    // 添加到队列
    errorQueue.push(info);

    // 限制队列大小
    if (errorQueue.length > config.maxErrors) {
      errorQueue.shift();
    }

    // 批量发送
    if (!isReporting) {
      setTimeout(flush, 1000);
    }
  }

  /**
   * 发送错误报告
   */
  async function flush() {
    if (errorQueue.length === 0 || isReporting) return;

    isReporting = true;
    const errors = errorQueue.splice(0, errorQueue.length);

    try {
      // 发送到服务器
      if (navigator.sendBeacon) {
        navigator.sendBeacon(config.endpoint, JSON.stringify({ errors }));
      } else {
        await fetch(config.endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ errors }),
          keepalive: true
        });
      }
    } catch (e) {
      console.error('[ErrorReporter] Failed to send:', e);
      // 重新添加到队列
      errorQueue.unshift(...errors);
    } finally {
      isReporting = false;

      // 继续发送剩余错误
      if (errorQueue.length > 0) {
        setTimeout(flush, 5000);
      }
    }
  }

  /**
   * 检查是否应该忽略
   */
  function shouldIgnore(message, filename) {
    // 检查消息模式
    for (const pattern of config.ignorePatterns) {
      if (pattern.test(message)) return true;
    }

    // 检查 URL
    if (filename) {
      for (const pattern of config.ignoreUrls) {
        if (pattern.test(filename)) return true;
      }
    }

    return false;
  }

  /**
   * 获取错误统计
   */
  function getStats() {
    return {
      queueLength: errorQueue.length,
      isReporting
    };
  }

  /**
   * 设置配置
   */
  function setConfig(options) {
    Object.assign(config, options);
  }

  // ==================== 导出 ====================
  window.ErrorReporter = {
    init,
    reportError,
    flush,
    getStats,
    setConfig,
    config
  };

})();
