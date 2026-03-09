/**
 * Utils - 公共工具函数模块
 * 提供通用的 DOM 操作、字符串处理、函数工具等
 */

// ==================== DOM 快捷方法 ====================

/**
 * getElementById 快捷方式
 * @param {string} id - 元素 ID
 * @returns {HTMLElement|null}
 */
const $ = id => document.getElementById(id);

/**
 * querySelectorAll 快捷方式
 * @param {string} sel - CSS 选择器
 * @returns {NodeList}
 */
const $$ = sel => document.querySelectorAll(sel);

/**
 * querySelector 快捷方式
 * @param {string} sel - CSS 选择器
 * @returns {HTMLElement|null}
 */
const $one = sel => document.querySelector(sel);

// ==================== 字符串处理 ====================

/**
 * HTML 转义，防止 XSS
 * @param {string} str - 原始字符串
 * @returns {string} 转义后的字符串
 */
function escapeHtml(str) {
  if (str == null) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

/**
 * 截断字符串并添加省略号
 * @param {string} str - 原始字符串
 * @param {number} maxLen - 最大长度
 * @returns {string}
 */
function truncate(str, maxLen) {
  if (!str || str.length <= maxLen) return str || '';
  return str.substring(0, maxLen) + '...';
}

// ==================== 函数工具 ====================

/**
 * 防抖函数
 * @param {Function} fn - 要执行的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {Function}
 */
function debounce(fn, delay = 300) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

/**
 * 节流函数
 * @param {Function} fn - 要执行的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function}
 */
function throttle(fn, limit = 100) {
  let inThrottle;
  return (...args) => {
    if (!inThrottle) {
      fn(...args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// ==================== 时间格式化 ====================

/**
 * 获取当前时间字符串 [HH:MM]
 * @returns {string}
 */
function getTimestamp() {
  const now = new Date();
  const h = String(now.getHours()).padStart(2, '0');
  const m = String(now.getMinutes()).padStart(2, '0');
  return `[${h}:${m}]`;
}

// ==================== 随机数生成 ====================

/**
 * 生成指定范围内的随机数
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {number}
 */
function random(min, max) {
  return Math.random() * (max - min) + min;
}

/**
 * 生成指定范围内的随机整数
 * @param {number} min - 最小值（包含）
 * @param {number} max - 最大值（包含）
 * @returns {number}
 */
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// ==================== 常量 ====================

const RUNE_CHARS = [
  '\u25C8', '\u25C9', '\u25CA', '\u25CB', '\u25CC',
  '\u25CD', '\u25CE', '\u25CF', '\u25D0', '\u25D1',
  '\u25D2', '\u2B21', '\u2B22', '\u25B2', '\u25BC', '\u25C6'
];

const PARTICLE_COUNT = 15;
const WHALE_SPEECH_MAX_LEN = 30;
const RUNE_COUNT = 12;

// ==================== 导出 ====================

window.Utils = {
  $,
  $$,
  $one,
  escapeHtml,
  truncate,
  debounce,
  throttle,
  getTimestamp,
  random,
  randomInt,
  RUNE_CHARS,
  PARTICLE_COUNT,
  WHALE_SPEECH_MAX_LEN,
  RUNE_COUNT
};