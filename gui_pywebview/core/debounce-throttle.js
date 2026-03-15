/**
 * Debounce & Throttle - 防抖和节流工具
 * 性能优化常用工具函数
 */

(function () {
  'use strict';

  /**
   * 防抖函数
   * 延迟执行，如果在延迟期间再次调用，则重新计时
   * @param {Function} func - 要防抖的函数
   * @param {number} wait - 延迟时间(ms)
   * @param {boolean} immediate - 是否立即执行第一次
   * @returns {Function} 防抖后的函数
   */
  function debounce(func, wait = 300, immediate = false) {
    let timeout;
    let result;

    const debounced = function (...args) {
      const context = this;

      const later = function () {
        timeout = null;
        if (!immediate) {
          result = func.apply(context, args);
        }
      };

      const callNow = immediate && !timeout;

      clearTimeout(timeout);
      timeout = setTimeout(later, wait);

      if (callNow) {
        result = func.apply(context, args);
      }

      return result;
    };

    // 取消方法
    debounced.cancel = function () {
      clearTimeout(timeout);
      timeout = null;
    };

    // 立即执行方法
    debounced.flush = function () {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
        return func.apply(this);
      }
    };

    return debounced;
  }

  /**
   * 节流函数
   * 在指定时间内最多执行一次
   * @param {Function} func - 要节流的函数
   * @param {number} limit - 限制时间(ms)
   * @param {boolean} trailing - 是否在尾部执行
   * @returns {Function} 节流后的函数
   */
  function throttle(func, limit = 300, trailing = true) {
    let inThrottle;
    let lastFunc;
    let lastTime;

    const throttled = function (...args) {
      const context = this;

      if (!inThrottle) {
        func.apply(context, args);
        lastTime = Date.now();
        inThrottle = true;

        setTimeout(() => {
          inThrottle = false;
          if (trailing && lastFunc) {
            lastFunc();
            lastFunc = null;
          }
        }, limit);
      } else if (trailing) {
        lastFunc = function () {
          func.apply(context, args);
        };
      }
    };

    // 取消方法
    throttled.cancel = function () {
      inThrottle = false;
      lastFunc = null;
    };

    return throttled;
  }

  /**
   * 带 leading 和 trailing 选项的节流函数
   * @param {Function} func - 要节流的函数
   * @param {number} wait - 等待时间(ms)
   * @param {Object} options - 选项
   * @returns {Function}
   */
  function throttleAdvanced(func, wait = 300, options = {}) {
    const { leading = true, trailing = true } = options;

    let timeout;
    let previous = 0;
    let result;
    let lastArgs;
    let lastThis;

    const throttled = function (...args) {
      const now = Date.now();
      const remaining = wait - (now - previous);

      lastArgs = args;
      lastThis = this;

      const later = function () {
        previous = leading ? Date.now() : 0;
        timeout = undefined;
        result = func.apply(lastThis, lastArgs);
        lastArgs = lastThis = undefined;
      };

      if (remaining <= 0 || remaining > wait) {
        if (timeout) {
          clearTimeout(timeout);
          timeout = undefined;
        }
        previous = now;
        result = func.apply(this, args);
      } else if (!timeout && trailing) {
        timeout = setTimeout(later, remaining);
      }

      return result;
    };

    throttled.cancel = function () {
      if (timeout) {
        clearTimeout(timeout);
      }
      previous = 0;
      timeout = undefined;
      lastArgs = lastThis = undefined;
    };

    throttled.flush = function () {
      if (timeout) {
        result = func.apply(lastThis, lastArgs);
        previous = Date.now();
        clearTimeout(timeout);
        timeout = undefined;
        lastArgs = lastThis = undefined;
      }
      return result;
    };

    return throttled;
  }

  /**
   * 请求动画帧节流
   * 使用 requestAnimationFrame 进行节流
   * @param {Function} func - 要节流的函数
   * @returns {Function}
   */
  function rafThrottle(func) {
    let ticking = false;

    return function (...args) {
      const context = this;

      if (!ticking) {
        requestAnimationFrame(() => {
          func.apply(context, args);
          ticking = false;
        });
        ticking = true;
      }
    };
  }

  /**
   * 记忆化函数
   * 缓存函数结果，避免重复计算
   * @param {Function} func - 要记忆化的函数
   * @param {Function} keyResolver - 缓存键生成函数
   * @returns {Function}
   */
  function memoize(func, keyResolver = null) {
    const cache = new Map();

    const memoized = function (...args) {
      const key = keyResolver ? keyResolver.apply(this, args) : JSON.stringify(args);

      if (cache.has(key)) {
        return cache.get(key);
      }

      const result = func.apply(this, args);
      cache.set(key, result);
      return result;
    };

    memoized.cache = cache;
    memoized.clear = function () {
      cache.clear();
    };

    return memoized;
  }

  /**
   * 批量处理函数
   * 将多次调用合并为一次批量处理
   * @param {Function} func - 处理函数
   * @param {number} wait - 等待时间(ms)
   * @returns {Function}
   */
  function batch(func, wait = 100) {
    let queue = [];
    let timeout;

    const process = function () {
      if (queue.length > 0) {
        func(queue);
        queue = [];
      }
    };

    return function (item) {
      queue.push(item);

      clearTimeout(timeout);
      timeout = setTimeout(process, wait);
    };
  }

  // ==================== 导出 ====================
  window.DebounceThrottle = {
    debounce,
    throttle,
    throttleAdvanced,
    rafThrottle,
    memoize,
    batch
  };

  // 也导出单个函数
  window.debounce = debounce;
  window.throttle = throttle;
  window.memoize = memoize;

})();
