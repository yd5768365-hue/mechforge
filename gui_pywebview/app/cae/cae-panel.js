/**
 * CAE Panel - CAE工作台界面模块
 * 处理CAE工作台面板的初始化
 * 完全独立：不依赖 index.html 的 CSS
 */

(function() {
  'use strict';

  // ==================== 加载自己的 CSS ====================
  (function() {
    const cssFiles = ['css/panels.css'];
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
  const CAE_PANEL_HTML = `
<!-- CAE Panel - CAE工作台界面 -->
<div class="tab-panel" id="cae-panel">
  <div class="panel-header">
    <h2>CAE 工作台</h2>
    <p>模型加载、网格划分、求解和可视化</p>
  </div>
  <div class="cae-toolbar">
    <button class="cae-btn" id="demo-btn">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="5 3 19 12 5 21 5 3"/>
      </svg>
      示例悬臂梁
    </button>
    <button class="cae-btn" id="load-model-btn">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
      加载模型
    </button>
    <button class="cae-btn" id="mesh-btn">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/>
        <line x1="12" y1="22" x2="12" y2="15.5"/>
        <polyline points="22 8.5 12 15.5 2 8.5"/>
      </svg>
      网格
    </button>
    <button class="cae-btn" id="solve-btn">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="5 3 19 12 5 21 5 3"/>
      </svg>
      求解
    </button>
    <button class="cae-btn" id="visualize-btn">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <circle cx="12" cy="12" r="3"/>
        <line x1="12" y1="2" x2="12" y2="6"/>
        <line x1="12" y1="18" x2="12" y2="22"/>
      </svg>
      可视化
    </button>
    <button class="cae-btn" id="clear-btn">
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M3 6h18"/>
        <path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
      </svg>
      清除
    </button>
  </div>
  <div class="cae-viewport" id="cae-viewport">
    <canvas id="cae-canvas"></canvas>
    <div class="viewport-overlay" id="viewport-overlay">
      <div class="overlay-content">
        <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1">
          <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
          <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
          <line x1="12" y1="22.08" x2="12" y2="12"/>
        </svg>
        <p>CAE 工作台就绪</p>
        <span>加载模型以开始仿真</span>
      </div>
    </div>
  </div>
  <div class="cae-status" id="cae-status">
    <div class="status-item">
      <span class="status-label">状态:</span>
      <span class="status-value" id="status-text">就绪</span>
    </div>
    <div class="status-item">
      <span class="status-label">模型:</span>
      <span class="status-value" id="model-name">无</span>
    </div>
    <div class="status-item">
      <span class="status-label">单元:</span>
      <span class="status-value" id="element-count">0</span>
    </div>
    <div class="status-item">
      <span class="status-label">节点:</span>
      <span class="status-value" id="node-count">0</span>
    </div>
  </div>
</div>
`;

  // 导出到全局
  window.CAEPanel = {
    init: initCAEPanel,
    isInitialized: false,
    html: CAE_PANEL_HTML
  };

  /**
   * 加载 CAE 面板 HTML
   */
  function loadHtml() {
    return new Promise((resolve) => {
      const placeholder = document.getElementById('cae-panel-placeholder');

      if (placeholder) {
        placeholder.outerHTML = CAE_PANEL_HTML;
        console.log('[CAEPanel] HTML 已加载到页面');
      } else {
        const existingPanel = document.getElementById('cae-panel');
        if (!existingPanel) {
          // 查找 settings-panel 并在其后插入
          const settingsPanel = document.getElementById('settings-panel');
          if (settingsPanel) {
            settingsPanel.insertAdjacentHTML('afterend', CAE_PANEL_HTML);
          }
        }
      }

      resolve();
    });
  }

  /**
   * 初始化 CAE 面板
   */
  async function initCAEPanel() {
    if (window.CAEPanel.isInitialized) {
      return;
    }

    console.log('[CAEPanel] 初始化 CAE 面板');

    // 加载 HTML
    await loadHtml();

    // 触发 CAEWorkbench 初始化
    // CAEWorkbench 是懒加载的，当用户切换到 CAE 标签时加载
    window.CAEPanel.isInitialized = true;
    console.log('[CAEPanel] 初始化完成');
  }

  // 保留原有 init 别名
  function init() {
    return initCAEPanel();
  }

  // 立即执行
  loadHtml();

})();
