/**
 * KnowledgeUI - 知识库模块
 * 冷锻工业全息风格 - 处理知识库搜索、结果展示等功能
 */

(function () {
  'use strict';

  const { $, escapeHtml } = Utils;

  // ==================== DOM 元素 ====================
  let searchInput = null;
  let searchBtn = null;
  let searchResults = null;
  let knowledgeTags = null;

  // ==================== 状态 ====================
  let aiService = null;
  let currentFilter = 'all';
  let searchHistory = [];

  // ==================== 模拟数据 ====================
  const mockResults = [
    {
      title: 'Hydraulic System Failure Analysis',
      type: 'critical',
      content: 'Critical failure in main hydraulic pump due to contamination. Immediate maintenance required to prevent catastrophic system failure.',
      score: 0.95,
      source: 'Maintenance Log #2847',
      date: '2024-03-08',
      tags: ['hydraulic', 'critical', 'pump']
    },
    {
      title: 'CNC Machine Calibration Procedure',
      type: 'manual',
      content: 'Standard calibration procedure for 5-axis CNC machining centers. Includes spindle alignment and tool offset verification.',
      score: 0.88,
      source: 'Technical Manual v3.2',
      date: '2024-02-15',
      tags: ['cnc', 'calibration', 'procedure']
    },
    {
      title: 'Bearing Temperature Warning Threshold',
      type: 'warning',
      content: 'Main drive bearing temperature exceeded warning threshold (75°C). Recommend inspection of lubrication system.',
      score: 0.82,
      source: 'Sensor Alert #1523',
      date: '2024-03-09',
      tags: ['bearing', 'temperature', 'warning']
    },
    {
      title: 'Gearbox Specification Sheet',
      type: 'spec',
      content: 'Technical specifications for industrial gearbox model IG-4500. Includes torque ratings, efficiency curves, and maintenance intervals.',
      score: 0.79,
      source: 'Spec Sheet IG-4500',
      date: '2024-01-20',
      tags: ['gearbox', 'specification', 'torque']
    },
    {
      title: 'Welding Robot Path Optimization',
      type: 'case',
      content: 'Case study on optimizing welding robot paths for automotive chassis assembly. Reduced cycle time by 15%.',
      score: 0.76,
      source: 'Case Study #89',
      date: '2024-02-28',
      tags: ['welding', 'robot', 'optimization']
    },
    {
      title: 'Preventive Maintenance Schedule',
      type: 'manual',
      content: 'Quarterly preventive maintenance schedule for forging press equipment. Includes inspection checklists and part replacement intervals.',
      score: 0.72,
      source: 'PM Schedule Q1 2024',
      date: '2024-01-05',
      tags: ['maintenance', 'schedule', 'forging']
    }
  ];

  /**
   * 初始化知识库模块
   * @param {Object} service - AIService 实例
   */
  function init(service) {
    aiService = service;

    searchInput = $('knowledge-search');
    searchBtn = $('search-btn');
    searchResults = $('search-results');
    knowledgeTags = $('knowledge-tags');

    setupEventListeners();
    setupTagFilters();
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
   * 设置标签过滤器
   */
  function setupTagFilters() {
    if (!knowledgeTags) return;

    const tags = knowledgeTags.querySelectorAll('.knowledge-tag');
    tags.forEach(tag => {
      tag.addEventListener('click', () => {
        // 移除所有 active 状态
        tags.forEach(t => t.classList.remove('active'));
        // 添加当前 active
        tag.classList.add('active');
        // 更新过滤器
        currentFilter = tag.dataset.filter;
        // 如果有搜索内容，重新搜索
        if (searchInput?.value.trim()) {
          performSearch();
        }
      });
    });
  }

  /**
   * 执行搜索
   */
  async function performSearch() {
    const query = searchInput?.value.trim();
    if (!query) return;

    showLoading();
    searchHistory.unshift(query);
    if (searchHistory.length > 10) searchHistory.pop();

    // 模拟搜索延迟
    await new Promise(resolve => setTimeout(resolve, 800));

    try {
      // 过滤结果
      let results = filterResults(mockResults, query, currentFilter);
      displayResults(results);
    } catch (error) {
      showError(error.message);
    }
  }

  /**
   * 过滤结果
   * @param {Array} results - 原始结果
   * @param {string} query - 搜索词
   * @param {string} filter - 过滤器类型
   */
  function filterResults(results, query, filter) {
    let filtered = results.filter(r => {
      const matchQuery = !query || 
        r.title.toLowerCase().includes(query.toLowerCase()) ||
        r.content.toLowerCase().includes(query.toLowerCase()) ||
        r.tags.some(t => t.toLowerCase().includes(query.toLowerCase()));
      
      const matchFilter = filter === 'all' || r.type === filter;
      
      return matchQuery && matchFilter;
    });

    // 按分数排序
    return filtered.sort((a, b) => b.score - a.score);
  }

  /**
   * 显示加载状态 - 工业风格
   */
  function showLoading() {
    if (searchResults) {
      searchResults.innerHTML = `
        <div class="industrial-loader">
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
          <div class="bar"></div>
        </div>
        <div style="text-align: center; color: var(--ind-text-dim); font-size: 12px; letter-spacing: 2px;">
          RETRIEVING DATA...
        </div>
      `;
    }
  }

  /**
   * 显示错误
   * @param {string} message - 错误信息
   */
  function showError(message) {
    if (searchResults) {
      searchResults.innerHTML = `
        <div class="result-placeholder">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#ff4757" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <p style="color: var(--ind-alert);">SYSTEM ERROR</p>
          <span style="font-size: 11px; color: var(--ind-text-dim);">${escapeHtml(message)}</span>
        </div>
      `;
    }
  }

  /**
   * 获取类型标签样式
   * @param {string} type - 类型
   */
  function getTypeBadge(type) {
    const badges = {
      critical: { text: 'CRITICAL', class: 'critical' },
      warning: { text: 'WARNING', class: 'warning' },
      manual: { text: 'MANUAL', class: '' },
      spec: { text: 'SPEC', class: '' },
      case: { text: 'CASE', class: '' }
    };
    const badge = badges[type] || { text: type.toUpperCase(), class: '' };
    return `<span class="result-type ${badge.class}">${badge.text}</span>`;
  }

  /**
   * 显示搜索结果 - 工业风格
   * @param {Array} results - 结果数组
   */
  function displayResults(results) {
    if (!searchResults) return;

    if (!results || results.length === 0) {
      searchResults.innerHTML = `
        <div class="result-placeholder">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1">
            <circle cx="11" cy="11" r="8"/>
            <path d="M21 21l-4.35-4.35"/>
          </svg>
          <p>NO DATA FOUND</p>
          <span style="font-size: 11px; color: var(--ind-text-dim);">Try adjusting your search terms or filters</span>
        </div>
      `;
      return;
    }

    searchResults.innerHTML = results.map((result, index) => `
      <div class="result-item ${result.type}" style="animation: slideIn 0.3s ease-out ${index * 0.05}s both;">
        <div class="result-title">
          ${getTypeBadge(result.type)}
          ${escapeHtml(result.title)}
        </div>
        <div class="result-snippet">${escapeHtml(result.content)}</div>
        <div class="result-meta">
          <span>RELEVANCE: ${(result.score * 100).toFixed(0)}%</span>
          <span>SRC: ${escapeHtml(result.source)}</span>
          <span>DATE: ${result.date}</span>
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
