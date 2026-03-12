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
    expEnabled: false,
    availableModels: [],
    ggufLoaded: false,
    ggufModelName: '',
    ggufModelPath: '',
    ggufScannedModels: [],
    ggufDirectory: '',
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

    try {
      cacheElements();
      setupEventListeners();
      console.log('[StatusBar] Event listeners bound');
    } catch (err) {
      console.error('[StatusBar] Failed to setup listeners:', err);
    }

    // 网络请求不阻塞事件绑定
    loadInitialState().catch(err => {
      console.warn('[StatusBar] loadInitialState error (non-fatal):', err);
    });

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
      expTrigger: document.querySelector('[data-status="exp"]'),
      ggufSection: $('gguf-section'),
      ggufModelList: $('gguf-model-list'),
      ggufScanBtn: $('gguf-scan-btn'),
      ggufBrowseBtn: $('gguf-browse-btn'),
      ggufBrowseDirBtn: $('gguf-browse-dir-btn'),
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
      state.ggufModelPath = ggufInfo.model_path || '';
      state.pendingAPI = state.currentAPI;

      // 更新 UI
      updateAPIUI();
      updateModelUI();
      updateRAGUI();
      updateExpUI();
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

    // 经验库按钮点击
    elements.expTrigger?.addEventListener('click', handleExpTriggerClick);

    // GGUF 按钮
    elements.ggufScanBtn?.addEventListener('click', (e) => { e.stopPropagation(); scanGGUFModels(); });
    elements.ggufBrowseBtn?.addEventListener('click', (e) => { e.stopPropagation(); browseGGUFFile(); });
    elements.ggufBrowseDirBtn?.addEventListener('click', (e) => { e.stopPropagation(); browseGGUFDirectory(); });

    // 点击外部关闭选择器
    document.addEventListener('click', handleDocumentClick, false);

    // 定期更新内存
    setInterval(updateMemoryUI, 30000);
  }

  /**
   * 处理文档点击（关闭选择器）
   */
  function handleDocumentClick(e) {
    const target = e.target;

    // 点击在任何弹窗/选择器内部时不关闭
    if (elements.apiTrigger?.contains(target)) return;
    if ($('model-selector-popup')?.contains(target)) return;
    if ($('memory-popup')?.contains(target)) return;

    // 点击在状态栏按钮上时不关闭（各自的handler会处理）
    if (elements.modelTrigger?.contains(target)) return;
    if (elements.memoryTrigger?.contains(target)) return;
    if (elements.ragTrigger?.contains(target)) return;
    if (elements.expTrigger?.contains(target)) return;

    closeAllSelectors();
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

    // GGUF 模型列表项点击
    const ggufItem = e.target.closest('.gguf-model-item');
    if (ggufItem) {
      const modelPath = ggufItem.dataset.path;
      const modelName = ggufItem.dataset.name;
      if (modelPath) {
        selectGGUFModel(modelPath, modelName);
      }
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

    // 展开/收起 GGUF 区域
    if (elements.ggufSection) {
      elements.ggufSection.classList.toggle('visible', api === 'gguf');
    }

    if (api === 'gguf' && state.ggufScannedModels.length === 0) {
      scanGGUFModels();
    }

    if (elements.ggufModelInfo) {
      if (api === 'gguf') {
        elements.ggufModelInfo.textContent = state.ggufLoaded
          ? `已加载: ${state.ggufModelName}`
          : '请选择一个 GGUF 模型';
        elements.ggufModelInfo.className = state.ggufLoaded ? 'gguf-model-info loaded' : 'gguf-model-info';
      } else {
        elements.ggufModelInfo.textContent = '';
        elements.ggufModelInfo.className = 'gguf-model-info';
      }
    }
  }

  /**
   * 切换到选中的 API
   */
  async function switchToSelectedAPI() {
    const apiNames = { ollama: 'Ollama', gguf: '本地 GGUF' };

    if (state.pendingAPI === 'gguf' && !state.ggufLoaded) {
      showToast('请先选择并加载一个 GGUF 模型', 'warning');
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
      const ollamaModel = state.availableModels.find(m => m.provider === 'ollama');
      state.currentModel = ollamaModel?.name || 'qwen2.5:3b';
    }
    updateModelUI();

    try {
      await apiClient.post('/config/provider', { provider: state.pendingAPI });
      showToast(`已切换到 ${apiNames[state.pendingAPI]}`, 'success');
    } catch (error) {
      console.error('[StatusBar] Switch failed:', error);
      showToast('切换失败', 'error');
    }
  }

  /**
   * 扫描 GGUF 模型目录
   */
  async function scanGGUFModels(directory = '') {
    if (!elements.ggufModelList) return;

    elements.ggufModelList.innerHTML = '<div class="gguf-model-list-loading">扫描中...</div>';

    try {
      const url = directory ? `/gguf/scan?directory=${encodeURIComponent(directory)}` : '/gguf/scan';
      const result = await apiClient.get(url);

      state.ggufScannedModels = result.models || [];
      state.ggufDirectory = result.directory || '';

      renderGGUFModelList();
    } catch (error) {
      console.error('[StatusBar] GGUF scan failed:', error);
      elements.ggufModelList.innerHTML = '<div class="gguf-model-list-empty">扫描失败</div>';
    }
  }

  /**
   * 渲染 GGUF 模型列表
   */
  function renderGGUFModelList() {
    if (!elements.ggufModelList) return;

    if (state.ggufScannedModels.length === 0) {
      elements.ggufModelList.innerHTML = `
        <div class="gguf-model-list-empty">
          未找到 .gguf 文件
          ${state.ggufDirectory ? `<br><span class="gguf-dir-hint">${state.ggufDirectory}</span>` : ''}
        </div>`;
      return;
    }

    const html = state.ggufScannedModels.map(m => {
      const sizeMB = (m.size / 1024 / 1024).toFixed(1);
      const isActive = m.loaded;
      return `
        <div class="gguf-model-item ${isActive ? 'active' : ''}"
             data-path="${m.path}" data-name="${m.filename}" title="${m.path}">
          <div class="gguf-model-item-info">
            <span class="gguf-model-item-name">${m.name}</span>
            <span class="gguf-model-item-size">${sizeMB} MB</span>
          </div>
          <span class="gguf-model-item-status">${isActive ? '● 已加载' : ''}</span>
        </div>`;
    }).join('');

    elements.ggufModelList.innerHTML = html;

    if (state.ggufDirectory) {
      const dirLabel = document.createElement('div');
      dirLabel.className = 'gguf-dir-label';
      dirLabel.textContent = state.ggufDirectory;
      elements.ggufModelList.prepend(dirLabel);
    }
  }

  /**
   * 选择并加载一个 GGUF 模型
   */
  async function selectGGUFModel(modelPath, modelName) {
    if (elements.ggufModelInfo) {
      elements.ggufModelInfo.textContent = `正在加载 ${modelName}...`;
      elements.ggufModelInfo.className = 'gguf-model-info';
    }

    // 高亮选中项
    elements.ggufModelList?.querySelectorAll('.gguf-model-item').forEach(el => {
      el.classList.toggle('selected', el.dataset.path === modelPath);
    });

    try {
      const response = await apiClient.post('/gguf/load', { model_path: modelPath });
      if (response.success) {
        state.ggufLoaded = true;
        state.ggufModelName = response.model;
        state.ggufModelPath = modelPath;
        state.pendingAPI = 'gguf';

        if (elements.ggufModelInfo) {
          elements.ggufModelInfo.textContent = `已加载: ${response.model}`;
          elements.ggufModelInfo.className = 'gguf-model-info loaded';
        }

        // 更新列表中的加载状态
        state.ggufScannedModels.forEach(m => {
          m.loaded = (m.path === modelPath);
        });
        renderGGUFModelList();

        showToast(`模型已加载: ${response.model}`, 'success');
      }
    } catch (error) {
      if (elements.ggufModelInfo) {
        elements.ggufModelInfo.textContent = error.message || '加载失败';
        elements.ggufModelInfo.className = 'gguf-model-info error';
      }
      showToast('模型加载失败', 'error');
    }
  }

  /**
   * 浏览并选择 GGUF 文件
   */
  async function browseGGUFFile() {
    if (!window.pywebview?.api) {
      showToast('开发模式下请使用目录扫描', 'info');
      return;
    }

    const api = window.pywebview.api;
    if (api?.select_gguf_file) {
      try {
        const filePath = await api.select_gguf_file();
        if (filePath) {
          await selectGGUFModel(filePath, filePath.split(/[\\/]/).pop());
        }
      } catch (error) {
        console.error('[StatusBar] File dialog failed:', error);
        showToast('文件选择失败', 'error');
      }
    } else {
      showToast('文件选择对话框不可用', 'info');
    }
  }

  /**
   * 浏览并设置 GGUF 模型目录
   */
  async function browseGGUFDirectory() {
    if (window.pywebview?.api?.select_folder) {
      try {
        const dirPath = await window.pywebview.api.select_folder('选择 GGUF 模型目录');
        if (dirPath) {
          await scanGGUFModels(dirPath);
          showToast(`已设置模型目录: ${dirPath}`, 'success');
        }
      } catch (error) {
        console.error('[StatusBar] Folder dialog failed:', error);
        showToast('目录选择失败', 'error');
      }
    } else {
      const dir = prompt('请输入 GGUF 模型所在目录路径:');
      if (dir) {
        await scanGGUFModels(dir);
      }
    }
  }

  /**
   * 更新 API UI
   */
  function updateAPIUI() {
    if (!elements.apiTrigger) return;

    const apiNames = { ollama: 'Ollama', gguf: '本地 GGUF' };

    elements.apiTrigger.classList.remove('api-ollama', 'api-gguf');
    elements.apiTrigger.classList.add(`api-${state.currentAPI}`);

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
        <span>切换模型</span>
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
      return '<div class="selector-empty">暂无可用模型</div>';
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
      showToast(`已切换模型: ${model}`, 'success');
    } catch (error) {
      console.error('[StatusBar] Failed to set model:', error);
    }
  }

  /**
   * 更新 Model UI
   */
  function updateModelUI() {
    if (elements.modelTrigger) {
      elements.modelTrigger.textContent = `模型: ${state.currentModel}`;
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
      showToast(`RAG 已${state.ragEnabled ? '开启' : '关闭'}`, 'info');

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
      elements.ragTrigger.textContent = state.ragEnabled ? 'RAG: 开启' : 'RAG: 关闭';
      elements.ragTrigger.classList.toggle('status-on', state.ragEnabled);
    }
  }

  // ==================== 经验库模式 ====================

  /**
   * 处理经验库按钮点击
   */
  function handleExpTriggerClick(e) {
    e.preventDefault();
    e.stopPropagation();
    toggleExp();
  }

  /**
   * 切换经验库模式
   */
  function toggleExp() {
    state.expEnabled = !state.expEnabled;
    updateExpUI();

    if (state.expEnabled) {
      showToast('已开启经验库模式 — AI 将完全按照经验库内容回答您的问题', 'success');

      // 通知 AI Service 使用经验库模式
      if (window.AppState?.aiService) {
        window.AppState.aiService.setSystemPrompt?.(
          '你是一个严格基于经验库的工程助手。你只能使用经验库中已有的知识回答用户问题。' +
          '如果经验库中没有相关内容，请明确告知用户"经验库中暂无相关记录"，不要自行推测或编造答案。' +
          '回答时务必引用经验库条目的标题和来源标准。'
        );
      }

      // 触发事件
      if (window.eventBus && typeof Events !== 'undefined') {
        eventBus.emit('exp:enabled');
      }

      // 在聊天区显示系统提示
      if (window.ChatUI?.addSystemMessage) {
        ChatUI.addSystemMessage('已切换到经验库模式 — AI 将完全按照经验库内容回答您的问题');
      }
    } else {
      showToast('已关闭经验库模式 — AI 恢复正常对话', 'info');

      // 恢复默认 system prompt
      if (window.AppState?.aiService) {
        window.AppState.aiService.setSystemPrompt?.('');
      }

      if (window.eventBus && typeof Events !== 'undefined') {
        eventBus.emit('exp:disabled');
      }

      if (window.ChatUI?.addSystemMessage) {
        ChatUI.addSystemMessage('已恢复正常 AI 对话模式');
      }
    }
  }

  /**
   * 更新经验库 UI
   */
  function updateExpUI() {
    if (elements.expTrigger) {
      elements.expTrigger.textContent = state.expEnabled ? '经验库: 开启' : '经验库: 关闭';
      elements.expTrigger.classList.toggle('status-on', state.expEnabled);
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
        <span>内存占用</span>
        <button class="selector-close">&times;</button>
      </div>
      <div class="selector-content">
        <div class="memory-item">
          <span class="memory-label">对话历史</span>
          <span class="memory-value">${memoryInfo.history}</span>
        </div>
        <div class="memory-item">
          <span class="memory-label">消息条数</span>
          <span class="memory-value">${memoryInfo.messageCount}</span>
        </div>
        <div class="memory-item">
          <span class="memory-label">本地存储</span>
          <span class="memory-value">${memoryInfo.localStorage}</span>
        </div>
        <div class="memory-actions">
          <button class="memory-action-btn" id="clear-history-btn">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
            </svg>
            清空历史
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
      elements.memoryTrigger.textContent = `内存: ${memoryInfo.history}`;
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
      showToast('对话历史已清空', 'success');
    } catch (error) {
      console.error('[StatusBar] Failed to clear history:', error);
      showToast('清空历史失败', 'error');
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
    updateExpUI,
    updateMemoryUI,
    getCurrentAPI: () => state.currentAPI,
    getCurrentModel: () => state.currentModel,
    isRAGEnabled: () => state.ragEnabled,
    isExpEnabled: () => state.expEnabled
  };

})();