/**
 * ChatFeatures - 聊天增强功能模块
 * 提供消息操作、历史管理、快捷键等功能
 */

(function () {
  'use strict';

  const { $, escapeHtml, debounce } = Utils;

  // ==================== 状态 ====================
  let state = {
    draft: '',
    isGenerating: false,
    abortController: null
  };

  // ==================== 存储键 ====================
  const STORAGE_KEYS = {
    DRAFT: 'mechforge_chat_draft',
    HISTORY: 'mechforge_chat_history'
  };

  // ==================== 初始化 ====================

  /**
   * 初始化聊天增强功能
   */
  function init() {
    initDraftAutoSave();
    initKeyboardShortcuts();
    initStopGeneration();
    initMessageActions();
    initHistoryControls();
    
    // 恢复草稿
    restoreDraft();
    
    console.log('[ChatFeatures] 初始化完成');
  }

  // ==================== 草稿自动保存 ====================

  /**
   * 初始化草稿自动保存
   */
  function initDraftAutoSave() {
    const chatInput = ChatUI.getInput();
    if (!chatInput) return;

    // 使用防抖保存
    const saveDraft = debounce(() => {
      const text = chatInput.value.trim();
      if (text) {
        localStorage.setItem(STORAGE_KEYS.DRAFT, text);
      } else {
        localStorage.removeItem(STORAGE_KEYS.DRAFT);
      }
    }, 500);

    chatInput.addEventListener('input', saveDraft);
  }

  /**
   * 恢复草稿
   */
  function restoreDraft() {
    const draft = localStorage.getItem(STORAGE_KEYS.DRAFT);
    if (draft) {
      const chatInput = ChatUI.getInput();
      if (chatInput && !chatInput.value) {
        chatInput.value = draft;
        chatInput.focus();
      }
    }
  }

  /**
   * 清除草稿
   */
  function clearDraft() {
    localStorage.removeItem(STORAGE_KEYS.DRAFT);
  }

  // ==================== 快捷键支持 ====================

  /**
   * 初始化快捷键
   */
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      const chatInput = ChatUI.getInput();
      const isInputFocused = document.activeElement === chatInput;

      // Ctrl/Cmd + Enter: 发送消息
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        ChatHandler.sendMessage();
        return;
      }

      // Escape: 停止生成 或 清空输入
      if (e.key === 'Escape') {
        if (state.isGenerating) {
          stopGeneration();
        } else if (isInputFocused && chatInput) {
          chatInput.value = '';
          clearDraft();
        }
        return;
      }

      // Ctrl/Cmd + L: 清空对话
      if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
        e.preventDefault();
        clearChat();
        return;
      }

      // Ctrl/Cmd + E: 导出对话
      if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
        e.preventDefault();
        exportChat();
        return;
      }

      // /: 聚焦输入框
      if (e.key === '/' && !isInputFocused) {
        e.preventDefault();
        chatInput?.focus();
        return;
      }
    });
  }

  // ==================== 停止生成 ====================

  /**
   * 初始化停止生成功能
   */
  function initStopGeneration() {
    // 创建停止按钮
    const sendBtn = ChatUI.getSendBtn();
    if (!sendBtn) return;

    // 添加停止按钮样式
    const style = document.createElement('style');
    style.textContent = `
      .stop-btn {
        padding: 10px 28px;
        border-radius: 50px;
        border: 1px solid rgba(255, 71, 87, 0.5);
        cursor: pointer;
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.3), rgba(255, 71, 87, 0.2));
        color: #ff4757;
        font-family: sans-serif;
        font-size: 13px;
        font-weight: 600;
        display: none;
        align-items: center;
        gap: 8px;
        transition: all 0.3s;
      }
      .stop-btn:hover {
        background: linear-gradient(135deg, rgba(255, 71, 87, 0.5), rgba(255, 71, 87, 0.4));
        box-shadow: 0 0 15px rgba(255, 71, 87, 0.4);
      }
      .stop-btn.visible {
        display: flex;
      }
      .send-btn-container {
        display: flex;
        gap: 8px;
      }
    `;
    document.head.appendChild(style);

    // 创建停止按钮
    const stopBtn = document.createElement('button');
    stopBtn.className = 'stop-btn';
    stopBtn.id = 'stop-btn';
    stopBtn.innerHTML = `
      <svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor">
        <rect x="6" y="6" width="12" height="12" rx="2"/>
      </svg>
      停止
    `;

    // 插入到发送按钮旁边
    sendBtn.parentNode.insertBefore(stopBtn, sendBtn.nextSibling);

    // 点击事件
    stopBtn.addEventListener('click', stopGeneration);
  }

  /**
   * 显示停止按钮
   */
  function showStopButton() {
    const stopBtn = $('stop-btn');
    const sendBtn = $('send-btn');
    if (stopBtn) stopBtn.classList.add('visible');
    if (sendBtn) sendBtn.style.display = 'none';
    state.isGenerating = true;
  }

  /**
   * 隐藏停止按钮
   */
  function hideStopButton() {
    const stopBtn = $('stop-btn');
    const sendBtn = $('send-btn');
    if (stopBtn) stopBtn.classList.remove('visible');
    if (sendBtn) sendBtn.style.display = '';
    state.isGenerating = false;
  }

  /**
   * 停止生成
   */
  function stopGeneration() {
    if (state.abortController) {
      state.abortController.abort();
      state.abortController = null;
    }
    
    hideStopButton();
    Mascot.stopResonance();
    ChatUI.hidePulseIndicator();
    ChatUI.setInputDisabled(false);
    ChatUI.addSystemMessage('⏹️ 生成已停止');
  }

  // ==================== 消息操作 ====================

  /**
   * 初始化消息操作
   */
  function initMessageActions() {
    // 添加消息操作样式
    const style = document.createElement('style');
    style.textContent = `
      .message-actions {
        display: none;
        position: absolute;
        right: 8px;
        top: 8px;
        gap: 4px;
      }
      .chat-message:hover .message-actions {
        display: flex;
      }
      .message-action-btn {
        width: 28px;
        height: 28px;
        border-radius: 4px;
        border: 1px solid rgba(0, 229, 255, 0.2);
        background: rgba(0, 14, 20, 0.9);
        color: var(--text-dim);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        transition: all 0.2s;
      }
      .message-action-btn:hover {
        background: rgba(0, 229, 255, 0.1);
        color: var(--accent-primary);
        border-color: rgba(0, 229, 255, 0.4);
      }
      .chat-message {
        position: relative;
      }
      .copy-toast {
        position: fixed;
        bottom: 60px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 229, 255, 0.9);
        color: #0a1520;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        z-index: 10000;
        animation: toastFade 2s forwards;
      }
      @keyframes toastFade {
        0%, 80% { opacity: 1; }
        100% { opacity: 0; }
      }
    `;
    document.head.appendChild(style);

    // 事件委托处理消息操作
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('.message-action-btn');
      if (!btn) return;

      const message = btn.closest('.chat-message');
      if (!message) return;

      const action = btn.dataset.action;
      const text = message.textContent.replace(/复制重新生成/, '').trim();

      switch (action) {
        case 'copy':
          await copyToClipboard(text);
          break;
        case 'regenerate':
          regenerateLastMessage();
          break;
      }
    });
  }

  /**
   * 复制到剪贴板
   * @param {string} text - 要复制的文本
   */
  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      showToast('已复制到剪贴板');
    } catch (err) {
      console.error('复制失败:', err);
      showToast('复制失败');
    }
  }

  /**
   * 显示提示
   * @param {string} message - 提示消息
   */
  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'copy-toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 2000);
  }

  /**
   * 重新生成最后一条消息
   */
  function regenerateLastMessage() {
    // 获取倒数第二条消息（用户消息）
    const messages = document.querySelectorAll('.chat-message');
    if (messages.length < 2) return;

    const userMessage = messages[messages.length - 2];
    const text = userMessage.textContent.replace(/复制重新生成/, '').trim();

    // 删除最后一条 AI 消息
    messages[messages.length - 1].remove();

    // 重新发送
    const chatInput = ChatUI.getInput();
    if (chatInput) {
      chatInput.value = text;
      ChatHandler.sendMessage();
    }
  }

  // ==================== 历史管理 ====================

  /**
   * 初始化历史控制
   */
  function initHistoryControls() {
    // 添加控制按钮到聊天面板
    const chatPanel = $('chat-panel');
    if (!chatPanel) return;

    // 创建控制栏
    const controlsBar = document.createElement('div');
    controlsBar.className = 'chat-controls-bar';
    controlsBar.innerHTML = `
      <button class="chat-control-btn" id="clear-chat-btn" title="清空对话 (Ctrl+L)">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
        </svg>
        清空
      </button>
      <button class="chat-control-btn" id="export-chat-btn" title="导出对话 (Ctrl+E)">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
        </svg>
        导出
      </button>
    `;

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
      .chat-controls-bar {
        display: flex;
        gap: 8px;
        padding: 8px 16px;
        border-top: 1px solid var(--border-color);
        background: rgba(0, 0, 0, 0.2);
      }
      .chat-control-btn {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 4px;
        border: 1px solid var(--border-color);
        background: transparent;
        color: var(--text-dim);
        font-size: 11px;
        cursor: pointer;
        transition: all 0.2s;
      }
      .chat-control-btn:hover {
        background: rgba(0, 229, 255, 0.1);
        border-color: rgba(0, 229, 255, 0.3);
        color: var(--accent-primary);
      }
    `;
    document.head.appendChild(style);

    // 插入到输入框之前
    const inputContainer = chatPanel.querySelector('.chat-input-container');
    if (inputContainer) {
      inputContainer.parentNode.insertBefore(controlsBar, inputContainer);
    }

    // 绑定事件
    $('clear-chat-btn')?.addEventListener('click', clearChat);
    $('export-chat-btn')?.addEventListener('click', exportChat);
  }

  /**
   * 清空对话
   */
  function clearChat() {
    const chatOutput = ChatUI.getOutput();
    if (!chatOutput) return;

    if (chatOutput.children.length > 0) {
      if (!confirm('确定要清空所有对话吗？')) return;
    }

    chatOutput.innerHTML = '';
    clearDraft();
    
    // 清空服务端历史
    if (window.AppState?.aiService) {
      window.AppState.aiService.clearHistory();
    }

    showToast('对话已清空');
  }

  /**
   * 导出对话
   */
  function exportChat() {
    const chatOutput = ChatUI.getOutput();
    if (!chatOutput) return;

    const messages = [];
    chatOutput.querySelectorAll('.chat-message').forEach(msg => {
      const isUser = msg.classList.contains('user');
      const text = msg.textContent.trim();
      messages.push({
        role: isUser ? 'user' : 'assistant',
        content: text
      });
    });

    if (messages.length === 0) {
      showToast('没有可导出的对话');
      return;
    }

    // 生成 Markdown 格式
    const markdown = messages.map(msg => {
      const prefix = msg.role === 'user' ? '**用户**' : '**AI**';
      return `${prefix}: ${msg.content}`;
    }).join('\n\n---\n\n');

    // 创建下载
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('对话已导出');
  }

  // ==================== 公共 API ====================

  /**
   * 为消息添加操作按钮
   * @param {HTMLElement} messageEl - 消息元素
   * @param {boolean} isAI - 是否为 AI 消息
   */
  function addMessageActions(messageEl, isAI = false) {
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'message-actions';
    
    // 复制按钮
    actionsDiv.innerHTML = `
      <button class="message-action-btn" data-action="copy" title="复制">
        <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2"/>
          <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
        </svg>
      </button>
    `;

    // AI 消息添加重新生成按钮
    if (isAI) {
      actionsDiv.innerHTML += `
        <button class="message-action-btn" data-action="regenerate" title="重新生成">
          <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 4v6h6M23 20v-6h-6"/>
            <path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 013.51 15"/>
          </svg>
        </button>
      `;
    }

    messageEl.appendChild(actionsDiv);
  }

  // ==================== 导出 ====================
  window.ChatFeatures = {
    init,
    showStopButton,
    hideStopButton,
    addMessageActions,
    clearDraft,
    showToast,
    stopGeneration
  };

})();