/**
 * Button Component - 按钮组件
 * 提供多种样式和状态的按钮
 */

(function () {
  'use strict';

  /**
   * 按钮配置
   */
  const ButtonConfig = {
    variants: {
      primary: {
        background: 'linear-gradient(135deg, rgba(0, 229, 255, 0.2), rgba(0, 183, 212, 0.2))',
        borderColor: 'rgba(0, 229, 255, 0.3)',
        color: '#00e5ff',
        hoverBackground: 'linear-gradient(135deg, rgba(0, 229, 255, 0.3), rgba(0, 183, 212, 0.3))',
        hoverShadow: '0 0 15px rgba(0, 229, 255, 0.2)'
      },
      secondary: {
        background: 'transparent',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        color: '#8ab4c8',
        hoverBackground: 'rgba(255, 255, 255, 0.05)',
        hoverBorderColor: 'rgba(255, 255, 255, 0.2)'
      },
      danger: {
        background: 'linear-gradient(135deg, rgba(255, 71, 87, 0.2), rgba(255, 71, 87, 0.1))',
        borderColor: 'rgba(255, 71, 87, 0.3)',
        color: '#ff4757',
        hoverBackground: 'linear-gradient(135deg, rgba(255, 71, 87, 0.3), rgba(255, 71, 87, 0.2))',
        hoverShadow: '0 0 15px rgba(255, 71, 87, 0.2)'
      },
      success: {
        background: 'linear-gradient(135deg, rgba(46, 213, 115, 0.2), rgba(46, 213, 115, 0.1))',
        borderColor: 'rgba(46, 213, 115, 0.3)',
        color: '#2ed573',
        hoverBackground: 'linear-gradient(135deg, rgba(46, 213, 115, 0.3), rgba(46, 213, 115, 0.2))',
        hoverShadow: '0 0 15px rgba(46, 213, 115, 0.2)'
      },
      ghost: {
        background: 'transparent',
        borderColor: 'transparent',
        color: '#8ab4c8',
        hoverBackground: 'rgba(255, 255, 255, 0.05)',
        hoverColor: '#c8d8e0'
      }
    },
    sizes: {
      sm: { padding: '6px 12px', fontSize: '12px', height: '28px' },
      md: { padding: '8px 16px', fontSize: '13px', height: '36px' },
      lg: { padding: '10px 20px', fontSize: '14px', height: '44px' }
    }
  };

  /**
   * 创建按钮
   * @param {Object} options - 配置选项
   * @returns {HTMLElement}
   */
  function create(options = {}) {
    const {
      text = '',
      variant = 'primary',
      size = 'md',
      disabled = false,
      loading = false,
      icon = null,
      iconPosition = 'left',
      fullWidth = false,
      onClick,
      className = '',
      id = '',
      title = ''
    } = options;

    const button = document.createElement('button');
    button.className = `mf-button mf-button-${variant} mf-button-${size} ${className}`;
    button.disabled = disabled || loading;

    if (id) button.id = id;
    if (title) button.title = title;
    if (fullWidth) button.style.width = '100%';

    // 应用样式
    applyStyles(button, variant, size);

    // 构建内容
    let content = '';

    if (loading) {
      content += `<span class="mf-button-spinner"></span>`;
    }

    if (icon && iconPosition === 'left') {
      content += `<span class="mf-button-icon mf-button-icon-left">${icon}</span>`;
    }

    if (text) {
      content += `<span class="mf-button-text">${text}</span>`;
    }

    if (icon && iconPosition === 'right') {
      content += `<span class="mf-button-icon mf-button-icon-right">${icon}</span>`;
    }

    button.innerHTML = content;

    // 绑定事件
    if (onClick && !disabled && !loading) {
      button.addEventListener('click', onClick);
    }

    return button;
  }

  /**
   * 应用样式
   * @param {HTMLElement} button - 按钮元素
   * @param {string} variant - 变体
   * @param {string} size - 尺寸
   */
  function applyStyles(button, variant, size) {
    const variantStyles = ButtonConfig.variants[variant];
    const sizeStyles = ButtonConfig.sizes[size];

    if (!variantStyles || !sizeStyles) return;

    // 基础样式
    button.style.cssText = `
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      border: 1px solid ${variantStyles.borderColor};
      border-radius: 6px;
      background: ${variantStyles.background};
      color: ${variantStyles.color};
      font-family: inherit;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      outline: none;
      white-space: nowrap;
      padding: ${sizeStyles.padding};
      font-size: ${sizeStyles.fontSize};
      height: ${sizeStyles.height};
    `;

    // 添加 hover 效果
    button.addEventListener('mouseenter', () => {
      if (!button.disabled) {
        button.style.background = variantStyles.hoverBackground;
        if (variantStyles.hoverBorderColor) {
          button.style.borderColor = variantStyles.hoverBorderColor;
        }
        if (variantStyles.hoverColor) {
          button.style.color = variantStyles.hoverColor;
        }
        if (variantStyles.hoverShadow) {
          button.style.boxShadow = variantStyles.hoverShadow;
        }
      }
    });

    button.addEventListener('mouseleave', () => {
      button.style.background = variantStyles.background;
      button.style.borderColor = variantStyles.borderColor;
      button.style.color = variantStyles.color;
      button.style.boxShadow = 'none';
    });

    // 添加点击效果
    button.addEventListener('mousedown', () => {
      if (!button.disabled) {
        button.style.transform = 'scale(0.98)';
      }
    });

    button.addEventListener('mouseup', () => {
      button.style.transform = 'scale(1)';
    });

    // 禁用样式
    if (button.disabled) {
      button.style.opacity = '0.5';
      button.style.cursor = 'not-allowed';
    }
  }

  /**
   * 更新按钮状态
   * @param {HTMLElement} button - 按钮元素
   * @param {Object} options - 新选项
   */
  function update(button, options = {}) {
    if (options.loading !== undefined) {
      button.disabled = options.loading;
      const spinner = button.querySelector('.mf-button-spinner');
      if (options.loading && !spinner) {
        const spinnerSpan = document.createElement('span');
        spinnerSpan.className = 'mf-button-spinner';
        button.insertBefore(spinnerSpan, button.firstChild);
      } else if (!options.loading && spinner) {
        spinner.remove();
      }
    }

    if (options.text !== undefined) {
      const textSpan = button.querySelector('.mf-button-text');
      if (textSpan) {
        textSpan.textContent = options.text;
      }
    }

    if (options.disabled !== undefined) {
      button.disabled = options.disabled;
      button.style.opacity = options.disabled ? '0.5' : '1';
      button.style.cursor = options.disabled ? 'not-allowed' : 'pointer';
    }
  }

  /**
   * 添加全局样式
   */
  function addGlobalStyles() {
    if (document.getElementById('mf-button-styles')) return;

    const style = document.createElement('style');
    style.id = 'mf-button-styles';
    style.textContent = `
      .mf-button-spinner {
        width: 14px;
        height: 14px;
        border: 2px solid currentColor;
        border-right-color: transparent;
        border-radius: 50%;
        animation: mf-button-spin 0.75s linear infinite;
      }

      @keyframes mf-button-spin {
        to { transform: rotate(360deg); }
      }

      .mf-button-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
      }

      .mf-button-icon-left {
        margin-right: 2px;
      }

      .mf-button-icon-right {
        margin-left: 2px;
      }
    `;
    document.head.appendChild(style);
  }

  // 初始化
  addGlobalStyles();

  // ==================== 导出 ====================
  window.ButtonComponent = {
    create,
    update,
    config: ButtonConfig
  };

})();
