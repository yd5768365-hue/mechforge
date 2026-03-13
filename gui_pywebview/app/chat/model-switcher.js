/**
 * ModelSwitcher - 聊天界面模型切换器
 * 提供模型下拉选择功能
 */

(function () {
  'use strict';

  const { $, escapeHtml } = Utils;

  // ==================== 状态 ====================
  const state = {
    availableModels: [],
    currentModel: null,
    currentProvider: 'ollama',
    isLoading: false
  };

  // ==================== DOM 元素 ====================
  let elements = {
    switcher: null,
    trigger: null,
    dropdown: null,
    modelList: null
  };

  // ==================== 初始化 ====================

  /**
   * 初始化模型切换器
   */
  function init() {
    createSwitcherUI();
    setupEventListeners();
    
    // 先加载当前模型，再加载模型列表
    updateCurrentModel().then(() => {
      loadModels();
    });
    
    // 监听配置更新
    if (typeof eventBus !== 'undefined' && eventBus && typeof Events !== 'undefined') {
      eventBus.on(Events.CONFIG_LOADED, updateCurrentModel);
      eventBus.on(Events.CONFIG_UPDATED, ({ ai }) => {
        if (ai) {
          state.currentModel = ai.model;
          state.currentProvider = ai.provider || 'ollama';
          updateTriggerText(state.currentModel || '未知模型');
        }
      });
    }
    
    console.log('[ModelSwitcher] 初始化完成');
  }

  /**
   * 创建切换器 UI
   */
  function createSwitcherUI() {
    // 使用侧边栏中已有的按钮
    const sidebarTrigger = $('sidebar-model-switcher');
    if (!sidebarTrigger) return;

    elements.trigger = sidebarTrigger;
    
    // 创建下拉菜单容器（相对于侧边栏定位）
    const dropdown = document.createElement('div');
    dropdown.className = 'model-switcher-dropdown';
    dropdown.id = 'model-switcher-dropdown';
    dropdown.style.display = 'none';
    
    const modelList = document.createElement('div');
    modelList.className = 'model-switcher-list';
    modelList.id = 'model-switcher-list';
    
    dropdown.appendChild(modelList);
    
    // 添加到 body，使用绝对定位
    document.body.appendChild(dropdown);
    
    elements.dropdown = dropdown;
    elements.modelList = modelList;
    
    // 添加样式
    addStyles();
  }

  /**
   * 添加样式
   */
  function addStyles() {
    if (document.getElementById('model-switcher-styles')) return;
    
    const style = document.createElement('style');
    style.id = 'model-switcher-styles';
    style.textContent = `
      .model-switcher {
        position: relative;
        margin: 8px 16px;
      }
      
      .model-switcher-trigger {
        width: 100%;
        padding: 8px 12px;
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 6px;
        color: var(--text-primary);
        font-size: 12px;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: all 0.2s;
      }
      
      .model-switcher-trigger:hover {
        background: rgba(0, 229, 255, 0.1);
        border-color: rgba(0, 229, 255, 0.4);
      }
      
      .model-switcher-icon {
        font-size: 14px;
      }
      
      .model-switcher-text {
        flex: 1;
        text-align: left;
        font-weight: 500;
      }
      
      .model-switcher-arrow {
        transition: transform 0.2s;
        color: var(--text-dim);
      }
      
      .model-switcher.open .model-switcher-arrow {
        transform: rotate(180deg);
      }
      
      .model-switcher-dropdown {
        position: fixed;
        left: 68px;
        bottom: 12px;
        width: 320px;
        background: rgba(10, 14, 20, 0.98);
        border: 1px solid rgba(0, 229, 255, 0.3);
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        z-index: 10000;
        max-height: 400px;
        overflow-y: auto;
      }
      
      .sidebar-icon.model-switcher-trigger {
        margin-top: auto;
      }
      
      .sidebar-icon.model-switcher-trigger.active {
        background: rgba(0, 229, 255, 0.15);
        border-color: rgba(0, 229, 255, 0.4);
        color: var(--accent-primary);
      }
      
      .model-switcher-label {
        font-size: 10px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
      }
      
      .model-switcher-list {
        padding: 4px;
      }
      
      .model-group {
        margin-bottom: 8px;
      }
      
      .model-group-label {
        padding: 6px 12px;
        font-size: 10px;
        font-weight: 600;
        color: var(--accent-primary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      
      .model-item {
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: all 0.2s;
        margin-bottom: 2px;
      }
      
      .model-item:hover {
        background: rgba(0, 229, 255, 0.1);
      }
      
      .model-item.selected {
        background: rgba(0, 229, 255, 0.15);
        border-left: 2px solid var(--accent-primary);
      }
      
      .model-item-name {
        flex: 1;
        font-size: 12px;
        color: var(--text-primary);
        font-weight: 500;
      }
      
      .model-item-meta {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 10px;
        color: var(--text-dim);
      }
      
      .model-item-status {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: rgba(0, 229, 255, 0.5);
      }
      
      .model-item-status.loaded {
        background: #50fa7b;
        box-shadow: 0 0 6px rgba(80, 250, 123, 0.5);
      }
      
      .model-switcher-loading {
        padding: 12px;
        text-align: center;
        color: var(--text-dim);
        font-size: 11px;
      }
      
      .model-switcher-empty {
        padding: 12px;
        text-align: center;
        color: var(--text-dim);
        font-size: 11px;
      }
    `;
    document.head.appendChild(style);
  }

  /**
   * 设置事件监听器
   */
  function setupEventListeners() {
    // 点击触发按钮
    elements.trigger?.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleDropdown();
    });
    
    // 点击外部关闭
    document.addEventListener('click', (e) => {
      if (!elements.trigger?.contains(e.target) && !elements.dropdown?.contains(e.target)) {
        closeDropdown();
      }
    });
    
    // ESC 关闭
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && elements.dropdown?.style.display !== 'none') {
        closeDropdown();
      }
    });
    
    // 窗口大小改变时重新定位
    window.addEventListener('resize', () => {
      if (elements.dropdown?.style.display !== 'none') {
        openDropdown(); // 重新计算位置
      }
    });
  }

  /**
   * 切换下拉菜单
   */
  function toggleDropdown() {
    if (elements.dropdown?.style.display === 'none') {
      openDropdown();
    } else {
      closeDropdown();
    }
  }

  /**
   * 打开下拉菜单
   */
  function openDropdown() {
    if (!elements.dropdown || !elements.trigger) return;
    
    // 计算位置（侧边栏右侧）
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
      const rect = sidebar.getBoundingClientRect();
      elements.dropdown.style.left = `${rect.right + 8}px`;
      elements.dropdown.style.bottom = `${window.innerHeight - rect.bottom + 12}px`;
    }
    
    elements.dropdown.style.display = 'block';
    elements.trigger.classList.add('active');
    renderModelList();
  }

  /**
   * 关闭下拉菜单
   */
  function closeDropdown() {
    if (!elements.dropdown || !elements.trigger) return;
    
    elements.dropdown.style.display = 'none';
    elements.trigger.classList.remove('active');
  }

  /**
   * 加载模型列表
   */
  async function loadModels() {
    if (state.isLoading) return;
    
    state.isLoading = true;
    updateTriggerText('加载中...');
    
    try {
      const response = await apiClient.get('/models');
      state.availableModels = Array.isArray(response) ? response : [];
      
      // 获取当前模型
      await updateCurrentModel();
      
      renderModelList();
    } catch (error) {
      console.error('[ModelSwitcher] 加载模型列表失败:', error);
      updateTriggerText('加载失败');
    } finally {
      state.isLoading = false;
    }
  }

  /**
   * 更新当前模型
   */
  async function updateCurrentModel() {
    try {
      const config = await apiClient.get('/config');
      if (config?.ai) {
        state.currentModel = config.ai.model;
        state.currentProvider = config.ai.provider || 'ollama';
        updateTriggerText(state.currentModel || '加载中...');
        return true;
      }
    } catch (error) {
      console.error('[ModelSwitcher] 获取当前模型失败:', error);
      updateTriggerText('未知模型');
    }
    return false;
  }

  /**
   * 更新触发按钮文本（在侧边栏标签中显示）
   */
  function updateTriggerText(text) {
    const labelEl = elements.trigger?.querySelector('.model-switcher-label');
    if (labelEl) {
      // 如果文本太长，截断
      const shortText = text.length > 6 ? text.substring(0, 6) + '...' : text;
      labelEl.textContent = shortText;
      elements.trigger.title = `当前模型: ${text}`;
    }
  }

  /**
   * 渲染模型列表
   */
  function renderModelList() {
    if (!elements.modelList) return;
    
    if (state.isLoading) {
      elements.modelList.innerHTML = '<div class="model-switcher-loading">加载中...</div>';
      return;
    }
    
    if (state.availableModels.length === 0) {
      elements.modelList.innerHTML = '<div class="model-switcher-empty">暂无可用模型</div>';
      return;
    }
    
    // 按 provider 分组
    const grouped = {};
    state.availableModels.forEach(m => {
      const provider = m.provider || 'unknown';
      if (!grouped[provider]) grouped[provider] = [];
      grouped[provider].push(m);
    });
    
    let html = '';
    for (const [provider, models] of Object.entries(grouped)) {
      html += `<div class="model-group">
        <div class="model-group-label">${provider.toUpperCase()}</div>
        ${models.map(m => {
          const isSelected = m.name === state.currentModel && m.provider === state.currentProvider;
          const sizeText = m.size ? formatSize(m.size) : '';
          return `
            <div class="model-item ${isSelected ? 'selected' : ''}" 
                 data-model="${escapeHtml(m.name)}" 
                 data-provider="${escapeHtml(m.provider || 'unknown')}">
              <span class="model-item-name">${escapeHtml(m.name)}</span>
              <div class="model-item-meta">
                ${sizeText ? `<span>${sizeText}</span>` : ''}
                <span class="model-item-status ${m.loaded ? 'loaded' : ''}"></span>
              </div>
            </div>
          `;
        }).join('')}
      </div>`;
    }
    
    elements.modelList.innerHTML = html;
    
    // 绑定点击事件
    elements.modelList.querySelectorAll('.model-item').forEach(item => {
      item.addEventListener('click', async () => {
        const model = item.dataset.model;
        const provider = item.dataset.provider;
        await selectModel(model, provider);
      });
    });
  }

  /**
   * 选择模型
   */
  async function selectModel(model, provider) {
    if (state.isLoading) return;
    
    state.isLoading = true;
    updateTriggerText('切换中...');
    closeDropdown();
    
    try {
      const response = await apiClient.post('/config/model', {
        model,
        provider
      });
      
      if (response?.success) {
        state.currentModel = model;
        state.currentProvider = provider;
        updateTriggerText(model);
        
        // 显示成功提示
        if (window.showToast) {
          window.showToast(`已切换到 ${model}`, 'success');
        }
        
        // 触发配置更新事件
        if (typeof eventBus !== 'undefined' && eventBus && typeof Events !== 'undefined') {
          eventBus.emit(Events.CONFIG_UPDATED, { ai: { model, provider } });
          
          // 如果 AIService 存在，更新其 provider
          if (window.AppState && window.AppState.aiService) {
            window.AppState.aiService.setProvider(provider);
          }
        }
      } else {
        throw new Error(response?.message || '切换失败');
      }
    } catch (error) {
      console.error('[ModelSwitcher] 切换模型失败:', error);
      updateTriggerText(state.currentModel || '切换失败');
      
      if (window.showToast) {
        window.showToast(`切换失败: ${error.message}`, 'error');
      }
    } finally {
      state.isLoading = false;
    }
  }

  /**
   * 格式化文件大小
   */
  function formatSize(bytes) {
    if (!bytes) return '';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  }

  // ==================== 导出 ====================
  window.ModelSwitcher = {
    init,
    loadModels,
    updateCurrentModel
  };

})();
