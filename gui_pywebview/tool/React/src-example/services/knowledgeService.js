// 知识库服务
import api from './api';

/**
 * 搜索知识库
 * @param {string} query - 搜索查询
 * @param {number} topK - 返回结果数量
 */
export const searchDocuments = (query, topK = 5) => 
  api.post('/knowledge/search', { query, top_k: topK });

/**
 * 获取所有文档
 */
export const getDocuments = () => api.get('/knowledge/documents');

/**
 * 添加文档
 * @param {File} file - 文件对象
 */
export const addDocument = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/knowledge/documents', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

/**
 * 删除文档
 * @param {string} docId - 文档ID
 */
export const deleteDocument = (docId) => 
  api.delete(`/knowledge/documents/${docId}`);

/**
 * 获取索引进度
 */
export const getIndexStatus = () => api.get('/knowledge/index-status');
