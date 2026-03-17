/**
 * MechForge AI - Settings Panel
 * 设置面板控制器
 * 完全独立：不依赖 index.html 的 CSS
 */

(function() {
  'use strict';

  // ==================== 加载自己的 CSS ====================
  (function() {
    const cssFiles = ['css/settings.css', 'css/industrial-theme.css'];
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
  const SETTINGS_PANEL_HTML = `
<!-- Settings Panel -->
<div class="tab-panel" id="settings-panel">
  <!-- 工业风背景 -->
  <div class="industrial-background"></div>

  <!-- 面板头部 -->
  <div class="panel-header">
    <span class="header-mark">系统</span>
    <h2>设置</h2>
    <p>应用配置与个性化选项</p>
    <span class="archive-id">MECHFORGE-CFG-V3.0</span>
  </div>

  <!-- 可滑动设置内容区 -->
  <div class="settings-scroll-container" id="settings-scroll">
    <!-- API 配置 -->
    <div class="settings-section">
      <div class="settings-section-title">
        <span class="section-icon">🔌</span>
        <span>API 配置</span>
      </div>
      <div class="settings-card">
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">AI 服务提供商</div>
            <div class="setting-desc">选择使用的 AI 后端服务</div>
          </div>
          <select class="setting-select" id="setting-provider">
            <option value="ollama">Ollama (本地)</option>
            <option value="gguf">GGUF (本地模型)</option>
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
          </select>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">API Key</div>
            <div class="setting-desc">在线服务所需的 API 密钥</div>
          </div>
          <input type="password" class="setting-input" id="setting-apikey" placeholder="sk-...">
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">模型名称</div>
            <div class="setting-desc">使用的 AI 模型</div>
          </div>
          <input type="text" class="setting-input" id="setting-model" placeholder="gpt-4o-mini">
        </div>
      </div>
    </div>

    <!-- 界面设置 -->
    <div class="settings-section">
      <div class="settings-section-title">
        <span class="section-icon">🎨</span>
        <span>界面设置</span>
      </div>
      <div class="settings-card">
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">主题</div>
            <div class="setting-desc">选择界面主题风格</div>
          </div>
          <select class="setting-select" id="setting-theme">
            <option value="dark">深色 (默认)</option>
            <option value="light">浅色</option>
            <option value="industrial">工业风</option>
          </select>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">语言</div>
            <div class="setting-desc">界面显示语言</div>
          </div>
          <select class="setting-select" id="setting-language">
            <option value="zh-CN">简体中文</option>
            <option value="en">English</option>
          </select>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">字体大小</div>
            <div class="setting-desc">调整界面字体大小</div>
          </div>
          <input type="range" class="setting-slider" id="setting-fontsize" min="12" max="20" value="14">
        </div>
      </div>
    </div>

    <!-- Daily Feed 设置 -->
    <div class="settings-section">
      <div class="settings-section-title">
        <span class="section-icon">📡</span>
        <span>Daily Feed 设置</span>
      </div>
      <div class="settings-card">
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">启用 Daily Feed</div>
            <div class="setting-desc">在经验库显示每日知识推送</div>
          </div>
          <button type="button" class="setting-btn setting-btn-daily" id="setting-daily-enabled-btn">
            开启
          </button>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">每日推送数量</div>
            <div class="setting-desc">每次生成的知识条目数</div>
          </div>
          <input type="range" class="setting-slider" id="setting-daily-count" min="1" max="5" value="3">
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">推送时间</div>
            <div class="setting-desc">自动生成时间 (自动模式)</div>
          </div>
          <input type="time" class="setting-input" id="setting-daily-time" value="07:00">
        </div>
      </div>
    </div>

    <!-- 知识库设置 -->
    <div class="settings-section">
      <div class="settings-section-title">
        <span class="section-icon">📚</span>
        <span>知识库设置</span>
      </div>
      <div class="settings-card">
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">知识库路径</div>
            <div class="setting-desc">本地知识库文件夹位置</div>
          </div>
          <div class="setting-path">
            <input type="text" class="setting-input" id="setting-kb-path" readonly value="./knowledge">
            <button class="setting-btn" id="btn-select-kb">选择</button>
          </div>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">启用 RAG</div>
            <div class="setting-desc">检索增强生成功能</div>
          </div>
          <label class="setting-toggle">
            <input type="checkbox" id="setting-rag-enabled" checked>
            <span class="toggle-slider"></span>
          </label>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">RAGFlow 向导</div>
            <div class="setting-desc">配置 RAGFlow 云端知识库（支持 OCR、表格解析）</div>
          </div>
          <button class="setting-btn primary" id="btn-ragflow-wizard" onclick="openRagflowWizard()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
            </svg>
            启动向导
          </button>
        </div>
        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-name">Obsidian 同步</div>
            <div class="setting-desc">同步 Obsidian Vault 笔记到知识库</div>
          </div>
          <button class="setting-btn" id="btn-obsidian-sync" onclick="openObsidianSyncPanel()">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            配置
          </button>
        </div>
      </div>
    </div>

    <!-- 关于 -->
    <div class="settings-section">
      <div class="settings-section-title">
        <span class="section-icon">ℹ️</span>
        <span>关于</span>
      </div>
      <div class="settings-card about-card">
        <div class="about-logo">
          <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#00e5ff" stroke-width="1.5">
            <path d="M12 2L2 7l10 5 10-5-10-5z"/>
            <path d="M2 17l10 5 10-5"/>
            <path d="M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div class="about-info">
          <div class="about-name">MechForge AI</div>
          <div class="about-version">版本 0.5.0</div>
          <div class="about-desc">机械工程智能助手</div>
        </div>
        <div class="about-links">
          <a href="#" class="about-link">文档</a>
          <a href="#" class="about-link">GitHub</a>
          <a href="#" class="about-link">反馈</a>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="settings-actions">
      <button class="settings-btn secondary" id="btn-reset">重置</button>
      <button class="settings-btn primary" id="btn-save">保存设置</button>
    </div>
  </div>
</div>
`;

  // 导出到全局
  window.SettingsPanel = {
    init: initSettingsPanel,
    isInitialized: false,
    html: SETTINGS_PANEL_HTML
  };

  // 默认配置
  const DEFAULT_CONFIG = {
    provider: 'ollama',
    apiKey: '',
    model: 'qwen2.5:3b',
    theme: 'dark',
    language: 'zh-CN',
    fontSize: 14,
    dailyEnabled: true,
    dailyCount: 3,
    dailyTime: '07:00',
    kbPath: './knowledge',
    ragEnabled: true
  };

  // 当前配置
  let config = { ...DEFAULT_CONFIG };

  // DOM 元素缓存
  const elements = {};

  /**
   * 加载设置面板 HTML
   */
  function loadHtml() {
    return new Promise((resolve) => {
      const placeholder = document.getElementById('settings-panel-placeholder');

      if (placeholder) {
        placeholder.outerHTML = SETTINGS_PANEL_HTML;
        console.log('[SettingsPanel] HTML 已加载到页面');
      } else {
        const existingPanel = document.getElementById('settings-panel');
        if (!existingPanel) {
          // 查找 experience-panel 并在其后插入
          const experiencePanel = document.getElementById('experience-panel');
          if (experiencePanel) {
            experiencePanel.insertAdjacentHTML('afterend', SETTINGS_PANEL_HTML);
          }
        }
      }

      resolve();
    });
  }

  /**
   * 初始化设置面板
   */
  async function initSettingsPanel() {
    if (window.SettingsPanel.isInitialized) {
      return;
    }

    console.log('[Settings] 初始化设置面板');

    // 加载 HTML
    await loadHtml();

    // 缓存 DOM 元素
    cacheElements();

    // 加载配置（优先后端，再合并 localStorage）
    await loadConfig();

    // 绑定事件
    bindEvents();

    // 应用当前配置到 UI
    applyConfig();

    window.SettingsPanel.isInitialized = true;
    console.log('[Settings] 初始化完成');
  }

  // 保留原有 init 别名
  function init() {
    return initSettingsPanel();
  }

  // 立即执行
  loadHtml().then(() => {
    cacheElements();
    loadConfig().then(() => {
      bindEvents();
      applyConfig();
      window.SettingsPanel.isInitialized = true;
    });
  });

  /**
   * 缓存 DOM 元素
   */
  function cacheElements() {
    const ids = [
      'setting-provider',
      'setting-apikey',
      'setting-model',
      'setting-theme',
      'setting-language',
      'setting-fontsize',
      'setting-daily-enabled-btn',
      'setting-daily-count',
      'setting-daily-time',
      'setting-kb-path',
      'setting-rag-enabled',
      'btn-select-kb',
      'btn-reset',
      'btn-save'
    ];

    ids.forEach(id => {
      elements[id] = document.getElementById(id);
    });
  }

  /**
   * 绑定事件
   */
  function bindEvents() {
    // 保存按钮
    if (elements['btn-save']) {
      elements['btn-save'].addEventListener('click', saveConfig);
    }

    // 重置按钮
    if (elements['btn-reset']) {
      elements['btn-reset'].addEventListener('click', resetConfig);
    }

    // 选择知识库路径
    if (elements['btn-select-kb']) {
      elements['btn-select-kb'].addEventListener('click', selectKbPath);
    }

    // 实时预览主题
    if (elements['setting-theme']) {
      elements['setting-theme'].addEventListener('change', (e) => {
        previewTheme(e.target.value);
      });
    }

    // 实时预览字体大小
    if (elements['setting-fontsize']) {
      elements['setting-fontsize'].addEventListener('input', (e) => {
        previewFontSize(e.target.value);
      });
    }

    // 滑块值显示
    if (elements['setting-daily-count']) {
      elements['setting-daily-count'].addEventListener('input', (e) => {
        showSliderValue(e.target, e.target.value + ' 条');
      });
    }

    // Daily Feed 按钮开关
    if (elements['setting-daily-enabled-btn']) {
      elements['setting-daily-enabled-btn'].addEventListener('click', toggleDailyFeed);
    }
  }

  // Daily Feed 开关状态
  let dailyFeedEnabled = true;

  /**
   * 切换 Daily Feed 开关
   */
  function toggleDailyFeed() {
    dailyFeedEnabled = !dailyFeedEnabled;
    updateDailyFeedBtn();
  }

  /**
   * 更新按钮样式和文本
   */
  function updateDailyFeedBtn() {
    const btn = elements['setting-daily-enabled-btn'];
    if (!btn) return;

    btn.classList.remove('is-on', 'is-off');
    if (dailyFeedEnabled) {
      btn.textContent = '开启';
      btn.classList.add('is-on');
    } else {
      btn.textContent = '关闭';
      btn.classList.add('is-off');
    }
  }

  /**
   * 获取 API 基础地址
   */
  function getApiBase() {
    if (window.location && window.location.protocol === 'file:') {
      return 'http://localhost:5000';
    }
    return window.location?.origin || 'http://localhost:5000';
  }

  /**
   * 加载配置（优先从后端，再合并 localStorage）
   */
  async function loadConfig() {
    try {
      const res = await fetch(`${getApiBase()}/api/config`);
      if (res.ok) {
        const data = await res.json();
        config = {
          ...DEFAULT_CONFIG,
          provider: data.ai?.provider || 'ollama',
          model: data.ai?.model || '',
          theme: data.ui?.theme || 'dark',
          language: data.ui?.language || 'zh-CN',
          kbPath: data.knowledge?.path || './knowledge',
          ragEnabled: data.rag?.enabled ?? true
        };
        console.log('[Settings] 已从后端加载配置');
      }
    } catch (e) {
      console.warn('[Settings] 从后端加载失败，使用本地缓存:', e);
    }

    try {
      const saved = localStorage.getItem('mechforge-config');
      if (saved) {
        const parsed = JSON.parse(saved);
        config = {
          ...config,
          apiKey: parsed.apiKey ?? config.apiKey,
          fontSize: parsed.fontSize ?? config.fontSize,
          dailyEnabled: parsed.dailyEnabled ?? config.dailyEnabled,
          dailyCount: parsed.dailyCount ?? config.dailyCount,
          dailyTime: parsed.dailyTime ?? config.dailyTime
        };
      }
    } catch (e) {
      console.warn('[Settings] 合并 localStorage 失败:', e);
    }
  }

  /**
   * 应用配置到 UI
   */
  function applyConfig() {
    if (elements['setting-provider']) {
      elements['setting-provider'].value = config.provider;
    }
    if (elements['setting-apikey']) {
      elements['setting-apikey'].value = config.apiKey;
    }
    if (elements['setting-model']) {
      elements['setting-model'].value = config.model;
    }
    if (elements['setting-theme']) {
      elements['setting-theme'].value = config.theme;
    }
    if (elements['setting-language']) {
      elements['setting-language'].value = config.language;
    }
    if (elements['setting-fontsize']) {
      elements['setting-fontsize'].value = config.fontSize;
    }
    if (elements['setting-daily-enabled-btn']) {
      dailyFeedEnabled = config.dailyEnabled;
      updateDailyFeedBtn();
    }
    if (elements['setting-daily-count']) {
      elements['setting-daily-count'].value = config.dailyCount;
    }
    if (elements['setting-daily-time']) {
      elements['setting-daily-time'].value = config.dailyTime;
    }
    if (elements['setting-kb-path']) {
      elements['setting-kb-path'].value = config.kbPath;
    }
    if (elements['setting-rag-enabled']) {
      elements['setting-rag-enabled'].checked = config.ragEnabled;
    }
  }

  /**
   * 从 UI 收集配置
   */
  function collectConfig() {
    return {
      provider: elements['setting-provider']?.value || 'ollama',
      apiKey: elements['setting-apikey']?.value || '',
      model: elements['setting-model']?.value || '',
      theme: elements['setting-theme']?.value || 'dark',
      language: elements['setting-language']?.value || 'zh-CN',
      fontSize: parseInt(elements['setting-fontsize']?.value || '14'),
      dailyEnabled: dailyFeedEnabled,
      dailyCount: parseInt(elements['setting-daily-count']?.value || '3'),
      dailyTime: elements['setting-daily-time']?.value || '07:00',
      kbPath: elements['setting-kb-path']?.value || './knowledge',
      ragEnabled: elements['setting-rag-enabled']?.checked ?? true
    };
  }

  /**
   * 保存配置
   */
  async function saveConfig() {
    config = collectConfig();

    try {
      localStorage.setItem('mechforge-config', JSON.stringify(config));
      console.log('[Settings] 配置已保存到本地');

      // 应用 UI 配置
      applyTheme(config.theme);
      applyFontSize(config.fontSize);

      // 同步到后端
      const ok = await notifyBackendConfigChange(config);
      if (ok) {
        showToast('设置已保存');
        if (typeof eventBus !== 'undefined' && typeof Events !== 'undefined') {
          eventBus.emit(Events.CONFIG_UPDATED, {
            ai: { provider: config.provider, model: config.model },
            rag: { enabled: config.ragEnabled }
          });
        }
      } else {
        showToast('设置已保存（后端同步失败）', 'error');
      }
    } catch (e) {
      console.error('[Settings] 保存配置失败:', e);
      showToast('保存失败', 'error');
    }
  }

  /**
   * 重置配置
   */
  function resetConfig() {
    if (confirm('确定要重置所有设置为默认值吗？')) {
      config = { ...DEFAULT_CONFIG };
      applyConfig();
      saveConfig();
      showToast('已重置为默认设置');
    }
  }

  /**
   * 选择知识库路径
   */
  function selectKbPath() {
    // 使用文件选择器(如果可用)
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.select_folder('选择知识库文件夹')
        .then(path => {
          if (path && elements['setting-kb-path']) {
            elements['setting-kb-path'].value = path;
          }
        })
        .catch(err => {
          console.warn('[Settings] 选择文件夹失败:', err);
        });
    } else {
      // 降级方案:手动输入
      const path = prompt('请输入知识库路径:', config.kbPath);
      if (path && elements['setting-kb-path']) {
        elements['setting-kb-path'].value = path;
      }
    }
  }

  /**
   * 预览主题
   */
  function previewTheme(theme) {
    document.body.setAttribute('data-theme', theme);
  }

  /**
   * 应用主题
   */
  function applyTheme(theme) {
    document.body.setAttribute('data-theme', theme);
  }

  /**
   * 预览字体大小
   */
  function previewFontSize(size) {
    document.documentElement.style.fontSize = size + 'px';
  }

  /**
   * 应用字体大小
   */
  function applyFontSize(size) {
    document.documentElement.style.fontSize = size + 'px';
  }

  /**
   * 显示滑块值
   */
  function showSliderValue(slider, text) {
    const wrapper = slider.parentElement;
    if (!wrapper) return;

    wrapper.classList.add('slider-wrapper');

    let tooltip = wrapper.querySelector('.slider-tooltip');
    if (!tooltip) {
      tooltip = document.createElement('span');
      tooltip.className = 'slider-tooltip';
      wrapper.appendChild(tooltip);
    }
    tooltip.textContent = text;
  }

  /**
   * 显示提示（使用统一 NotificationManager）
   */
  function showToast(message, type = 'success') {
    if (window.showToast) {
      window.showToast(message, type);
    } else {
      console.log(`[Toast] ${type}: ${message}`);
    }
  }

  /**
   * 同步配置到后端
   * @returns {Promise<boolean>} 是否成功
   */
  async function notifyBackendConfigChange(config) {
    const base = getApiBase();
    try {
      const res = await fetch(`${base}/api/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      return res.ok;
    } catch (err) {
      console.warn('[Settings] 同步后端失败:', err);
      return false;
    }
  }

  /**
   * 获取当前配置
   */
  function getConfig() {
    return { ...config };
  }

  /**
   * 更新配置项
   */
  function updateConfig(key, value) {
    config[key] = value;
    saveConfig();
  }

  // 暴露 API
  window.SettingsPanel = {
    init,
    getConfig,
    updateConfig,
    saveConfig,
    resetConfig
  };

})();
