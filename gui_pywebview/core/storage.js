/**
 * Storage - 前端存储管理模块
 * 提供统一的本地存储管理，支持命名空间、过期时间、加密等
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    prefix: 'mechforge_',
    defaultExpiry: 24 * 60 * 60 * 1000 // 默认过期时间：24小时
  };

  // ==================== 存储键定义 ====================
  const Keys = {
    THEME: 'theme',
    CHAT_DRAFT: 'chat_draft',
    CHAT_HISTORY: 'chat_history',
    USER_CONFIG: 'user_config',
    LAST_MODEL: 'last_model',
    SIDEBAR_STATE: 'sidebar_state'
  };

  // ==================== 工具函数 ====================

  /**
   * 生成带前缀的键
   * @param {string} key
   * @returns {string}
   */
  function prefixKey(key) {
    return config.prefix + key;
  }

  /**
   * 检查是否过期
   * @param {Object} item
   * @returns {boolean}
   */
  function isExpired(item) {
    if (!item.expiry) return false;
    return Date.now() > item.expiry;
  }

  // ==================== 存储操作 ====================

  /**
   * 设置存储项
   * @param {string} key - 键
   * @param {*} value - 值
   * @param {Object} options - 选项
   * @param {number} options.expiry - 过期时间（毫秒）
   */
  function set(key, value, options = {}) {
    const item = {
      value,
      timestamp: Date.now(),
      expiry: options.expiry ? Date.now() + options.expiry : null
    };

    try {
      localStorage.setItem(prefixKey(key), JSON.stringify(item));
      return true;
    } catch (e) {
      console.error('[Storage] Set failed:', e);
      return false;
    }
  }

  /**
   * 获取存储项
   * @param {string} key - 键
   * @param {*} defaultValue - 默认值
   * @returns {*}
   */
  function get(key, defaultValue = null) {
    try {
      const raw = localStorage.getItem(prefixKey(key));
      if (!raw) return defaultValue;

      const item = JSON.parse(raw);

      // 检查过期
      if (isExpired(item)) {
        remove(key);
        return defaultValue;
      }

      return item.value;
    } catch (e) {
      console.error('[Storage] Get failed:', e);
      return defaultValue;
    }
  }

  /**
   * 移除存储项
   * @param {string} key - 键
   */
  function remove(key) {
    try {
      localStorage.removeItem(prefixKey(key));
      return true;
    } catch (e) {
      console.error('[Storage] Remove failed:', e);
      return false;
    }
  }

  /**
   * 检查存储项是否存在
   * @param {string} key - 键
   * @returns {boolean}
   */
  function has(key) {
    const raw = localStorage.getItem(prefixKey(key));
    if (!raw) return false;

    try {
      const item = JSON.parse(raw);
      if (isExpired(item)) {
        remove(key);
        return false;
      }
      return true;
    } catch (e) {
      return false;
    }
  }

  /**
   * 清空所有应用存储
   */
  function clear() {
    try {
      const keysToRemove = [];
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(config.prefix)) {
          keysToRemove.push(key);
        }
      }
      keysToRemove.forEach(key => localStorage.removeItem(key));
      return true;
    } catch (e) {
      console.error('[Storage] Clear failed:', e);
      return false;
    }
  }

  /**
   * 获取所有键
   * @returns {string[]}
   */
  function keys() {
    const result = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(config.prefix)) {
        result.push(key.slice(config.prefix.length));
      }
    }
    return result;
  }

  /**
   * 获取存储大小（字节）
   * @returns {number}
   */
  function size() {
    let total = 0;
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(config.prefix)) {
        const value = localStorage.getItem(key);
        if (value) {
          total += key.length + value.length;
        }
      }
    }
    return total * 2; // UTF-16 编码
  }

  // ==================== 便捷方法 ====================

  /**
   * 获取主题
   * @returns {string}
   */
  function getTheme() {
    return get(Keys.THEME, 'dark');
  }

  /**
   * 设置主题
   * @param {string} theme
   */
  function setTheme(theme) {
    return set(Keys.THEME, theme);
  }

  /**
   * 获取聊天草稿
   * @returns {string}
   */
  function getChatDraft() {
    return get(Keys.CHAT_DRAFT, '');
  }

  /**
   * 设置聊天草稿
   * @param {string} draft
   */
  function setChatDraft(draft) {
    return set(Keys.CHAT_DRAFT, draft);
  }

  /**
   * 清除聊天草稿
   */
  function clearChatDraft() {
    return remove(Keys.CHAT_DRAFT);
  }

  /**
   * 获取用户配置
   * @returns {Object}
   */
  function getUserConfig() {
    return get(Keys.USER_CONFIG, {});
  }

  /**
   * 设置用户配置
   * @param {Object} config
   */
  function setUserConfig(config) {
    return set(Keys.USER_CONFIG, config);
  }

  /**
   * 更新用户配置（合并）
   * @param {Object} updates
   */
  function updateUserConfig(updates) {
    const current = getUserConfig();
    return setUserConfig({ ...current, ...updates });
  }

  // ==================== 导出 ====================
  window.Storage = {
    // 基础操作
    set,
    get,
    remove,
    has,
    clear,
    keys,
    size,

    // 便捷方法
    getTheme,
    setTheme,
    getChatDraft,
    setChatDraft,
    clearChatDraft,
    getUserConfig,
    setUserConfig,
    updateUserConfig,

    // 键常量
    Keys
  };

})();