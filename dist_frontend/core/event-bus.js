/**
 * EventBus - 事件总线模块
 * 提供模块间通信能力，实现松耦合
 */

// 事件类型常量
const Events = {
  // AI 相关
  AI_MESSAGE_SENT: 'ai:message-sent',
  AI_RESPONSE_RECEIVED: 'ai:response-received',
  AI_STREAMING: 'ai:streaming',
  AI_ERROR: 'ai:error',

  // RAG 相关
  RAG_ENABLED: 'rag:enabled',
  RAG_DISABLED: 'rag:disabled',
  RAG_RESULT: 'rag:result',
  RAG_ERROR: 'rag:error',

  // 模式切换相关
  MODE_SWITCHED_TO_KNOWLEDGE: 'mode:switched-to-knowledge',
  MODE_SWITCHED_TO_CHAT: 'mode:switched-to-chat',
  MODE_RESET: 'mode:reset',
  MODE_SWITCH_ERROR: 'mode:switch-error',

  // 配置相关
  CONFIG_UPDATED: 'config:updated',
  CONFIG_LOADED: 'config:loaded',

  // UI 相关
  UI_TAB_CHANGED: 'ui:tab-changed',
  UI_LOADING: 'ui:loading',
  UI_READY: 'ui:ready'
};

class EventBus {
  constructor() {
    this.listeners = new Map();
    this.initializeListeners();
  }

  initializeListeners() {
    // 初始化所有事件类型的监听器数组
    Object.values(Events).forEach(eventType => {
      this.listeners.set(eventType, []);
    });
  }

  /**
   * 订阅事件
   * @param {string} eventType - 事件类型
   * @param {Function} callback - 回调函数
   * @returns {Function} 取消订阅的函数
   */
  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }

    const listeners = this.listeners.get(eventType);
    listeners.push(callback);

    // 返回取消订阅的函数
    return () => {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    };
  }

  /**
   * 取消订阅
   * @param {string} eventType - 事件类型
   * @param {Function} callback - 回调函数
   */
  off(eventType, callback) {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      const index = listeners.indexOf(callback);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * 发布事件
   * @param {string} eventType - 事件类型
   * @param {*} data - 事件数据
   */
  emit(eventType, data) {
    const listeners = this.listeners.get(eventType);
    if (listeners) {
      listeners.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event handler for ${eventType}:`, error);
        }
      });
    }
  }

  /**
   * 只触发一次
   * @param {string} eventType - 事件类型
   * @param {Function} callback - 回调函数
   */
  once(eventType, callback) {
    const wrapper = (data) => {
      callback(data);
      this.off(eventType, wrapper);
    };
    this.on(eventType, wrapper);
  }

  /**
   * 清空所有监听器
   */
  clear() {
    this.listeners.forEach(listeners => {
      listeners.length = 0;
    });
  }

  /**
   * 获取事件监听器数量
   * @param {string} eventType - 事件类型
   * @returns {number}
   */
  listenerCount(eventType) {
    const listeners = this.listeners.get(eventType);
    return listeners ? listeners.length : 0;
  }
}

// 创建全局事件总线实例
const eventBus = new EventBus();

// 导出
window.EventBus = EventBus;
window.Events = Events;
window.eventBus = eventBus;
