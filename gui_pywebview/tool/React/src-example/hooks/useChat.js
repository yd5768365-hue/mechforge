// AI 聊天 Hook
import { useState, useCallback, useRef } from 'react';
import { sendMessageStream } from '../services/aiService';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef(null);

  /**
   * 发送消息
   * @param {string} content - 消息内容
   */
  const sendMessage = useCallback(async (content) => {
    if (!content.trim() || isStreaming) return;

    // 添加用户消息
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content,
      timestamp: new Date().toISOString(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setIsStreaming(true);

    // 准备AI消息占位
    const aiMessageId = Date.now() + 1;
    setMessages(prev => [...prev, {
      id: aiMessageId,
      type: 'assistant',
      content: '',
      timestamp: new Date().toISOString(),
    }]);

    try {
      // 获取历史记录（最近10条）
      const history = messages.slice(-10).map(m => ({
        role: m.type === 'user' ? 'user' : 'assistant',
        content: m.content,
      }));

      // 流式接收响应
      await sendMessageStream(content, history, (chunk) => {
        setMessages(prev => 
          prev.map(msg => 
            msg.id === aiMessageId 
              ? { ...msg, content: msg.content + chunk }
              : msg
          )
        );
      });
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => 
        prev.map(msg => 
          msg.id === aiMessageId 
            ? { ...msg, content: '抱歉，发生了错误，请稍后重试。' }
            : msg
        )
      );
    } finally {
      setIsStreaming(false);
    }
  }, [messages, isStreaming]);

  /**
   * 清空对话
   */
  const clearChat = useCallback(() => {
    setMessages([]);
  }, []);

  /**
   * 停止生成
   */
  const stopGeneration = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  }, []);

  return {
    messages,
    isStreaming,
    sendMessage,
    clearChat,
    stopGeneration,
  };
};
