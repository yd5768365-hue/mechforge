/**
 * Input Component - 输入框组件
 * 提供多种类型的输入框
 */

(function () {
  'use strict';

  /**
   * 创建输入框
   * @param {Object} options - 配置选项
   * @returns {HTMLElement}
   */
  function create(options = {}) {
    const {
      type = 'text',
      placeholder = '',
      value = '',
      label = '',
      helper = '',
      error = '',
      disabled = false,
      readonly = false,
      required = false,
      autofocus = false,
      autocomplete = 'off',
      min,
      max,
      step,
      minLength,
      maxLength,
      pattern,
      name = '',
      id = '',
      className = '',
      fullWidth = false,
      size = 'md',
      prefix = '',
      suffix = '',
      clearable = false,
      onChange,
      onFocus,
      onBlur,
      onKeyDown,
      onKeyUp,
      onEnter
    } = options;

    // 创建容器
    const container = document.createElement('div');
    container.className = `mf-input-wrapper mf-input-${size} ${className}`;
    if (fullWidth) container.style.width = '100%';

    // 标签
    if (label) {
      const labelEl = document.createElement('label');
      labelEl.className = 'mf-input-label';
      labelEl.textContent = label;
      if (required) {
        const requiredMark = document.createElement('span');
        requiredMark.className = 'mf-input-required';
        requiredMark.textContent = ' *';
        labelEl.appendChild(requiredMark);
      }
      container.appendChild(labelEl);
    }

    // 输入框容器
    const inputContainer = document.createElement('div');
    inputContainer.className = 'mf-input-container';
    if (error) inputContainer.classList.add('mf-input-error');
    if (disabled) inputContainer.classList.add('mf-input-disabled');

    // 前缀
    if (prefix) {
      const prefixEl = document.createElement('span');
      prefixEl.className = 'mf-input-prefix';
      prefixEl.innerHTML = prefix;
      inputContainer.appendChild(prefixEl);
    }

    // 输入框
    const input = document.createElement('input');
    input.type = type;
    input.className = 'mf-input';
    input.placeholder = placeholder;
    input.value = value;
    input.disabled = disabled;
    input.readOnly = readonly;
    input.required = required;
    input.autofocus = autofocus;
    input.autocomplete = autocomplete;
    if (name) input.name = name;
    if (id) input.id = id;
    if (min !== undefined) input.min = min;
    if (max !== undefined) input.max = max;
    if (step !== undefined) input.step = step;
    if (minLength !== undefined) input.minLength = minLength;
    if (maxLength !== undefined) input.maxLength = maxLength;
    if (pattern) input.pattern = pattern;

    // 事件绑定
    if (onChange) input.addEventListener('input', onChange);
    if (onFocus) input.addEventListener('focus', onFocus);
    if (onBlur) input.addEventListener('blur', onBlur);
    if (onKeyDown) input.addEventListener('keydown', onKeyDown);
    if (onKeyUp) input.addEventListener('keyup', onKeyUp);
    if (onEnter) {
      input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') onEnter(e);
      });
    }

    inputContainer.appendChild(input);

    // 清除按钮
    if (clearable && !disabled && !readonly) {
      const clearBtn = document.createElement('button');
      clearBtn.type = 'button';
      clearBtn.className = 'mf-input-clear';
      clearBtn.innerHTML = '&times;';
      clearBtn.style.display = value ? 'flex' : 'none';

      clearBtn.addEventListener('click', () => {
        input.value = '';
        clearBtn.style.display = 'none';
        input.focus();
        if (onChange) onChange({ target: input });
      });

      input.addEventListener('input', () => {
        clearBtn.style.display = input.value ? 'flex' : 'none';
      });

      inputContainer.appendChild(clearBtn);
    }

    // 后缀
    if (suffix) {
      const suffixEl = document.createElement('span');
      suffixEl.className = 'mf-input-suffix';
      suffixEl.innerHTML = suffix;
      inputContainer.appendChild(suffixEl);
    }

    container.appendChild(inputContainer);

    // 辅助文本
    if (helper && !error) {
      const helperEl = document.createElement('div');
      helperEl.className = 'mf-input-helper';
      helperEl.textContent = helper;
      container.appendChild(helperEl);
    }

    // 错误文本
    if (error) {
      const errorEl = document.createElement('div');
      errorEl.className = 'mf-input-error-text';
      errorEl.textContent = error;
      container.appendChild(errorEl);
    }

    // 添加样式
    addStyles();

    return container;
  }

  /**
   * 创建文本域
   * @param {Object} options - 配置选项
   * @returns {HTMLElement}
   */
  function createTextarea(options = {}) {
    const {
      placeholder = '',
      value = '',
      label = '',
      helper = '',
      error = '',
      disabled = false,
      readonly = false,
      required = false,
      rows = 4,
      minLength,
      maxLength,
      name = '',
      id = '',
      className = '',
      fullWidth = false,
      size = 'md',
      autoResize = false,
      onChange,
      onFocus,
      onBlur
    } = options;

    const container = document.createElement('div');
    container.className = `mf-input-wrapper mf-textarea-wrapper mf-input-${size} ${className}`;
    if (fullWidth) container.style.width = '100%';

    // 标签
    if (label) {
      const labelEl = document.createElement('label');
      labelEl.className = 'mf-input-label';
      labelEl.textContent = label;
      if (required) {
        const requiredMark = document.createElement('span');
        requiredMark.className = 'mf-input-required';
        requiredMark.textContent = ' *';
        labelEl.appendChild(requiredMark);
      }
      container.appendChild(labelEl);
    }

    // 文本域
    const textarea = document.createElement('textarea');
    textarea.className = 'mf-input mf-textarea';
    textarea.placeholder = placeholder;
    textarea.value = value;
    textarea.disabled = disabled;
    textarea.readOnly = readonly;
    textarea.required = required;
    textarea.rows = rows;
    if (name) textarea.name = name;
    if (id) textarea.id = id;
    if (minLength !== undefined) textarea.minLength = minLength;
    if (maxLength !== undefined) textarea.maxLength = maxLength;

    if (error) textarea.classList.add('mf-input-error');

    // 自动调整高度
    if (autoResize) {
      textarea.style.resize = 'none';
      textarea.style.overflow = 'hidden';

      const adjustHeight = () => {
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight}px`;
      };

      textarea.addEventListener('input', adjustHeight);
      adjustHeight();
    }

    // 事件绑定
    if (onChange) textarea.addEventListener('input', onChange);
    if (onFocus) textarea.addEventListener('focus', onFocus);
    if (onBlur) textarea.addEventListener('blur', onBlur);

    container.appendChild(textarea);

    // 辅助文本
    if (helper && !error) {
      const helperEl = document.createElement('div');
      helperEl.className = 'mf-input-helper';
      helperEl.textContent = helper;
      container.appendChild(helperEl);
    }

    // 错误文本
    if (error) {
      const errorEl = document.createElement('div');
      errorEl.className = 'mf-input-error-text';
      errorEl.textContent = error;
      container.appendChild(errorEl);
    }

    addStyles();

    return container;
  }

  /**
   * 添加样式
   */
  function addStyles() {
    if (document.getElementById('mf-input-styles')) return;

    const style = document.createElement('style');
    style.id = 'mf-input-styles';
    style.textContent = `
      .mf-input-wrapper {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }

      .mf-input-label {
        font-size: 13px;
        font-weight: 500;
        color: #c8d8e0;
      }

      .mf-input-required {
        color: #ff4757;
      }

      .mf-input-container {
        display: flex;
        align-items: center;
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 6px;
        background: rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
        overflow: hidden;
      }

      .mf-input-container:focus-within {
        border-color: rgba(0, 229, 255, 0.5);
        box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.1);
      }

      .mf-input-container.mf-input-error {
        border-color: rgba(255, 71, 87, 0.5);
      }

      .mf-input-container.mf-input-error:focus-within {
        box-shadow: 0 0 0 2px rgba(255, 71, 87, 0.1);
      }

      .mf-input-container.mf-input-disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .mf-input {
        flex: 1;
        border: none;
        background: transparent;
        color: #c8d8e0;
        font-family: inherit;
        font-size: 14px;
        outline: none;
        padding: 10px 12px;
      }

      .mf-input-sm .mf-input {
        padding: 6px 10px;
        font-size: 12px;
      }

      .mf-input-lg .mf-input {
        padding: 14px 16px;
        font-size: 15px;
      }

      .mf-input::placeholder {
        color: #3a5068;
      }

      .mf-input:disabled {
        cursor: not-allowed;
      }

      .mf-input-prefix,
      .mf-input-suffix {
        display: flex;
        align-items: center;
        padding: 0 12px;
        color: #8ab4c8;
        font-size: 14px;
      }

      .mf-input-clear {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        border: none;
        background: rgba(255, 255, 255, 0.1);
        color: #8ab4c8;
        border-radius: 50%;
        cursor: pointer;
        font-size: 14px;
        margin-right: 8px;
        transition: all 0.2s;
      }

      .mf-input-clear:hover {
        background: rgba(255, 255, 255, 0.2);
        color: #c8d8e0;
      }

      .mf-input-helper {
        font-size: 12px;
        color: #8ab4c8;
      }

      .mf-input-error-text {
        font-size: 12px;
        color: #ff4757;
      }

      /* Textarea */
      .mf-textarea-wrapper {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }

      .mf-textarea {
        min-height: 80px;
        resize: vertical;
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 6px;
        background: rgba(0, 0, 0, 0.3);
        color: #c8d8e0;
        font-family: inherit;
        font-size: 14px;
        padding: 10px 12px;
        outline: none;
        transition: all 0.2s ease;
      }

      .mf-textarea:focus {
        border-color: rgba(0, 229, 255, 0.5);
        box-shadow: 0 0 0 2px rgba(0, 229, 255, 0.1);
      }

      .mf-textarea.mf-input-error {
        border-color: rgba(255, 71, 87, 0.5);
      }

      .mf-textarea::placeholder {
        color: #3a5068;
      }
    `;
    document.head.appendChild(style);
  }

  // ==================== 导出 ====================
  window.InputComponent = {
    create,
    createTextarea
  };

})();
