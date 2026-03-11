/**
 * Components Index - 组件库入口
 * 统一导出所有组件
 */

(function () {
  'use strict';

  // 组件列表
  const components = [
    'button',
    'input',
    'card'
  ];

  // 等待所有组件加载完成
  function waitForComponents(callback, timeout = 5000) {
    const startTime = Date.now();

    function check() {
      const allLoaded = components.every(name => {
        const componentName = `${name.charAt(0).toUpperCase() + name.slice(1)}Component`;
        return window[componentName] !== undefined;
      });

      if (allLoaded) {
        callback();
      } else if (Date.now() - startTime > timeout) {
        console.warn('[Components] Timeout waiting for components');
        callback();
      } else {
        setTimeout(check, 50);
      }
    }

    check();
  }

  // 初始化组件库
  function init() {
    console.log('[Components] Component library initialized');

    // 触发组件库就绪事件
    window.dispatchEvent(new CustomEvent('components-ready', {
      detail: { components }
    }));
  }

  // 等待组件加载
  waitForComponents(init);

  // ==================== 导出 ====================
  window.Components = {
    list: components,
    waitForComponents,
    init
  };

})();
