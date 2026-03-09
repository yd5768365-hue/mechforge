/**
 * WindowControl - 窗口控制模块
 * 处理标题栏拖拽、最小化、最大化、关闭等操作
 */

(function () {
  'use strict';

  const { $$ } = Utils;

  // ==================== 初始化 ====================

  /**
   * 初始化窗口控制
   */
  function init() {
    const windowBtns = $$('.window-btn');
    windowBtns.forEach(btn => {
      btn.addEventListener('click', () => handleWindowAction(btn.dataset.action));
    });
  }

  /**
   * 处理窗口操作
   * @param {string} action - 操作类型: minimize, maximize, close
   */
  async function handleWindowAction(action) {
    try {
      // PyWebView 通过 js_api 暴露的 API
      const api = window.pywebview?.api;
      if (api) {
        switch (action) {
          case 'minimize':
            await api.minimize();
            break;
          case 'maximize':
            await api.maximize();
            break;
          case 'close':
            await api.close();
            break;
          default:
            console.warn('Unknown window action:', action);
        }
      } else {
        // 开发模式下仅打印日志
        console.log(`[dev] window action: ${action}`);
      }
    } catch (error) {
      console.error('Window action failed:', error);
    }
  }

  // ==================== 导出 ====================
  window.WindowControl = {
    init,
    handleWindowAction
  };

})();