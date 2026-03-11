/**
 * I18n - 国际化模块
 * 提供多语言支持和翻译功能
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    defaultLocale: 'zh-CN',
    fallbackLocale: 'en-US',
    storageKey: 'mechforge_locale'
  };

  // ==================== 当前状态 ====================
  let currentLocale = config.defaultLocale;
  let translations = {};
  let listeners = [];

  // ==================== 内置翻译 ====================
  const builtinTranslations = {
    'zh-CN': {
      // 通用
      'common.confirm': '确认',
      'common.cancel': '取消',
      'common.close': '关闭',
      'common.save': '保存',
      'common.delete': '删除',
      'common.edit': '编辑',
      'common.add': '添加',
      'common.search': '搜索',
      'common.loading': '加载中...',
      'common.success': '成功',
      'common.error': '错误',
      'common.warning': '警告',
      'common.info': '提示',
      'common.yes': '是',
      'common.no': '否',
      'common.ok': '确定',
      'common.back': '返回',
      'common.next': '下一步',
      'common.prev': '上一步',
      'common.finish': '完成',
      'common.submit': '提交',
      'common.reset': '重置',
      'common.clear': '清空',
      'common.refresh': '刷新',
      'common.copy': '复制',
      'common.paste': '粘贴',
      'common.cut': '剪切',
      'common.selectAll': '全选',
      'common.undo': '撤销',
      'common.redo': '重做',

      // 导航
      'nav.chat': 'AI 对话',
      'nav.knowledge': '知识库',
      'nav.cae': 'CAE 工作台',
      'nav.experience': '经验库',
      'nav.settings': '设置',

      // 聊天
      'chat.inputPlaceholder': '输入消息...',
      'chat.send': '发送',
      'chat.stop': '停止',
      'chat.clear': '清空对话',
      'chat.export': '导出',
      'chat.empty': '暂无消息',
      'chat.thinking': '思考中...',
      'chat.copySuccess': '已复制',
      'chat.regenerate': '重新生成',
      'chat.user': '用户',
      'chat.assistant': 'AI',

      // 设置
      'settings.title': '设置',
      'settings.general': '通用',
      'settings.appearance': '外观',
      'settings.language': '语言',
      'settings.theme': '主题',
      'settings.api': 'API 设置',
      'settings.model': '模型',
      'settings.version': '版本',
      'settings.saveSuccess': '设置已保存',
      'settings.reset': '恢复默认',

      // 状态
      'status.online': '在线',
      'status.offline': '离线',
      'status.connecting': '连接中',
      'status.ready': '就绪',
      'status.error': '错误'
    },
    'en-US': {
      // Common
      'common.confirm': 'Confirm',
      'common.cancel': 'Cancel',
      'common.close': 'Close',
      'common.save': 'Save',
      'common.delete': 'Delete',
      'common.edit': 'Edit',
      'common.add': 'Add',
      'common.search': 'Search',
      'common.loading': 'Loading...',
      'common.success': 'Success',
      'common.error': 'Error',
      'common.warning': 'Warning',
      'common.info': 'Info',
      'common.yes': 'Yes',
      'common.no': 'No',
      'common.ok': 'OK',
      'common.back': 'Back',
      'common.next': 'Next',
      'common.prev': 'Previous',
      'common.finish': 'Finish',
      'common.submit': 'Submit',
      'common.reset': 'Reset',
      'common.clear': 'Clear',
      'common.refresh': 'Refresh',
      'common.copy': 'Copy',
      'common.paste': 'Paste',
      'common.cut': 'Cut',
      'common.selectAll': 'Select All',
      'common.undo': 'Undo',
      'common.redo': 'Redo',

      // Navigation
      'nav.chat': 'AI Chat',
      'nav.knowledge': 'Knowledge',
      'nav.cae': 'CAE Workbench',
      'nav.experience': 'Experience',
      'nav.settings': 'Settings',

      // Chat
      'chat.inputPlaceholder': 'Type a message...',
      'chat.send': 'Send',
      'chat.stop': 'Stop',
      'chat.clear': 'Clear Chat',
      'chat.export': 'Export',
      'chat.empty': 'No messages',
      'chat.thinking': 'Thinking...',
      'chat.copySuccess': 'Copied',
      'chat.regenerate': 'Regenerate',
      'chat.user': 'User',
      'chat.assistant': 'AI',

      // Settings
      'settings.title': 'Settings',
      'settings.general': 'General',
      'settings.appearance': 'Appearance',
      'settings.language': 'Language',
      'settings.theme': 'Theme',
      'settings.api': 'API',
      'settings.version': 'Version',
      'settings.saveSuccess': 'Saved',
      'settings.reset': 'Reset'
    }
  };

  // ==================== 初始化 ====================

  /**
   * 初始化国际化
   * @param {Object} options - 配置选项
   */
  function init(options = {}) {
    Object.assign(config, options);

    // 从存储加载语言设置
    const saved = localStorage.getItem(config.storageKey);
    if (saved) {
      currentLocale = saved;
    }


    // 加载内置翻译
    loadTranslations(currentLocale);

    console.log(`[I18n] Initialized with locale: ${currentLocale}`);
  }

  /**
   * 加载翻译
   * @param {string} locale - 语言代码
   */
  function loadTranslations(locale) {
    if (builtinTranslations[locale]) {
      translations[locale] = builtinTranslations[locale];
    }
  }

  // ==================== 核心功能 ====================

  /**
   * 获取翻译
   * @param {string} key - 翻译键
   * @param {Object} params - 参数
   * @returns {string}
   */
  function t(key, params = {}) {
    const translation = getTranslation(key);
    return interpolate(translation, params);
  }

  /**
   * 获取翻译（带回退）
   * @param {string} key - 键
   * @returns {string}
   */
  function getTranslation(key) {
    // 优先当前语言
    if (translations[currentLocale]?.[key]) {
      return translations[currentLocale][key];
    }
    // 回退到默认语言
    if (translations[config.fallbackLocale]?.[key] {
      return translations[config.fallbackLocale][key] || key;
  }

  /**
   * 插值替换
   * @param {string} text - 原文本
   * @param {Object} params - 参数
   * @returns {string}
   */
  function interpolate(text, params) {
    if (!text) return '';
    return text.replace(/\{(\w+)\}/g, (match, key) => {
      return params[key] !== undefined ? params[key] : match;
    });
  }

  // ==================== 语言管理 ====================

  /**
   * 设置当前语言
   * @param {string} locale - 语言代码
   */
  function setLocale(locale) {
    if (!translations[locale] && !builtinTranslations[locale]) {
      console.warn(`[I18n] Locale not found: ${locale}`);
      return;
    }

    currentLocale = locale;
    loadTranslations(locale);

    // 保存到存储
    localStorage.setItem(config.storageKey, locale);

    // 触发监听器
    listeners.forEach(fn => fn(locale));

    console.log(`[I18n] Locale changed to: ${locale}`);
  }

  /**
   * 获取当前语言
   * @returns {string}
   */
  function getLocale() {
    return currentLocale;
  }

  /**
   * 获取可用语言列表
   * @returns {Array}
   */
  function getAvailableLocales() {
    return Object.keys(builtinTranslations);
  }

  // ==================== 翻译管理 ====================

  /**
   * 添加翻译
   * @param {string} locale - 语言代码
   * @param {Object} msgs - 翻译对象
   */
  function addTranslations(locale, msgs) {
    if (!translations[locale]) {
      translations[locale] = {};
    }
    Object.assign(translations[locale], msgs);
  }

  /**
   * 加载外部翻译文件
   * @param {string} locale - 语言代码
   * @param {string} url - 文件URL
   * @returns {Promise}
   */
  async function loadTranslationFile(locale, url) {
    try {
      const response = await fetch(url);
      const data = await response.json();
      addTranslations(locale, data;
      const data = await response.json();
      addTranslations(locale, data;
      addTranslations(locale, data
    } catch (error) {
      console.error(`[I18n] Failed to load: ${url}`);
    }
  }

  // ==================== 监听 ====================

  /**
   * 监听语言变化
   * @param {Function} callback - 回调函数
   */
  function onChange(callback) {
    listeners.push(callback);
  }

  /**
   * 移除监听器
   * @param {Function} callback - 回调函数
   */
  function offChange(callback) {
    listeners = listeners.filter(fn => fn !== callback);
  }

  // ==================== 快捷方法 ====================

  function __(key, params) {
    return t(key, params);
  }

  // ==================== 导出 ====================
  window.I18n = {
    config,
    init,
    t,
    __,
    setLocale,
    getLocale,
    getAvailableLocales,
    addTranslations,
    loadTranslationFile,
    onChange,
    offChange
  };

})();
