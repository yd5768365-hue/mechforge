/**
 * ThemeManager - 主题管理模块
 * 支持暗色/亮色主题切换
 */

(function () {
  'use strict';

  // ==================== 主题定义 ====================
  const themes = {
    dark: {
      '--bg-primary': '#0a0e14',
      '--bg-secondary': '#0d1117',
      '--bg-tertiary': '#111820',
      '--border-color': '#1a2535',
      '--border-highlight': '#1e2d3d',
      '--text-primary': '#c8d8e0',
      '--text-secondary': '#8ab4c8',
      '--text-muted': '#3a5068',
      '--text-dim': '#3a6070',
      '--accent-primary': '#00e5ff',
      '--accent-secondary': '#00b8d4',
      '--accent-tertiary': '#0097a7',
      '--accent-glow': 'rgba(0, 229, 255, 0.3)',
      '--accent-glow-strong': 'rgba(0, 183, 212, 0.4)',
      '--danger': '#ff4757',
      '--success': '#2ed573',
      '--warning': '#ffa502'
    },
    light: {
      '--bg-primary': '#1a1d23',
      '--bg-secondary': '#22262e',
      '--bg-tertiary': '#2a2f38',
      '--border-color': '#3a4050',
      '--border-highlight': '#4a5060',
      '--text-primary': '#e4e8ef',
      '--text-secondary': '#a8b4c4',
      '--text-muted': '#6a7a8a',
      '--text-dim': '#5a6a7a',
      '--accent-primary': '#00b8d4',
      '--accent-secondary': '#0097a7',
      '--accent-tertiary': '#007a8a',
      '--accent-glow': 'rgba(0, 184, 212, 0.25)',
      '--accent-glow-strong': 'rgba(0, 151, 167, 0.35)',
      '--danger': '#ff6b7a',
      '--success': '#4ade80',
      '--warning': '#fbbf24'
    }
  };

  // ==================== 状态 ====================
  let currentTheme = 'dark';
  const STORAGE_KEY = 'mechforge_theme';

  // ==================== 初始化 ====================

  /**
   * 初始化主题管理器
   */
  function init() {
    // 从存储加载主题
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && themes[saved]) {
      currentTheme = saved;
    }

    // 应用主题
    applyTheme(currentTheme);

    // 添加主题切换按钮
    addThemeToggle();

    console.log('[ThemeManager] Initialized with theme:', currentTheme);
  }

  /**
   * 应用主题
   * @param {string} themeName - 主题名称
   */
  function applyTheme(themeName) {
    const theme = themes[themeName];
    if (!theme) return;

    const root = document.documentElement;

    Object.entries(theme).forEach(([property, value]) => {
      root.style.setProperty(property, value);
    });

    // 设置 data 属性
    root.setAttribute('data-theme', themeName);

    // 更新 body 背景色
    document.body.style.background = theme['--bg-primary'];
    document.body.style.color = theme['--text-primary'];

    currentTheme = themeName;

    // 触发事件
    if (window.eventBus) {
      eventBus.emit('theme:changed', { theme: themeName });
    }
  }

  /**
   * 切换主题
   */
  function toggle() {
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
  }

  /**
   * 设置主题
   * @param {string} themeName - 主题名称
   */
  function setTheme(themeName) {
    if (!themes[themeName]) return;

    applyTheme(themeName);
    localStorage.setItem(STORAGE_KEY, themeName);

    console.log('[ThemeManager] Theme changed to:', themeName);
  }

  /**
   * 获取当前主题
   * @returns {string}
   */
  function getTheme() {
    return currentTheme;
  }

  /**
   * 获取所有可用主题
   * @returns {string[]}
   */
  function getAvailableThemes() {
    return Object.keys(themes);
  }

  /**
   * 添加主题切换按钮
   */
  function addThemeToggle() {
    // 查找状态栏
    const statusBar = document.querySelector('.status-bar');
    if (!statusBar) return;

    // 创建切换按钮
    const toggleBtn = document.createElement('span');
    toggleBtn.className = 'status-bar-item theme-toggle';
    toggleBtn.dataset.theme = 'toggle';
    toggleBtn.innerHTML = `
      <svg class="theme-icon-dark" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
      <svg class="theme-icon-light" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" style="display:none">
        <circle cx="12" cy="12" r="5"/>
        <line x1="12" y1="1" x2="12" y2="3"/>
        <line x1="12" y1="21" x2="12" y2="23"/>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
        <line x1="1" y1="12" x2="3" y2="12"/>
        <line x1="21" y1="12" x2="23" y2="12"/>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
      </svg>
    `;

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
      .theme-toggle {
        cursor: pointer;
        transition: all 0.2s;
      }
      .theme-toggle:hover {
        color: var(--accent-primary) !important;
      }
      [data-theme="dark"] .theme-icon-dark { display: block; }
      [data-theme="dark"] .theme-icon-light { display: none; }
      [data-theme="light"] .theme-icon-dark { display: none; }
      [data-theme="light"] .theme-icon-light { display: block; }
    `;
    document.head.appendChild(style);

    // 插入到状态栏
    const brandEl = statusBar.querySelector('.status-bar-brand');
    if (brandEl) {
      brandEl.after(toggleBtn);
    } else {
      statusBar.appendChild(toggleBtn);
    }

    // 绑定事件
    toggleBtn.addEventListener('click', toggle);
  }

  // ==================== 导出 ====================
  window.ThemeManager = {
    init,
    toggle,
    setTheme,
    getTheme,
    getAvailableThemes
  };

})();