/**
 * KnowledgeUI - 知识库模块
 * 处理知识库搜索、结果展示等功能
 */

(function () {
  'use strict';

  const { $, escapeHtml } = Utils;

  // ==================== DOM 元素 ====================
  let searchInput = null;
  let searchBtn = null;
  let searchResults = null;

  // ==================== 服务 ====================
  let aiService = null;

  /**
   * 初始化知识库模块
   * @param {Object} service - AIService 实例
   */
  function init(service) {
    aiService = service;

    searchInput = $('knowledge-search');
    searchBtn = $('search-btn');
    searchResults = $('search-results');

    setupEventListeners();
  }

  /**
   * 设置事件监听器
   */
  function setupEventListeners() {
    searchInput?.addEventListener('keypress', e => {
      if (e.key === 'Enter') performSearch();
    });

    searchBtn?.addEventListener('click', performSearch);
  }

  /**
   * 执行搜索
   */
  async function performSearch() {
    const query = searchInput?.value.trim();
    if (!query || !aiService) return;

    showLoading();

    try {
      const raw = await aiService.searchKnowledge(query);
      // 处理返回格式：可能是数组或 {results: [...]}
      const results = Array.isArray(raw) ? raw : (raw?.results ?? []);
      displayResults(results);
    } catch (error) {
      showError(error.message);
    }
  }

  /**
   * 显示加载状态
   */
  function showLoading() {
    if (searchResults) {
      searchResults.innerHTML = '<div class="result-placeholder">Searching...</div>';
    }
  }

  /**
   * 显示错误
   * @param {string} message - 错误信息
   */
  function showError(message) {
    if (searchResults) {
      searchResults.innerHTML = `<div class="result-placeholder">Error: ${escapeHtml(message)}</div>`;
    }
  }

  /**
   * 显示搜索结果
   * @param {Array} results - 结果数组
   */
  function displayResults(results) {
    if (!searchResults) return;

    if (!results || results.length === 0) {
      searchResults.innerHTML = '<div class="result-placeholder">No results found</div>';
      return;
    }

    searchResults.innerHTML = results.map((result, index) => `
      <div class="result-item">
        <div class="result-title">${escapeHtml(result.title || `Result ${index + 1}`)}</div>
        <div class="result-snippet">${escapeHtml(result.content || result.snippet || '')}</div>
        <div class="result-meta">
          <span>Score: ${(result.score || 0).toFixed(2)}</span>
          ${result.source ? `<span>Source: ${escapeHtml(result.source)}</span>` : ''}
        </div>
      </div>
    `).join('');
  }

  // ==================== 导出 ====================
  window.KnowledgeUI = {
    init,
    performSearch
  };

})();