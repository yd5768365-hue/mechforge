/**
 * ModeIndicator - AI 模式指示器模块
 * 显示当前AI模式（正常聊天/知识库）并提供切换功能
 */

(function () {
  'use strict';

  // ==================== 状态 ====================
  let currentMode = 'chat';
  let indicatorElement = null;
  let badgeElement = null;
  let tooltipElement = null;

  // ==================== 配置 ====================
  const MODE_CONFIG = {
    chat: {
      label: 'AI 聊天',
      icon: '💬',
      color: '#00e5ff',
      bgColor: 'rgba(0, 229, 255, 0.1)',
      description: '友好对话模式 - 可以聊任何话题',
      className: 'mode-chat'
    },
    knowledge: {
      label: '知识库',
      icon: '📚',
      color: '#ff6b35',
      bgColor: 'rgba(255, 107, 53, 0.1)',
      description: '知识库模式 - 仅回答技术问题',
      className: 'mode-knowledge'
    }
  };

  // ==================== 初始化 ====================
  function init() {
    createIndicator();
    bindEvents();
    console.log('[ModeIndicator] Initialized');
  }

  /**
   * 创建模式指示器元素
   */
  function createIndicator() {
    // 检查是否已存在
    if (document.getElementById('mode-indicator')) {
      return;
    }

    // 创建指示器容器
    indicatorElement = document.createElement('div');
    indicatorElement.id = 'mode-indicator';
    indicatorElement.className = 'mode-indicator mode-chat';
    indicatorElement.innerHTML = `
      <span class="mode-icon">💬</span>
      <span class="mode-label">AI 聊天</span>
      <span class="mode-arrow">▼</span>
    `;

    // 创建下拉菜单
    const dropdown = document.createElement('div');
    dropdown.className = 'mode-dropdown';
    dropdown.innerHTML = `
      <div class="mode-option" data-mode="chat">
        <span class="mode-option-icon">💬</span>
        <div class="mode-option-info">
          <span class="mode-option-label">AI 聊天模式</span>
          <span class="mode-option-desc">友好对话，可以聊任何话题</span>
        </div>
      </div>
      <div class="mode-option" data-mode="knowledge">
        <span class="mode-option-icon">📚</span>
        <div class="mode-option-info">
          <span class="mode-option-label">知识库模式</span>
          <span class="mode-option-desc">仅回答机械工程技术问题</span>
        </div>
      </div>
    `;
    indicatorElement.appendChild(dropdown);

    // 创建提醒徽章
    badgeElement = document.createElement('div');
    badgeElement.id = 'mode-badge';
    badgeElement.className = 'mode-badge hidden';
    badgeElement.innerHTML = `
      <span class="badge-icon">⚠️</span>
      <span class="badge-text">知识库模式已激活</span>
      <span class="badge-close">×</span>
    `;

    // 创建提示框
    tooltipElement = document.createElement('div');
    tooltipElement.id = 'mode-tooltip';
    tooltipElement.className = 'mode-tooltip';

    // 添加到页面
    const chatPanel = document.getElementById('chat-panel');
    if (chatPanel) {
      chatPanel.insertBefore(indicatorElement, chatPanel.firstChild);
      chatPanel.insertBefore(badgeElement, chatPanel.firstChild);
    }

    document.body.appendChild(tooltipElement);

    // 绑定下拉菜单事件
    dropdown.querySelectorAll('.mode-option').forEach(option => {
      option.addEventListener('click', (e) => {
        const mode = e.currentTarget.dataset.mode;
        switchMode(mode);
        hideDropdown();
      });
    });

    // 点击外部关闭下拉菜单
    document.addEventListener('click', (e) => {
      if (!indicatorElement.contains(e.target)) {
        hideDropdown();
      }
    });

    // 指示器点击事件
    indicatorElement.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleDropdown();
    });

    // 徽章关闭按钮
    badgeElement.querySelector('.badge-close').addEventListener('click', () => {
      hideBadge();
    });
  }

  /**
   * 绑定事件监听
   */
  function bindEvents() {
    // 监听模式切换事件
    if (window.eventBus) {
      eventBus.on(Events.MODE_SWITCHED_TO_KNOWLEDGE, () => {
        updateUI('knowledge');
        showKnowledgeModeAlert();
      });

      eventBus.on(Events.MODE_SWITCHED_TO_CHAT, () => {
        updateUI('chat');
        hideBadge();
      });

      eventBus.on(Events.RAG_ENABLED, () => {
        // 当RAG启用时，自动切换到知识库模式
        if (currentMode !== 'knowledge') {
          switchMode('knowledge');
        }
      });

      eventBus.on(Events.RAG_DISABLED, () => {
        // 当RAG禁用时，切换回聊天模式
        if (currentMode === 'knowledge') {
          switchMode('chat');
        }
      });
    }
  }

  // ==================== UI 操作 ====================

  /**
   * 切换下拉菜单显示
   */
  function toggleDropdown() {
    indicatorElement.classList.toggle('open');
  }

  /**
   * 隐藏下拉菜单
   */
  function hideDropdown() {
    indicatorElement.classList.remove('open');
  }

  /**
   * 显示知识库模式提醒
   */
  function showKnowledgeModeAlert() {
    badgeElement.classList.remove('hidden');
    badgeElement.classList.add('show');

    // 5秒后自动隐藏
    setTimeout(() => {
      hideBadge();
    }, 5000);
  }

  /**
   * 隐藏徽章
   */
  function hideBadge() {
    badgeElement.classList.remove('show');
    badgeElement.classList.add('hidden');
  }

  /**
   * 更新UI
   * @param {string} mode - 'chat' 或 'knowledge'
   */
  function updateUI(mode) {
    currentMode = mode;
    const config = MODE_CONFIG[mode];

    // 更新指示器
    indicatorElement.className = `mode-indicator ${config.className}`;
    indicatorElement.querySelector('.mode-icon').textContent = config.icon;
    indicatorElement.querySelector('.mode-label').textContent = config.label;

    // 更新选中状态
    const dropdown = indicatorElement.querySelector('.mode-dropdown');
    dropdown.querySelectorAll('.mode-option').forEach(option => {
      option.classList.toggle('active', option.dataset.mode === mode);
    });

    // 更新提示框
    tooltipElement.textContent = config.description;

    console.log(`[ModeIndicator] Mode switched to: ${mode}`);
  }

  // ==================== 模式切换 ====================

  /**
   * 切换模式
   * @param {string} mode - 'chat' 或 'knowledge'
   */
  async function switchMode(mode) {
    if (mode === currentMode) return;

    try {
      if (window.aiService) {
        await aiService.setMode(mode);
      }
      updateUI(mode);
    } catch (error) {
      console.error('[ModeIndicator] Failed to switch mode:', error);
      showError(`模式切换失败: ${error.message}`);
    }
  }

  /**
   * 显示错误提示（使用统一 NotificationManager）
   * @param {string} message - 错误消息
   */
  function showError(message) {
    if (window.showToast) {
      window.showToast(message, 'error');
    } else {
      console.error('[ModeIndicator]', message);
    }
  }

  // ==================== 公共 API ====================

  /**
   * 获取当前模式
   * @returns {string}
   */
  function getCurrentMode() {
    return currentMode;
  }

  /**
   * 是否为知识库模式
   * @returns {boolean}
   */
  function isKnowledgeMode() {
    return currentMode === 'knowledge';
  }

  /**
   * 手动设置模式（不触发API调用）
   * @param {string} mode - 'chat' 或 'knowledge'
   */
  function setModeUI(mode) {
    updateUI(mode);
  }

  // ==================== 导出 ====================
  window.ModeIndicator = {
    init,
    switchMode,
    getCurrentMode,
    isKnowledgeMode,
    setModeUI
  };
})();
