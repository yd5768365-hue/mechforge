/**
 * ModuleLoader - 模块加载器
 * 支持动态导入、懒加载和代码分割
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    lazyModules: ['CAEWorkbench', 'ExperienceLibrary'],
    preloadDelay: 2000, // 延迟预加载时间
    maxRetries: 3,
    retryDelay: 1000
  };

  // ==================== 状态 ====================
  const loadedModules = new Map();
  const loadingPromises = new Map();
  const moduleDependencies = new Map();

  // ==================== 模块定义 ====================
  const moduleRegistry = {
    'Utils': { path: 'core/utils.js', required: true },
    'EventBus': { path: 'core/event-bus.js', required: true },
    'APIClient': { path: 'core/api-client.js', required: true },
    'Logger': { path: 'core/logger.js', required: true },
    'Storage': { path: 'core/storage.js', required: true },
    'ErrorHandler': { path: 'core/error-handler.js', required: true },
    'Markdown': { path: 'core/markdown.js', required: true },
    'ThemeManager': { path: 'core/theme.js', required: true },
    
    'AIService': { path: 'services/ai-service.js', required: true },
    'ConfigService': { path: 'services/config-service.js', required: true },
    
    'ChatUI': { path: 'app/chat/chat-ui.js', required: true },
    'ChatHandler': { path: 'app/chat/chat-handler.js', required: true },
    'ChatFeatures': { path: 'app/chat/chat-features.js', required: false },
    
    'Particles': { path: 'app/ui/particles.js', required: true },
    'WindowControl': { path: 'app/ui/window-control.js', required: true },
    'Mascot': { path: 'app/ui/mascot.js', required: false },
    
    'KnowledgeUI': { path: 'app/knowledge/knowledge-ui.js', required: false },
    'CAEWorkbench': { path: 'app/cae/cae-workbench.js', required: false, lazy: true },
    'StatusBarManager': { path: 'app/settings/status-bar.js', required: true }
  };

  // ==================== 核心功能 ====================

  /**
   * 加载模块
   * @param {string} name - 模块名称
   * @param {number} retryCount - 重试次数
   * @returns {Promise}
   */
  async function load(name, retryCount = 0) {
    // 已加载
    if (loadedModules.has(name)) {
      return loadedModules.get(name);
    }

    // 正在加载中
    if (loadingPromises.has(name)) {
      return loadingPromises.get(name);
    }

    const moduleDef = moduleRegistry[name];
    if (!moduleDef) {
      throw new Error(`Module "${name}" not found in registry`);
    }

    // 检查依赖
    if (moduleDef.dependencies) {
      await Promise.all(moduleDef.dependencies.map(dep => load(dep)));
    }

    // 检查模块是否已存在于 window（通过 script 标签加载）
    if (window[name]) {
      console.log(`[ModuleLoader] Module "${name}" already loaded via script tag`);
      loadedModules.set(name, window[name]);
      return window[name];
    }

    // 创建加载Promise
    const loadPromise = loadScript(moduleDef.path, retryCount)
      .then(() => {
        const module = window[name];
        if (!module && moduleDef.required) {
          throw new Error(`Module "${name}" failed to load`);
        }
        loadedModules.set(name, module);
        loadingPromises.delete(name);
        console.log(`[ModuleLoader] Loaded: ${name}`);
        return module;
      })
      .catch(error => {
        loadingPromises.delete(name);
        if (retryCount < config.maxRetries) {
          console.warn(`[ModuleLoader] Retrying ${name} (${retryCount + 1}/${config.maxRetries})`);
          return new Promise(resolve =>
            setTimeout(() => resolve(load(name, retryCount + 1)), config.retryDelay)
          );
        }
        throw error;
      });

    loadingPromises.set(name, loadPromise);
    return loadPromise;
  }

  /**
   * 加载脚本
   * @param {string} path - 脚本路径
   * @param {number} retryCount - 重试次数
   * @returns {Promise}
   */
  function loadScript(path, retryCount = 0) {
    // 验证路径
    if (!path || path === 'undefined') {
      return Promise.reject(new Error(`Invalid script path: ${path}`));
    }
    
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = path;
      script.async = true;

      script.onload = () => resolve();
      script.onerror = () => reject(new Error(`Failed to load ${path}`));

      document.head.appendChild(script);
    });
  }

  /**
   * 预加载模块
   * @param {string} name - 模块名称
   */
  function preload(name) {
    if (!loadedModules.has(name) && !loadingPromises.has(name)) {
      const moduleDef = moduleRegistry[name];
      if (!moduleDef || !moduleDef.path) {
        console.warn(`[ModuleLoader] Cannot preload module "${name}": definition not found`);
        return;
      }
      
      const link = document.createElement('link');
      link.rel = 'preload';
      link.as = 'script';
      link.href = moduleDef.path;
      document.head.appendChild(link);
    }
  }

  /**
   * 懒加载模块
   * @param {string} name - 模块名称
   * @returns {Promise}
   */
  async function lazyLoad(name) {
    const moduleDef = moduleRegistry[name];
    if (!moduleDef) {
      throw new Error(`Module "${name}" not found`);
    }
    
    if (moduleDef.lazy && !loadedModules.has(name)) {
      console.log(`[ModuleLoader] Lazy loading: ${name}`);
    }
    
    return load(name);
  }

  /**
   * 初始化核心模块
   */
  async function initCore() {
    const coreModules = Object.entries(moduleRegistry)
      .filter(([_, def]) => def.required)
      .map(([name]) => name);
    
    await Promise.all(coreModules.map(name => load(name)));
    console.log('[ModuleLoader] Core modules initialized');
  }

  /**
   * 初始化懒加载模块
   */
  function initLazy() {
    // 延迟预加载非关键模块
    setTimeout(() => {
      config.lazyModules.forEach(name => preload(name));
    }, config.preloadDelay);
  }

  /**
   * 获取已加载模块
   * @param {string} name - 模块名称
   * @returns {*}
   */
  function get(name) {
    return loadedModules.get(name);
  }

  /**
   * 检查模块是否已加载
   * @param {string} name - 模块名称
   * @returns {boolean}
   */
  function isLoaded(name) {
    return loadedModules.has(name);
  }

  /**
   * 等待模块加载完成
   * @param {string} name - 模块名称
   * @param {number} timeout - 超时时间
   * @returns {Promise}
   */
  async function waitFor(name, timeout = 10000) {
    if (loadedModules.has(name)) {
      return loadedModules.get(name);
    }
    
    return new Promise((resolve, reject) => {
      const checkInterval = setInterval(() => {
        if (loadedModules.has(name)) {
          clearInterval(checkInterval);
          clearTimeout(timeoutId);
          resolve(loadedModules.get(name));
        }
      }, 100);
      
      const timeoutId = setTimeout(() => {
        clearInterval(checkInterval);
        reject(new Error(`Timeout waiting for module "${name}"`));
      }, timeout);
    });
  }

  // ==================== 导出 ====================
  window.ModuleLoader = {
    load,
    preload,
    lazyLoad,
    initCore,
    initLazy,
    get,
    isLoaded,
    waitFor,
    registry: moduleRegistry
  };

})();
