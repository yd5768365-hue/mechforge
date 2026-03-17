/**
 * Knowledge Panel - 知识库界面模块
 * 处理知识库面板的交互、搜索、书籍展示
 * 完全独立：不依赖 index.html 的 CSS
 */

(function() {
  'use strict';

  // ==================== 加载自己的 CSS ====================
  (function() {
    const cssFiles = ['css/knowledge.css', 'css/industrial-theme.css'];
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
  const KNOWLEDGE_PANEL_HTML = `\n<!-- Knowledge Panel - 知识库界面 -->\n<div class="tab-panel" id="knowledge-panel">\n  <!-- 工业风背景 -->\n  <div class="industrial-background"></div>\n  \n  <!-- 工业网格 - 粗细不均 + 烧蚀感 -->\n  <svg class="industrial-grid" xmlns="http://www.w3.org/2000/svg">\n    <defs>\n      <!-- 粗线条 - 主要应力线 -->\n      <pattern id="ind-grid-thick" x="0" y="0" width="120" height="120" patternUnits="userSpaceOnUse">\n        <path d="M0 60 Q60 55, 120 60" class="grid-thick" fill="none"/>\n        <path d="M60 0 Q55 60, 60 120" class="grid-thick" fill="none"/>\n      </pattern>\n      <!-- 中等线条 - 普通加工线 -->\n      <pattern id="ind-grid-medium" x="0" y="0" width="60" height="60" patternUnits="userSpaceOnUse">\n        <line x1="0" y1="30" x2="60" y2="30" class="grid-medium"/>\n        <line x1="30" y1="0" x2="30" y2="60" class="grid-medium"/>\n      </pattern>\n      <!-- 细线条 - 细微划痕 -->\n      <pattern id="ind-grid-thin" x="0" y="0" width="30" height="30" patternUnits="userSpaceOnUse">\n        <line x1="0" y1="15" x2="30" y2="15" class="grid-thin"/>\n        <line x1="15" y1="0" x2="15" y2="30" class="grid-thin"/>\n      </pattern>\n      <!-- 烧蚀线条 - 模糊断裂 -->\n      <pattern id="ind-grid-burn" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">\n        <path d="M0 40 Q20 35, 40 40 T80 40" class="grid-burn" fill="none"/>\n        <path d="M40 0 Q35 20, 40 40 T40 80" class="grid-burn" fill="none"/>\n      </pattern>\n      <!-- 热影响区线条 -->\n      <pattern id="ind-grid-heat" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">\n        <line x1="0" y1="50" x2="100" y2="50" class="grid-heat"/>\n        <line x1="50" y1="0" x2="50" y2="100" class="grid-heat"/>\n      </pattern>\n      <!-- 断裂线 -->\n      <pattern id="ind-grid-broken" x="0" y="0" width="45" height="45" patternUnits="userSpaceOnUse">\n        <line x1="0" y1="22" x2="45" y2="22" class="grid-broken"/>\n        <line x1="22" y1="0" x2="22" y2="45" class="grid-broken"/>\n      </pattern>\n      <!-- 警示网格 -->\n      <pattern id="ind-grid-alert" x="0" y="0" width="200" height="200" patternUnits="userSpaceOnUse">\n        <rect x="0" y="0" width="200" height="3" class="grid-alert" fill="none"/>\n        <rect x="0" y="197" width="200" height="3" class="grid-alert" fill="none"/>\n      </pattern>\n    </defs>\n    <rect width="100%" height="100%" fill="url(#ind-grid-thick)" opacity="0.5"/>\n    <rect width="100%" height="100%" fill="url(#ind-grid-medium)" opacity="0.4"/>\n    <rect width="100%" height="100%" fill="url(#ind-grid-thin)" opacity="0.3"/>\n    <rect width="100%" height="100%" fill="url(#ind-grid-burn)" opacity="0.35"/>\n    <rect width="100%" height="100%" fill="url(#ind-grid-heat)" opacity="0.25"/>\n    <rect width="100%" height="100%" fill="url(#ind-grid-broken)" opacity="0.3"/>\n    <rect width="100%" height="100%" fill="url(#ind-grid-alert)" opacity="0.2"/>\n  </svg>\n  \n  <!-- 金属尘埃粒子容器 -->\n  <div class="metal-dust-container" id="metal-dust-container"></div>\n  \n  <!-- 热应力波脉冲容器 -->\n  <div class="heat-pulse-container" id="heat-pulse-container"></div>\n  \n  <div class="panel-header">\n    <span class="header-mark">锻造</span>\n    <h2>知识库</h2>\n    <p>机械工程专业书籍库</p>\n    <span class="archive-id">MECHFORGE-KB-V3.0</span>\n  </div>\n  \n  <!-- 分类标签 -->\n  <div class="knowledge-tags" id="knowledge-tags">\n    <span class="knowledge-tag active" data-filter="all">全部</span>\n    <span class="knowledge-tag" data-filter="mechanics">力学</span>\n    <span class="knowledge-tag" data-filter="materials">材料</span>\n    <span class="knowledge-tag" data-filter="design">设计</span>\n    <span class="knowledge-tag" data-filter="manufacturing">制造</span>\n    <span class="knowledge-tag" data-filter="thermo">热力学</span>\n    <span class="knowledge-tag" data-filter="control">控制</span>\n    <span class="knowledge-tag" data-filter="fea">有限元</span>\n    <span class="knowledge-tag" data-filter="fluid">流体</span>\n    <span class="knowledge-tag" data-filter="tribology">摩擦学</span>\n  </div>\n  \n  <div class="search-container">\n    <div class="search-wrapper">\n      <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">\n        <circle cx="11" cy="11" r="8"/>\n        <path d="M21 21l-4.35-4.35"/>\n      </svg>\n      <input type="text" id="knowledge-search" placeholder="搜索书籍名称、作者或关键词...">\n      <button id="search-btn">搜索</button>\n    </div>\n  </div>\n\n  <!-- 书籍轮播区域 -->\n  <div class="book-carousel-section" id="book-carousel-section">\n    <div class="book-carousel-header">\n      <h3>推荐书籍</h3>\n      <div class="carousel-nav">\n        <button class="add-book-btn" onclick="openAddBookModal()" title="添加书籍到知识库">\n          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">\n            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>\n          </svg>\n          添加书籍\n        </button>\n        <button class="carousel-nav-btn" id="carousel-prev" title="上一页">‹</button>\n        <button class="carousel-nav-btn" id="carousel-next" title="下一页">›</button>\n      </div>\n    </div>\n    <div class="book-carousel" id="book-carousel"></div>\n  </div>\n\n  <!-- 搜索结果 / 全部书籍列表 -->\n  <div class="search-results" id="search-results"></div>\n\n  <!-- 详情抽屉 - 全息投影机密板 -->\n  <div class="detail-overlay" id="detail-overlay"></div>\n  <div class="detail-drawer" id="detail-drawer">\n    <!-- 能量线边框 -->\n    <div class="drawer-energy-border">\n      <div class="energy-line top"></div>\n      <div class="energy-line right"></div>\n      <div class="energy-line bottom"></div>\n      <div class="energy-line left"></div>\n      <div class="energy-corner tl"></div>\n      <div class="energy-corner tr"></div>\n      <div class="energy-corner bl"></div>\n      <div class="energy-corner br"></div>\n    </div>\n\n    <!-- 关闭按钮 -->\n    <button class="drawer-close" id="drawer-close" title="关闭档案">\n      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">\n        <line x1="18" y1="6" x2="6" y2="18"/>\n        <line x1="6" y1="6" x2="18" y2="18"/>\n      </svg>\n    </button>\n\n    <!-- 抽屉内容 -->\n    <div class="drawer-content" id="drawer-content">\n      <!-- 头部 -->\n      <div class="drawer-header">\n        <div class="drawer-classification">MechForge 知识库 // 书籍详情</div>\n        <div class="drawer-title" id="drawer-title"></div>\n        <div class="drawer-badges" id="drawer-badges"></div>\n      </div>\n\n      <!-- 元信息 -->\n      <div class="drawer-meta" id="drawer-meta"></div>\n\n      <!-- 分隔线 -->\n      <div class="drawer-divider">\n        <div class="divider-line"></div>\n        <div class="divider-glow"></div>\n      </div>\n\n      <!-- 主体内容 -->\n      <div class="drawer-body" id="drawer-body"></div>\n\n      <!-- 底部 -->\n      <div class="drawer-footer">\n        <a class="drawer-source" id="drawer-source" href="#" target="_blank">\n          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">\n            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>\n            <polyline points="15,3 21,3 21,9"/>\n            <line x1="10" y1="14" x2="21" y2="3"/>\n          </svg>\n          查看源文档\n        </a>\n      </div>\n    </div>\n  </div>\n\n  <!-- 用户知识库 CSS -->\n  <style>\n  .user-kb-header{display:flex;align-items:center;justify-content:space-between;padding:16px 4px 12px;margin-bottom:14px}\n  .user-kb-title{display:flex;align-items:center;gap:8px;font-size:14px;font-weight:600;color:#e0f7ff}\n  .user-kb-dot{width:6px;height:6px;border-radius:50%;background:#00d4ff;box-shadow:0 0 6px #00d4ff;flex-shrink:0}\n  .user-kb-count{font-size:12px;font-weight:400;color:rgba(160,196,212,0.55)}\n  .user-kb-actions{display:flex;gap:8px}\n  .kb-refresh-btn{display:flex;align-items:center;gap:5px;padding:5px 13px;background:transparent;border:1px solid rgba(0,212,255,0.3);border-radius:6px;color:rgba(160,196,212,0.7);font-size:12px;cursor:pointer;transition:all .2s}\n  .kb-refresh-btn:hover{border-color:rgba(0,212,255,0.6);color:#00d4ff;background:rgba(0,212,255,0.06)}\n  .kb-add-btn{display:flex;align-items:center;gap:5px;padding:5px 13px;background:rgba(0,212,255,0.1);border:1px solid rgba(0,212,255,0.45);border-radius:6px;color:#00d4ff;font-size:12px;font-weight:600;cursor:pointer;transition:all .2s}\n  .kb-add-btn:hover{background:rgba(0,212,255,0.2)}\n  .user-kb-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:14px;min-height:160px;padding:0 4px}\n  .kb-empty-state{grid-column:1/-1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 0;gap:8px}\n  .kb-empty-icon{font-size:36px;opacity:.4}\n  .kb-empty-text{font-size:13px;color:rgba(160,196,212,0.45)}\n  .kb-empty-sub{font-size:11px;color:rgba(160,196,212,0.3)}\n  .user-book-card{position:relative;border-radius:10px;border:1px solid rgba(0,212,255,0.15);background:rgba(255,255,255,0.02);padding:14px 12px 12px;cursor:pointer;transition:all .2s;display:flex;flex-direction:column;gap:8px;overflow:hidden}\n  .user-book-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--card-color,#00d4ff),transparent)}\n  .user-book-card:hover{border-color:rgba(0,212,255,0.4);transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,0.3)}\n  .card-icon{font-size:26px;text-align:center;padding:6px 0 2px}\n  .card-title{font-size:12.5px;font-weight:600;color:#e0f7ff;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}\n  .card-author{font-size:11px;color:rgba(160,196,212,0.5);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}\n  .card-tag{display:inline-block;font-size:10px;padding:2px 7px;border-radius:10px;font-weight:600;align-self:flex-start}\n  .card-chunks{font-size:10px;color:rgba(160,196,212,0.35)}\n  .card-status{position:absolute;top:8px;right:8px;width:7px;height:7px;border-radius:50%}\n  .card-status.ready{background:#00ff88;box-shadow:0 0 5px #00ff88}\n  .kb-toast{position:fixed;bottom:36px;left:50%;transform:translateX(-50%) translateY(20px);background:rgba(13,31,45,0.95);border:1px solid rgba(0,212,255,0.3);border-radius:8px;padding:9px 20px;font-size:13px;color:#e0f7ff;opacity:0;pointer-events:none;transition:all .3s;z-index:9999;white-space:nowrap}\n  .kb-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}\n  .kb-toast.success{border-color:rgba(0,255,136,0.4);color:#00ff88}\n  .kb-toast.error{border-color:rgba(255,77,109,0.4);color:#ff4d6d}\n  </style>\n\n  <!-- 用户知识库 -->\n  <div class="user-kb-header">\n    <div class="user-kb-title">\n      <span class="user-kb-dot"></span>\n      我的知识库\n      <span class="user-kb-count" id="user-book-count">0 本</span>\n    </div>\n    <div class="user-kb-actions">\n      <button class="kb-refresh-btn" id="refresh-btn" onclick="refreshUserBooks()">刷新</button>\n      <button class="kb-add-btn" onclick="openAddBookModal()">+ 添加书籍</button>\n    </div>\n  </div>\n  <div class="user-kb-grid" id="user-book-grid">\n    <div class="kb-empty-state" id="kb-empty">\n      <div class="kb-empty-icon">📂</div>\n      <div class="kb-empty-text">还没有添加书籍</div>\n      <div class="kb-empty-sub">点击「添加书籍」导入文件</div>\n    </div>\n  </div>\n  <div class="kb-toast" id="kb-toast"></div>\n</div>\n`;

  // 导出到全局
  window.KnowledgePanel = {
    init: initKnowledgePanel,
    isInitialized: false,
    html: KNOWLEDGE_PANEL_HTML
  };

  // DOM 元素
  let knowledgePanel;
  let knowledgeSearch;
  let searchBtn;
  let knowledgeTags;
  let bookCarousel;
  let detailOverlay;
  let detailDrawer;
  let drawerClose;
  let drawerContent;

  // 状态
  let currentFilter = 'all';
  let allBooks = [];
  let filteredBooks = [];

  /**
   * 加载知识库面板 HTML
   */
  function loadHtml() {
    return new Promise((resolve) => {
      const placeholder = document.getElementById('knowledge-panel-placeholder');

      if (placeholder) {
        placeholder.outerHTML = KNOWLEDGE_PANEL_HTML;
        console.log('[KnowledgePanel] HTML 已加载到页面');
      } else {
        const existingPanel = document.getElementById('knowledge-panel');
        if (!existingPanel) {
          // 查找 chat-panel 并在其后插入
          const chatPanel = document.getElementById('chat-panel');
          if (chatPanel) {
            chatPanel.insertAdjacentHTML('afterend', KNOWLEDGE_PANEL_HTML);
          }
        }
      }

      resolve();
    });
  }

  /**
   * 初始化知识库面板
   */
  async function initKnowledgePanel() {
    if (window.KnowledgePanel.isInitialized) {
      return;
    }

    console.log('[KnowledgePanel] 初始化知识库面板');

    // 加载 HTML
    await loadHtml();

    // 缓存 DOM 元素
    knowledgePanel = document.getElementById('knowledge-panel');
    knowledgeSearch = document.getElementById('knowledge-search');
    searchBtn = document.getElementById('search-btn');
    knowledgeTags = document.getElementById('knowledge-tags');
    bookCarousel = document.getElementById('book-carousel');
    detailOverlay = document.getElementById('detail-overlay');
    detailDrawer = document.getElementById('detail-drawer');
    drawerClose = document.getElementById('drawer-close');
    drawerContent = document.getElementById('drawer-content');

    if (!knowledgePanel) return;

    bindEvents();
    loadBooks();

    window.KnowledgePanel.isInitialized = true;
    console.log('[KnowledgePanel] 初始化完成');
  }

  // 保留原有的 init 函数别名（供 window.SettingsPanel 调用）
  function init() {
    return initKnowledgePanel();
  }

  // 立即执行（不是等待 DOMContentLoaded）
  // 这样可以确保在其他模块加载之前 HTML 就存在了
  loadHtml().then(() => {
    // 缓存 DOM 元素
    knowledgePanel = document.getElementById('knowledge-panel');
    knowledgeSearch = document.getElementById('knowledge-search');
    searchBtn = document.getElementById('search-btn');
    knowledgeTags = document.getElementById('knowledge-tags');
    bookCarousel = document.getElementById('book-carousel');
    detailOverlay = document.getElementById('detail-overlay');
    detailDrawer = document.getElementById('detail-drawer');
    drawerClose = document.getElementById('drawer-close');
    drawerContent = document.getElementById('drawer-content');

    if (knowledgePanel) {
      bindEvents();
      loadBooks();
      window.KnowledgePanel.isInitialized = true;
      // 延迟等 DOM 稳定后刷新用户知识库
      setTimeout(() => { if (typeof refreshUserBooks === 'function') refreshUserBooks(); }, 400);
    }
  });

  /**
   * 绑定事件
   */
  function bindEvents() {
    // 搜索
    searchBtn?.addEventListener('click', handleSearch);
    knowledgeSearch?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSearch();
    });

    // 标签过滤
    knowledgeTags?.addEventListener('click', (e) => {
      const tag = e.target.closest('.knowledge-tag');
      if (tag) {
        handleFilter(tag.dataset.filter);
      }
    });

    // 详情抽屉关闭
    drawerClose?.addEventListener('click', closeDetailDrawer);
    detailOverlay?.addEventListener('click', closeDetailDrawer);
  }

  /**
   * 加载书籍数据
   */
  async function loadBooks() {
    try {
      const res = await fetch('/api/rag/books');
      allBooks = await res.json();
      filteredBooks = [...allBooks];
      renderCarousel(allBooks);
    } catch (err) {
      console.error('加载书籍失败:', err);
    }
  }

  /**
   * 处理搜索
   */
  function handleSearch() {
    const query = knowledgeSearch?.value.trim().toLowerCase() || '';
    if (!query) {
      filteredBooks = currentFilter === 'all'
        ? [...allBooks]
        : allBooks.filter(b => b.category === currentFilter);
    } else {
      filteredBooks = allBooks.filter(b =>
        b.title?.toLowerCase().includes(query) ||
        b.author?.toLowerCase().includes(query) ||
        b.tags?.some(t => t.toLowerCase().includes(query))
      );
      if (currentFilter !== 'all') {
        filteredBooks = filteredBooks.filter(b => b.category === currentFilter);
      }
    }
    renderSearchResults(filteredBooks);
  }

  /**
   * 处理过滤
   */
  function handleFilter(filter) {
    currentFilter = filter;

    // 更新标签状态
    knowledgeTags?.querySelectorAll('.knowledge-tag').forEach(tag => {
      tag.classList.toggle('active', tag.dataset.filter === filter);
    });

    // 过滤书籍
    filteredBooks = filter === 'all'
      ? [...allBooks]
      : allBooks.filter(b => b.category === filter);

    renderCarousel(filteredBooks);
  }

  /**
   * 渲染书籍轮播
   */
  function renderCarousel(books) {
    if (!bookCarousel) return;

    if (!books.length) {
      bookCarousel.innerHTML = '<div class="result-placeholder">暂无书籍</div>';
      return;
    }

    bookCarousel.innerHTML = books.map(book => createBookCard(book)).join('');
  }

  /**
   * 渲染搜索结果
   */
  function renderSearchResults(books) {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;

    const carouselSection = document.getElementById('book-carousel-section');

    if (!books.length) {
      searchResults.innerHTML = '<div class="result-placeholder">未找到相关书籍</div>';
      carouselSection.style.display = 'none';
      searchResults.style.display = 'block';
      return;
    }

    carouselSection.style.display = 'none';
    searchResults.style.display = 'block';
    searchResults.innerHTML = books.map(book => createResultItem(book)).join('');
  }

  /**
   * 创建书籍卡片HTML
   */
  function createBookCard(book) {
    const tags = book.tags || [];
    const categoryIcon = getCategoryIcon(book.category);

    return `
      <div class="book-card" onclick="showBookDetail('${book.id}')">
        <div class="book-card-icon">${categoryIcon}</div>
        <div class="book-card-title">${book.title}</div>
        <div class="book-card-meta">${book.author || '未知'}</div>
        <div class="book-card-tags">
          ${tags.slice(0, 2).map(t => `<span class="book-tag">${t}</span>`).join('')}
        </div>
      </div>
    `;
  }

  /**
   * 创建搜索结果项HTML
   */
  function createResultItem(book) {
    const tags = book.tags || [];
    const typeClass = getTypeClass(book.type);

    return `
      <div class="result-item ${typeClass}" onclick="showBookDetail('${book.id}')">
        <div class="result-type ${typeClass}">${book.type || 'book'}</div>
        <div class="result-title">${book.title}</div>
        <div class="result-snippet">${book.description || ''}</div>
        <div class="result-meta">
          <span>${book.author || '未知'}</span>
          <span>${book.year || ''}</span>
        </div>
      </div>
    `;
  }

  /**
   * 获取分类图标
   */
  function getCategoryIcon(category) {
    const icons = {
      mechanics: '⚙️',
      materials: '🔬',
      design: '📐',
      manufacturing: '🔧',
      thermo: '🔥',
      control: '🎛️',
      fea: '📊',
      fluid: '💧',
      tribology: '⚡'
    };
    return icons[category] || '📚';
  }

  /**
   * 获取类型样式类
   */
  function getTypeClass(type) {
    if (type === 'critical') return 'critical';
    if (type === 'warning') return 'warning';
    return 'info';
  }

  /**
   * 显示书籍详情
   */
  async function showBookDetail(bookId) {
    try {
      const res = await fetch(`/api/rag/book/${bookId}`);
      const book = await res.json();
      renderDetailDrawer(book);
      openDetailDrawer();
    } catch (err) {
      console.error('加载书籍详情失败:', err);
    }
  }

  /**
   * 渲染详情抽屉
   */
  function renderDetailDrawer(book) {
    if (!drawerContent) return;

    const badges = (book.tags || []).map(tag =>
      `<span class="drawer-badge">${tag}</span>`
    ).join('');

    drawerContent.innerHTML = `
      <div class="drawer-header">
        <div class="drawer-classification">MechForge 知识库 // 书籍详情</div>
        <div class="drawer-title">${book.title}</div>
        <div class="drawer-badges">${badges}</div>
      </div>
      <div class="drawer-meta">
        <span>作者: ${book.author || '未知'}</span>
        <span>年份: ${book.year || '未知'}</span>
      </div>
      <div class="drawer-divider">
        <div class="divider-line"></div>
        <div class="divider-glow"></div>
      </div>
      <div class="drawer-body">${book.content || book.description || '暂无内容'}</div>
      <div class="drawer-footer">
        <a class="drawer-source" href="${book.source || '#'}" target="_blank">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
            <polyline points="15,3 21,3 21,9"/>
            <line x1="10" y1="14" x2="21" y2="3"/>
          </svg>
          查看源文档
        </a>
      </div>
    `;
  }

  /**
   * 打开详情抽屉
   */
  function openDetailDrawer() {
    detailDrawer?.classList.add('open');
    detailOverlay?.classList.add('visible');
  }

  /**
   * 关闭详情抽屉
   */
  function closeDetailDrawer() {
    detailDrawer?.classList.remove('open');
    detailOverlay?.classList.remove('visible');
  }

  // 导出到全局
  window.KnowledgePanel = {
    init,
    showBookDetail,
    handleSearch,
    handleFilter
  };

})();
