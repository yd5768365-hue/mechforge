/**
 * ChatHandler - 聊天逻辑处理模块
 * 处理消息发送、流式输出、与 AI Service 交互
 */

(function () {
  'use strict';

  const { $ } = Utils;

  // ==================== 状态 ====================
  let booted = false;
  let aiService = null;
  let isGenerating = false;
  let currentReader = null;

  /**
   * 初始化聊天处理器
   * @param {Object} service - AIService 实例
   */
  function init(service) {
    aiService = service;
    setupEventListeners();
    
    // 初始化聊天增强功能
    if (window.ChatFeatures) {
      ChatFeatures.init();
    }
  }

  /**
   * 设置启动完成状态
   * @param {boolean} status - 是否完成
   */
  function setBooted(status) {
    booted = status;
  }

  /**
   * 设置事件监听器
   */
  function setupEventListeners() {
    const chatInput = ChatUI.getInput();
    const sendBtn = ChatUI.getSendBtn();

    // Enter 发送，Shift+Enter 换行
    chatInput?.addEventListener('keydown', e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    sendBtn?.addEventListener('click', sendMessage);
  }

  /**
   * 发送消息
   */
  async function sendMessage() {
    const chatInput = ChatUI.getInput();
    const text = chatInput?.value.trim();

    if (!text || !booted || !aiService || isGenerating) return;

    // 设置生成状态
    isGenerating = true;
    
    // 禁用输入
    ChatUI.setInputDisabled(true);

    // 显示停止按钮
    if (window.ChatFeatures) {
      ChatFeatures.showStopButton();
    }

    // 启动共鸣效果
    Mascot.startResonance();
    ChatUI.showPulseThinking();

    // 创建发送爆发效果
    const sendBtn = ChatUI.getSendBtn();
    if (sendBtn) {
      const rect = sendBtn.getBoundingClientRect();
      Particles.createSendBurst(rect.left + rect.width / 2, rect.top + rect.height / 2);
    }

    // 添加用户消息
    const time = ChatUI.getTimestamp();
    ChatUI.addUserMessage(text, time);
    ChatUI.clearInput();

    // 清除草稿
    if (window.ChatFeatures) {
      ChatFeatures.clearDraft();
    }

    try {
      let aiMessageEl = null;
      let fullContent = '';

      // 使用 AbortController 支持取消
      const abortController = new AbortController();
      currentReader = abortController;

      await aiService.sendMessageStream(text, (content, isDone) => {
        if (abortController.signal.aborted) return;

        if (!aiMessageEl) {
          ChatUI.showPulseResponding(0);
          aiMessageEl = ChatUI.createAIMessageContainer();
        }

        if (isDone) {
          // 流式完成，渲染最终内容
          if (window.Markdown) {
            aiMessageEl.innerHTML = Markdown.render(content);
          }
          
          // 添加操作按钮
          if (window.ChatFeatures) {
            ChatFeatures.addMessageActions(aiMessageEl, true);
          }
        } else {
          // 流式更新中
          const newContent = content.slice(fullContent.length);
          if (newContent) {
            ChatUI.appendToAIMessage(aiMessageEl, newContent);
            fullContent = content;

            // 更新鲸鱼语音
            Mascot.updateWhaleSpeech(content);

            // 更新进度
            ChatUI.showPulseResponding(fullContent.length / 100);
          }
        }
      });

    } catch (error) {
      if (error.name === 'AbortError') {
        ChatUI.addSystemMessage('⏹️ 生成已停止');
      } else {
        ChatUI.addSystemMessage(`Error: ${error.message}`);
      }
    } finally {
      // 重置状态
      isGenerating = false;
      currentReader = null;

      // 停止共鸣效果
      Mascot.stopResonance();
      ChatUI.hidePulseIndicator();

      // 隐藏停止按钮
      if (window.ChatFeatures) {
        ChatFeatures.hideStopButton();
      }

      // 恢复输入
      ChatUI.setInputDisabled(false);
      ChatUI.focusInput();
    }
  }

  /**
   * 停止生成
   */
  function stopGeneration() {
    if (currentReader) {
      currentReader.abort();
      currentReader = null;
    }
    isGenerating = false;
  }

  /**
   * 检查是否正在生成
   * @returns {boolean}
   */
  function isCurrentlyGenerating() {
    return isGenerating;
  }

  // ==================== 导出 ====================
  window.ChatHandler = {
    init,
    setBooted,
    sendMessage,
    stopGeneration,
    isCurrentlyGenerating
  };

})();