/**
 * NotificationManager - 通知管理器
 * 提供 Toast、Snackbar、Alert 等多种通知形式
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    defaultDuration: 3000,
    maxNotifications: 5,
    position: 'top-right',
    animation: true
  };

  // ==================== 通知容器 ====================
  let container = null;
  const notifications = [];

  // ==================== 初始化 ====================

  /**
   * 初始化通知系统
   */
  function init() {
    if (container) return;

    container = document.createElement('div');
    container.className = 'notification-container';
    container.style.cssText = `
      position: fixed;
      z-index: 10000;
      pointer-events: none;
    `;

    // 根据位置设置样式
    setPosition(config.position);

    document.body.appendChild(container);

    // 添加样式
    addStyles();
  }

  /**
   * 设置位置
   * @param {string} position - 位置
   */
  function setPosition(position) {
    config.position = position;
    if (!container) return;

    const positions = {
      'top-left': { top: '20px', left: '20px', right: 'auto', bottom: 'auto' },
      'top-center': { top: '20px', left: '50%', right: 'auto', bottom: 'auto', transform: 'translateX(-50%)' },
      'top-right': { top: '20px', right: '20px', left: 'auto', bottom: 'auto' },
      'bottom-left': { bottom: '20px', left: '20px', right: 'auto', top: 'auto' },
      'bottom-center': { bottom: '20px', left: '50%', right: 'auto', top: 'auto', transform: 'translateX(-50%)' },
      'bottom-right': { bottom: '20px', right: '20px', left: 'auto', top: 'auto' }
    };

    const pos = positions[position] || positions['top-right'];
    Object.assign(container.style, pos);
  }

  /**
   * 添加样式
   */
  function addStyles() {
    if (document.getElementById('notification-styles')) return;

    const style = document.createElement('style');
    style.id = 'notification-styles';
    style.textContent = `
      .notification-container {
        display: flex;
        flex-direction: column;
        gap: 8px;
      }

      .notification {
        pointer-events: auto;
        min-width: 280px;
        max-width: 400px;
        padding: 12px 16px;
        border-radius: 8px;
        background: rgba(13, 17, 23, 0.95);
        border: 1px solid rgba(0, 229, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: flex-start;
        gap: 12px;
        animation: notificationSlideIn 0.3s ease-out;
        backdrop-filter: blur(10px);
      }

      .notification.notification-exit {
        animation: notificationSlideOut 0.3s ease-in forwards;
      }

      .notification-icon {
        width: 20px;
        height: 20px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      .notification-content {
        flex: 1;
        min-width: 0;
      }

      .notification-title {
        font-size: 14px;
        font-weight: 600;
        color: #c8d8e0;
        margin-bottom: 4px;
      }

      .notification-message {
        font-size: 13px;
        color: #8ab4c8;
        line-height: 1.5;
      }

      .notification-close {
        width: 20px;
        height: 20px;
        border: none;
        background: transparent;
        color: #3a5068;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: all 0.2s;
        flex-shrink: 0;
      }

      .notification-close:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #c8d8e0;
      }

      .notification-progress {
        position: absolute;
        bottom: 0;
        left: 0;
        height: 2px;
        background: linear-gradient(90deg, #00e5ff, #00b8d4);
        border-radius: 0 0 0 8px;
        transition: width linear;
      }

      /* 类型样式 */
      .notification-success {
        border-color: rgba(46, 213, 115, 0.3);
      }
      .notification-success .notification-icon {
        color: #2ed573;
      }

      .notification-error {
        border-color: rgba(255, 71, 87, 0.3);
      }
      .notification-error .notification-icon {
        color: #ff4757;
      }

      .notification-warning {
        border-color: rgba(255, 165, 2, 0.3);
      }
      .notification-warning .notification-icon {
        color: #ffa502;
      }

      .notification-info {
        border-color: rgba(0, 229, 255, 0.3);
      }
      .notification-info .notification-icon {
        color: #00e5ff;
      }

      @keyframes notificationSlideIn {
        from {
          opacity: 0;
          transform: translateX(100%);
        }
        to {
          opacity: 1;
          transform: translateX(0);
        }
      }

      @keyframes notificationSlideOut {
        from {
          opacity: 1;
          transform: translateX(0);
        }
        to {
          opacity: 0;
          transform: translateX(100%);
        }
      }

      /* 底部位置的动画 */
      .notification-container[style*="bottom"] .notification {
        animation: notificationSlideUp 0.3s ease-out;
      }

      .notification-container[style*="bottom"] .notification.notification-exit {
        animation: notificationSlideDown 0.3s ease-in forwards;
      }

      @keyframes notificationSlideUp {
        from {
          opacity: 0;
          transform: translateY(100%);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }

      @keyframes notificationSlideDown {
        from {
          opacity: 1;
          transform: translateY(0);
        }
        to {
          opacity: 0;
          transform: translateY(100%);
        }
      }
    `;
    document.head.appendChild(style);
  }

  // ==================== 图标 ====================
  const icons = {
    success: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`,
    error: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`,
    warning: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`,
    info: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`,
    close: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>`
  };

  // ==================== 核心功能 ====================

  /**
   * 显示通知
   * @param {Object} options - 选项
   * @returns {Object} 通知实例
   */
  function show(options = {}) {
    init();

    const {
      type = 'info',
      title = '',
      message = '',
      duration = config.defaultDuration,
      closable = true,
      progress = true,
      onClose,
      actions = []
    } = options;

    // 限制通知数量
    if (notifications.length >= config.maxNotifications) {
      const oldest = notifications[0];
      if (oldest) {
        close(oldest.id);
      }
    }

    // 创建通知元素
    const notification = document.createElement('div');
    const id = Date.now() + Math.random();
    notification.className = `notification notification-${type}`;
    notification.dataset.id = id;

    // 构建内容
    let html = `
      <div class="notification-icon">${icons[type]}</div>
      <div class="notification-content">
        ${title ? `<div class="notification-title">${escapeHtml(title)}</div>` : ''}
        <div class="notification-message">${escapeHtml(message)}</div>
      </div>
    `;

    if (closable) {
      html += `<button class="notification-close" onclick="NotificationManager.close('${id}')">${icons.close}</button>`;
    }

    if (progress && duration > 0) {
      html += `<div class="notification-progress" style="width: 100%; transition-duration: ${duration}ms;"></div>`;
    }

    notification.innerHTML = html;
    container.appendChild(notification);

    // 存储通知
    const notificationObj = {
      id,
      element: notification,
      onClose,
      timer: null
    };
    notifications.push(notificationObj);

    // 启动进度条动画
    if (progress && duration > 0) {
      requestAnimationFrame(() => {
        const progressBar = notification.querySelector('.notification-progress');
        if (progressBar) {
          progressBar.style.width = '0%';
        }
      });
    }

    // 自动关闭
    if (duration > 0) {
      notificationObj.timer = setTimeout(() => {
        close(id);
      }, duration);
    }

    return {
      id,
      close: () => close(id)
    };
  }

  /**
   * 关闭通知
   * @param {string} id - 通知 ID
   */
  function close(id) {
    const index = notifications.findIndex(n => n.id === id);
    if (index === -1) return;

    const notification = notifications[index];

    // 清除定时器
    if (notification.timer) {
      clearTimeout(notification.timer);
    }

    // 添加退出动画
    notification.element.classList.add('notification-exit');

    // 动画结束后移除
    setTimeout(() => {
      notification.element.remove();
      notifications.splice(index, 1);

      if (notification.onClose) {
        notification.onClose();
      }
    }, 300);
  }

  /**
   * 关闭所有通知
   */
  function closeAll() {
    [...notifications].forEach(n => close(n.id));
  }

  /**
   * 更新通知
   * @param {string} id - 通知 ID
   * @param {Object} options - 更新选项
   */
  function update(id, options = {}) {
    const notification = notifications.find(n => n.id === id);
    if (!notification) return;

    const { title, message, type } = options;

    if (title !== undefined) {
      const titleEl = notification.element.querySelector('.notification-title');
      if (titleEl) {
        titleEl.textContent = title;
      }
    }

    if (message !== undefined) {
      const messageEl = notification.element.querySelector('.notification-message');
      if (messageEl) {
        messageEl.textContent = message;
      }
    }

    if (type !== undefined) {
      notification.element.className = notification.element.className.replace(/notification-\w+/, `notification-${type}`);
      const iconEl = notification.element.querySelector('.notification-icon');
      if (iconEl) {
        iconEl.innerHTML = icons[type];
      }
    }
  }

  // ==================== 快捷方法 ====================

  function success(message, title = '', options = {}) {
    return show({ type: 'success', message, title, ...options });
  }

  function error(message, title = '', options = {}) {
    return show({ type: 'error', message, title, ...options });
  }

  function warning(message, title = '', options = {}) {
    return show({ type: 'warning', message, title, ...options });
  }

  function info(message, title = '', options = {}) {
    return show({ type: 'info', message, title, ...options });
  }

  /**
   * 统一 Toast 快捷方法（供各模块调用）
   * @param {string} message - 提示消息
   * @param {string} type - success | error | warning | info
   */
  function showToast(message, type = 'info') {
    const t = (type && ['success', 'error', 'warning', 'info'].includes(type)) ? type : 'info';
    return show({ type: t, message, title: '', duration: 3000 });
  }

  // ==================== 工具函数 ====================

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ==================== 导出 ====================
  const api = {
    config,
    init,
    show,
    close,
    closeAll,
    update,
    success,
    error,
    warning,
    info,
    showToast,
    setPosition
  };
  window.NotificationManager = api;
  window.showToast = showToast;

})();
