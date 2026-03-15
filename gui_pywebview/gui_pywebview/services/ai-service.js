/**
 * AIService - AI 对话服务模块
 * 封装 AI 聊天相关业务逻辑
 */

class AIService {
  constructor(apiClient, eventBus) {
    this.apiClient = apiClient;
    this.eventBus = eventBus;
    this.history = [];
    this.ragEnabled = false;
    this.isProcessing = false;
    this.useStreaming = true;
    this.currentProvider = 'ollama';
    this.customSystemPrompt = '';
  }

  /**
   * 设置当前使用的 provider
   * @param {string} provider - 'ollama' 或 'gguf'
   */
  setProvider(provider) {
    this.currentProvider = provider === 'gguf' ? 'gguf' : 'ollama';
    console.log('[AIService] Provider set to:', this.currentProvider);
  }

  /**
   * 设置自定义系统提示词
   * @param {string} prompt - 系统提示词，空字符串表示使用默认
   */
  setSystemPrompt(prompt) {
    this.customSystemPrompt = prompt || '';
    console.log('[AIService] System prompt:', prompt ? 'custom' : 'default');
  }

  /**
   * 发送消息（非流式）
   * @param {string} text - 用户消息
   * @returns {Promise<string>} AI 回复
   */
  async sendMessage(text) {
    if (!text.trim() || this.isProcessing) {
      return null;
    }

    this.isProcessing = true;

    // 添加用户消息到历史
    const userMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };
    this.history.push(userMessage);

    // 发送事件：消息已发送
    this.eventBus.emit(Events.AI_MESSAGE_SENT, { message: userMessage });

    try {
      const payload = {
        message: text,
        rag: this.ragEnabled
      };
      if (this.customSystemPrompt) {
        payload.system_prompt = this.customSystemPrompt;
      }
      const response = await this.apiClient.post('/chat', payload);

      // 添加 AI 回复到历史
      const aiMessage = {
        role: 'assistant',
        content: response.response || response.message,
        timestamp: new Date().toISOString(),
        model: response.model,
        rag_used: response.rag_used || false
      };
      this.history.push(aiMessage);

      // 发送事件：收到回复
      this.eventBus.emit(Events.AI_RESPONSE_RECEIVED, {
        message: aiMessage,
        fullResponse: response
      });

      return aiMessage.content;
    } catch (error) {
      // 发送错误事件
      this.eventBus.emit(Events.AI_ERROR, {
        error: error.message,
        originalMessage: text
      });
      throw error;
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * 流式发送消息
   * @param {string} text - 用户消息
   * @param {Function} onChunk - 流式回调 (content: string, isDone: boolean) => void
   * @returns {Promise<string>} 完整回复
   */
  async sendMessageStream(text, onChunk) {
    if (!text.trim() || this.isProcessing) {
      return null;
    }

    this.isProcessing = true;

    const userMessage = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };
    this.history.push(userMessage);
    this.eventBus.emit(Events.AI_MESSAGE_SENT, { message: userMessage });

    let fullResponse = '';
    const ragUsed = false;

    // 统一使用 /api/chat/stream，后端会根据 current_provider 自动选择后端

    try {
      const streamPayload = {
        message: text,
        rag: this.ragEnabled,
        stream: true
      };
      if (this.customSystemPrompt) {
        streamPayload.system_prompt = this.customSystemPrompt;
      }
      const response = await fetch(`${this.apiClient.baseURL}/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(streamPayload)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            if (dataStr === '[DONE]') {
              // 完成
              const aiMessage = {
                role: 'assistant',
                content: fullResponse,
                timestamp: new Date().toISOString(),
                rag_used: ragUsed
              };
              this.history.push(aiMessage);

              this.eventBus.emit(Events.AI_RESPONSE_RECEIVED, {
                message: aiMessage
              });

              if (onChunk) {
                onChunk(fullResponse, true);
              }

              this.isProcessing = false;
              return fullResponse;
            }

            try {
              const data = JSON.parse(dataStr);

              if (data.error) {
                throw new Error(data.error);
              }

              if (data.content) {
                fullResponse += data.content;

                if (onChunk) {
                  onChunk(fullResponse, false);
                }

                this.eventBus.emit(Events.AI_STREAMING, {
                  content: data.content,
                  fullResponse
                });
              }
            } catch (e) {
              console.error('Parse chunk error:', e);
            }
          }
        }
      }
    } catch (error) {
      this.eventBus.emit(Events.AI_ERROR, {
        error: error.message,
        originalMessage: text
      });
      this.isProcessing = false;
      throw error;
    }
  }

  /**
   * 获取对话历史
   * @returns {Array}
   */
  getHistory() {
    return [...this.history];
  }

  /**
   * 清空对话历史
   */
  async clearHistory() {
    try {
      await this.apiClient.clearHistory();
      this.history = [];
      this.eventBus.emit(Events.HISTORY_CLEARED);
      return true;
    } catch (error) {
      this.eventBus.emit(Events.AI_ERROR, { error: error.message });
      throw error;
    }
  }

  /**
   * 切换 RAG 开关
   * @param {boolean} enabled - 是否启用
   */
  async toggleRAG(enabled) {
    this.ragEnabled = enabled;

    try {
      await this.apiClient.toggleRAG(enabled);

      if (enabled) {
        this.eventBus.emit(Events.RAG_ENABLED);
      } else {
        this.eventBus.emit(Events.RAG_DISABLED);
      }
    } catch (error) {
      // 回滚状态
      this.ragEnabled = !enabled;
      this.eventBus.emit(Events.RAG_ERROR, { error: error.message });
      throw error;
    }
  }

  /**
   * 获取 RAG 状态
   * @returns {boolean}
   */
  isRAGEnabled() {
    return this.ragEnabled;
  }

  /**
   * 检查 RAG 是否可用
   * @returns {Promise<boolean>}
   */
  async checkRAGAvailable() {
    try {
      const status = await this.apiClient.getRAGStatus();
      return status.available || false;
    } catch (error) {
      return false;
    }
  }

  /**
   * 搜索知识库
   * @param {string} query - 查询内容
   * @returns {Promise<Array>}
   */
  async searchKnowledge(query) {
    try {
      const results = await this.apiClient.searchKnowledge(query);
      this.eventBus.emit(Events.RAG_RESULT, { results });
      return results;
    } catch (error) {
      this.eventBus.emit(Events.RAG_ERROR, { error: error.message });
      throw error;
    }
  }

  /**
   * 获取服务状态
   * @returns {object}
   */
  getStatus() {
    return {
      isProcessing: this.isProcessing,
      ragEnabled: this.ragEnabled,
      historyLength: this.history.length,
      useStreaming: this.useStreaming
    };
  }

  /**
   * 切换流式模式
   * @param {boolean} enabled
   */
  setStreaming(enabled) {
    this.useStreaming = enabled;
  }

  /**
   * 加载历史记录
   * @param {Array} history
   */
  loadHistory(history) {
    this.history = history || [];
  }

  /**
   * 重新加载历史记录（从服务器）
   */
  async reloadHistory() {
    try {
      const data = await this.apiClient.getHistory();
      if (data.history) {
        this.history = data.history;
        this.eventBus.emit(Events.HISTORY_LOADED, { history: this.history });
      }
      return this.history;
    } catch (error) {
      this.eventBus.emit(Events.AI_ERROR, { error: error.message });
      throw error;
    }
  }
}

// 导出
window.AIService = AIService;
