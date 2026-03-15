/**
 * ChatUI - 聊天界面渲染模块
 * 处理消息显示、启动序列、AI 脉冲指示器等 UI 渲染
 */

(function () {
  'use strict';

  const { $, escapeHtml, getTimestamp } = Utils;

  // ==================== 常量 ====================
  const BOOT_COMPLETE_DELAY = 300;

  // ==================== 启动序列配置 ====================
  const bootLines = [
    { text: '[21:04] SYSTEM: Initializing MechForge AI...', delay: 0, color: '#c8d8e0', cls: 'system' },
    { text: '> AI Assistant Ready', delay: 600, color: '#00e5ff', cls: 'info' },
    { text: 'Model: qwen2.5:3b', delay: 1000, color: '#00e5ff', cls: 'info' },
    { text: 'RAG Status: Active', delay: 1200, color: '#00e5ff', cls: 'info' },
    { text: 'API: Ollama', delay: 1400, color: '#00e5ff', cls: 'info' },
    { text: 'Memory: 42 KB', delay: 1600, color: '#00e5ff', cls: 'info' },
    { text: 'Awaiting input...', delay: 2000, color: '#c8d8e0', cls: 'waiting' }
  ];

  // ==================== DOM 元素 ====================
  let bootSequence = null;
  let chatOutput = null;
  let chatInput = null;
  let sendBtn = null;

  // ==================== AI 脉冲指示器 ====================
  let pulseIndicator = null;
  let pulseStatusEl = null;
  let pulseProgressBar = null;

  // ==================== 工具函数 ====================

  /**
   * 获取当前模型名称（从状态栏 / 模型切换器）
   * @returns {string|null}
   */
  function getCurrentModelName() {
    try {
      if (window.StatusBarManager?.getCurrentModel) {
        return window.StatusBarManager.getCurrentModel();
      }
    } catch (e) {
      console.warn('[ChatUI] Failed to get model from StatusBarManager:', e);
    }
    return null;
  }

  /**
   * 初始化聊天 UI
   */
  function init() {
    bootSequence = $('boot-sequence');
    chatOutput = $('chat-output');
    chatInput = $('chat-input');
    sendBtn = $('send-btn');
  }

  /**
   * 获取聊天输入框元素
   * @returns {HTMLInputElement|null}
   */
  function getInput() {
    return chatInput;
  }

  /**
   * 获取发送按钮元素
   * @returns {HTMLButtonElement|null}
   */
  function getSendBtn() {
    return sendBtn;
  }

  /**
   * 获取聊天输出区域元素
   * @returns {HTMLElement|null}
   */
  function getOutput() {
    return chatOutput;
  }

  // ==================== 启动序列 ====================

  /**
   * 运行启动序列动画
   * @param {Function} onComplete - 完成回调
   */
  function runBootSequence(onComplete) {
    bootLines.forEach((line, index) => {
      setTimeout(() => {
        const lineEl = document.createElement('div');
        lineEl.className = `boot-line ${line.cls}`;
        lineEl.style.color = line.color;
        lineEl.textContent = line.text;
        bootSequence?.appendChild(lineEl);

        if (index === bootLines.length - 1) {
          setTimeout(() => {
            // 添加分隔线
            const sep = document.createElement('div');
            sep.style.cssText = 'height:1px;background:linear-gradient(90deg,#00e5ff33,transparent);margin:12px 0;';
            bootSequence?.appendChild(sep);

            // 添加光标
            const cursor = document.createElement('div');
            cursor.className = 'boot-line waiting-cursor';
            cursor.innerHTML = '<span class="cursor">_</span>';
            bootSequence?.appendChild(cursor);

            // 创建脉冲指示器
            createPulseIndicator();

            if (onComplete) onComplete();
          }, BOOT_COMPLETE_DELAY);
        }
      }, line.delay);
    });
  }

  // ==================== AI 脉冲指示器 ====================

  /**
   * 创建 AI 脉冲指示器
   */
  function createPulseIndicator() {
    pulseIndicator = document.createElement('div');
    pulseIndicator.className = 'ai-pulse-indicator';
    pulseIndicator.innerHTML = `
      <div class="pulse-wave"></div>
      <div class="pulse-dots">
        <div class="pulse-dot"></div>
        <div class="pulse-dot"></div>
        <div class="pulse-dot"></div>
      </div>
      <span class="pulse-status">Ready</span>
      <div class="response-progress">
        <div class="response-progress-bar"></div>
      </div>
    `;
    bootSequence?.appendChild(pulseIndicator);

    pulseStatusEl = pulseIndicator.querySelector('.pulse-status');
    pulseProgressBar = pulseIndicator.querySelector('.response-progress-bar');
  }

  /**
   * 显示"思考中"状态
   */
  function showPulseThinking() {
    if (!pulseIndicator) return;

    pulseIndicator.classList.add('active', 'thinking');
    pulseIndicator.classList.remove('responding');

    if (pulseStatusEl) pulseStatusEl.textContent = 'AI Thinking...';
    if (pulseProgressBar) pulseProgressBar.style.width = '0%';
  }

  /**
   * 显示"响应中"状态
   * @param {number} progress - 进度 (0-1)
   */
  function showPulseResponding(progress = 0) {
    if (!pulseIndicator) return;

    pulseIndicator.classList.add('active', 'responding');
    pulseIndicator.classList.remove('thinking');

    // 根据进度显示不同状态文本
    let statusText = 'AI Responding...';
    if (progress > 0.8) {
      statusText = 'AI Finishing...';
    } else if (progress > 0.5) {
      statusText = 'AI Generating...';
    } else if (progress > 0.1) {
      statusText = 'AI Thinking...';
    }

    if (pulseStatusEl) pulseStatusEl.textContent = statusText;

    if (pulseProgressBar) {
      // 平滑更新进度，避免跳跃
      const current = parseFloat(pulseProgressBar.style.width) || 0;
      const target = Math.min(95, Math.max(current, progress * 100));
      pulseProgressBar.style.width = `${target}%`;
      
      // 添加过渡效果
      pulseProgressBar.style.transition = 'width 0.3s ease-out';
    }
  }

  /**
   * 隐藏脉冲指示器
   */
  function hidePulseIndicator() {
    if (!pulseIndicator) return;

    if (pulseProgressBar) pulseProgressBar.style.width = '100%';

    setTimeout(() => {
      pulseIndicator.classList.remove('active', 'thinking', 'responding');
      if (pulseStatusEl) pulseStatusEl.textContent = 'Ready';
      if (pulseProgressBar) pulseProgressBar.style.width = '0%';
    }, 300);
  }

  // ==================== 消息渲染 ====================

  /**
   * 添加用户消息
   * @param {string} text - 消息内容
   * @param {string} time - 时间戳
   */
  function addUserMessage(text, time) {
    const el = document.createElement('div');
    el.className = 'chat-message user slide-in';

    const safeText = escapeHtml(text).replace(/\n/g, '<br>');

    el.innerHTML = `
      <div class="message-meta">
        <span class="message-role">YOU</span>
        <span class="message-time">${time}</span>
      </div>
      <div class="message-body">
        ${safeText}
      </div>
    `;
    chatOutput?.appendChild(el);
    
    // 添加消息操作按钮
    if (window.ChatFeatures) {
      ChatFeatures.addMessageActions(el, false);
    }
    
    scrollToBottom();
  }

  /**
   * 添加 AI 消息
   * @param {string} text - 消息内容
   * @param {boolean} useMarkdown - 是否使用 Markdown 渲染
   * @returns {HTMLElement} 消息元素
   */
  function addAIMessage(text, useMarkdown = true) {
    const el = document.createElement('div');
    el.className = 'chat-message ai slide-in';
    const time = getTimestamp();
    const modelName = getCurrentModelName();

    // 元信息行（模型标签后续由其他逻辑注入）
    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.innerHTML = `
      <span class="message-role">MECHFORGE</span>
      <span class="message-time">${time}</span>
      ${modelName ? `<span class="message-model" title="点击左下『模型』按钮切换">${escapeHtml(modelName)}</span>` : ''}
    `;

    const body = document.createElement('div');
    body.className = 'message-body';

    // 使用 Markdown 渲染或纯文本
    if (useMarkdown && window.Markdown) {
      body.innerHTML = Markdown.render(text);
    } else {
      body.innerHTML = text.split('\n').map(line =>
        line.startsWith('>')
          ? `<div><span class="ai-prefix">${escapeHtml(line)}</span></div>`
          : `<div>${escapeHtml(line)}</div>`
      ).join('');
    }

    el.appendChild(meta);
    el.appendChild(body);

    chatOutput?.appendChild(el);
    
    // 添加消息操作按钮
    if (window.ChatFeatures) {
      ChatFeatures.addMessageActions(el, true);
    }
    
    scrollToBottom();
    return el;
  }

  /**
   * 创建 AI 消息容器（用于流式输出）
   * @returns {HTMLElement}
   */
  function createAIMessageContainer() {
    const el = document.createElement('div');
    el.className = 'chat-message ai slide-in';
    const time = getTimestamp();
    const modelName = getCurrentModelName();

    const meta = document.createElement('div');
    meta.className = 'message-meta';
    meta.innerHTML = `
      <span class="message-role">MECHFORGE</span>
      <span class="message-time">${time}</span>
      ${modelName ? `<span class="message-model" title="点击左下『模型』按钮切换">${escapeHtml(modelName)}</span>` : ''}
    `;

    const body = document.createElement('div');
    body.className = 'message-body';

    el.appendChild(meta);
    el.appendChild(body);
    chatOutput?.appendChild(el);
    return el;
  }

  /**
   * 追加内容到 AI 消息
   * @param {HTMLElement} container - 消息容器
   * @param {string} content - 新内容
   */
  function appendToAIMessage(container, content) {
    const target = container.querySelector('.message-body') || container;
    const span = document.createElement('span');
    span.textContent = content;
    target.appendChild(span);
    scrollToBottom();
  }

  /**
   * 使用 Markdown 渲染流式完成后的 AI 消息正文
   * @param {HTMLElement} container - 消息容器
   * @param {string} text - 完整文本
   */
  function renderAIMessageBody(container, text) {
    const target = container.querySelector('.message-body') || container;
    if (window.Markdown) {
      target.innerHTML = Markdown.render(text);
    } else {
      target.innerHTML = escapeHtml(text).replace(/\n/g, '<br>');
    }
  }

  /**
   * 添加系统消息（错误等）
   * @param {string} text - 消息内容
   */
  function addSystemMessage(text) {
    const el = document.createElement('div');
    el.className = 'chat-message system slide-in';
    el.innerHTML = `<div class="message-body" style="color:#ff4757;">${escapeHtml(text)}</div>`;
    chatOutput?.appendChild(el);
    scrollToBottom();
  }

  /**
   * 添加错误消息卡片（带重试按钮）
   * @param {Object} errorInfo - 错误信息对象 {type, message, detail, retryable, suggestion}
   * @param {Function} onRetry - 重试回调函数
   */
  function addErrorMessage(errorInfo, onRetry) {
    const el = document.createElement('div');
    el.className = 'chat-message error-message slide-in';
    
    const icons = {
      network: '🌐',
      api: '⚠️',
      timeout: '⏱️',
      model: '🤖',
      unknown: '❌'
    };
    
    const icon = icons[errorInfo.type] || icons.unknown;
    
    el.innerHTML = `
      <div class="error-card">
        <div class="error-header">
          <span class="error-icon">${icon}</span>
          <span class="error-title">${escapeHtml(errorInfo.message)}</span>
        </div>
        ${errorInfo.suggestion ? `<div class="error-suggestion">${escapeHtml(errorInfo.suggestion)}</div>` : ''}
        <details class="error-details">
          <summary>查看详情</summary>
          <pre class="error-detail-text">${escapeHtml(errorInfo.detail)}</pre>
        </details>
        ${errorInfo.retryable && onRetry ? '<button class="error-retry-btn">重试</button>' : ''}
      </div>
    `;
    
    // 绑定重试按钮事件
    if (errorInfo.retryable && onRetry) {
      const retryBtn = el.querySelector('.error-retry-btn');
      if (retryBtn) {
        retryBtn.addEventListener('click', () => {
          retryBtn.disabled = true;
          retryBtn.textContent = '重试中...';
          onRetry();
        });
      }
    }
    
    chatOutput?.appendChild(el);
    scrollToBottom();
    
    // 添加错误消息样式（如果还没有）
    if (!document.getElementById('error-message-styles')) {
      const style = document.createElement('style');
      style.id = 'error-message-styles';
      style.textContent = `
        .error-message {
          margin: 12px 0;
        }
        .error-card {
          background: rgba(255, 71, 87, 0.1);
          border: 1px solid rgba(255, 71, 87, 0.3);
          border-radius: 8px;
          padding: 12px 16px;
          max-width: 100%;
        }
        .error-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
        }
        .error-icon {
          font-size: 18px;
        }
        .error-title {
          color: #ff4757;
          font-weight: 600;
          font-size: 14px;
        }
        .error-suggestion {
          color: rgba(200, 216, 224, 0.8);
          font-size: 12px;
          margin-top: 6px;
          margin-bottom: 8px;
        }
        .error-details {
          margin-top: 8px;
          font-size: 11px;
        }
        .error-details summary {
          color: rgba(200, 216, 224, 0.6);
          cursor: pointer;
          user-select: none;
        }
        .error-details summary:hover {
          color: rgba(200, 216, 224, 0.9);
        }
        .error-detail-text {
          margin-top: 6px;
          padding: 8px;
          background: rgba(0, 0, 0, 0.3);
          border-radius: 4px;
          color: rgba(255, 71, 87, 0.8);
          font-size: 10px;
          overflow-x: auto;
          white-space: pre-wrap;
          word-break: break-all;
        }
        .error-retry-btn {
          margin-top: 10px;
          padding: 6px 16px;
          background: linear-gradient(135deg, rgba(0, 229, 255, 0.2), rgba(0, 229, 255, 0.1));
          border: 1px solid rgba(0, 229, 255, 0.4);
          border-radius: 4px;
          color: #00e5ff;
          font-size: 12px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
        }
        .error-retry-btn:hover {
          background: linear-gradient(135deg, rgba(0, 229, 255, 0.3), rgba(0, 229, 255, 0.2));
          box-shadow: 0 0 10px rgba(0, 229, 255, 0.3);
        }
      `;
      document.head.appendChild(style);
    }
  }

  /**
   * 滚动到底部
   */
  function scrollToBottom() {
    if (chatOutput) {
      chatOutput.scrollTop = chatOutput.scrollHeight;
    }
  }

  /**
   * 设置输入状态
   * @param {boolean} disabled - 是否禁用
   */
  function setInputDisabled(disabled) {
    if (chatInput) chatInput.disabled = disabled;
    if (sendBtn) sendBtn.disabled = disabled;
  }

  /**
   * 清空输入框
   */
  function clearInput() {
    if (chatInput) chatInput.value = '';
  }

  /**
   * 聚焦输入框
   */
  function focusInput() {
    chatInput?.focus();
  }

  // ==================== 导出 ====================
  window.ChatUI = {
    init,
    getInput,
    getSendBtn,
    getOutput,
    runBootSequence,
    showPulseThinking,
    showPulseResponding,
    hidePulseIndicator,
    addUserMessage,
    addAIMessage,
    createAIMessageContainer,
    appendToAIMessage,
    renderAIMessageBody,
    addSystemMessage,
    addErrorMessage,
    setInputDisabled,
    clearInput,
    focusInput,
    getTimestamp
  };

})();