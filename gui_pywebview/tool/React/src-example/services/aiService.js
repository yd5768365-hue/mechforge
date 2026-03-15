// AI 对话服务
import api from './api';

/**
 * 发送消息并获取流式响应
 * @param {string} message - 用户消息
 * @param {Array} history - 对话历史
 * @param {Function} onChunk - 处理每个数据块的回调
 */
export const sendMessageStream = async (message, history, onChunk) => {
  try {
    const response = await fetch('http://localhost:8000/api/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, history }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      
      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  } catch (error) {
    console.error('Stream error:', error);
    throw error;
  }
};

/**
 * 获取可用模型列表
 */
export const getModels = () => api.get('/models');

/**
 * 切换当前模型
 * @param {string} modelId - 模型ID
 */
export const switchModel = (modelId) => api.post('/models/switch', { model_id: modelId });

/**
 * 获取AI状态
 */
export const getAIStatus = () => api.get('/status');
