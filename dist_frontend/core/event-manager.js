/**
 * EventManager - 事件管理器
 * 优化版本：事件委托、自动清理、内存管理
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    autoCleanupInterval: 30000, // 自动清理间隔
    maxListenersPerType: 100, // 每类事件最大监听器数
    warnThreshold: 50 // 警告阈值
  };

  // ==================== 状态 ====================
  const listeners = new Map(); // 事件监听器
  const delegatedListeners = new Map(); // 委托监听器
  const observerRegistry = new WeakMap(); // DOM观察器注册表
  let cleanupInterval = null;

  // ==================== 核心功能 ====================

  /**
   * 添加事件监听器
   * @param {HTMLElement} element - 目标元素
   * @param {string} event - 事件类型
   * @param {Function} handler - 处理函数
   * @param {Object} options - 选项
   */
  function on(element, event, handler, options = {}) {
    if (!element || !event || !handler) return;

    const { once = false, passive = true, capture = false } = options;
    
    const wrappedHandler = once 
      ? (e) => {
          handler(e);
          off(element, event, wrappedHandler);
        }
      : handler;

    element.addEventListener(event, wrappedHandler, { passive, capture });

    // 记录监听器
    if (!listeners.has(element)) {
      listeners.set(element, new Map());
    }
    const elementListeners = listeners.get(element);
    if (!elementListeners.has(event)) {
      elementListeners.set(event, new Set());
    }
    elementListeners.get(event).add(wrappedHandler);

    // 检查监听器数量
    checkListenerCount(event);
  }

  /**
   * 移除事件监听器
   * @param {HTMLElement} element - 目标元素
   * @param {string} event - 事件类型
   * @param {Function} handler - 处理函数
   */
  function off(element, event, handler) {
    if (!element || !event) return;

    element.removeEventListener(event, handler);

    // 从记录中移除
    const elementListeners = listeners.get(element);
    if (elementListeners) {
      const eventListeners = elementListeners.get(event);
      if (eventListeners) {
        eventListeners.delete(handler);
        if (eventListeners.size === 0) {
          elementListeners.delete(event);
        }
      }
      if (elementListeners.size === 0) {
        listeners.delete(element);
      }
    }
  }

  /**
   * 一次性事件监听
   * @param {HTMLElement} element - 目标元素
   * @param {string} event - 事件类型
   * @param {Function} handler - 处理函数
   * @param {Object} options - 选项
   */
  function once(element, event, handler, options = {}) {
    on(element, event, handler, { ...options, once: true });
  }

  /**
   * 事件委托
   * @param {HTMLElement} container - 容器元素
   * @param {string} selector - CSS选择器
   * @param {string} event - 事件类型
   * @param {Function} handler - 处理函数
   */
  function delegate(container, selector, event, handler) {
    if (!container || !selector || !event || !handler) return;

    const delegatedHandler = (e) => {
      const target = e.target.closest(selector);
      if (target && container.contains(target)) {
        handler.call(target, e, target);
      }
    };

    on(container, event, delegatedHandler);

    // 记录委托监听器
    if (!delegatedListeners.has(container)) {
      delegatedListeners.set(container, new Map());
    }
    const containerDelegates = delegatedListeners.get(container);
    if (!containerDelegates.has(event)) {
      containerDelegates.set(event, new Map());
    }
    containerDelegates.get(event).set(selector, delegatedHandler);
  }

  /**
   * 移除委托监听器
   * @param {HTMLElement} container - 容器元素
   * @param {string} selector - CSS选择器
   * @param {string} event - 事件类型
   */
  function undelegate(container, selector, event) {
    const containerDelegates = delegatedListeners.get(container);
    if (!containerDelegates) return;

    const eventDelegates = containerDelegates.get(event);
    if (!eventDelegates) return;

    const handler = eventDelegates.get(selector);
    if (handler) {
      off(container, event, handler);
      eventDelegates.delete(selector);
    }
  }

  /**
   * 触发自定义事件
   * @param {HTMLElement} element - 目标元素
   * @param {string} eventName - 事件名称
   * @param {*} detail - 事件数据
   */
  function emit(element, eventName, detail = null) {
    const event = new CustomEvent(eventName, {
      detail,
      bubbles: true,
      cancelable: true
    });
    element.dispatchEvent(event);
  }

  /**
   * 检查监听器数量
   * @param {string} event - 事件类型
   */
  function checkListenerCount(event) {
    let count = 0;
    listeners.forEach(elementListeners => {
      const eventListeners = elementListeners.get(event);
      if (eventListeners) {
        count += eventListeners.size;
      }
    });

    if (count > config.maxListenersPerType) {
      console.warn(`[EventManager] Too many listeners for "${event}": ${count}`);
    } else if (count > config.warnThreshold) {
      console.log(`[EventManager] High listener count for "${event}": ${count}`);
    }
  }

  /**
   * 清理已移除元素的监听器
   */
  function cleanup() {
    const toRemove = [];
    
    listeners.forEach((elementListeners, element) => {
      if (!document.contains(element)) {
        // 元素已从DOM移除，清理其监听器
        elementListeners.forEach((handlers, event) => {
          handlers.forEach(handler => {
            element.removeEventListener(event, handler);
          });
        });
        toRemove.push(element);
      }
    });

    toRemove.forEach(element => listeners.delete(element));

    if (toRemove.length > 0) {
      console.log(`[EventManager] Cleaned up ${toRemove.length} orphaned listeners`);
    }
  }

  /**
   * 观察元素移除
   * @param {HTMLElement} element - 要观察的元素
   * @param {Function} callback - 移除时的回调
   */
  function observeRemoval(element, callback) {
    if (!element || !element.parentNode) return;

    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.removedNodes.forEach((node) => {
          if (node === element || (node.contains && node.contains(element))) {
            callback();
            observer.disconnect();
            observerRegistry.delete(element);
          }
        });
      });
    });

    observer.observe(element.parentNode, { childList: true, subtree: true });
    observerRegistry.set(element, observer);
  }

  /**
   * 自动清理设置
   */
  function startAutoCleanup() {
    if (cleanupInterval) return;
    cleanupInterval = setInterval(cleanup, config.autoCleanupInterval);
  }

  /**
   * 停止自动清理
   */
  function stopAutoCleanup() {
    if (cleanupInterval) {
      clearInterval(cleanupInterval);
      cleanupInterval = null;
    }
  }

  /**
   * 获取统计信息
   */
  function getStats() {
    let totalListeners = 0;
    const eventCounts = {};

    listeners.forEach(elementListeners => {
      elementListeners.forEach((handlers, event) => {
        totalListeners += handlers.size;
        eventCounts[event] = (eventCounts[event] || 0) + handlers.size;
      });
    });

    return {
      totalListeners,
      eventCounts,
      trackedElements: listeners.size
    };
  }

  /**
   * 销毁所有监听器
   */
  function destroy() {
    stopAutoCleanup();
    
    listeners.forEach((elementListeners, element) => {
      elementListeners.forEach((handlers, event) => {
        handlers.forEach(handler => {
          element.removeEventListener(event, handler);
        });
      });
    });
    
    listeners.clear();
    delegatedListeners.clear();
    
    // 断开所有观察器
    observerRegistry.forEach(observer => observer.disconnect());
  }

  // ==================== 初始化 ====================
  startAutoCleanup();

  // ==================== 导出 ====================
  window.EventManager = {
    on,
    off,
    once,
    delegate,
    undelegate,
    emit,
    cleanup,
    observeRemoval,
    startAutoCleanup,
    stopAutoCleanup,
    getStats,
    destroy
  };

})();
