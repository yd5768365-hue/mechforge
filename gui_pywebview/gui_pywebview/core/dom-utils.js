/**
 * DOMUtils - DOM 操作工具集
 * 提供高效、安全的 DOM 操作方法
 */

(function () {
  'use strict';

  // ==================== 元素选择 ====================

  /**
   * 安全地获取元素
   * @param {string|HTMLElement} selector - 选择器或元素
   * @param {HTMLElement} context - 上下文元素
   * @returns {HTMLElement|null}
   */
  function $(selector, context = document) {
    if (typeof selector === 'string') {
      return context.querySelector(selector);
    }
    return selector instanceof HTMLElement ? selector : null;
  }

  /**
   * 获取所有匹配元素
   * @param {string} selector - 选择器
   * @param {HTMLElement} context - 上下文元素
   * @returns {Array<HTMLElement>}
   */
  function $$(selector, context = document) {
    return Array.from(context.querySelectorAll(selector));
  }

  /**
   * 创建元素
   * @param {string} tag - 标签名
   * @param {Object} attributes - 属性对象
   * @param {string|HTMLElement|Array} children - 子元素
   * @returns {HTMLElement}
   */
  function create(tag, attributes = {}, children = null) {
    const element = document.createElement(tag);

    // 设置属性
    Object.entries(attributes).forEach(([key, value]) => {
      if (key === 'className') {
        element.className = value;
      } else if (key === 'dataset') {
        Object.entries(value).forEach(([dataKey, dataValue]) => {
          element.dataset[dataKey] = dataValue;
        });
      } else if (key.startsWith('on') && typeof value === 'function') {
        const event = key.slice(2).toLowerCase();
        element.addEventListener(event, value);
      } else {
        element.setAttribute(key, value);
      }
    });

    // 添加子元素
    if (children) {
      if (typeof children === 'string') {
        element.innerHTML = children;
      } else if (children instanceof HTMLElement) {
        element.appendChild(children);
      } else if (Array.isArray(children)) {
        children.forEach(child => {
          if (typeof child === 'string') {
            element.insertAdjacentHTML('beforeend', child);
          } else if (child instanceof HTMLElement) {
            element.appendChild(child);
          }
        });
      }
    }

    return element;
  }

  // ==================== 类操作 ====================

  /**
   * 添加类名
   * @param {HTMLElement} element - 目标元素
   * @param {string|Array} classes - 类名
   */
  function addClass(element, classes) {
    if (!element) return;
    const classList = Array.isArray(classes) ? classes : classes.split(' ');
    element.classList.add(...classList.filter(Boolean));
  }

  /**
   * 移除类名
   * @param {HTMLElement} element - 目标元素
   * @param {string|Array} classes - 类名
   */
  function removeClass(element, classes) {
    if (!element) return;
    const classList = Array.isArray(classes) ? classes : classes.split(' ');
    element.classList.remove(...classList.filter(Boolean));
  }

  /**
   * 切换类名
   * @param {HTMLElement} element - 目标元素
   * @param {string} className - 类名
   * @param {boolean} force - 强制添加或移除
   */
  function toggleClass(element, className, force) {
    if (!element) return;
    element.classList.toggle(className, force);
  }

  /**
   * 检查是否有类名
   * @param {HTMLElement} element - 目标元素
   * @param {string} className - 类名
   * @returns {boolean}
   */
  function hasClass(element, className) {
    return element ? element.classList.contains(className) : false;
  }

  // ==================== 样式操作 ====================

  /**
   * 设置样式
   * @param {HTMLElement} element - 目标元素
   * @param {Object} styles - 样式对象
   */
  function setStyle(element, styles) {
    if (!element) return;
    Object.assign(element.style, styles);
  }

  /**
   * 获取计算样式
   * @param {HTMLElement} element - 目标元素
   * @param {string} property - CSS 属性
   * @returns {string}
   */
  function getStyle(element, property) {
    if (!element) return '';
    return window.getComputedStyle(element).getPropertyValue(property);
  }

  /**
   * 显示元素
   * @param {HTMLElement} element - 目标元素
   * @param {string} display - 显示类型
   */
  function show(element, display = 'block') {
    if (!element) return;
    element.style.display = display;
  }

  /**
   * 隐藏元素
   * @param {HTMLElement} element - 目标元素
   */
  function hide(element) {
    if (!element) return;
    element.style.display = 'none';
  }

  /**
   * 切换显示/隐藏
   * @param {HTMLElement} element - 目标元素
   * @param {string} display - 显示类型
   */
  function toggle(element, display = 'block') {
    if (!element) return;
    element.style.display = element.style.display === 'none' ? display : 'none';
  }

  // ==================== 属性操作 ====================

  /**
   * 设置属性
   * @param {HTMLElement} element - 目标元素
   * @param {string} name - 属性名
   * @param {string} value - 属性值
   */
  function setAttr(element, name, value) {
    if (!element) return;
    element.setAttribute(name, value);
  }

  /**
   * 获取属性
   * @param {HTMLElement} element - 目标元素
   * @param {string} name - 属性名
   * @returns {string|null}
   */
  function getAttr(element, name) {
    return element ? element.getAttribute(name) : null;
  }

  /**
   * 移除属性
   * @param {HTMLElement} element - 目标元素
   * @param {string} name - 属性名
   */
  function removeAttr(element, name) {
    if (!element) return;
    element.removeAttribute(name);
  }

  // ==================== 内容操作 ====================

  /**
   * 设置文本内容
   * @param {HTMLElement} element - 目标元素
   * @param {string} text - 文本内容
   */
  function setText(element, text) {
    if (!element) return;
    element.textContent = text;
  }

  /**
   * 设置 HTML 内容
   * @param {HTMLElement} element - 目标元素
   * @param {string} html - HTML 内容
   */
  function setHTML(element, html) {
    if (!element) return;
    element.innerHTML = html;
  }

  /**
   * 清空元素内容
   * @param {HTMLElement} element - 目标元素
   */
  function empty(element) {
    if (!element) return;
    element.innerHTML = '';
  }

  // ==================== DOM 遍历 ====================

  /**
   * 获取父元素
   * @param {HTMLElement} element - 目标元素
   * @param {string} selector - 可选的选择器
   * @returns {HTMLElement|null}
   */
  function parent(element, selector = null) {
    if (!element) return null;
    if (!selector) return element.parentElement;

    let parent = element.parentElement;
    while (parent) {
      if (parent.matches(selector)) return parent;
      parent = parent.parentElement;
    }
    return null;
  }

  /**
   * 获取子元素
   * @param {HTMLElement} element - 目标元素
   * @param {string} selector - 选择器
   * @returns {Array<HTMLElement>}
   */
  function children(element, selector = null) {
    if (!element) return [];
    const children = Array.from(element.children);
    return selector ? children.filter(child => child.matches(selector)) : children;
  }

  /**
   * 查找最近的匹配元素
   * @param {HTMLElement} element - 目标元素
   * @param {string} selector - 选择器
   * @returns {HTMLElement|null}
   */
  function closest(element, selector) {
    return element ? element.closest(selector) : null;
  }

  /**
   * 获取兄弟元素
   * @param {HTMLElement} element - 目标元素
   * @param {string} selector - 选择器
   * @returns {Array<HTMLElement>}
   */
  function siblings(element, selector = null) {
    if (!element || !element.parentElement) return [];
    const siblings = Array.from(element.parentElement.children).filter(el => el !== element);
    return selector ? siblings.filter(el => el.matches(selector)) : siblings;
  }

  // ==================== DOM 插入 ====================

  /**
   * 在元素前插入
   * @param {HTMLElement} element - 目标元素
   * @param {HTMLElement} newElement - 新元素
   */
  function before(element, newElement) {
    if (!element || !newElement) return;
    element.parentElement?.insertBefore(newElement, element);
  }

  /**
   * 在元素后插入
   * @param {HTMLElement} element - 目标元素
   * @param {HTMLElement} newElement - 新元素
   */
  function after(element, newElement) {
    if (!element || !newElement) return;
    element.parentElement?.insertBefore(newElement, element.nextSibling);
  }

  /**
   * 在元素开头插入
   * @param {HTMLElement} element - 目标元素
   * @param {HTMLElement} newElement - 新元素
   */
  function prepend(element, newElement) {
    if (!element || !newElement) return;
    element.insertBefore(newElement, element.firstChild);
  }

  /**
   * 在元素末尾插入
   * @param {HTMLElement} element - 目标元素
   * @param {HTMLElement} newElement - 新元素
   */
  function append(element, newElement) {
    if (!element || !newElement) return;
    element.appendChild(newElement);
  }

  /**
   * 移除元素
   * @param {HTMLElement} element - 目标元素
   */
  function remove(element) {
    if (!element) return;
    element.remove();
  }

  // ==================== 尺寸和位置 ====================

  /**
   * 获取元素尺寸
   * @param {HTMLElement} element - 目标元素
   * @returns {Object}
   */
  function getSize(element) {
    if (!element) return { width: 0, height: 0 };
    const rect = element.getBoundingClientRect();
    return {
      width: rect.width,
      height: rect.height,
      top: rect.top,
      left: rect.left,
      right: rect.right,
      bottom: rect.bottom
    };
  }

  /**
   * 获取元素在视口中的位置
   * @param {HTMLElement} element - 目标元素
   * @returns {Object}
   */
  function getViewportPosition(element) {
    if (!element) return { top: 0, left: 0 };
    const rect = element.getBoundingClientRect();
    return {
      top: rect.top,
      left: rect.left,
      bottom: rect.bottom,
      right: rect.right,
      centerX: rect.left + rect.width / 2,
      centerY: rect.top + rect.height / 2
    };
  }

  /**
   * 检查元素是否在视口内
   * @param {HTMLElement} element - 目标元素
   * @param {number} threshold - 阈值
   * @returns {boolean}
   */
  function isInViewport(element, threshold = 0) {
    if (!element) return false;
    const rect = element.getBoundingClientRect();
    return (
      rect.top >= -threshold &&
      rect.left >= -threshold &&
      rect.bottom <= window.innerHeight + threshold &&
      rect.right <= window.innerWidth + threshold
    );
  }

  // ==================== 动画 ====================

  /**
   * 淡入
   * @param {HTMLElement} element - 目标元素
   * @param {number} duration - 持续时间(ms)
   * @returns {Promise}
   */
  function fadeIn(element, duration = 300) {
    if (!element) return Promise.resolve();
    return new Promise(resolve => {
      element.style.opacity = '0';
      element.style.display = 'block';
      element.style.transition = `opacity ${duration}ms ease`;

      requestAnimationFrame(() => {
        element.style.opacity = '1';
        setTimeout(resolve, duration);
      });
    });
  }

  /**
   * 淡出
   * @param {HTMLElement} element - 目标元素
   * @param {number} duration - 持续时间(ms)
   * @returns {Promise}
   */
  function fadeOut(element, duration = 300) {
    if (!element) return Promise.resolve();
    return new Promise(resolve => {
      element.style.transition = `opacity ${duration}ms ease`;
      element.style.opacity = '0';

      setTimeout(() => {
        element.style.display = 'none';
        resolve();
      }, duration);
    });
  }

  /**
   * 滑动显示
   * @param {HTMLElement} element - 目标元素
   * @param {number} duration - 持续时间(ms)
   * @returns {Promise}
   */
  function slideDown(element, duration = 300) {
    if (!element) return Promise.resolve();
    return new Promise(resolve => {
      element.style.display = 'block';
      const height = element.scrollHeight;
      element.style.height = '0';
      element.style.overflow = 'hidden';
      element.style.transition = `height ${duration}ms ease`;

      requestAnimationFrame(() => {
        element.style.height = `${height}px`;
        setTimeout(() => {
          element.style.height = '';
          element.style.overflow = '';
          resolve();
        }, duration);
      });
    });
  }

  /**
   * 滑动隐藏
   * @param {HTMLElement} element - 目标元素
   * @param {number} duration - 持续时间(ms)
   * @returns {Promise}
   */
  function slideUp(element, duration = 300) {
    if (!element) return Promise.resolve();
    return new Promise(resolve => {
      const height = element.scrollHeight;
      element.style.height = `${height}px`;
      element.style.overflow = 'hidden';
      element.style.transition = `height ${duration}ms ease`;

      requestAnimationFrame(() => {
        element.style.height = '0';
        setTimeout(() => {
          element.style.display = 'none';
          element.style.height = '';
          element.style.overflow = '';
          resolve();
        }, duration);
      });
    });
  }

  // ==================== 导出 ====================
  window.DOMUtils = {
    $,
    $$,
    create,
    addClass,
    removeClass,
    toggleClass,
    hasClass,
    setStyle,
    getStyle,
    show,
    hide,
    toggle,
    setAttr,
    getAttr,
    removeAttr,
    setText,
    setHTML,
    empty,
    parent,
    children,
    closest,
    siblings,
    before,
    after,
    prepend,
    append,
    remove,
    getSize,
    getViewportPosition,
    isInViewport,
    fadeIn,
    fadeOut,
    slideDown,
    slideUp
  };

  // 简写导出
  window.$ = $;
  window.$$ = $$;

})();
