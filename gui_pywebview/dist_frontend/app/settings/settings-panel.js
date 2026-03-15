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
  function init() {
    console.log('[Settings] 初始化设置面板');

    // 检查 DOM 元素是否存在
    const scrollContainer = document.getElementById('settings-scroll');
    console.log('[Settings] scrollContainer:', scrollContainer ? '存在' : '不存在');
    if (scrollContainer) {
      console.log('[Settings] scrollContainer overflowY:', getComputedStyle(scrollContainer).overflowY);
      console.log('[Settings] scrollContainer height:', getComputedStyle(scrollContainer).height);
      console.log('[Settings] scrollContainer scrollHeight:', scrollContainer.scrollHeight);
      console.log('[Settings] scrollContainer clientHeight:', scrollContainer.clientHeight);
    }

    // 缓存 DOM 元素
    cacheElements();

    // 加载保存的配置
    loadConfig();

    // 绑定事件
    bindEvents();

    // 应用当前配置
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

    if (dailyFeedEnabled) {
      btn.textContent = '开启';
      btn.style.background = 'linear-gradient(135deg, #00e5ff, #00a8ff)';
      btn.style.color = '#0d1117';
    } else {
      btn.textContent = '关闭';
      btn.style.background = 'rgba(100, 116, 139, 0.3)';
      btn.style.color = 'rgba(200, 216, 224, 0.6)';
    }
  }

  /**
   * 加载配置
   */
  function loadConfig() {
    try {
      const saved = localStorage.getItem('mechforge-config');
      if (saved) {
        config = { ...DEFAULT_CONFIG, ...JSON.parse(saved) };
        console.log('[Settings] 已加载保存的配置');
      }
    } catch (e) {
      console.warn('[Settings] 加载配置失败:', e);
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
  function saveConfig() {
    config = collectConfig();

    try {
      localStorage.setItem('mechforge-config', JSON.stringify(config));
      console.log('[Settings] 配置已保存');

      // 应用配置
      applyTheme(config.theme);
      applyFontSize(config.fontSize);

      // 显示成功提示
      showToast('设置已保存');

      // 通知后端配置变更
      notifyBackendConfigChange(config);
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
    // 创建或更新提示
    let tooltip = slider.parentElement.querySelector('.slider-tooltip');
    if (!tooltip) {
      tooltip = document.createElement('span');
      tooltip.className = 'slider-tooltip';
      tooltip.style.cssText = `
        position: absolute;
        right: 0;
        top: -20px;
        font-size: 11px;
        color: #00e5ff;
        font-family: monospace;
      `;
      slider.parentElement.style.position = 'relative';
      slider.parentElement.appendChild(tooltip);
    }
    tooltip.textContent = text;
  }

  /**
   * 显示提示
   */
  function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      bottom: 80px;
      right: 20px;
      padding: 12px 24px;
      background: ${type === 'error' ? 'rgba(255, 71, 87, 0.9)' : 'rgba(0, 229, 255, 0.9)'};
      color: ${type === 'error' ? '#fff' : '#0d1117'};
      border-radius: 4px;
      font-family: 'Orbitron', monospace;
      font-size: 12px;
      letter-spacing: 1px;
      z-index: 10000;
      animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  /**
   * 通知后端配置变更
   */
  function notifyBackendConfigChange(config) {
    // 通过 API 通知后端
    fetch('/api/config/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    }).catch(err => {
      console.warn('[Settings] 通知后端失败:', err);
    });
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
