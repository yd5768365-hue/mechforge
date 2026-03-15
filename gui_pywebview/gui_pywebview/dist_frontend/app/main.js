/**
 * Main - 应用主入口（优化版本）
 * 集成模块加载器、性能监控、事件管理器
 */

(function () {
  'use strict';

  // ==================== 全局状态 ====================
  const state = {
    activeTab: 'chat',
    booted: false,
    aiService: null,
    configService: null,
    initErrors: [],
    initTime: 0
  };

  // ==================== 初始化 ====================

  /**
   * 应用初始化入口
   */
  async function init() {
    const startTime = performance.now();
    console.log('[Main] Starting initialization...');

    try {
      // 初始化性能监控
      if (window.PerformanceMonitor) {
        PerformanceMonitor.start();
        PerformanceMonitor.mark('init-start');
      }

      // 初始化事件管理器
      if (window.EventManager) {
        EventManager.startAutoCleanup();
      }

      // 初始化核心模块
      await initCore();
      
      // 初始化服务
      await initServices();
      
      // 初始化UI模块
      await initUIModules();
      
      // 运行启动序列
      await runBootSequence();
      
      // 设置事件监听
      setupEventListeners();
      registerEventHandlers();
      
      // 初始化懒加载
      if (window.ModuleLoader) {
        ModuleLoader.initLazy();
      }

      // 记录初始化时间
      state.initTime = performance.now() - startTime;
      console.log(`[Main] Initialization complete in ${state.initTime.toFixed(2)}ms`);
      
      if (window.PerformanceMonitor) {
        PerformanceMonitor.mark('init-end');
        PerformanceMonitor.measureBetween('init-start', 'init-end', 'app-initialization');
      }

    } catch (error) {
      console.error('[Main] Initialization failed:', error);
      PerformanceMonitor?.recordError(error, 'initialization');
      state.initErrors.push(error.message);
      showInitError(error);
    }
  }

  /**
   * 初始化核心模块
   */
  async function initCore() {
    if (!window.ModuleLoader) {
      throw new Error('ModuleLoader not available');
    }
    
    await ModuleLoader.initCore();
    console.log('[Main] Core modules loaded');
  }

  /**
   * 初始化服务
   */
  async function initServices() {
    // 检查依赖
    if (typeof apiClient === 'undefined') {
      throw new Error('APIClient not loaded');
    }
    if (typeof eventBus === 'undefined') {
      throw new Error('EventBus not loaded');
    }

    // 等待服务模块加载
    const AIService = ModuleLoader.get('AIService');
    const ConfigService = ModuleLoader.get('ConfigService');

    if (!AIService || !ConfigService) {
      throw new Error('Required services not loaded');
    }

    state.aiService = new AIService(apiClient, eventBus);
    state.configService = new ConfigService(apiClient, eventBus);

    try {
      const { config } = await state.configService.init();
      if (config) updateStatusBar(config);
    } catch (error) {
      console.warn('[Main] ConfigService init failed, using defaults:', error);
    }
  }

  /**
   * 初始化UI模块
   */
  async function initUIModules() {
    const modules = [
      { name: 'ThemeManager', required: true },
      { name: 'ChatUI', required: true },
      { name: 'Particles', required: true },
      { name: 'WindowControl', required: true },
      { name: 'Mascot', required: false },
      { name: 'ModeIndicator', required: false },
      { name: 'ChatHandler', required: true, deps: ['aiService'] },
      { name: 'KnowledgeUI', required: false, deps: ['aiService'] },
      { name: 'StatusBarManager', required: true }
    ];

    for (const { name, required, deps } of modules) {
      try {
        // 优先从 ModuleLoader 获取，否则从 window 获取
        let module = ModuleLoader.get(name);
        if (!module && window[name]) {
          module = window[name];
        }
        
        if (!module) {
          if (required) {
            console.warn(`[Main] Required module ${name} not available`);
          }
          continue;
        }

        // 准备初始化参数
        const initArgs = [];
        if (deps) {
          deps.forEach(dep => {
            if (dep === 'aiService') initArgs.push(state.aiService);
          });
        }

        // 测量初始化时间
        const initStart = performance.now();
        if (module.init) {
          await module.init(...initArgs);
        }
        const initTime = performance.now() - initStart;
        
        console.log(`[Main] ${name} initialized (${initTime.toFixed(2)}ms)`);
      } catch (error) {
        console.error(`[Main] ${name} init failed:`, error);
        PerformanceMonitor?.recordError(error, `${name}-init`);
        if (required) {
          state.initErrors.push(`${name}: ${error.message}`);
        }
      }
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
   * 运行启动序列
   */
  async function runBootSequence() {
    const ChatUI = ModuleLoader.get('ChatUI');
    const ChatHandler = ModuleLoader.get('ChatHandler');
    
    if (ChatUI && ChatUI.runBootSequence) {
      return new Promise((resolve) => {
        ChatUI.runBootSequence(() => {
          state.booted = true;
          if (ChatHandler && ChatHandler.setBooted) {
            ChatHandler.setBooted(true);
          }
          resolve();
        });
      });
    }
  }

  /**
   * 设置事件监听器（使用事件委托优化）
   */
  function setupEventListeners() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;

    // 使用事件委托处理Tab切换
    EventManager?.delegate(sidebar, '.sidebar-icon', 'click', (e, target) => {
      const tab = target.dataset.tab;
      if (tab) switchTab(tab);
    });

    // 使用事件委托处理hover效果
    EventManager?.delegate(sidebar, '.sidebar-icon', 'mouseenter', (e, target) => {
      const { left, top, width, height } = target.getBoundingClientRect();
      if (window.Particles) {
        Particles.createHoverSplash(left + width / 2, top + height / 2);
      }
    });
  }

  /**
   * 注册事件总线处理器
   */
  function registerEventHandlers() {
    if (!eventBus) return;

    const handlers = {
      [Events.AI_MESSAGE_SENT]: ({ message }) => {
        console.log('Sent:', message);
      },
      [Events.AI_RESPONSE_RECEIVED]: ({ message }) => {
        console.log('Received:', message);
      },
      [Events.AI_ERROR]: ({ error }) => {
        console.error('AI Error:', error);
        const ChatUI = ModuleLoader.get('ChatUI');
        ChatUI?.addSystemMessage?.(`Error: ${error}`);
        PerformanceMonitor?.recordError(new Error(error), 'ai-response');
      },
      [Events.CONFIG_LOADED]: ({ config }) => {
        updateStatusBar(config);
      },
      [Events.RAG_ENABLED]: () => updateRAGStatus(true),
      [Events.RAG_DISABLED]: () => updateRAGStatus(false)
    };

    Object.entries(handlers).forEach(([event, handler]) => {
      eventBus.on(event, handler);
    });
  }

  // ==================== Tab 切换 ====================

  /**
   * 切换 Tab
   * @param {string} tab - Tab 名称
   */
  async function switchTab(tab) {
    const oldTab = state.activeTab;
    state.activeTab = tab;

    // 更新侧边栏状态
    document.querySelectorAll('.sidebar-icon').forEach(icon => {
      const isActive = icon.dataset.tab === tab;
      icon.classList.toggle('active', isActive);
      icon.setAttribute('aria-selected', isActive);
    });

    // 更新面板显示
    document.querySelectorAll('.tab-panel').forEach(panel => {
      panel.classList.toggle('active', panel.id === `${tab}-panel`);
    });

    // 懒加载CAE模块
    if (tab === 'cae' && !ModuleLoader.isLoaded('CAEWorkbench')) {
      try {
        await ModuleLoader.lazyLoad('CAEWorkbench');
        const CAEWorkbench = ModuleLoader.get('CAEWorkbench');
        CAEWorkbench?.init();
      } catch (error) {
        console.error('[Main] Failed to load CAEWorkbench:', error);
      }
    }

    // Experience Library 控制
    if (tab === 'experience') {
      window.ExpLib?.resume();
    } else {
      window.ExpLib?.pause();
    }

    // Settings Panel 控制
    if (tab === 'settings') {
      window.SettingsPanel?.init();
    }

    // 确保当前面板可以滚动
    enablePanelScrolling(tab);

    eventBus?.emit(Events.UI_TAB_CHANGED, { tab, oldTab });
  }

  /**
   * 启用面板滚动
   */
  function enablePanelScrolling(tab) {
    // 获取当前面板
    const panel = document.getElementById(`${tab}-panel`);
    if (!panel) return;

    // 查找可滚动容器 (使用 ID 选择器)
    const scrollableIds = ['chat-output', 'search-results', 'exp-results', 'cae-viewport', 'settings-scroll'];
    scrollableIds.forEach(id => {
      const el = document.getElementById(id);
      if (el) {
        // 确保滚动容器可以接收触摸事件
        el.style.touchAction = 'pan-y';
        el.style.webkitOverflowScrolling = 'touch';
        
        // 调试信息
        const rect = el.getBoundingClientRect();
        console.log(`[Main] ${id}: height=${rect.height}, overflow=${getComputedStyle(el).overflowY}`);
      }
    });

    console.log(`[Main] 已启用 ${tab} 面板的滚动支持`);
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

  // ==================== 性能监控命令 ====================

  /**
   * 获取性能报告
   */
  window.getPerformanceReport = () => {
    return PerformanceMonitor?.getReport();
  };

  /**
   * 获取应用状态
   */
  window.getAppState = () => ({
    ...state,
    loadedModules: Object.keys(window.ModuleLoader?.registry || {}),
    eventStats: window.EventManager?.getStats?.()
  });

  // ==================== 启动应用 ====================

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // 导出全局状态
  window.AppState = state;

})();
