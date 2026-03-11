/**
 * CacheManager - 缓存管理器
 * 提供多级缓存策略：内存缓存 + localStorage
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    memoryCacheLimit: 50, // 内存缓存最大条目数
    localStoragePrefix: 'mf_', // localStorage 键前缀
    defaultTTL: 5 * 60 * 1000, // 默认缓存时间 5分钟
    cleanupInterval: 60 * 1000 // 清理间隔 1分钟
  };

  // ==================== 内存缓存 ====================
  const memoryCache = new Map();
  let cleanupTimer = null;

  // ==================== 核心功能 ====================

  /**
   * 生成缓存键
   * @param {string} key - 原始键
   * @returns {string} 带前缀的键
   */
  function getKey(key) {
    return `${config.localStoragePrefix}${key}`;
  }

  /**
   * 设置缓存
   * @param {string} key - 缓存键
   * @param {*} value - 缓存值
   * @param {number} ttl - 过期时间(ms)
   * @param {string} level - 缓存级别 ('memory' | 'persistent' | 'both')
   */
  function set(key, value, ttl = config.defaultTTL, level = 'both') {
    const item = {
      value,
      expiry: Date.now() + ttl,
      created: Date.now()
    };

    // 内存缓存
    if (level === 'memory' || level === 'both') {
      // LRU: 如果超过限制，删除最旧的条目
      if (memoryCache.size >= config.memoryCacheLimit) {
        const firstKey = memoryCache.keys().next().value;
        memoryCache.delete(firstKey);
      }
      memoryCache.set(key, item);
    }

    // 持久化缓存
    if (level === 'persistent' || level === 'both') {
      try {
        localStorage.setItem(getKey(key), JSON.stringify(item));
      } catch (e) {
        console.warn('[CacheManager] localStorage set failed:', e);
      }
    }
  }

  /**
   * 获取缓存
   * @param {string} key - 缓存键
   * @param {*} defaultValue - 默认值
   * @returns {*} 缓存值或默认值
   */
  function get(key, defaultValue = null) {
    // 先检查内存缓存
    if (memoryCache.has(key)) {
      const item = memoryCache.get(key);
      if (item.expiry > Date.now()) {
        // 更新访问顺序（LRU）
        memoryCache.delete(key);
        memoryCache.set(key, item);
        return item.value;
      }
      // 已过期
      memoryCache.delete(key);
    }

    // 检查持久化缓存
    try {
      const stored = localStorage.getItem(getKey(key));
      if (stored) {
        const item = JSON.parse(stored);
        if (item.expiry > Date.now()) {
          // 恢复到内存缓存
          memoryCache.set(key, item);
          return item.value;
        }
        // 已过期，删除
        localStorage.removeItem(getKey(key));
      }
    } catch (e) {
      console.warn('[CacheManager] localStorage get failed:', e);
    }

    return defaultValue;
  }

  /**
   * 检查缓存是否存在且有效
   * @param {string} key - 缓存键
   * @returns {boolean}
   */
  function has(key) {
    // 检查内存缓存
    if (memoryCache.has(key)) {
      const item = memoryCache.get(key);
      if (item.expiry > Date.now()) {
        return true;
      }
      memoryCache.delete(key);
    }

    // 检查持久化缓存
    try {
      const stored = localStorage.getItem(getKey(key));
      if (stored) {
        const item = JSON.parse(stored);
        if (item.expiry > Date.now()) {
          return true;
        }
        localStorage.removeItem(getKey(key));
      }
    } catch (e) {
      return false;
    }

    return false;
  }

  /**
   * 删除缓存
   * @param {string} key - 缓存键
   */
  function remove(key) {
    memoryCache.delete(key);
    try {
      localStorage.removeItem(getKey(key));
    } catch (e) {
      console.warn('[CacheManager] localStorage remove failed:', e);
    }
  }

  /**
   * 清空所有缓存
   * @param {string} pattern - 可选的键匹配模式
   */
  function clear(pattern = null) {
    // 清空内存缓存
    if (pattern) {
      const regex = new RegExp(pattern);
      for (const key of memoryCache.keys()) {
        if (regex.test(key)) {
          memoryCache.delete(key);
        }
      }
    } else {
      memoryCache.clear();
    }

    // 清空持久化缓存
    try {
      if (pattern) {
        const regex = new RegExp(pattern);
        for (let i = localStorage.length - 1; i >= 0; i--) {
          const key = localStorage.key(i);
          if (key && key.startsWith(config.localStoragePrefix)) {
            const originalKey = key.slice(config.localStoragePrefix.length);
            if (regex.test(originalKey)) {
              localStorage.removeItem(key);
            }
          }
        }
      } else {
        // 只清除带前缀的键
        for (let i = localStorage.length - 1; i >= 0; i--) {
          const key = localStorage.key(i);
          if (key && key.startsWith(config.localStoragePrefix)) {
            localStorage.removeItem(key);
          }
        }
      }
    } catch (e) {
      console.warn('[CacheManager] localStorage clear failed:', e);
    }
  }

  /**
   * 获取或设置缓存
   * @param {string} key - 缓存键
   * @param {Function} factory - 工厂函数，用于生成缓存值
   * @param {number} ttl - 过期时间
   * @returns {Promise<*>} 缓存值
   */
  async function remember(key, factory, ttl = config.defaultTTL) {
    if (has(key)) {
      return get(key);
    }

    const value = await factory();
    set(key, value, ttl);
    return value;
  }

  /**
   * 清理过期缓存
   */
  function cleanup() {
    const now = Date.now();

    // 清理内存缓存
    for (const [key, item] of memoryCache.entries()) {
      if (item.expiry <= now) {
        memoryCache.delete(key);
      }
    }

    // 清理持久化缓存
    try {
      for (let i = localStorage.length - 1; i >= 0; i--) {
        const key = localStorage.key(i);
        if (key && key.startsWith(config.localStoragePrefix)) {
          try {
            const item = JSON.parse(localStorage.getItem(key));
            if (item.expiry <= now) {
              localStorage.removeItem(key);
            }
          } catch (e) {
            // 无效的缓存项，删除
            localStorage.removeItem(key);
          }
        }
      }
    } catch (e) {
      console.warn('[CacheManager] cleanup failed:', e);
    }
  }

  /**
   * 启动自动清理
   */
  function startAutoCleanup() {
    if (cleanupTimer) return;
    cleanupTimer = setInterval(cleanup, config.cleanupInterval);
  }

  /**
   * 停止自动清理
   */
  function stopAutoCleanup() {
    if (cleanupTimer) {
      clearInterval(cleanupTimer);
      cleanupTimer = null;
    }
  }

  /**
   * 获取缓存统计
   */
  function getStats() {
    let persistentCount = 0;
    try {
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(config.localStoragePrefix)) {
          persistentCount++;
        }
      }
    } catch (e) {
      // ignore
    }

    return {
      memory: memoryCache.size,
      persistent: persistentCount,
      total: memoryCache.size + persistentCount
    };
  }

  // ==================== 初始化 ====================
  startAutoCleanup();

  // ==================== 导出 ====================
  window.CacheManager = {
    set,
    get,
    has,
    remove,
    clear,
    remember,
    cleanup,
    startAutoCleanup,
    stopAutoCleanup,
    getStats,
    config
  };

})();
