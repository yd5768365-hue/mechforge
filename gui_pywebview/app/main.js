/**
 * Main - 应用主入口
 * 负责初始化所有模块、协调模块间通信、管理全局状态
 */

(function () {
  'use strict';

  const { $$ } = Utils;

  // ==================== 全局状态 ====================
  const state = {
    activeTab: 'chat',
    booted: false,
    aiService: null,
    configService: null,
    initErrors: []
  };

  // ==================== 初始化 ====================

  /**
   * 应用初始化入口
   */
  function init() {
    console.log('[Main] Starting initialization...');
    
    try {
      initServices();
      initModules();
      runBootSequence();
      setupEventListeners();
      registerEventHandlers();
      console.log('[Main] Initialization complete');
    } catch (error) {
      console.error('[Main] Initialization failed:', error);
      state.initErrors.push(error.message);
      showInitError(error);
    }
  }

  /**
   * 显示初始化错误
   * @param {Error} error - 错误对象
   */
  function showInitError(error) {
    const bootSequence = document.getElementById('boot-sequence');
    if (bootSequence) {
      const errorEl = document.createElement('div');
      errorEl.className = 'boot-line error';
      errorEl.style.color = '#ff4757';
      errorEl.textContent = `[ERROR] ${error.message}`;
      bootSequence.appendChild(errorEl);
    }
  }

  /**
   * 初始化服务
   */
  function initServices() {
    // 检查依赖是否加载
    if (typeof apiClient === 'undefined') {
      throw new Error('APIClient not loaded');
    }
    if (typeof eventBus === 'undefined') {
      throw new Error('EventBus not loaded');
    }

    state.aiService = new AIService(apiClient, eventBus);
    state.configService = new ConfigService(apiClient, eventBus);

    state.configService.init()
      .then(({ config }) => {
        if (config) updateStatusBar(config);
      })
      .catch((error) => {
        console.warn('[Main] ConfigService init failed, using defaults:', error);
      });
  }

  /**
   * 初始化各功能模块
   */
  function initModules() {
    const modules = [
      { name: 'ThemeManager', init: () => ThemeManager.init() },
      { name: 'ChatUI', init: () => ChatUI.init() },
      { name: 'Particles', init: () => Particles.init() },
      { name: 'WindowControl', init: () => WindowControl.init() },
      { name: 'Mascot', init: () => Mascot.init() },
      { name: 'ChatHandler', init: () => ChatHandler.init(state.aiService) },
      { name: 'KnowledgeUI', init: () => KnowledgeUI.init(state.aiService) },
      { name: 'CAEWorkbench', init: () => CAEWorkbench.init() },
      { name: 'StatusBarManager', init: () => StatusBarManager.init() },
    ];

    for (const { name, init } of modules) {
      try {
        if (typeof window[name] !== 'undefined') {
          init();
          console.log(`[Main] ${name} initialized`);
        } else {
          console.warn(`[Main] ${name} not available`);
        }
      } catch (error) {
        console.error(`[Main] ${name} init failed:`, error);
        state.initErrors.push(`${name}: ${error.message}`);
      }
    }
  }

  /**
   * 运行启动序列
   */
  function runBootSequence() {
    ChatUI.runBootSequence(() => {
      state.booted = true;
      ChatHandler.setBooted(true);
    });
  }

  /**
   * 设置事件监听器
   */
  function setupEventListeners() {
    // Tab 切换
    $$('.sidebar-icon').forEach(icon => {
      icon.addEventListener('click', () => switchTab(icon.dataset.tab));
      icon.addEventListener('mouseenter', () => {
        const { left, top, width, height } = icon.getBoundingClientRect();
        Particles.createHoverSplash(left + width / 2, top + height / 2);
      });
    });
  }

  /**
   * 注册事件总线处理器
   */
  function registerEventHandlers() {
    eventBus.on(Events.AI_MESSAGE_SENT, ({ message }) => {
      console.log('Sent:', message);
    });

    eventBus.on(Events.AI_RESPONSE_RECEIVED, ({ message }) => {
      console.log('Received:', message);
    });

    eventBus.on(Events.AI_ERROR, ({ error }) => {
      console.error('AI Error:', error);
      ChatUI.addSystemMessage(`Error: ${error}`);
    });

    eventBus.on(Events.CONFIG_LOADED, ({ config }) => {
      updateStatusBar(config);
    });

    eventBus.on(Events.RAG_ENABLED, () => {
      updateRAGStatus(true);
    });

    eventBus.on(Events.RAG_DISABLED, () => {
      updateRAGStatus(false);
    });
  }

  // ==================== Tab 切换 ====================

  /**
   * 切换 Tab
   * @param {string} tab - Tab 名称
   */
  function switchTab(tab) {
    state.activeTab = tab;

    $$('.sidebar-icon').forEach(icon => {
      icon.classList.toggle('active', icon.dataset.tab === tab);
    });

    $$('.tab-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === `${tab}-panel`);
    });

    eventBus.emit(Events.UI_TAB_CHANGED, { tab });

    // Experience Library 走马灯控制
    if (tab === 'experience') {
      window.ExpLib?.resume();
    } else {
      window.ExpLib?.pause();
    }
  }

  // ==================== 状态栏更新 ====================

  /**
   * 更新状态栏
   * @param {Object} config - 配置对象
   */
  function updateStatusBar(config) {
    const modelEl = document.querySelector('[data-status="model"]');
    const apiEl = document.querySelector('[data-status="api"]');

    if (modelEl && config.ai) {
      modelEl.textContent = `Model: ${config.ai.model || 'qwen2.5:3b'}`;
    }
    if (apiEl && config.ai) {
      apiEl.textContent = `API: ${config.ai.provider || 'Ollama'}`;
    }
  }

  /**
   * 更新 RAG 状态
   * @param {boolean} enabled - 是否启用
   */
  function updateRAGStatus(enabled) {
    const ragEl = document.querySelector('[data-status="rag"]');
    if (!ragEl) return;

    ragEl.textContent = enabled ? 'RAG: ON' : 'RAG: OFF';
    ragEl.classList.toggle('status-on', enabled);
  }

  // ==================== 启动应用 ====================

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // 导出全局状态（调试用）
  window.AppState = state;

})();