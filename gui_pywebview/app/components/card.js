/**
 * Card Component - 卡片组件
 * 提供卡片容器和多种变体
 */

(function () {
  'use strict';

  /**
   * 创建卡片
   * @param {Object} options - 配置选项
   * @returns {HTMLElement}
   */
  function create(options = {}) {
    const {
      title = '',
      subtitle = '',
      content = '',
      footer = '',
      headerActions = [],
      footerActions = [],
      hoverable = false,
      clickable = false,
      padding = 'md',
      shadow = 'md',
      border = true,
      className = '',
      id = '',
      onClick,
      image,
      imagePosition = 'top'
    } = options;

    const card = document.createElement('div');
    card.className = `mf-card mf-card-padding-${padding} mf-card-shadow-${shadow} ${className}`;
    if (hoverable) card.classList.add('mf-card-hoverable');
    if (clickable) card.classList.add('mf-card-clickable');
    if (!border) card.classList.add('mf-card-no-border');
    if (id) card.id = id;

    // 图片（顶部）
    if (image && imagePosition === 'top') {
      const imgContainer = document.createElement('div');
      imgContainer.className = 'mf-card-image-top';
      const img = document.createElement('img');
      img.src = image;
      img.alt = title || 'Card image';
      imgContainer.appendChild(img);
      card.appendChild(imgContainer);
    }

    // 头部
    if (title || subtitle || headerActions.length > 0) {
      const header = document.createElement('div');
      header.className = 'mf-card-header';

      const headerContent = document.createElement('div');
      headerContent.className = 'mf-card-header-content';

      if (title) {
        const titleEl = document.createElement('div');
        titleEl.className = 'mf-card-title';
        titleEl.textContent = title;
        headerContent.appendChild(titleEl);
      }

      if (subtitle) {
        const subtitleEl = document.createElement('div');
        subtitleEl.className = 'mf-card-subtitle';
        subtitleEl.textContent = subtitle;
        headerContent.appendChild(subtitleEl);
      }

      header.appendChild(headerContent);

      if (headerActions.length > 0) {
        const actionsEl = document.createElement('div');
        actionsEl.className = 'mf-card-header-actions';
        headerActions.forEach(action => {
          actionsEl.appendChild(action);
        });
        header.appendChild(actionsEl);
      }

      card.appendChild(header);
    }

    // 内容
    if (content) {
      const contentEl = document.createElement('div');
      contentEl.className = 'mf-card-content';
      if (typeof content === 'string') {
        contentEl.innerHTML = content;
      } else {
        contentEl.appendChild(content);
      }
      card.appendChild(contentEl);
    }

    // 图片（底部）
    if (image && imagePosition === 'bottom') {
      const imgContainer = document.createElement('div');
      imgContainer.className = 'mf-card-image-bottom';
      const img = document.createElement('img');
      img.src = image;
      img.alt = title || 'Card image';
      imgContainer.appendChild(img);
      card.appendChild(imgContainer);
    }

    // 底部
    if (footer || footerActions.length > 0) {
      const footerEl = document.createElement('div');
      footerEl.className = 'mf-card-footer';

      if (footer) {
        const footerText = document.createElement('div');
        footerText.className = 'mf-card-footer-text';
        footerText.textContent = footer;
        footerEl.appendChild(footerText);
      }

      if (footerActions.length > 0) {
        const actionsEl = document.createElement('div');
        actionsEl.className = 'mf-card-footer-actions';
        footerActions.forEach(action => {
          actionsEl.appendChild(action);
        });
        footerEl.appendChild(actionsEl);
      }

      card.appendChild(footerEl);
    }

    // 点击事件
    if (onClick) {
      card.addEventListener('click', onClick);
    }

    // 添加样式
    addStyles();

    return card;
  }

  /**
   * 创建卡片组
   * @param {Array} cards - 卡片数组
   * @param {Object} options - 配置选项
   * @returns {HTMLElement}
   */
  function createGroup(cards = [], options = {}) {
    const {
      columns = 3,
      gap = 'md',
      className = ''
    } = options;

    const group = document.createElement('div');
    group.className = `mf-card-group mf-card-group-${columns} mf-card-group-gap-${gap} ${className}`;

    cards.forEach(card => {
      if (typeof card === 'object' && !(card instanceof HTMLElement)) {
        group.appendChild(create(card));
      } else {
        group.appendChild(card);
      }
    });

    addStyles();

    return group;
  }

  /**
   * 添加样式
   */
  function addStyles() {
    if (document.getElementById('mf-card-styles')) return;

    const style = document.createElement('style');
    style.id = 'mf-card-styles';
    style.textContent = `
      .mf-card {
        background: rgba(13, 17, 23, 0.8);
        border: 1px solid rgba(0, 229, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
        transition: all 0.3s ease;
      }

      .mf-card-no-border {
        border: none;
      }

      .mf-card-hoverable:hover {
        border-color: rgba(0, 229, 255, 0.3);
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.1);
        transform: translateY(-2px);
      }

      .mf-card-clickable {
        cursor: pointer;
      }

      .mf-card-clickable:active {
        transform: translateY(0);
      }

      /* Padding */
      .mf-card-padding-sm .mf-card-header,
      .mf-card-padding-sm .mf-card-content,
      .mf-card-padding-sm .mf-card-footer {
        padding: 12px;
      }

      .mf-card-padding-md .mf-card-header,
      .mf-card-padding-md .mf-card-content,
      .mf-card-padding-md .mf-card-footer {
        padding: 16px;
      }

      .mf-card-padding-lg .mf-card-header,
      .mf-card-padding-lg .mf-card-content,
      .mf-card-padding-lg .mf-card-footer {
        padding: 20px;
      }

      /* Shadow */
      .mf-card-shadow-none {
        box-shadow: none;
      }

      .mf-card-shadow-sm {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      }

      .mf-card-shadow-md {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
      }

      .mf-card-shadow-lg {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
      }

      /* Header */
      .mf-card-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
        border-bottom: 1px solid rgba(0, 229, 255, 0.05);
      }

      .mf-card-header-content {
        flex: 1;
        min-width: 0;
      }

      .mf-card-title {
        font-size: 16px;
        font-weight: 600;
        color: #c8d8e0;
        margin-bottom: 4px;
      }

      .mf-card-subtitle {
        font-size: 13px;
        color: #8ab4c8;
      }

      .mf-card-header-actions {
        display: flex;
        gap: 8px;
        flex-shrink: 0;
      }

      /* Content */
      .mf-card-content {
        color: #8ab4c8;
        font-size: 14px;
        line-height: 1.6;
      }

      /* Footer */
      .mf-card-footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        border-top: 1px solid rgba(0, 229, 255, 0.05);
        background: rgba(0, 0, 0, 0.2);
      }

      .mf-card-footer-text {
        font-size: 12px;
        color: #3a5068;
      }

      .mf-card-footer-actions {
        display: flex;
        gap: 8px;
      }

      /* Image */
      .mf-card-image-top,
      .mf-card-image-bottom {
        width: 100%;
        overflow: hidden;
      }

      .mf-card-image-top img,
      .mf-card-image-bottom img {
        width: 100%;
        height: auto;
        display: block;
      }

      .mf-card-image-top {
        border-bottom: 1px solid rgba(0, 229, 255, 0.1);
      }

      .mf-card-image-bottom {
        border-top: 1px solid rgba(0, 229, 255, 0.1);
      }

      /* Card Group */
      .mf-card-group {
        display: grid;
      }

      .mf-card-group-1 {
        grid-template-columns: 1fr;
      }

      .mf-card-group-2 {
        grid-template-columns: repeat(2, 1fr);
      }

      .mf-card-group-3 {
        grid-template-columns: repeat(3, 1fr);
      }

      .mf-card-group-4 {
        grid-template-columns: repeat(4, 1fr);
      }

      .mf-card-group-gap-sm {
        gap: 12px;
      }

      .mf-card-group-gap-md {
        gap: 16px;
      }

      .mf-card-group-gap-lg {
        gap: 24px;
      }

      @media (max-width: 768px) {
        .mf-card-group-3,
        .mf-card-group-4 {
          grid-template-columns: repeat(2, 1fr);
        }
      }

      @media (max-width: 480px) {
        .mf-card-group-2,
        .mf-card-group-3,
        .mf-card-group-4 {
          grid-template-columns: 1fr;
        }
      }
    `;
    document.head.appendChild(style);
  }

  // ==================== 导出 ====================
  window.CardComponent = {
    create,
    createGroup
  };

})();
