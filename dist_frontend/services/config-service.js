/**
 * ConfigService - 配置服务模块
 * 封装配置管理相关业务逻辑
 */

class ConfigService {
  constructor(apiClient, eventBus) {
    this.apiClient = apiClient;
    this.eventBus = eventBus;
    this.config = null;
    this.models = [];
  }

  /**
   * 初始化配置
   */
  async init() {
    try {
      const [config, models, status] = await Promise.all([
        this.apiClient.getConfig(),
        this.apiClient.getModels(),
        this.apiClient.getStatus()
      ]);

      this.config = config;
      this.models = models || [];

      this.eventBus.emit(Events.CONFIG_LOADED, {
        config,
        models: this.models,
        status
      });

      return { config, models, status };
    } catch (error) {
      console.error('Failed to initialize config:', error);
      // 使用默认配置
      this.config = this.getDefaultConfig();
      this.eventBus.emit(Events.CONFIG_LOADED, {
        config: this.config,
        models: [],
        status: null,
        error: error.message
      });
      return { config: this.config, models: [], status: null };
    }
  }

  /**
   * 获取默认配置
   */
  getDefaultConfig() {
    return {
      ai: {
        provider: 'ollama',
        model: 'qwen2.5:3b'
      },
      rag: {
        enabled: false,
        backend: 'local',
        top_k: 5
      },
      ui: {
        theme: 'dark',
        language: 'zh-CN'
      }
    };
  }

  /**
   * 获取配置值
   * @param {string} key - 配置键 (支持 dot 语法)
   * @param {*} defaultValue - 默认值
   */
  get(key, defaultValue = null) {
    if (!this.config) {
      return defaultValue;
    }

    if (!key) {
      return this.config;
    }

    // 支持 dot 语法，如 'ai.provider'
    const keys = key.split('.');
    let value = this.config;

    for (const k of keys) {
      if (value && typeof value === 'object' && k in value) {
        value = value[k];
      } else {
        return defaultValue;
      }
    }

    return value;
  }

  /**
   * 设置配置值
   * @param {string|object} key - 配置键或对象
   * @param {*} value - 配置值
   */
  async set(key, value) {
    const oldConfig = { ...this.config };

    if (typeof key === 'object') {
      // 批量设置
      this.config = { ...this.config, ...key };
    } else {
      // 单个设置，支持 dot 语法
      const keys = key.split('.');
      let target = this.config;

      for (let i = 0; i < keys.length - 1; i++) {
        const k = keys[i];
        if (!target[k]) {
          target[k] = {};
        }
        target = target[k];
      }
      target[keys[keys.length - 1]] = value;
    }

    try {
      await this.save();
      this.eventBus.emit(Events.CONFIG_UPDATED, {
        key,
        value,
        oldConfig,
        newConfig: this.config
      });
    } catch (error) {
      // 回滚
      this.config = oldConfig;
      throw error;
    }
  }

  /**
   * 保存配置到服务器
   */
  async save() {
    if (!this.config) {
      return;
    }

    await this.apiClient.updateConfig(this.config);
  }

  /**
   * 重新加载配置
   */
  async reload() {
    await this.init();
  }

  /**
   * 获取可用模型列表
   */
  getModels() {
    return [...this.models];
  }

  /**
   * 获取当前使用的模型
   */
  getCurrentModel() {
    return this.get('ai.model', 'qwen2.5:3b');
  }

  /**
   * 设置 AI 模型
   * @param {string} model - 模型名称
   */
  async setModel(model) {
    await this.set('ai.model', model);
  }

  /**
   * 获取 AI 提供商
   */
  getProvider() {
    return this.get('ai.provider', 'ollama');
  }

  /**
   * 设置 AI 提供商
   * @param {string} provider - 提供商名称
   */
  async setProvider(provider) {
    await this.set('ai.provider', provider);
  }

  /**
   * 获取 RAG 配置
   */
  getRAGConfig() {
    return this.get('rag', {});
  }

  /**
   * 设置 RAG 配置
   * @param {object} ragConfig
   */
  async setRAGConfig(ragConfig) {
    await this.set('rag', ragConfig);
  }

  /**
   * 获取完整配置
   */
  getAll() {
    return { ...this.config };
  }
}

// 导出
window.ConfigService = ConfigService;
