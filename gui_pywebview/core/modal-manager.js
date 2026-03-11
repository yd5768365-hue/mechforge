/**
 * ModalManager - 模态框管理器
 * 提供对话框、确认框、提示框等模态组件
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    zIndexBase: 10000,
    animation: true,
    backdropClose: true,
    escapeClose: true
  };

  // ==================== 状态 ====================
  const modals = [];
  let modalIdCounter = 0;

  // ==================== 样式 ====================
  function addStyles() {
    if (document.getElementById('modal-styles')) return;

    const style = document.createElement('style');
    style.id = 'modal-styles';
    style.textContent = `
      .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s ease;
        backdrop-filter: blur(4px);
      }

      .modal-overlay.active {
        opacity: 1;
      }

      .modal-container {
        background: rgba(13, 17, 23, 0.95);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 12px;
        min-width: 320px;
        max-width: 90vw;
        max-height: 90vh;
        overflow: hidden;
        transform: scale(0.9) translateY(-20px);
        transition: transform 0.3s ease;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
      }

      .modal-overlay.active .modal-container {
        transform: scale(1) translateY(0);
      }

      .modal-header {
        padding: 16px 20px;
        border-bottom: 1px solid rgba(0, 229, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
      }

      .modal-title {
        font-size: 16px;
        font-weight: 600;
        color: #c8d8e0;
      }

      .modal-close {
        width: 28px;
        height: 28px;
        border: none;
        background: transparent;
        color: #3a5068;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 4px;
        transition: all 0.2s;
      }

      .modal-close:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #c8d8e0;
      }

      .modal-body {
        padding: 20px;
        color: #8ab4c8;
        font-size: 14px;
        line-height: 1.6;
      }

      .modal-footer {
        padding: 16px 20px;
        border-top: 1px solid rgba(0, 229, 255, 0.1);
        display: flex;
        justify-content: flex-end;
        gap: 12px;
      }

      .modal-btn {
        padding: 8px 16px;
        border-radius: 6px;
        border: 1px solid transparent;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
      }

      .modal-btn-primary {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.2), rgba(0, 183, 212, 0.2));
        border-color: rgba(0, 229, 255, 0.3);
        color: #00e5ff;
      }

      .modal-btn-primary:hover {
        background: linear-gradient(135deg, rgba(0, 229, 255, 0.3), rgba(0, 183, 212, 0.3));
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
      }

      .modal-btn-secondary {
        background: transparent;
        border-color: rgba(255, 255, 255, 0.1);
        color: #8ab4c8;
      }

      .modal-btn-secondary:hover {
        background: rgba(255, 255, 255, 0.05);
        border-color: rgba(255, 255, 255, 0.2);
      }

      .modal-btn-danger {
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.2), rgba(255, 71, 87, 0.1);
        border-color: rgba(255, 71, 87, 0.3);
        color: #ff4757;
      }

      .modal-btn-danger:hover {
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.3), rgba(255, 71, 87, 0.2));
        box-shadow: 0 0 15px rgba(255, 71, 87, 0.2);
      }

      /* 输入框样式 */
      .modal-input {
        width: 100%;
        padding: 10px 12px;
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 6px;
        background: rgba(0, 0, 0, 0.3);
        color: #c8d8e0;
        font-size: 14px;
        margin-top: 8px;
      }

      .modal-input:focus {
        outline: none;
        border-color: rgba(0, 229, 255, 0.5);
        box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.1);
      }
    `;
    document.head.appendChild(style);
  }

  // ==================== 核心功能 ====================

  /**
   * 创建模态框
   * @param {Object} options - 选项
   * @returns {Object}
   */
  function create(options = {}) {
    addStyles();

    const {
      title = '',
      content = '',
      width = 'auto',
      showClose = true,
      backdropClose = config.backdropClose,
      escapeClose = config.escapeClose,
      onOpen,
      onClose
    } = options;

    const id = ++modalIdCounter;
    const zIndex = config.zIndexBase + modals.length * 10;

    // 创建遮罩
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.style.zIndex = zIndex;
    overlay.dataset.modalId = id;

    // 创建容器
    const container = document.createElement('div');
    container.className = 'modal-container';
    if (width !== 'auto') {
      container.style.width = width;
    }

    // 构建内容
    let html = '';

    if (title) {
      html += `
        <div class="modal-header">
          <div class="modal-title">${escapeHtml(title)}</div>
          ${showClose ? '<button class="modal-close">&times;</button>' : ''}
        </div>
      `;
    }

    html += `<div class="modal-body">${content}</div>`;
    container.innerHTML = html;
    overlay.appendChild(container);

    // 事件绑定
    if (showClose) {
      const closeBtn = container.querySelector('.modal-close');
      closeBtn?.addEventListener('click', () => close(id));
    }

    if (backdropClose) {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          close(id);
        }
      });
    }

    if (escapeClose) {
      const handleEscape = (e) => {
        if (e.key === 'Escape') {
          close(id);
          document.removeEventListener('keydown', handleEscape);
        }
      };
      document.addEventListener('keydown', handleEscape);
    }

    // 添加到页面
    document.body.appendChild(overlay);

    // 存储
    const modal = {
      id,
      overlay,
      container,
      onClose
    };
    modals.push(modal);

    // 显示动画
    requestAnimationFrame(() => {
      overlay.classList.add('active');
      if (onOpen) onOpen();
    });

    return {
      id,
      close: () => close(id),
      update: (newContent) => update(id, newContent)
    };
  }

  /**
   * 关闭模态框
   * @param {number} id - 模态框ID
   */
  function close(id) {
    const index = modals.findIndex(m => m.id === id);
    if (index === -1) return;

    const modal = modals[index];

    // 关闭动画
    modal.overlay.classList.remove('active');

    setTimeout(() => {
      modal.overlay.remove();
      modals.splice(index, 1);
      if (modal.onClose) modal.onClose();
    }, 300);
  }

  /**
   * 更新内容
   * @param {number} id - 模态框ID
   * @param {string} content - 新内容
   */
  function update(id, content) {
    const modal = modals.find(m => m.id === id);
    if (!modal) return;

    const body = modal.container.querySelector('.modal-body');
    if (body) {
      body.innerHTML = content;
    }
  }

  /**
   * 关闭所有模态框
   */
  function closeAll() {
    [...modals].forEach(m => close(m.id));
  }

  // ==================== 预设对话框 ====================

  /**
   * 确认对话框
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function confirm(options = {}) {
    const {
      title = '确认',
      message = '',
      confirmText = '确认',
      cancelText = '取消',
      type = 'primary'
    } = options;

    return new Promise(resolve => {
      const content = `
        <p>${escapeHtml(message)}</p>
        <div class="modal-footer" style="margin-top: 20px; padding: 0;">
          <button class="modal-btn modal-btn-secondary" id="modal-cancel">${escapeHtml(cancelText)}</button>
          <button class="modal-btn modal-btn-${type}" id="modal-confirm">${escapeHtml(confirmText)}</button>
        </div>
      `;

      const modal = create({
        title,
        content,
        showClose: false,
        backdropClose: false,
        escapeClose: true
      });

      const overlay = document.querySelector(`[data-modal-id="${modal.id}"]`);
      overlay.querySelector('#modal-confirm')?.addEventListener('click', () => {
        modal.close();
        resolve(true);
      });
      overlay.querySelector('#modal-cancel')?.addEventListener('click', () => {
        modal.close();
        resolve(false);
      });
    });
  }

  /**
   * 提示对话框
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function alert(options = {}) {
    const {
      title = '提示',
      message = '',
      okText = '确定',
      type = 'primary'
    } = options;

    return new Promise(resolve => {
      const content = `
        <p>${escapeHtml(message)}</p>
        <div class="modal-footer" style="margin-top: 20px; padding: 0;">
          <button class="modal-btn modal-btn-${type}" id="modal-ok">${escapeHtml(okText)}</button>
        </div>
      `;

      const modal = create({
        title,
        content,
        showClose: false,
        backdropClose: false
      });

      const overlay = document.querySelector(`[data-modal-id="${modal.id}"]`);
      overlay.querySelector('#modal-ok')?.addEventListener('click', () => {
        modal.close();
        resolve();
      });
    });
  }

  /**
   * 输入对话框
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function prompt(options = {}) {
    const {
      title = '输入',
      message = '',
      defaultValue = '',
      placeholder = '',
      confirmText = '确认',
      cancelText = '取消'
    } = options;

    return new Promise(resolve => {
      const content = `
        <p>${escapeHtml(message)}</p>
        <input type="text" class="modal-input" id="modal-input" 
               value="${escapeHtml(defaultValue)}" 
               placeholder="${escapeHtml(placeholder)}">
        <div class="modal-footer" style="margin-top: 20px; padding: 0;">
          <button class="modal-btn modal-btn-secondary" id="modal-cancel">${escapeHtml(cancelText)}</button>
          <button class="modal-btn modal-btn-primary" id="modal-confirm">${escapeHtml(confirmText)}</button>
        </div>
      `;

      const modal = create({
        title,
        content,
        showClose: false,
        backdropClose: false
      });

      const overlay = document.querySelector(`[data-modal-id="${modal.id}"]`);
      const input = overlay.querySelector('#modal-input');
      input?.focus();
      input?.select();

      overlay.querySelector('#modal-confirm')?.addEventListener('click', () => {
        const value = input?.value;
        modal.close();
        resolve(value);
      });

      overlay.querySelector('#modal-cancel')?.addEventListener('click', () => {
        modal.close();
        resolve(null);
      });

      input?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          overlay.querySelector('#modal-confirm')?.click();
        }
      });
    });
  }

  // ==================== 工具函数 ====================

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ==================== 导出 ====================
  window.ModalManager = {
    config,
    create,
    close,
    closeAll,
    update,
    confirm,
    alert,
    prompt
  };

})();
