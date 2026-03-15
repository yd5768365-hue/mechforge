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

    if (pulseStatusEl) pulseStatusEl.textContent = 'AI Responding...';

    if (pulseProgressBar) {
      const current = parseFloat(pulseProgressBar.style.width) || 0;
      pulseProgressBar.style.width = `${Math.min(90, Math.max(current, progress * 0.9))}%`;
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
    el.innerHTML = `<span class="message-time">${time}</span><span class="message-prefix">&gt;</span> ${escapeHtml(text)}`;
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

    // 使用 Markdown 渲染或纯文本
    if (useMarkdown && window.Markdown) {
      el.innerHTML = Markdown.render(text);
    } else {
      el.innerHTML = text.split('\n').map(line =>
        line.startsWith('>')
          ? `<div><span class="ai-prefix">${escapeHtml(line)}</span></div>`
          : `<div>${escapeHtml(line)}</div>`
      ).join('');
    }

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
    el.innerHTML = '<span class="ai-prefix">&gt;</span>';
    chatOutput?.appendChild(el);
    return el;
  }

  /**
   * 追加内容到 AI 消息
   * @param {HTMLElement} container - 消息容器
   * @param {string} content - 新内容
   */
  function appendToAIMessage(container, content) {
    const span = document.createElement('span');
    span.textContent = content;
    container.appendChild(span);
    scrollToBottom();
  }

  /**
   * 添加系统消息（错误等）
   * @param {string} text - 消息内容
   */
  function addSystemMessage(text) {
    const el = document.createElement('div');
    el.className = 'chat-message ai slide-in';
    el.innerHTML = `<span style="color:#ff4757;">${escapeHtml(text)}</span>`;
    chatOutput?.appendChild(el);
    scrollToBottom();
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
    addSystemMessage,
    setInputDisabled,
    clearInput,
    focusInput,
    getTimestamp
  };

})();