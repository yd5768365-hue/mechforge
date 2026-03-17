/**
 * Experience Panel - 经验库界面模块
 * 处理经验库面板的交互、内容展示
 * 完全独立：不依赖 index.html 的 CSS
 */

(function() {
  'use strict';

  // ==================== 加载自己的 CSS ====================
  (function() {
    const cssFiles = ['css/experience.css', 'css/industrial-theme.css'];
    cssFiles.forEach(cssFile => {
      if (!document.querySelector(`link[href="${cssFile}"]`)) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = cssFile;
        document.head.appendChild(link);
      }
    });
  })();

  // ==================== HTML 内容 ====================
  const EXPERIENCE_PANEL_HTML = `
<!-- Experience Library Panel -->
<div class="tab-panel" id="experience-panel">
  <!-- 工业风背景 -->
  <div class="industrial-background"></div>

  <!-- 面板头部 -->
  <div class="panel-header">
    <span class="header-mark">锻造</span>
    <h2>经验库</h2>
    <p>机械工程故障案例与解决方案</p>
    <span class="archive-id">MECHFORGE-EXP-V3.0</span>
  </div>

  <!-- 搜索容器 -->
  <div class="exp-search-section">
    <div class="search-wrapper">
      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/>
        <path d="M21 21l-4.35-4.35"/>
      </svg>
      <input type="text" id="exp-search-input" placeholder="搜索故障案例、标签或关键词...">
      <span id="exp-count-badge" class="exp-count-badge">12</span>
    </div>
  </div>

  <!-- Daily Feed 区域 -->
  <div id="daily-feed-section">
    <div class="df-embedded-header">
      <div>
        <div class="df-embedded-title">◈ DAILY KNOWLEDGE FEED</div>
        <div class="df-embedded-date" id="df-embedded-date">── 未生成 ──</div>
      </div>
    </div>
    <div id="df-history-selector" class="df-history-selector"></div>
    <div class="df-embedded-content" id="df-embedded-content">
      <div class="df-embedded-empty" id="df-embedded-empty">
        <div class="df-embedded-empty-icon">📡</div>
        <div class="df-embedded-empty-text">每日机械工程知识推送</div>
        <button class="df-generate-btn" id="df-generate-btn">
          <span class="btn-icon">⚡</span>
          <span class="btn-text">生成今日推送</span>
        </button>
        <div class="df-generate-hint">自动使用当前 AI 模型生成 3 条机械工程知识</div>
      </div>
      <div class="df-embedded-list" id="df-embedded-list" style="display:none;"></div>
      <div class="df-embedded-actions" id="df-actions-bar" style="display:none;">
        <button class="df-embedded-btn primary" id="df-refresh-btn">⟳ 重新生成</button>
        <button class="df-embedded-btn history" id="df-history-btn">📅 历史</button>
      </div>
    </div>
  </div>

  <!-- 标签过滤 -->
  <div class="exp-tags-container" id="exp-tags-container"></div>

  <!-- 经验卡片网格 -->
  <div class="search-results" id="exp-results">
    <div class="result-placeholder">
      <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="currentColor" stroke-width="1">
        <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
      </svg>
      <p>加载中...</p>
    </div>
  </div>

  <!-- 详情弹窗 -->
  <div class="exp-modal-overlay" id="exp-modal-overlay">
    <div class="exp-modal-container" id="exp-modal">
      <button class="exp-modal-close" id="exp-modal-close">&times;</button>
      <div class="exp-modal-header">
        <div class="exp-modal-tags" id="exp-modal-tags"></div>
        <h2 class="exp-modal-title" id="exp-modal-title"></h2>
        <div class="exp-modal-meta" id="exp-modal-meta"></div>
      </div>
      <div class="exp-modal-body">
        <div class="exp-modal-section">
          <h3>故障条件</h3>
          <p id="exp-modal-condition"></p>
        </div>
        <div class="exp-modal-section">
          <h3>原因分析</h3>
          <p id="exp-modal-cause"></p>
        </div>
        <div class="exp-modal-section">
          <h3>解决方案</h3>
          <pre id="exp-modal-solution"></pre>
        </div>
      </div>
      <div class="exp-modal-footer">
        <span class="exp-modal-source" id="exp-modal-source"></span>
        <a href="#" class="exp-modal-link" id="exp-modal-link" target="_blank">查看来源 →</a>
      </div>
    </div>
  </div>
</div>
`;

  // 导出到全局
  window.ExperiencePanel = {
    init: initExperiencePanel,
    isInitialized: false,
    html: EXPERIENCE_PANEL_HTML
  };

  // DOM 元素
  let experiencePanel;
  let experienceGrid;

  // 状态
  let experiences = [];

  /**
   * 加载经验库面板 HTML
   */
  function loadHtml() {
    return new Promise((resolve) => {
      const placeholder = document.getElementById('experience-panel-placeholder');

      if (placeholder) {
        placeholder.outerHTML = EXPERIENCE_PANEL_HTML;
        console.log('[ExperiencePanel] HTML 已加载到页面');
      } else {
        const existingPanel = document.getElementById('experience-panel');
        if (!existingPanel) {
          // 查找 knowledge-panel 并在其后插入
          const knowledgePanel = document.getElementById('knowledge-panel');
          if (knowledgePanel) {
            knowledgePanel.insertAdjacentHTML('afterend', EXPERIENCE_PANEL_HTML);
          }
        }
      }

      resolve();
    });
  }

  /**
   * 初始化经验库面板
   */
  async function initExperiencePanel() {
    if (window.ExperiencePanel.isInitialized) {
      return;
    }

    console.log('[ExperiencePanel] 初始化经验库面板');

    // 加载 HTML
    await loadHtml();

    // 缓存 DOM 元素
    experiencePanel = document.getElementById('experience-panel');
    experienceGrid = document.getElementById('exp-results');

    if (!experiencePanel) return;

    bindEvents();
    loadExperiences();

    window.ExperiencePanel.isInitialized = true;
    console.log('[ExperiencePanel] 初始化完成');
  }

  // 保留原有 init 别名
  function init() {
    return initExperiencePanel();
  }

  // 立即执行
  loadHtml().then(() => {
    experiencePanel = document.getElementById('experience-panel');
    experienceGrid = document.getElementById('exp-results');

    if (experiencePanel) {
      bindEvents();
      loadExperiences();
      window.ExperiencePanel.isInitialized = true;
    }
  });

  /**
   * 绑定事件
   */
  function bindEvents() {
    // 经验卡片点击
    const expResults = document.getElementById('exp-results');
    expResults?.addEventListener('click', (e) => {
      const card = e.target.closest('.exp-card');
      if (card) {
        handleCardClick(card.dataset.id);
      }
    });
  }

  /**
   * 加载经验数据
   */
  async function loadExperiences() {
    try {
      const res = await fetch('/api/experience/list');
      experiences = await res.json();
      renderExperiences(experiences);
    } catch (err) {
      console.error('加载经验失败:', err);
      // 加载演示数据
      experiences = getDemoExperiences();
      renderExperiences(experiences);
    }
  }

  /**
   * 渲染经验卡片
   */
  function renderExperiences(data) {
    const container = document.getElementById('exp-results');
    if (!container) return;

    if (!data || data.length === 0) {
      container.innerHTML = '<div class="result-placeholder"><p>暂无经验数据</p></div>';
      return;
    }

    container.innerHTML = data.map(exp => createExperienceCard(exp)).join('');
  }

  /**
   * 创建经验卡片 HTML
   */
  function createExperienceCard(exp) {
    const tags = exp.tags || [];
    const tagsHtml = tags.slice(0, 3).map(tag =>
      `<span class="exp-card-tag">${tag}</span>`
    ).join('');

    return `
      <div class="exp-card" data-id="${exp.id}">
        <div class="exp-card-header">
          <span class="exp-card-severity ${exp.severity || 'warning'}">${exp.severity === 'critical' ? '严重' : '一般'}</span>
          ${tagsHtml}
        </div>
        <h3 class="exp-card-title">${exp.title || '未命名'}</h3>
        <p class="exp-card-desc">${exp.description || ''}</p>
        <div class="exp-card-footer">
          <span class="exp-card-category">${exp.category || '机械'}</span>
        </div>
      </div>
    `;
  }

  /**
   * 获取演示经验数据
   */
  function getDemoExperiences() {
    return [
      {
        id: '1',
        title: '轴承过早失效',
        description: '某生产线电机轴承在使用3个月后出现异常磨损',
        severity: 'critical',
        category: '旋转设备',
        tags: ['轴承', '磨损', '润滑']
      },
      {
        id: '2',
        title: '焊接裂纹问题',
        description: '钢结构焊接后出现热裂纹',
        severity: 'warning',
        category: '焊接',
        tags: ['焊接', '裂纹', '热处理']
      },
      {
        id: '3',
        title: '齿轮箱噪音异常',
        description: '齿轮箱运行时有异常噪音和振动',
        severity: 'warning',
        category: '齿轮传动',
        tags: ['齿轮', '振动', '噪音']
      }
    ];
  }

  /**
   * 处理卡片点击
   */
  function handleCardClick(id) {
    const exp = experiences.find(e => e.id === id);
    if (exp) {
      showModal(exp);
    }
  }

  /**
   * 显示详情弹窗
   */
  function showModal(exp) {
    const overlay = document.getElementById('exp-modal-overlay');
    const modal = document.getElementById('exp-modal');

    if (!overlay || !modal) return;

    // 填充内容
    const tagsEl = document.getElementById('exp-modal-tags');
    const titleEl = document.getElementById('exp-modal-title');
    const metaEl = document.getElementById('exp-modal-meta');
    const conditionEl = document.getElementById('exp-modal-condition');
    const causeEl = document.getElementById('exp-modal-cause');
    const solutionEl = document.getElementById('exp-modal-solution');
    const sourceEl = document.getElementById('exp-modal-source');
    const linkEl = document.getElementById('exp-modal-link');

    if (tagsEl) tagsEl.innerHTML = (exp.tags || []).map(t => `<span class="exp-tag">${t}</span>`).join('');
    if (titleEl) titleEl.textContent = exp.title || '';
    if (metaEl) metaEl.textContent = `${exp.category || ''} | ${exp.severity === 'critical' ? '严重' : '一般'}`;
    if (conditionEl) conditionEl.textContent = exp.condition || exp.description || '';
    if (causeEl) causeEl.textContent = exp.cause || '';
    if (solutionEl) solutionEl.textContent = exp.solution || '';
    if (sourceEl) sourceEl.textContent = exp.source || '';
    if (linkEl && exp.link) {
      linkEl.href = exp.link;
      linkEl.style.display = 'inline';
    } else if (linkEl) {
      linkEl.style.display = 'none';
    }

    // 显示弹窗
    overlay.classList.add('active');
    modal.classList.add('active');

    // 绑定关闭事件
    const closeBtn = document.getElementById('exp-modal-close');
    const closeHandler = () => {
      overlay.classList.remove('active');
      modal.classList.remove('active');
      closeBtn?.removeEventListener('click', closeHandler);
      overlay?.removeEventListener('click', overlayHandler);
    };

    closeBtn?.addEventListener('click', closeHandler);
    const overlayHandler = (e) => {
      if (e.target === overlay) closeHandler();
    };
    overlay?.addEventListener('click', overlayHandler);
  }

  // 导出到全局
  window.ExperiencePanel = {
    ...window.ExperiencePanel,
    init,
    loadExperiences,
    renderExperiences
  };

})();
