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
  let lastFailedMessage = null; // 用于重试

  /**
   * 初始化聊天处理器
   * @param {Object} service - AIService 实例
   */
  function init(service) {
    aiService = service;
    setupEventListeners();
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
   * 分类聊天错误
   * @param {Error} error - 错误对象
   * @returns {Object} 错误信息对象
   */
  function classifyChatError(error) {
    const message = error.message || String(error);
    let type = 'unknown';
    let friendlyMessage = '发生未知错误';
    let retryable = false;
    let suggestion = '';

    // 网络错误
    if (message.includes('fetch') || message.includes('network') || message.includes('Failed to fetch')) {
      type = 'network';
      friendlyMessage = '网络连接失败';
      retryable = true;
      suggestion = '请检查网络连接后重试';
    }
    // HTTP 错误
    else if (message.includes('HTTP') || message.includes('status')) {
      const statusMatch = message.match(/HTTP (\d+)/);
      const status = statusMatch ? parseInt(statusMatch[1]) : 0;
      type = 'api';
      retryable = status >= 500 || status === 429; // 服务器错误或限流可重试
      
      if (status === 503) {
        friendlyMessage = '服务暂时不可用';
        suggestion = '模型可能未加载，请检查模型状态';
      } else if (status === 429) {
        friendlyMessage = '请求过于频繁';
        suggestion = '请稍后再试';
      } else if (status === 401 || status === 403) {
        friendlyMessage = '认证失败';
        suggestion = '请检查 API Key 配置';
      } else {
        friendlyMessage = `服务器错误 (${status})`;
        suggestion = '请稍后重试';
      }
    }
    // 超时错误
    else if (message.includes('timeout') || message.includes('超时')) {
      type = 'timeout';
      friendlyMessage = '响应超时';
      retryable = true;
      suggestion = '生成时间过长，可以重试或使用更小的模型';
    }
    // 模型错误
    else if (message.includes('model') || message.includes('GGUF') || message.includes('not loaded')) {
      type = 'model';
      friendlyMessage = '模型未就绪';
      retryable = false;
      suggestion = '请先加载模型或切换到其他模型';
    }
    // 其他错误
    else {
      type = 'unknown';
      friendlyMessage = '生成失败';
      retryable = true;
      suggestion = '请稍后重试';
    }

    return {
      type,
      message: friendlyMessage,
      detail: message,
      retryable,
      suggestion,
      originalError: error
    };
  }

  /**
   * 发送消息
   */
  async function sendMessage(textToSend = null) {
    const chatInput = ChatUI.getInput();
    const text = textToSend || chatInput?.value.trim();

    if (!text || !booted || !aiService || isGenerating) return;

    // 保存最后发送的消息用于重试
    lastFailedMessage = null;

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

    // 隐藏命令面板
    if (window.ChatFeatures && window.ChatFeatures.hideCommandPalette) {
      window.ChatFeatures.hideCommandPalette();
    }

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
          // 流式完成，渲染最终内容（保留 meta 区）
          ChatUI.renderAIMessageBody(aiMessageEl, content);
          
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

            // 更新进度（基于内容长度估算，假设平均每个字符约0.3个token，目标约500-1000 tokens）
            const estimatedTokens = fullContent.length * 0.3;
            const targetTokens = 800; // 假设目标响应长度
            const progress = Math.min(0.95, estimatedTokens / targetTokens);
            ChatUI.showPulseResponding(progress);
          }
        }
      });

    } catch (error) {
      if (error.name === 'AbortError') {
        ChatUI.addSystemMessage('⏹️ 生成已停止');
      } else {
        // 保存失败的消息用于重试
        lastFailedMessage = text;
        // 分类错误并显示友好提示
        const errorInfo = classifyChatError(error);
        ChatUI.addErrorMessage(errorInfo, () => {
          // 重试回调
          if (lastFailedMessage) {
            sendMessage(lastFailedMessage);
          }
        });
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

  /**
   * 重试最后失败的消息
   */
  function retryLastMessage() {
    if (lastFailedMessage && !isGenerating) {
      sendMessage(lastFailedMessage);
    }
  }

  // ==================== 导出 ====================
  window.ChatHandler = {
    init,
    setBooted,
    sendMessage,
    stopGeneration,
    isCurrentlyGenerating,
    retryLastMessage
  };

})();