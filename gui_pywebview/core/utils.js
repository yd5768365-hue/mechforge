/**
 * @fileoverview Utils - 公共工具函数模块
 * @description 提供通用的 DOM 操作、字符串处理、函数工具等
 * @module Utils
 * @version 2.0.0
 */

(function () {
  'use strict';

  // ==================== DOM 快捷方法 ====================

  /**
   * getElementById 快捷方式
   * @param {string} id - 元素 ID
   * @returns {HTMLElement|null} 找到的元素或 null
   * @example
   * const element = $('myElement');
   */
  const $ = (id) => document.getElementById(id);

  /**
   * querySelectorAll 快捷方式
   * @param {string} selector - CSS 选择器
   * @returns {NodeList} 匹配的元素列表
   * @example
   * const buttons = $$('.btn');
   */
  const $$ = (selector) => document.querySelectorAll(selector);

  /**
   * querySelector 快捷方式
   * @param {string} selector - CSS 选择器
   * @returns {HTMLElement|null} 匹配的第一个元素
   * @example
   * const header = $one('.header');
   */
  const $one = (selector) => document.querySelector(selector);

  // ==================== 字符串处理 ====================

  /**
   * HTML 转义，防止 XSS 攻击
   * @param {string|number|null|undefined} str - 原始字符串
   * @returns {string} 转义后的字符串
   * @example
   * const safe = escapeHtml('<script>alert("xss")</script>');
   * // 返回: &lt;script&gt;alert("xss")&lt;/script&gt;
   */
  function escapeHtml(str) {
    if (str == null) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  /**
   * 截断字符串并添加省略号
   * @param {string} str - 原始字符串
   * @param {number} maxLen - 最大长度
   * @param {string} [suffix='...'] - 后缀字符串
   * @returns {string} 截断后的字符串
   * @example
   * const short = truncate('Hello World', 8); // 'Hello...'
   */
  function truncate(str, maxLen, suffix = '...') {
    if (!str || str.length <= maxLen) return str || '';
    return str.substring(0, maxLen - suffix.length) + suffix;
  }

  /**
   * 生成唯一 ID
   * @param {string} [prefix='id'] - ID 前缀
   * @returns {string} 唯一 ID
   * @example
   * const id = generateId('btn'); // 'btn-a7x9k2m'
   */
  function generateId(prefix = 'id') {
    return `${prefix}-${Math.random().toString(36).substring(2, 9)}`;
  }

  /**
   * 将字符串转换为驼峰命名
   * @param {string} str - 原始字符串
   * @returns {string} 驼峰命名字符串
   * @example
   * const camel = toCamelCase('hello-world'); // 'helloWorld'
   */
  function toCamelCase(str) {
    return str.replace(/-([a-z])/g, (match, letter) => letter.toUpperCase());
  }

  /**
   * 将字符串转换为短横线命名
   * @param {string} str - 原始字符串
   * @returns {string} 短横线命名字符串
   * @example
   * const kebab = toKebabCase('helloWorld'); // 'hello-world'
   */
  function toKebabCase(str) {
    return str.replace(/([A-Z])/g, '-$1').toLowerCase();
  }

  // ==================== 函数工具 ====================

  /**
   * 防抖函数
   * @param {Function} fn - 要执行的函数
   * @param {number} [delay=300] - 延迟时间（毫秒）
   * @returns {Function} 防抖后的函数
   * @example
   * const debouncedSearch = debounce(search, 300);
   * input.addEventListener('input', debouncedSearch);
   */
  function debounce(fn, delay = 300) {
    let timer = null;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  /**
   * 节流函数
   * @param {Function} fn - 要执行的函数
   * @param {number} [limit=100] - 时间限制（毫秒）
   * @returns {Function} 节流后的函数
   * @example
   * const throttledScroll = throttle(handleScroll, 100);
   * window.addEventListener('scroll', throttledScroll);
   */
  function throttle(fn, limit = 100) {
    let inThrottle = false;
    return function (...args) {
      if (!inThrottle) {
        fn.apply(this, args);
        inThrottle = true;
        setTimeout(() => { inThrottle = false; }, limit);
      }
    };
  }

  /**
   * 记忆化函数
   * @template T
   * @param {function(...*): T} fn - 要记忆的函数
   * @returns {function(...*): T} 记忆化后的函数
   * @example
   * const fib = memoize((n) => n < 2 ? n : fib(n - 1) + fib(n - 2));
   */
  function memoize(fn) {
    const cache = new Map();
    return function (...args) {
      const key = JSON.stringify(args);
      if (cache.has(key)) {
        return cache.get(key);
      }
      const result = fn.apply(this, args);
      cache.set(key, result);
      return result;
    };
  }

  /**
   * 管道函数，从左到右执行函数
   * @param {...Function} fns - 要执行的函数
   * @returns {Function} 组合后的函数
   * @example
   * const result = pipe(trim, toLowerCase)('  HELLO  '); // 'hello'
   */
  function pipe(...fns) {
    return (value) => fns.reduce((acc, fn) => fn(acc), value);
  }

  /**
   * 组合函数，从右到左执行函数
   * @param {...Function} fns - 要执行的函数
   * @returns {Function} 组合后的函数
   * @example
   * const result = compose(toLowerCase, trim)('  HELLO  '); // 'hello'
   */
  function compose(...fns) {
    return (value) => fns.reduceRight((acc, fn) => fn(acc), value);
  }

  // ==================== 时间格式化 ====================

  /**
   * 获取当前时间字符串 [HH:MM]
   * @returns {string} 格式化后的时间
   * @example
   * const time = getTimestamp(); // '[14:30]'
   */
  function getTimestamp() {
    const now = new Date();
    const h = String(now.getHours()).padStart(2, '0');
    const m = String(now.getMinutes()).padStart(2, '0');
    return `[${h}:${m}]`;
  }

  /**
   * 格式化日期时间
   * @param {Date} [date=new Date()] - 日期对象
   * @param {string} [format='YYYY-MM-DD HH:mm:ss'] - 格式模板
   * @returns {string} 格式化后的日期字符串
   * @example
   * const formatted = formatDateTime(new Date(), 'YYYY年MM月DD日');
   */
  function formatDateTime(date = new Date(), format = 'YYYY-MM-DD HH:mm:ss') {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return format
      .replace('YYYY', String(year))
      .replace('MM', month)
      .replace('DD', day)
      .replace('HH', hours)
      .replace('mm', minutes)
      .replace('ss', seconds);
  }

  /**
   * 延迟执行
   * @param {number} ms - 延迟毫秒数
   * @returns {Promise<void>}
   * @example
   * await delay(1000); // 等待1秒
   */
  function delay(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // ==================== 随机数生成 ====================

  /**
   * 生成指定范围内的随机数
   * @param {number} min - 最小值
   * @param {number} max - 最大值
   * @returns {number} 随机数
   * @example
   * const num = random(10, 20); // 10.5
   */
  function random(min, max) {
    return Math.random() * (max - min) + min;
  }

  /**
   * 生成指定范围内的随机整数
   * @param {number} min - 最小值（包含）
   * @param {number} max - 最大值（包含）
   * @returns {number} 随机整数
   * @example
   * const num = randomInt(1, 6); // 4
   */
  function randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  /**
   * 从数组中随机选择元素
   * @template T
   * @param {T[]} arr - 数组
   * @returns {T} 随机元素
   * @example
   * const item = randomChoice(['a', 'b', 'c']); // 'b'
   */
  function randomChoice(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  /**
   * 生成指定范围内的随机颜色
   * @returns {string} HEX 颜色值
   * @example
   * const color = randomColor(); // '#a7f3d0'
   */
  function randomColor() {
    return `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
  }

  // ==================== 数组/对象工具 ====================

  /**
   * 深拷贝对象
   * @template T
   * @param {T} obj - 要拷贝的对象
   * @returns {T} 深拷贝后的对象
   * @example
   * const copy = deepClone({ a: { b: 1 } });
   */
  function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj.getTime());
    if (obj instanceof Array) return obj.map((item) => deepClone(item));
    if (obj instanceof Object) {
      const cloned = {};
      for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
          cloned[key] = deepClone(obj[key]);
        }
      }
      return cloned;
    }
    return obj;
  }

  /**
   * 合并对象
   * @param {...Object} objects - 要合并的对象
   * @returns {Object} 合并后的对象
   * @example
   * const merged = mergeObjects({ a: 1 }, { b: 2 }); // { a: 1, b: 2 }
   */
  function mergeObjects(...objects) {
    return objects.reduce((acc, obj) => ({ ...acc, ...obj }), {});
  }

  /**
   * 从对象中选择指定属性
   * @param {Object} obj - 源对象
   * @param {string[]} keys - 要选择的属性名
   * @returns {Object} 新对象
   * @example
   * const picked = pick({ a: 1, b: 2, c: 3 }, ['a', 'c']); // { a: 1, c: 3 }
   */
  function pick(obj, keys) {
    return keys.reduce((acc, key) => {
      if (key in obj) acc[key] = obj[key];
      return acc;
    }, {});
  }

  /**
   * 从对象中排除指定属性
   * @param {Object} obj - 源对象
   * @param {string[]} keys - 要排除的属性名
   * @returns {Object} 新对象
   * @example
   * const omitted = omit({ a: 1, b: 2, c: 3 }, ['b']); // { a: 1, c: 3 }
   */
  function omit(obj, keys) {
    const result = { ...obj };
    keys.forEach((key) => delete result[key]);
    return result;
  }

  /**
   * 将对象转换为 URL 查询字符串
   * @param {Object} params - 参数对象
   * @returns {string} 查询字符串
   * @example
   * const query = toQueryString({ page: 1, size: 10 }); // 'page=1&size=10'
   */
  function toQueryString(params) {
    return Object.entries(params)
      .filter(([, value]) => value != null)
      .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
      .join('&');
  }

  // ==================== DOM 操作优化 ====================

  /**
   * 使用 DocumentFragment 批量插入元素
   * @param {HTMLElement} parent - 父元素
   * @param {HTMLElement[]} children - 子元素数组
   * @example
   * appendChildren(list, items.map(item => createItemElement(item)));
   */
  function appendChildren(parent, children) {
    if (!parent || !Array.isArray(children)) return;
    const fragment = document.createDocumentFragment();
    children.forEach((child) => {
      if (child instanceof HTMLElement) {
        fragment.appendChild(child);
      }
    });
    parent.appendChild(fragment);
  }

  /**
   * 安全地移除元素
   * @param {HTMLElement} element - 要移除的元素
   * @returns {boolean} 是否成功移除
   * @example
   * safeRemove(document.getElementById('temp'));
   */
  function safeRemove(element) {
    if (element && element.parentNode) {
      element.parentNode.removeChild(element);
      return true;
    }
    return false;
  }

  /**
   * 监听元素可见性变化
   * @param {HTMLElement} element - 要监听的元素
   * @param {function(HTMLElement): void} callback - 回调函数
   * @returns {IntersectionObserver|null} 观察器实例
   * @example
   * onVisible(image, (el) => el.src = el.dataset.src);
   */
  function onVisible(element, callback) {
    if (!element || typeof IntersectionObserver === 'undefined') return null;

    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          callback(entry.target);
          observer.unobserve(entry.target);
        }
      });
    });

    observer.observe(element);
    return observer;
  }

  /**
   * 创建带清理功能的元素
   * @param {string} tag - 标签名
   * @param {Object} [attributes={}] - 属性对象
   * @param {Object} [options={}] - 选项
   * @returns {HTMLElement} 创建的元素
   * @example
   * const btn = createElement('button', { className: 'btn', textContent: 'Click' });
   */
  function createElement(tag, attributes = {}, options = {}) {
    const element = document.createElement(tag);

    Object.entries(attributes).forEach(([key, value]) => {
      if (key === 'textContent' || key === 'innerHTML') {
        element[key] = value;
      } else if (key === 'className') {
        element.className = value;
      } else if (key === 'style' && typeof value === 'object') {
        Object.assign(element.style, value);
      } else {
        element.setAttribute(key, value);
      }
    });

    if (options.parent) {
      options.parent.appendChild(element);
    }

    return element;
  }

  // ==================== 性能监控 ====================

  /**
   * 测量函数执行时间
   * @template T
   * @param {function(...*): T} fn - 要测量的函数
   * @param {string} [label='Function'] - 标签
   * @returns {function(...*): T} 包装后的函数
   * @example
   * const measuredFn = measurePerformance(heavyCalculation, 'calc');
   */
  function measurePerformance(fn, label = 'Function') {
    return function (...args) {
      const start = performance.now();
      const result = fn.apply(this, args);
      const duration = performance.now() - start;
      console.log(`[Performance] ${label} took ${duration.toFixed(2)}ms`);
      return result;
    };
  }

  /**
   * 延迟执行（使用 requestIdleCallback 或 setTimeout）
   * @param {Function} fn - 要执行的函数
   * @param {number} [delay=0] - 延迟时间
   * @example
   * schedule(() => console.log('idle'), 100);
   */
  function schedule(fn, delay = 0) {
    if (typeof requestIdleCallback !== 'undefined' && delay === 0) {
      requestIdleCallback(fn);
    } else {
      setTimeout(fn, delay);
    }
  }

  // ==================== 验证工具 ====================

  /**
   * 检查值是否为空（null, undefined, '', [], {}）
   * @param {*} value - 要检查的值
   * @returns {boolean} 是否为空
   * @example
   * isEmpty(null); // true
   * isEmpty([]); // true
   * isEmpty({}); // true
   * isEmpty('text'); // false
   */
  function isEmpty(value) {
    if (value == null) return true;
    if (typeof value === 'string') return value.trim().length === 0;
    if (Array.isArray(value)) return value.length === 0;
    if (typeof value === 'object') return Object.keys(value).length === 0;
    return false;
  }

  /**
   * 检查值是否为有效数字
   * @param {*} value - 要检查的值
   * @returns {boolean} 是否为有效数字
   * @example
   * isNumber('123'); // false
   * isNumber(123); // true
   * isNumber(NaN); // false
   */
  function isNumber(value) {
    return typeof value === 'number' && !Number.isNaN(value);
  }

  /**
   * 检查值是否为有效字符串
   * @param {*} value - 要检查的值
   * @returns {boolean} 是否为有效字符串
   */
  function isString(value) {
    return typeof value === 'string';
  }

  /**
   * 检查值是否为有效函数
   * @param {*} value - 要检查的值
   * @returns {boolean} 是否为有效函数
   */
  function isFunction(value) {
    return typeof value === 'function';
  }

  /**
   * 检查值是否为有效对象
   * @param {*} value - 要检查的值
   * @returns {boolean} 是否为有效对象
   */
  function isObject(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value);
  }

  // ==================== 常量 ====================

  /**
   * 符文字符集
   * @constant {string[]}
   */
  const RUNE_CHARS = [
    '\u25C8', '\u25C9', '\u25CA', '\u25CB', '\u25CC',
    '\u25CD', '\u25CE', '\u25CF', '\u25D0', '\u25D1',
    '\u25D2', '\u2B21', '\u2B22', '\u25B2', '\u25BC', '\u25C6'
  ];

  /**
   * 默认粒子数量
   * @constant {number}
   */
  const PARTICLE_COUNT = 15;

  /**
   * 鲸鱼语音最大长度
   * @constant {number}
   */
  const WHALE_SPEECH_MAX_LEN = 30;

  /**
   * 符文数量
   * @constant {number}
   */
  const RUNE_COUNT = 12;

  // ==================== 导出 ====================

  /**
   * 工具函数集合
   * @namespace Utils
   */
  window.Utils = {
    // DOM 操作
    $,
    $$,
    $one,

    // 字符串处理
    escapeHtml,
    truncate,
    generateId,
    toCamelCase,
    toKebabCase,

    // 函数工具
    debounce,
    throttle,
    memoize,
    pipe,
    compose,

    // 时间处理
    getTimestamp,
    formatDateTime,
    delay,

    // 随机数
    random,
    randomInt,
    randomChoice,
    randomColor,

    // 对象操作
    deepClone,
    mergeObjects,
    pick,
    omit,
    toQueryString,

    // DOM 优化
    appendChildren,
    safeRemove,
    onVisible,
    createElement,

    // 性能
    measurePerformance,
    schedule,

    // 验证
    isEmpty,
    isNumber,
    isString,
    isFunction,
    isObject,

    // 常量
    RUNE_CHARS,
    PARTICLE_COUNT,
    WHALE_SPEECH_MAX_LEN,
    RUNE_COUNT
  };
})();
