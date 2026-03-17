/**
 * Chat Panel - AI聊天界面模块
 * 处理聊天面板的初始化和交互
 * 完全独立：不依赖 index.html 的 CSS
 */

(function() {
  'use strict';

  // ==================== 加载自己的 CSS ====================
  (function() {
    const cssFiles = ['css/chat.css', 'css/chat-markdown.css'];
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
  const CHAT_PANEL_HTML = `
<div class="tab-panel active" id="chat-panel">
  <!-- Mascot Toggle Button -->
  <button class="mascot-toggle" id="mascot-toggle" title="切换吉祥物">
    <svg class="gear-icon" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>
    </svg>
  </button>

  <!-- Mascot Whale (hidden by default) -->
  <div class="mascot-whale hidden">
    <img src="dj-whale.png" alt="MechForge 吉祥物" class="whale-img">
    <!-- 符文容器 - 数据共鸣效果 -->
    <div class="rune-container" id="rune-container">
      <div class="rune-ring"></div>
      <div class="rune-ring"></div>
      <div class="rune-ring"></div>
    </div>
    <!-- 思考波纹 -->
    <div class="thought-ripple"></div>
    <div class="thought-ripple"></div>
    <div class="thought-ripple"></div>
    <!-- AI 响应同步显示 -->
    <div class="whale-speech" id="whale-speech"></div>
  </div>

  <!-- Gear Animation (visible by default) -->
  <div class="default-gear">
    <svg class="spinning-gear" viewBox="0 0 24 24" width="80" height="80" fill="none" stroke="currentColor" stroke-width="0.5">
      <circle cx="12" cy="12" r="2" fill="rgba(0, 229, 255, 0.3)"/>
      <path d="M12 2v4M12 18v4M2 12h4M18 12h4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" stroke="rgba(0, 229, 255, 0.4)"/>
      <path d="M12 6a6 6 0 00-6 6 6 6 0 006 6 6 6 0 006-6 6 6 0 00-6-6z" stroke="rgba(0, 229, 255, 0.2)"/>
    </svg>
  </div>

  <!-- 内置模型下载提示 -->
  <div class="model-download-banner" id="model-download-banner" style="display: none;">
    <div class="mdb-icon">
      <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
    </div>
    <div class="mdb-content">
      <div class="mdb-title">下载内置 AI 模型</div>
      <div class="mdb-desc" id="mdb-desc">下载 Qwen2.5-1.5B 模型 (~1 GB)，即可离线使用 AI 对话</div>
      <div class="mdb-progress-wrap" id="mdb-progress-wrap" style="display: none;">
        <div class="mdb-progress-bar"><div class="mdb-progress-fill" id="mdb-progress-fill"></div></div>
        <div class="mdb-progress-text" id="mdb-progress-text">0%</div>
      </div>
    </div>
    <div class="mdb-actions" id="mdb-actions">
      <button class="mdb-btn primary" id="mdb-download-btn">开始下载</button>
      <button class="mdb-btn secondary" id="mdb-dismiss-btn">稍后</button>
    </div>
  </div>

  <div class="boot-sequence" id="boot-sequence">
    <div class="boot-line" id="boot-line-0">[21:04] 系统: 正在初始化 MechForge AI...</div>
  </div>
  <div class="chat-output" id="chat-output"></div>
  <div class="chat-input-container">
    <div class="input-wrapper">
      <input type="text" id="chat-input" placeholder="输入您的问题..." autocomplete="off">
      <button id="send-btn">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="white">
          <path d="M2 21l21-9L2 3v7l15 2-15 2z"/>
        </svg>
        发送
      </button>
    </div>
  </div>
</div>
`;

  // 导出到全局
  window.ChatPanel = {
    init: initChatPanel,
    isInitialized: false,
    html: CHAT_PANEL_HTML
  };

  /**
   * 立即加载聊天面板 HTML（不使用 DOMContentLoaded）
   */
  function loadHtmlImmediately() {
    const placeholder = document.getElementById('chat-panel-placeholder');

    if (placeholder) {
      placeholder.outerHTML = CHAT_PANEL_HTML;
      console.log('[ChatPanel] HTML 已加载到页面');
    } else {
      // 如果占位符不存在，检查是否已有 chat-panel
      const existingPanel = document.getElementById('chat-panel');
      if (!existingPanel) {
        // 查找 sidebar 并在其后插入
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) {
          sidebar.insertAdjacentHTML('afterend', CHAT_PANEL_HTML);
        }
      }
    }
  }

  /**
   * 初始化聊天面板
   */
  function initChatPanel() {
    if (window.ChatPanel.isInitialized) {
      return;
    }

    console.log('[ChatPanel] 初始化聊天面板');
    window.ChatPanel.isInitialized = true;
  }

  // 立即执行（不是等待 DOMContentLoaded）
  // 这样可以确保在其他 chat 模块加载之前 HTML 就存在了
  loadHtmlImmediately();

})();
