// 工具台服务
import api from './api';

/**
 * 导入几何文件
 * @param {File} file - 几何文件
 */
export const importGeometry = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/cae/import', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

/**
 * 生成网格
 * @param {Object} params - 网格参数
 */
export const generateMesh = (params) => 
  api.post('/cae/mesh', params);

/**
 * 运行求解器
 * @param {Object} config - 求解配置
 */
export const runSolver = (config) => 
  api.post('/cae/solve', config);

/**
 * 获取计算结果
 * @param {string} jobId - 任务ID
 */
export const getResults = (jobId) => 
  api.get(`/cae/results/${jobId}`);

/**
 * 连接WebSocket获取实时进度
 * @param {Function} onProgress - 进度回调
 * @param {Function} onLog - 日志回调
 */
export const connectProgressWS = (onProgress, onLog) => {
  const ws = new WebSocket('ws://localhost:8000/ws/cae/progress');
  
  ws.onopen = () => {
    console.log('WebSocket connected');
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'progress') {
      onProgress(data.value);
    } else if (data.type === 'log') {
      onLog(data.message);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };
  
  ws.onclose = () => {
    console.log('WebSocket disconnected');
  };
  
  return ws;
};
