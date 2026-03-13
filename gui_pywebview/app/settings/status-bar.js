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
      modelTrigger: document.querySelector('[data-status="model"]'),
      ragTrigger: document.querySelector('[data-status="rag"]'),
      memoryTrigger: document.querySelector('[data-status="memory"]'),
      expTrigger: document.querySelector('[data-status="exp"]'),
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

      if (window.aiService) {
        window.aiService.setProvider(state.currentAPI);
      }

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

    // Model 按钮点击
    elements.modelTrigger?.addEventListener('click', handleModelTriggerClick);

    // RAG 按钮点击
    elements.ragTrigger?.addEventListener('click', handleRAGTriggerClick);

    // Memory 按钮点击
    elements.memoryTrigger?.addEventListener('click', handleMemoryTriggerClick);

    // 经验库按钮点击
    elements.expTrigger?.addEventListener('click', handleExpTriggerClick);

    // 点击外部关闭选择器
    document.addEventListener('click', handleDocumentClick, false);

    // 定期更新内存
    setInterval(updateMemoryUI, 30000);

    // 定期同步后端 provider/model 状态（每 5 秒）
    setInterval(syncProviderState, 5000);

    // 监听 model-loaded 事件（内置模型下载完成后触发）
    if (window.eventBus) {
      window.eventBus.on('model-loaded', () => {
        syncProviderState();
      });
      // 设置面板保存配置后立即同步
      if (typeof Events !== 'undefined') {
        window.eventBus.on(Events.CONFIG_UPDATED, () => {
          syncProviderState();
        });
      }
    }
  }

  /**
   * 从后端同步当前 provider 和 model 状态
   */
  async function syncProviderState() {
    try {
      const [config, ggufInfo] = await Promise.all([
        apiClient.getConfig().catch(() => null),
        apiClient.get('/gguf/info').catch(() => ({ loaded: false }))
      ]);

      if (!config) return;

      const newAPI = config.ai?.provider || 'ollama';
      const newModel = config.ai?.model || state.currentModel;
      const newRAG = config.rag?.enabled ?? state.ragEnabled;

      const changed = newAPI !== state.currentAPI || newModel !== state.currentModel || newRAG !== state.ragEnabled;

      state.currentAPI = newAPI;
      state.currentModel = newModel;
      state.ragEnabled = newRAG;
      state.ggufLoaded = ggufInfo.loaded || false;
      state.ggufModelName = ggufInfo.model || '';
      state.ggufModelPath = ggufInfo.model_path || '';

      if (changed) {
        if (window.aiService) {
          window.aiService.setProvider(state.currentAPI);
        }
        updateAPIUI();
        updateModelUI();
        updateRAGUI();
      }
    } catch (e) {
      // 静默忽略
    }
  }

  /**
   * 处理文档点击（关闭选择器）
   */
  function handleDocumentClick(e) {
    const target = e.target;

    if ($('model-selector-popup')?.contains(target)) return;
    if ($('memory-popup')?.contains(target)) return;

    if (elements.modelTrigger?.contains(target)) return;
    if (elements.memoryTrigger?.contains(target)) return;
    if (elements.ragTrigger?.contains(target)) return;
    if (elements.expTrigger?.contains(target)) return;
    if (elements.apiTrigger?.contains(target)) return;

    closeAllSelectors();
  }

  /**
   * 处理 API 按钮点击 — 直接切换 Ollama ↔ GGUF
   */
  function handleAPITriggerClick(e) {
    e.preventDefault();
    e.stopPropagation();
    toggleProvider();
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

  // ==================== Provider 切换 ====================

  /**
   * 一键切换 Ollama ↔ 本地 GGUF
   */
  async function toggleProvider() {
    const targetAPI = state.currentAPI === 'gguf' ? 'ollama' : 'gguf';
    const apiNames = { ollama: 'Ollama', gguf: '本地模型' };

    if (targetAPI === 'gguf' && !state.ggufLoaded) {
      showToast('本地模型未加载，请先在聊天界面下载内置模型', 'warning');
      return;
    }

    const prevAPI = state.currentAPI;
    state.currentAPI = targetAPI;
    state.pendingAPI = targetAPI;

    if (targetAPI === 'gguf') {
      state.currentModel = state.ggufModelName || 'gguf-local';
    } else {
      const ollamaModel = state.availableModels.find(m => m.provider === 'ollama');
      state.currentModel = ollamaModel?.name || 'qwen2.5:3b';
    }

    updateAPIUI();
    updateModelUI();

    try {
      await apiClient.post('/config/provider', { provider: targetAPI });
      if (window.aiService) {
        window.aiService.setProvider(targetAPI);
      }
      showToast(`已切换到 ${apiNames[targetAPI]}`, 'success');
    } catch (error) {
      console.error('[StatusBar] Provider switch failed:', error);
      state.currentAPI = prevAPI;
      updateAPIUI();
      updateModelUI();
      showToast('切换失败: ' + (error.message || ''), 'error');
    }
  }

  /**
   * 更新 API UI — 实时反映当前 provider 状态
   */
  function updateAPIUI() {
    if (!elements.apiTrigger) return;

    const isGGUF = state.currentAPI === 'gguf';
    const apiLabel = isGGUF ? '本地模型' : 'Ollama';
    const apiIcon = isGGUF ? '📦' : '🦙';

    elements.apiTrigger.classList.remove('api-ollama', 'api-gguf');
    elements.apiTrigger.classList.add(`api-${state.currentAPI}`);
    elements.apiTrigger.textContent = `${apiIcon} ${apiLabel}`;
    elements.apiTrigger.title = isGGUF
      ? '当前: 本地 GGUF 模型 — 点击切换到 Ollama'
      : '当前: Ollama — 点击切换到本地模型';
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

    try {
      const modelData = state.availableModels.find(m => m.name === model && m.provider === provider);
      await apiClient.post('/config/model', {
        model,
        provider,
        model_path: modelData?.path || ''
      });
      if (window.aiService) {
        window.aiService.setProvider(provider);
      }
      showToast(`已切换模型: ${model}`, 'success');
    } catch (error) {
      console.error('[StatusBar] Failed to set model:', error);
      showToast('模型切换失败: ' + (error.message || ''), 'error');
    }
  }

  /**
   * 更新 Model UI — 显示当前模型名及来源
   */
  function updateModelUI() {
    if (!elements.modelTrigger) return;

    let displayName = state.currentModel || '未选择';
    if (displayName.length > 25) {
      displayName = displayName.substring(0, 22) + '…';
    }
    elements.modelTrigger.textContent = `模型: ${displayName}`;
    elements.modelTrigger.title = `${state.currentAPI === 'gguf' ? '本地 GGUF' : 'Ollama'} — ${state.currentModel}`;
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
   * 显示提示（使用统一 NotificationManager）
   */
  function showToast(message, type = 'info') {
    if (window.showToast) {
      window.showToast(message, type);
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