/**
 * StatusBarManager - 状态栏管理模块
 * 实现 API、Model、RAG、Memory 按钮功能
 */

(function () {
  'use strict';

  const { $, $$ } = Utils;

  // ==================== 状态 ====================
  const state = {
    currentAPI: 'ollama',
    currentModel: 'qwen2.5:3b',
    ragEnabled: true,
    availableModels: [],
    ggufLoaded: false,
    ggufModelName: '',
    pendingAPI: 'ollama',
    initialized: false
  };

  // ==================== DOM 元素 ====================
  let elements = {};

  // ==================== 初始化 ====================

  /**
   * 初始化状态栏管理器
   */
  function init() {
    // 防止重复初始化
    if (state.initialized) {
      console.log('[StatusBar] Already initialized, skipping');
      return;
    }
    state.initialized = true;

    cacheElements();
    loadInitialState();
    setupEventListeners();

    console.log('[StatusBar] Initialized');
  }

  /**
   * 缓存 DOM 元素
   */
  function cacheElements() {
    elements = {
      apiTrigger: $('api-trigger'),
      apiSelector: $('api-selector'),
      modelTrigger: document.querySelector('[data-status="model"]'),
      ragTrigger: document.querySelector('[data-status="rag"]'),
      memoryTrigger: document.querySelector('[data-status="memory"]'),
      ggufPathInput: $('gguf-model-path'),
      ggufLoadBtn: $('gguf-load-btn'),
      ggufBrowseBtn: $('gguf-browse-btn'),
      ggufRefreshBtn: $('gguf-refresh-btn'),
      ggufModelInfo: $('gguf-model-info')
    };
  }

  /**
   * 加载初始状态
   */
  async function loadInitialState() {
    try {
      // 并行加载配置
      const [config, models, ggufInfo] = await Promise.all([
        apiClient.getConfig().catch(() => null),
        apiClient.getModels().catch(() => []),
        apiClient.get('/gguf/info').catch(() => ({ loaded: false }))
      ]);

      // 更新状态
      if (config) {
        state.currentAPI = config.ai?.provider || 'ollama';
        state.currentModel = config.ai?.model || 'qwen2.5:3b';
        state.ragEnabled = config.rag?.enabled ?? true;
      }

      state.availableModels = Array.isArray(models) ? models : [];
      state.ggufLoaded = ggufInfo.loaded || false;
      state.ggufModelName = ggufInfo.model || '';
      state.pendingAPI = state.currentAPI;

      // 更新 UI
      updateAPIUI();
      updateModelUI();
      updateRAGUI();
      updateMemoryUI();

    } catch (error) {
      console.warn('[StatusBar] Failed to load initial state:', error);
    }
  }

  /**
   * 设置事件监听器
   */
  function setupEventListeners() {
    console.log('[StatusBar] Setting up event listeners...');
    console.log('[StatusBar] Elements:', elements);

    // API 按钮点击
    if (elements.apiTrigger) {
      elements.apiTrigger.addEventListener('click', handleAPITriggerClick);
      console.log('[StatusBar] API trigger listener added');
    } else {
      console.warn('[StatusBar] API trigger element not found!');
    }

    // API 选择器内部点击
    if (elements.apiSelector) {
      elements.apiSelector.addEventListener('click', handleAPISelectorClick);
      console.log('[StatusBar] API selector listener added');
    } else {
      console.warn('[StatusBar] API selector element not found!');
    }

    // Model 按钮点击
    elements.modelTrigger?.addEventListener('click', handleModelTriggerClick);

    // RAG 按钮点击
    elements.ragTrigger?.addEventListener('click', handleRAGTriggerClick);

    // Memory 按钮点击
    elements.memoryTrigger?.addEventListener('click', handleMemoryTriggerClick);

    // 点击外部关闭选择器 - 使用捕获阶段
    document.addEventListener('click', handleDocumentClick, true);

    // 定期更新内存
    setInterval(updateMemoryUI, 30000);
  }

  /**
   * 处理文档点击（关闭选择器）
   */
  function handleDocumentClick(e) {
    const target = e.target;
    
    // 检查是否点击在 API 相关元素上
    const isAPITriggerClick = elements.apiTrigger === target || 
      (elements.apiTrigger && !elements.apiSelector?.contains(target) && elements.apiTrigger.contains(target));
    const isAPISelectorClick = elements.apiSelector?.contains(target);
    
    // 如果点击的是 API 触发按钮，不关闭（toggleAPISelector 会处理）
    if (elements.apiTrigger === target || elements.apiTrigger?.contains(target)) {
      // 但如果点击的是选择器内部，不处理
      if (isAPISelectorClick) return;
      return;
    }
    
    // 如果点击在选择器内部，不关闭
    if (isAPISelectorClick) return;

    const isModelClick = elements.modelTrigger?.contains(target) || $('model-selector-popup')?.contains(target);
    const isMemoryClick = elements.memoryTrigger?.contains(target) || $('memory-popup')?.contains(target);

    if (!isModelClick && !isMemoryClick) {
      closeAllSelectors();
    }
  }

  /**
   * 处理 API 按钮点击
   */
  function handleAPITriggerClick(e) {
    console.log('[StatusBar] handleAPITriggerClick called', e);
    e.preventDefault();
    e.stopPropagation();
    toggleAPISelector();
  }

  /**
   * 处理 Model 按钮点击
   */
  function handleModelTriggerClick(e) {
    e.preventDefault();
    e.stopPropagation();
    showModelSelector();
  }

  /**
   * 处理 RAG 按钮点击
   */
  function handleRAGTriggerClick(e) {
    e.preventDefault();
    e.stopPropagation();
    toggleRAG();
  }

  /**
   * 处理 Memory 按钮点击
   */
  function handleMemoryTriggerClick(e) {
    e.preventDefault();
    e.stopPropagation();
    showMemoryDetails();
  }

  // ==================== API 选择器 ====================

  /**
   * 切换 API 选择器显示
   */
  function toggleAPISelector() {
    console.log('[StatusBar] toggleAPISelector called');
    const isOpen = elements.apiSelector?.classList.contains('active');
    console.log('[StatusBar] isOpen:', isOpen);
    closeAllSelectors();
    if (!isOpen) {
      elements.apiSelector?.classList.add('active');
      elements.apiTrigger?.classList.add('selector-open');
      console.log('[StatusBar] API selector opened');
    }
  }

  /**
   * 处理 API 选择器点击
   */
  function handleAPISelectorClick(e) {
    e.preventDefault();
    e.stopPropagation();

    const option = e.target.closest('.api-option');
    if (option) {
      selectAPI(option.dataset.api);
      return;
    }

    if (e.target.closest('#gguf-load-btn')) {
      loadGGUFModel();
      return;
    }

    if (e.target.closest('#gguf-browse-btn')) {
      browseGGUFFile();
      return;
    }

    if (e.target.closest('#gguf-refresh-btn')) {
      switchToSelectedAPI();
      
    }
  }

  /**
   * 选择 API
   */
  function selectAPI(api) {
    state.pendingAPI = api;

    $$('.api-option').forEach(opt => {
      opt.classList.toggle('selected', opt.dataset.api === api);
    });

    if (elements.ggufModelInfo) {
      if (api === 'gguf') {
        elements.ggufModelInfo.textContent = state.ggufLoaded ? `Ready: ${state.ggufModelName}` : 'Load a GGUF model first';
        elements.ggufModelInfo.className = state.ggufLoaded ? 'gguf-model-info loaded' : 'gguf-model-info';
      } else {
        elements.ggufModelInfo.textContent = 'Click Switch to apply';
        elements.ggufModelInfo.className = 'gguf-model-info';
      }
    }
  }

  /**
   * 切换到选中的 API
   */
  async function switchToSelectedAPI() {
    const apiNames = { ollama: 'Ollama', gguf: 'Local GGUF' };

    if (state.pendingAPI === 'gguf' && !state.ggufLoaded) {
      showToast('Please load a GGUF model first', 'warning');
      return;
    }

    state.currentAPI = state.pendingAPI;
    closeAllSelectors();

    // 更新 UI
    updateAPIUI();

    // 更新模型显示
    if (state.pendingAPI === 'gguf') {
      state.currentModel = state.ggufModelName;
    } else {
      // 获取 Ollama 默认模型
      const ollamaModel = state.availableModels.find(m => m.provider === 'ollama');
      state.currentModel = ollamaModel?.name || 'qwen2.5:3b';
    }
    updateModelUI();

    // 通知后端
    try {
      await apiClient.post('/config/provider', { provider: state.pendingAPI });
      showToast(`Switched to ${apiNames[state.pendingAPI]}`, 'success');
    } catch (error) {
      console.error('[StatusBar] Switch failed:', error);
      showToast('Switch failed', 'error');
    }
  }

  /**
   * 加载 GGUF 模型
   */
  async function loadGGUFModel() {
    const modelPath = elements.ggufPathInput?.value.trim();
    if (!modelPath) {
      if (elements.ggufModelInfo) {
        elements.ggufModelInfo.textContent = 'Please enter model path';
        elements.ggufModelInfo.className = 'gguf-model-info error';
      }
      return;
    }

    if (elements.ggufLoadBtn) elements.ggufLoadBtn.disabled = true;
    if (elements.ggufModelInfo) {
      elements.ggufModelInfo.textContent = 'Loading...';
      elements.ggufModelInfo.className = 'gguf-model-info';
    }

    try {
      const response = await apiClient.post('/gguf/load', { model_path: modelPath });
      if (response.success) {
        state.ggufLoaded = true;
        state.ggufModelName = response.model;
        state.pendingAPI = 'gguf';

        if (elements.ggufModelInfo) {
          elements.ggufModelInfo.textContent = `Loaded: ${response.model}`;
          elements.ggufModelInfo.className = 'gguf-model-info loaded';
        }
        if (elements.ggufLoadBtn) elements.ggufLoadBtn.textContent = 'Loaded';

        showToast(`Model loaded: ${response.model}`, 'success');
      }
    } catch (error) {
      if (elements.ggufModelInfo) {
        elements.ggufModelInfo.textContent = error.message || 'Load failed';
        elements.ggufModelInfo.className = 'gguf-model-info error';
      }
      if (elements.ggufLoadBtn) elements.ggufLoadBtn.disabled = false;
      showToast('Failed to load model', 'error');
    }
  }

  /**
   * 浏览 GGUF 文件
   */
  async function browseGGUFFile() {
    console.log('[StatusBar] browseGGUFFile called');

    // 等待 pywebview 就绪
    if (!window.pywebview?.api) {
      console.warn('[StatusBar] PyWebView API not ready');
      showToast('File browser not available in dev mode', 'info');
      if (elements.ggufPathInput) {
        elements.ggufPathInput.focus();
      }
      return;
    }

    const api = window.pywebview.api;

    if (api && api.select_gguf_file) {
      try {
        const filePath = await api.select_gguf_file();
        if (filePath && elements.ggufPathInput) {
          elements.ggufPathInput.value = filePath;
          await loadGGUFModel();
        }
      } catch (error) {
        console.error('[StatusBar] File dialog failed:', error);
        showToast('File dialog failed', 'error');
      }
    } else {
      console.warn('[StatusBar] select_gguf_file not available');
      if (elements.ggufPathInput) {
        elements.ggufPathInput.focus();
        showToast('Please enter model path manually', 'info');
      }
    }
  }

  /**
   * 更新 API UI
   */
  function updateAPIUI() {
    if (!elements.apiTrigger) return;

    const apiNames = { ollama: 'Ollama', gguf: 'Local GGUF' };

    elements.apiTrigger.classList.remove('api-ollama', 'api-gguf');
    elements.apiTrigger.classList.add(`api-${state.currentAPI}`);

    // 更新文本（保留子元素）
    const textNode = Array.from(elements.apiTrigger.childNodes).find(n => n.nodeType === 3);
    if (textNode) {
      textNode.textContent = `API: ${apiNames[state.currentAPI]} `;
    }
  }

  // ==================== Model 选择器 ====================

  /**
   * 显示模型选择器
   */
  function showModelSelector() {
    // 先关闭其他选择器
    closeAllSelectors();

    // 创建模型选择弹窗
    let selector = $('model-selector-popup');
    if (selector) {
      selector.remove();
    }

    selector = document.createElement('div');
    selector.id = 'model-selector-popup';
    selector.className = 'status-selector-popup';
    selector.innerHTML = `
      <div class="selector-header">
        <span>Select Model</span>
        <button class="selector-close">&times;</button>
      </div>
      <div class="selector-content">
        ${renderModelOptions()}
      </div>
    `;

    // 定位到按钮上方
    const rect = elements.modelTrigger?.getBoundingClientRect();
    if (rect) {
      selector.style.bottom = `${window.innerHeight - rect.top + 8}px`;
      selector.style.left = `${rect.left}px`;
    }

    document.body.appendChild(selector);

    // 绑定事件
    selector.querySelector('.selector-close')?.addEventListener('click', (e) => {
      e.stopPropagation();
      selector.remove();
    });

    selector.querySelectorAll('.model-option').forEach(opt => {
      opt.addEventListener('click', (e) => {
        e.stopPropagation();
        selectModel(opt.dataset.model, opt.dataset.provider);
      });
    });
  }

  /**
   * 渲染模型选项
   */
  function renderModelOptions() {
    if (state.availableModels.length === 0) {
      return '<div class="selector-empty">No models available</div>';
    }

    // 按提供商分组
    const grouped = {};
    state.availableModels.forEach(m => {
      const provider = m.provider || 'unknown';
      if (!grouped[provider]) grouped[provider] = [];
      grouped[provider].push(m);
    });

    let html = '';
    for (const [provider, models] of Object.entries(grouped)) {
      html += `<div class="selector-group">
        <div class="selector-group-label">${provider.toUpperCase()}</div>
        ${models.map(m => `
          <div class="model-option ${m.name === state.currentModel ? 'selected' : ''}"
               data-model="${m.name}" data-provider="${provider}">
            <span class="model-name">${m.name}</span>
            ${m.size ? `<span class="model-size">${formatSize(m.size)}</span>` : ''}
            ${m.loaded ? '<span class="model-status">●</span>' : ''}
          </div>
        `).join('')}
      </div>`;
    }

    return html;
  }

  /**
   * 选择模型
   */
  async function selectModel(model, provider) {
    state.currentModel = model;

    // 如果选择的是 GGUF 模型，需要先切换 provider
    if (provider === 'gguf' && state.currentAPI !== 'gguf') {
      state.currentAPI = 'gguf';
      updateAPIUI();
    } else if (provider === 'ollama' && state.currentAPI !== 'ollama') {
      state.currentAPI = 'ollama';
      updateAPIUI();
    }

    updateModelUI();

    // 关闭选择器
    $('model-selector-popup')?.remove();

    // 通知后端
    try {
      await apiClient.post('/config', { ai: { model, provider } });
      showToast(`Model: ${model}`, 'success');
    } catch (error) {
      console.error('[StatusBar] Failed to set model:', error);
    }
  }

  /**
   * 更新 Model UI
   */
  function updateModelUI() {
    if (elements.modelTrigger) {
      elements.modelTrigger.textContent = `Model: ${state.currentModel}`;
    }
  }

  // ==================== RAG 开关 ====================

  /**
   * 切换 RAG
   */
  async function toggleRAG() {
    state.ragEnabled = !state.ragEnabled;
    updateRAGUI();

    // 通知后端
    try {
      await apiClient.post('/rag/toggle', { enabled: state.ragEnabled });
      showToast(`RAG: ${state.ragEnabled ? 'ON' : 'OFF'}`, 'info');

      // 触发事件
      if (window.eventBus) {
        eventBus.emit(state.ragEnabled ? Events.RAG_ENABLED : Events.RAG_DISABLED);
      }

      // 自动切换AI模式
      if (state.ragEnabled && window.aiService) {
        // 启用RAG时切换到知识库模式
        try {
          await aiService.switchToKnowledgeMode();
          showToast('已切换到知识库模式', 'info');
        } catch (e) {
          console.error('[StatusBar] Failed to switch mode:', e);
        }
      } else if (!state.ragEnabled && window.aiService) {
        // 禁用RAG时切换回聊天模式
        try {
          await aiService.switchToChatMode();
          showToast('已切换到AI聊天模式', 'info');
        } catch (e) {
          console.error('[StatusBar] Failed to switch mode:', e);
        }
      }
    } catch (error) {
      console.error('[StatusBar] Failed to toggle RAG:', error);
      state.ragEnabled = !state.ragEnabled; // 回滚
      updateRAGUI();
    }
  }

  /**
   * 更新 RAG UI
   */
  function updateRAGUI() {
    if (elements.ragTrigger) {
      elements.ragTrigger.textContent = state.ragEnabled ? 'RAG: ON' : 'RAG: OFF';
      elements.ragTrigger.classList.toggle('status-on', state.ragEnabled);
    }
  }

  // ==================== Memory 显示 ====================

  /**
   * 显示内存详情
   */
  function showMemoryDetails() {
    // 先关闭其他选择器
    closeAllSelectors();

    // 创建内存详情弹窗
    let popup = $('memory-popup');
    if (popup) {
      popup.remove();
    }

    const memoryInfo = calculateMemoryUsage();

    popup = document.createElement('div');
    popup.id = 'memory-popup';
    popup.className = 'status-selector-popup memory-popup';
    popup.innerHTML = `
      <div class="selector-header">
        <span>Memory Usage</span>
        <button class="selector-close">&times;</button>
      </div>
      <div class="selector-content">
        <div class="memory-item">
          <span class="memory-label">Conversation History</span>
          <span class="memory-value">${memoryInfo.history}</span>
        </div>
        <div class="memory-item">
          <span class="memory-label">Messages</span>
          <span class="memory-value">${memoryInfo.messageCount}</span>
        </div>
        <div class="memory-item">
          <span class="memory-label">LocalStorage</span>
          <span class="memory-value">${memoryInfo.localStorage}</span>
        </div>
        <div class="memory-actions">
          <button class="memory-action-btn" id="clear-history-btn">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
            </svg>
            Clear History
          </button>
        </div>
      </div>
    `;

    // 定位
    const rect = elements.memoryTrigger?.getBoundingClientRect();
    if (rect) {
      popup.style.bottom = `${window.innerHeight - rect.top + 8}px`;
      popup.style.left = `${rect.left}px`;
    }

    document.body.appendChild(popup);

    // 绑定事件
    popup.querySelector('.selector-close')?.addEventListener('click', (e) => {
      e.stopPropagation();
      popup.remove();
    });

    popup.querySelector('#clear-history-btn')?.addEventListener('click', async (e) => {
      e.stopPropagation();
      await clearHistory();
      popup.remove();
    });
  }

  /**
   * 计算内存使用
   */
  function calculateMemoryUsage() {
    // 计算对话历史大小
    let historySize = 0;
    let messageCount = 0;

    if (window.AppState?.aiService) {
      const history = window.AppState.aiService.getHistory?.() || [];
      messageCount = history.length;
      historySize = new Blob([JSON.stringify(history)]).size;
    }

    // 计算 localStorage 大小
    let localStorageSize = 0;
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      const value = localStorage.getItem(key);
      if (key && value) {
        localStorageSize += key.length + value.length;
      }
    }

    return {
      history: formatSize(historySize),
      messageCount,
      localStorage: formatSize(localStorageSize * 2) // UTF-16
    };
  }

  /**
   * 更新 Memory UI
   */
  function updateMemoryUI() {
    const memoryInfo = calculateMemoryUsage();
    if (elements.memoryTrigger) {
      elements.memoryTrigger.textContent = `Memory: ${memoryInfo.history}`;
    }
  }

  /**
   * 清空历史
   */
  async function clearHistory() {
    try {
      if (window.AppState?.aiService) {
        await window.AppState.aiService.clearHistory();
      }
      await apiClient.clearHistory();
      updateMemoryUI();
      showToast('History cleared', 'success');
    } catch (error) {
      console.error('[StatusBar] Failed to clear history:', error);
      showToast('Failed to clear history', 'error');
    }
  }

  // ==================== 工具函数 ====================

  /**
   * 关闭所有选择器
   */
  function closeAllSelectors() {
    elements.apiSelector?.classList.remove('active');
    elements.apiTrigger?.classList.remove('selector-open');
    $('model-selector-popup')?.remove();
    $('memory-popup')?.remove();
  }

  /**
   * 格式化大小
   */
  function formatSize(bytes) {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }

  /**
   * 显示提示
   */
  function showToast(message, type = 'info') {
    if (window.ChatFeatures?.showToast) {
      ChatFeatures.showToast(message);
    } else {
      console.log(`[Toast] ${type}: ${message}`);
    }
  }

  // ==================== 导出 ====================
  window.StatusBarManager = {
    init,
    updateAPIUI,
    updateModelUI,
    updateRAGUI,
    updateMemoryUI,
    getCurrentAPI: () => state.currentAPI,
    getCurrentModel: () => state.currentModel,
    isRAGEnabled: () => state.ragEnabled
  };

})();