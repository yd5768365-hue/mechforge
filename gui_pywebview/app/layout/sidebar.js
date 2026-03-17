/**
 * Sidebar - 侧边栏导航模块
 * 完全独立：不依赖 index.html 的 CSS
 * 更新此文件不会影响其他界面
 */

(function() {
  'use strict';

  // ==================== 加载自己的 CSS ====================
  (function() {
    const cssFiles = ['css/layout.css'];
    cssFiles.forEach(cssFile => {
      if (!document.querySelector(`link[href="${cssFile}"]`)) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = cssFile;
        document.head.appendChild(link);
      }
    });
  })();

  // ==================== Sidebar HTML ====================
  const SIDEBAR_HTML = `
<!-- Sidebar -->
<div class="sidebar">
  <div class="sidebar-icon active" data-tab="chat" title="AI 助手">
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="12" cy="12" r="10"/>
      <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
      <circle cx="9" cy="10" r="1.5" fill="currentColor"/>
      <circle cx="15" cy="10" r="1.5" fill="currentColor"/>
    </svg>
    <span class="icon-label">AI</span>
  </div>
  <div class="sidebar-icon" data-tab="knowledge" title="知识库">
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/>
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
      <path d="M8 7h8M8 11h6M8 15h4"/>
    </svg>
    <span class="icon-label">RAG</span>
  </div>
  <div class="sidebar-icon" data-tab="cae" title="CAE 工作台">
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M2 20h20"/>
      <path d="M6 20V8l6-4 6 4v12"/>
      <path d="M10 20v-6h4v6"/>
      <circle cx="12" cy="4" r="2"/>
    </svg>
    <span class="icon-label">CAE</span>
  </div>
  <div class="sidebar-icon" data-tab="experience" title="经验库">
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5">
      <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
    </svg>
    <span class="icon-label">EXP</span>
  </div>
  <div class="sidebar-icon" data-tab="settings" title="设置">
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
    </svg>
    <span class="icon-label">设置</span>
  </div>
</div>
`;

  // 导出到全局
  window.Sidebar = {
    init: initSidebar,
    isInitialized: false,
    html: SIDEBAR_HTML
  };

  /**
   * 加载 Sidebar HTML
   */
  function loadHtml() {
    const placeholder = document.getElementById('sidebar-placeholder');

    if (placeholder) {
      placeholder.outerHTML = SIDEBAR_HTML;
      console.log('[Sidebar] HTML 已加载到页面');
    } else {
      // 如果没有占位符，尝试插入
      const mainContent = document.querySelector('.main-content');
      if (mainContent && !document.querySelector('.sidebar')) {
        mainContent.insertAdjacentHTML('afterbegin', SIDEBAR_HTML);
      }
    }
  }

  /**
   * 初始化 Sidebar
   */
  function initSidebar() {
    if (window.Sidebar.isInitialized) {
      return;
    }

    console.log('[Sidebar] 初始化侧边栏');
    loadHtml();

    // 绑定点击事件
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      sidebar.addEventListener('click', handleTabClick);
    }

    window.Sidebar.isInitialized = true;
    console.log('[Sidebar] 初始化完成');
  }

  /**
   * 处理 Tab 点击
   */
  function handleTabClick(e) {
    const icon = e.target.closest('.sidebar-icon');
    if (!icon) return;

    const tab = icon.dataset.tab;
    if (!tab) return;

    // 切换激活状态
    document.querySelectorAll('.sidebar-icon').forEach(el => {
      el.classList.remove('active');
    });
    icon.classList.add('active');

    // 切换面板显示
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.remove('active');
    });
    const targetPanel = document.getElementById(`${tab}-panel`);
    if (targetPanel) {
      targetPanel.classList.add('active');
    }

    // 触发事件
    if (window.eventBus) {
      window.eventBus.emit('ui:tab-changed', { tab });
    }

    // 触发面板特定初始化
    if (tab === 'settings' && window.SettingsPanel) {
      window.SettingsPanel.init();
    }
  }

  // 立即初始化
  loadHtml();

})();
