/**
 * WindowControl - 窗口控制模块
 * 处理标题栏拖拽、最小化、最大化、关闭等操作
 */

(function () {
  'use strict';

  const { $$ } = Utils;

  // ==================== 状态 ====================
  let initialized = false;
  let pywebviewReady = false;

  // ==================== 初始化 ====================

  /**
   * 初始化窗口控制
   */
  function init() {
    if (initialized) {
      console.log('[WindowControl] Already initialized');
      return;
    }
    initialized = true;

    console.log('[WindowControl] Initializing...');

    // 立即绑定事件（不依赖 pywebview）
    bindEvents();

    // 等待 pywebview 就绪
    waitForPyWebView(() => {
      pywebviewReady = true;
      console.log('[WindowControl] PyWebView API ready');
    });
  }

  /**
   * 绑定事件
   */
  function bindEvents() {
    const windowBtns = $$('.window-btn');
    console.log(`[WindowControl] Found ${windowBtns.length} window buttons`);

    windowBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const action = btn.dataset.action;
        console.log(`[WindowControl] Button clicked: ${action}`);
        handleWindowAction(action);
      });
    });
  }

  /**
   * 等待 pywebview 就绪
   * @param {Function} callback - 就绪后的回调
   */
  function waitForPyWebView(callback, maxAttempts = 50) {
    let attempts = 0;

    const check = () => {
      attempts++;
      if (window.pywebview?.api) {
        callback();
      } else if (attempts < maxAttempts) {
        setTimeout(check, 100);
      } else {
        console.warn('[WindowControl] PyWebView API not available after timeout');
      }
    };

    check();
  }

  /**
   * 处理窗口操作
   * @param {string} action - 操作类型: minimize, maximize, close
   */
  async function handleWindowAction(action) {
    console.log(`[WindowControl] Handling action: ${action}, pywebviewReady: ${pywebviewReady}`);

    try {
      // PyWebView 通过 js_api 暴露的 API
      const api = window.pywebview?.api;
      if (api) {
        switch (action) {
          case 'minimize':
            await api.minimize();
            console.log('[WindowControl] Window minimized');
            break;
          case 'maximize':
            await api.maximize();
            console.log('[WindowControl] Window maximized');
            break;
          case 'close':
            await api.close();
            console.log('[WindowControl] Window closed');
            break;
          default:
            console.warn('[WindowControl] Unknown window action:', action);
        }
      } else {
        // 开发模式下仅打印日志
        console.log(`[WindowControl] [dev] window action: ${action}`);
        showToast(`[Dev] ${action} clicked`);
      }
    } catch (error) {
      console.error('[WindowControl] Window action failed:', error);
      showToast(`Action failed: ${error.message}`, 'error');
    }
  }

  /**
   * 显示提示
   */
  function showToast(message, type = 'info') {
    if (window.ChatFeatures?.showToast) {
      ChatFeatures.showToast(message, type);
    } else {
      console.log(`[Toast] ${type}: ${message}`);
    }
  }

  // ==================== 导出 ====================
  window.WindowControl = {
    init,
    handleWindowAction
  };

})();