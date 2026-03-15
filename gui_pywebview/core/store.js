/**
 * Store - 全局状态管理
 * 提供类似 Vuex 的状态管理功能
 */

(function () {
  'use strict';

  /**
   * 创建 Store
   * @param {Object} options - 配置选项
   * @returns {Object}
   */
  function createStore(options = {}) {
    const {
      state = {},
      getters = {},
      mutations = {},
      actions = {},
      modules = {},
      plugins = [],
      strict = false
    } = options;

    // 内部状态
    const _state = deepClone(state);
    const _getters = {};
    let _mutations = { ...mutations };
    let _actions = { ...actions };
    const _subscribers = [];
    const _actionSubscribers = [];
    let _isCommitting = false;

    // 初始化模块
    Object.entries(modules).forEach(([name, module]) => {
      installModule(_state, _mutations, _actions, name, module);
    });

    // 计算属性
    Object.entries(getters).forEach(([name, fn]) => {
      Object.defineProperty(_getters, name, {
        get: () => fn(_state, _getters),
        enumerable: true
      });
    });

    // 安装模块
    function installModule(rootState, rootMutations, rootActions, path, module) {
      const namespace = typeof path === 'string' ? path : path.join('/');
      const moduleState = typeof module.state === 'function' ? module.state() : module.state;

      // 设置状态
      if (namespace) {
        setNestedProperty(rootState, namespace, moduleState);
      } else {
        Object.assign(rootState, moduleState);
      }

      // 注册 mutations
      if (module.mutations) {
        Object.entries(module.mutations).forEach(([name, handler]) => {
          const namespacedName = namespace ? `${namespace}/${name}` : name;
          rootMutations[namespacedName] = handler;
        });
      }

      // 注册 actions
      if (module.actions) {
        Object.entries(module.actions).forEach(([name, handler]) => {
          const namespacedName = namespace ? `${namespace}/${name}` : name;
          rootActions[namespacedName] = handler;
        });
      }

      // 递归安装子模块
      if (module.modules) {
        Object.entries(module.modules).forEach(([childName, childModule]) => {
          const childPath = namespace ? `${namespace}/${childName}` : childName;
          installModule(rootState, rootMutations, rootActions, childPath, childModule);
        });
      }
    }

    // 获取状态
    function getState() {
      return _state;
    }

    // 提交 mutation
    function commit(type, payload) {
      const handler = _mutations[type];
      if (!handler) {
        console.error(`[Store] Unknown mutation: ${type}`);
        return;
      }

      _isCommitting = true;
      handler(_state, payload);
      _isCommitting = false;

      // 通知订阅者
      _subscribers.forEach(sub => sub({ type, payload }, _state));
    }

    // 分发 action
    function dispatch(type, payload) {
      const handler = _actions[type];
      if (!handler) {
        console.error(`[Store] Unknown action: ${type}`);
        return Promise.reject(new Error(`Unknown action: ${type}`));
      }

      const context = {
        state: _state,
        getters: _getters,
        commit,
        dispatch
      };

      // 通知 action 订阅者（开始）
      _actionSubscribers.forEach(sub => {
        if (sub.before) sub.before({ type, payload }, _state);
      });

      const result = handler(context, payload);

      return Promise.resolve(result).then(
        res => {
          // 通知 action 订阅者（成功）
          _actionSubscribers.forEach(sub => {
            if (sub.after) sub.after({ type, payload }, _state);
          });
          return res;
        },
        err => {
          // 通知 action 订阅者（错误）
          _actionSubscribers.forEach(sub => {
            if (sub.error) sub.error({ type, payload }, _state, err);
          });
          throw err;
        }
      );
    }

    // 订阅
    function subscribe(fn) {
      _subscribers.push(fn);
      return () => {
        const index = _subscribers.indexOf(fn);
        if (index > -1) _subscribers.splice(index, 1);
      };
    }

    // 订阅 action
    function subscribeAction(fn) {
      _actionSubscribers.push(fn);
      return () => {
        const index = _actionSubscribers.indexOf(fn);
        if (index > -1) _actionSubscribers.splice(index, 1);
      };
    }

    // 注册模块
    function registerModule(path, module) {
      if (typeof path === 'string') path = [path];
      installModule(_state, _mutations, _actions, path, module);
    }

    // 卸载模块
    function unregisterModule(path) {
      if (typeof path === 'string') path = [path];
      const namespace = path.join('/');

      // 删除状态
      deleteNestedProperty(_state, namespace);

      // 删除 mutations 和 actions
      Object.keys(_mutations).forEach(key => {
        if (key.startsWith(`${namespace}/`)) {
          delete _mutations[key];
        }
      });

      Object.keys(_actions).forEach(key => {
        if (key.startsWith(`${namespace}/`)) {
          delete _actions[key];
        }
      });
    }

    // 热更新
    function hotUpdate(options) {
      if (options.mutations) {
        _mutations = { ..._mutations, ...options.mutations };
      }
      if (options.actions) {
        _actions = { ..._actions, ...options.actions };
      }
    }

    // 严格模式检查
    if (strict) {
      watchState(_state, () => {
        if (!_isCommitting) {
          console.error('[Store] Do not mutate state outside mutation handlers');
        }
      });
    }

    // 应用插件
    plugins.forEach(plugin => plugin({
      state: _state,
      getters: _getters,
      commit,
      dispatch,
      subscribe,
      subscribeAction
    }));

    return {
      get state() { return _state; },
      getters: _getters,
      commit,
      dispatch,
      subscribe,
      subscribeAction,
      registerModule,
      unregisterModule,
      hotUpdate
    };
  }

  // 深度克隆
  function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (obj instanceof Date) return new Date(obj);
    if (Array.isArray(obj)) return obj.map(deepClone);
    const cloned = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key]);
      }
    }
    return cloned;
  }

  // 设置嵌套属性
  function setNestedProperty(obj, path, value) {
    const keys = path.split('/');
    let current = obj;
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) current[keys[i]] = {};
      current = current[keys[i]];
    }
    current[keys[keys.length - 1]] = value;
  }

  // 删除嵌套属性
  function deleteNestedProperty(obj, path) {
    const keys = path.split('/');
    let current = obj;
    for (let i = 0; i < keys.length - 1; i++) {
      if (!current[keys[i]]) return;
      current = current[keys[i]];
    }
    delete current[keys[keys.length - 1]];
  }

  // 监听状态变化（简单实现）
  function watchState(state, callback) {
    // 实际实现需要使用 Proxy
    // 这里仅作为示例
  }

  // 创建默认 store
  const defaultStore = createStore({
    state: {
      app: {
        initialized: false,
        loading: false,
        error: null
      },
      user: {
        preferences: {},
        history: []
      },
      ui: {
        theme: 'dark',
        sidebarCollapsed: false,
        activeTab: 'chat'
      }
    },
    mutations: {
      SET_INITIALIZED(state, value) {
        state.app.initialized = value;
      },
      SET_LOADING(state, value) {
        state.app.loading = value;
      },
      SET_ERROR(state, error) {
        state.app.error = error;
      },
      SET_THEME(state, theme) {
        state.ui.theme = theme;
      },
      SET_ACTIVE_TAB(state, tab) {
        state.ui.activeTab = tab;
      },
      TOGGLE_SIDEBAR(state) {
        state.ui.sidebarCollapsed = !state.ui.sidebarCollapsed;
      },
      SET_PREFERENCE(state, { key, value }) {
        state.user.preferences[key] = value;
      }
    },
    actions: {
      async initApp({ commit }) {
        commit('SET_LOADING', true);
        try {
          // 初始化逻辑
          await new Promise(resolve => setTimeout(resolve, 500));
          commit('SET_INITIALIZED', true);
        } catch (error) {
          commit('SET_ERROR', error.message);
        } finally {
          commit('SET_LOADING', false);
        }
      }
    },
    getters: {
      isReady: state => state.app.initialized && !state.app.loading,
      currentTheme: state => state.ui.theme,
      preferences: state => state.user.preferences
    }
  });

  // ==================== 导出 ====================
  window.Store = {
    create: createStore,
    default: defaultStore
  };

})();
