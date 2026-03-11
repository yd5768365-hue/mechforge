/**
 * APISwitcher - API 切换器模块
 * 处理 Ollama / GGUF 切换逻辑
 */

(function () {
  'use strict';

  const { $ } = Utils;

  // ==================== 状态 ====================
  let currentAPI = 'ollama';
  let pendingAPI = 'ollama';
  let ggufLoaded = false;
  let ggufModelName = '';
  let availableModels = [];

  // ==================== DOM 元素 ====================
  let apiButton = null;
  let apiSelector = null;
  let ggufPathInput = null;
  let ggufLoadBtn = null;
  let ggufBrowseBtn = null;
  let ggufRefreshBtn = null;
  let ggufModelInfo = null;

  /**
   * 初始化 API 切换器
   */
  function init() {
    apiButton = $('api-trigger');
    apiSelector = $('api-selector');
    ggufPathInput = $('gguf-model-path');
    ggufLoadBtn = $('gguf-load-btn');
    ggufBrowseBtn = $('gguf-browse-btn');
    ggufRefreshBtn = $('gguf-refresh-btn');
    ggufModelInfo = $('gguf-model-info');

    // 如果元素未就绪，延迟重试
    if (!apiButton || !apiSelector) {
      setTimeout(init, 100);
      return;
    }

    loadAvailableModels();
    checkGGUFStatus();
    setupEventListeners();
  }

  /**
   * 设置事件监听器
   */
  function setupEventListeners() {
    // 点击 API 按钮切换选择器
    apiButton.addEventListener('click', (e) => {
      e.stopPropagation();
      apiSelector.classList.toggle('active');
      apiButton.classList.toggle('selector-open');
    });

    // 选择器内部点击
    apiSelector.addEventListener('click', handleSelectorClick);

    // 输入框事件
    ggufPathInput?.addEventListener('keypress', (e) => {
      e.stopPropagation();
      if (e.key === 'Enter') loadGGUFModel();
    });

    // 点击外部关闭
    document.addEventListener('click', (e) => {
      if (apiSelector.classList.contains('active') &&
          !apiButton.contains(e.target) &&
          !apiSelector.contains(e.target)) {
        apiSelector.classList.remove('active');
        apiButton.classList.remove('selector-open');
      }
    });
  }

  /**
   * 处理选择器内部点击
   * @param {Event} e - 点击事件
   */
  function handleSelectorClick(e) {
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
   * @param {string} api - API 类型: ollama 或 gguf
   */
  function selectAPI(api) {
    pendingAPI = api;

    document.querySelectorAll('.api-option').forEach(opt => {
      opt.classList.toggle('selected', opt.dataset.api === api);
    });

    if (ggufModelInfo) {
      if (api === 'gguf') {
        ggufModelInfo.textContent = ggufLoaded ? `Ready: ${ggufModelName}` : 'Load a GGUF model first';
        ggufModelInfo.className = ggufLoaded ? 'gguf-model-info loaded' : 'gguf-model-info';
      } else {
        ggufModelInfo.textContent = 'Click Switch to apply';
        ggufModelInfo.className = 'gguf-model-info';
      }
    }
  }

  /**
   * 加载可用模型列表
   */
  async function loadAvailableModels() {
    try {
      availableModels = await apiClient.get('/models');
    } catch (error) {
      console.warn('Failed to load models:', error);
    }
  }

  /**
   * 检查 GGUF 状态
   */
  async function checkGGUFStatus() {
    try {
      const response = await apiClient.get('/gguf/info');
      if (response.loaded) {
        ggufLoaded = true;
        ggufModelName = response.model;

        if (ggufModelInfo) {
          ggufModelInfo.textContent = `Loaded: ${response.model}`;
          ggufModelInfo.className = 'gguf-model-info loaded';
        }
      }
    } catch (error) {
      console.warn('Failed to check GGUF status:', error);
    }
  }

  /**
   * 加载 GGUF 模型
   */
  async function loadGGUFModel() {
    if (!ggufPathInput) return;

    const modelPath = ggufPathInput.value.trim();
    if (!modelPath) {
      if (ggufModelInfo) {
        ggufModelInfo.textContent = 'Please enter model path';
        ggufModelInfo.className = 'gguf-model-info error';
      }
      return;
    }

    if (ggufLoadBtn) ggufLoadBtn.disabled = true;
    if (ggufModelInfo) {
      ggufModelInfo.textContent = 'Loading...';
      ggufModelInfo.className = 'gguf-model-info';
    }

    try {
      const response = await apiClient.post('/gguf/load', { model_path: modelPath });
      if (response.success) {
        ggufLoaded = true;
        ggufModelName = response.model;
        pendingAPI = 'gguf';

        if (ggufModelInfo) {
          ggufModelInfo.textContent = `Loaded: ${response.model}`;
          ggufModelInfo.className = 'gguf-model-info loaded';
        }
        if (ggufLoadBtn) ggufLoadBtn.textContent = 'Loaded';
      }
    } catch (error) {
      if (ggufModelInfo) {
        ggufModelInfo.textContent = error.message || 'Load failed';
        ggufModelInfo.className = 'gguf-model-info error';
      }
      if (ggufLoadBtn) ggufLoadBtn.disabled = false;
    }
  }

  /**
   * 浏览 GGUF 文件
   */
  async function browseGGUFFile() {
    const api = window.pywebview?.api;

    if (api && api.select_gguf_file) {
      const filePath = await api.select_gguf_file();
      if (filePath && ggufPathInput) {
        ggufPathInput.value = filePath;
        await loadGGUFModel();
      }
    } else if (ggufPathInput) {
      ggufPathInput.focus();
    }
  }

  /**
   * 切换到选中的 API
   */
  async function switchToSelectedAPI() {
    const apiNames = { ollama: 'Ollama', gguf: 'Local GGUF' };

    if (pendingAPI === 'gguf' && !ggufLoaded) {
      alert('Please load a GGUF model first');
      return;
    }

    currentAPI = pendingAPI;

    // 关闭选择器
    apiSelector?.classList.remove('active');
    apiButton?.classList.remove('selector-open');

    // 更新按钮显示
    if (apiButton) {
      apiButton.classList.remove('api-ollama', 'api-gguf');
      apiButton.classList.add(`api-${pendingAPI}`);
      apiButton.childNodes[0].textContent = `API: ${apiNames[pendingAPI]} `;
    }

    // 更新模型显示
    const modelEl = document.querySelector('[data-status="model"]');
    if (modelEl) {
      modelEl.textContent = `Model: ${pendingAPI === 'gguf' ? ggufModelName : 'qwen2.5:3b'}`;
    }

    // 通知后端
    try {
      await apiClient.post('/config/provider', { provider: pendingAPI });
    } catch (error) {
      console.error('Switch failed:', error);
    }
  }

  /**
   * 获取当前 API
   * @returns {string}
   */
  function getCurrentAPI() {
    return currentAPI;
  }

  // ==================== 导出 ====================
  window.APISwitcher = {
    init,
    getCurrentAPI,
    selectAPI,
    switchToSelectedAPI
  };

})();