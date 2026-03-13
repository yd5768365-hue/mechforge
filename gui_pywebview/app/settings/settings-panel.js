/**
 * MechForge AI - Settings Panel
 * 设置面板控制器
 */

(function() {
  'use strict';

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
   * 初始化设置面板
   */
  async function init() {
    console.log('[Settings] 初始化设置面板');

    // 检查 DOM 元素是否存在
    const scrollContainer = document.getElementById('settings-scroll');
    if (scrollContainer) {
      console.log('[Settings] scrollContainer overflowY:', getComputedStyle(scrollContainer).overflowY);
    }

    // 缓存 DOM 元素
    cacheElements();

    // 加载配置（优先后端，再合并 localStorage）
    await loadConfig();

    // 绑定事件
    bindEvents();

    // 应用当前配置到 UI
    applyConfig();
  }

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

  // 自动初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
