// 知识库 Hook
import { useState, useEffect, useCallback } from 'react';
import {
  searchDocuments,
  getDocuments,
  addDocument,
  deleteDocument,
  getIndexStatus,
} from '../services/knowledgeService';

export const useKnowledge = () => {
  const [documents, setDocuments] = useState([]);
  const [searchResults, setSearchResults] = useState(null);
  const [indexProgress, setIndexProgress] = useState({
    progress: 0,
    status: 'idle',
    speed: '0 MB/s',
  });
  const [isLoading, setIsLoading] = useState(false);

  // 初始加载文档列表
  useEffect(() => {
    loadDocuments();
    const interval = setInterval(checkIndexStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  /**
   * 加载文档列表
   */
  const loadDocuments = async () => {
    try {
      const data = await getDocuments();
      setDocuments(data.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
    }
  };

  /**
   * 检查索引状态
   */
  const checkIndexStatus = async () => {
    try {
      const status = await getIndexStatus();
      setIndexProgress(status);
    } catch (error) {
      console.error('Failed to get index status:', error);
    }
  };

  /**
   * 搜索文档
   * @param {string} query - 搜索关键词
   */
  const search = useCallback(async (query) => {
    if (!query.trim()) {
      setSearchResults(null);
      return;
    }

    setIsLoading(true);
    try {
      const results = await searchDocuments(query);
      setSearchResults(results.documents || []);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * 添加文档
   * @param {File} file - 文件对象
   */
  const addDoc = useCallback(async (file) => {
    try {
      await addDocument(file);
      await loadDocuments(); // 重新加载列表
      return true;
    } catch (error) {
      console.error('Add document error:', error);
      return false;
    }
  }, []);

  /**
   * 删除文档
   * @param {string} docId - 文档ID
   */
  const removeDoc = useCallback(async (docId) => {
    try {
      await deleteDocument(docId);
      setDocuments(prev => prev.filter(d => d.id !== docId));
      return true;
    } catch (error) {
      console.error('Delete document error:', error);
      return false;
    }
  }, []);

  return {
    documents,
    searchResults,
    indexProgress,
    isLoading,
    search,
    addDoc,
    removeDoc,
    refresh: loadDocuments,
  };
};
