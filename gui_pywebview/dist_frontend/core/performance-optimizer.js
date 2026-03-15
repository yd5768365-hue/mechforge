/**
 * Performance Optimizations - 性能优化脚本
 * 懒加载、资源预加载、渲染优化
 */

(function () {
  'use strict';

  // ==================== 懒加载观察器 ====================

  const LazyLoader = {
    observer: null,
    loadedElements: new Set(),

    /**
     * 初始化懒加载观察器
     */
    init() {
      if (!('IntersectionObserver' in window)) {
        // 降级处理：直接加载所有
        this.loadAll();
        return;
      }

      this.observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              this.loadElement(entry.target);
              this.observer.unobserve(entry.target);
            }
          });
        },
        {
          root: null,
          rootMargin: '50px',
          threshold: 0.01,
        }
      );

      // 观察所有需要懒加载的元素
      document.querySelectorAll('[data-lazy]').forEach((el) => {
        this.observer.observe(el);
      });
    },

    /**
     * 加载单个元素
     */
    loadElement(element) {
      if (this.loadedElements.has(element)) return;

      const type = element.dataset.lazy;

      switch (type) {
        case 'image':
          this.loadImage(element);
          break;
        case 'iframe':
          this.loadIframe(element);
          break;
        case 'script':
          this.loadScript(element);
          break;
        case 'module':
          this.loadModule(element);
          break;
        default:
          this.loadContent(element);
      }

      this.loadedElements.add(element);
      element.removeAttribute('data-lazy');
    },

    /**
     * 加载图片
     */
    loadImage(img) {
      const src = img.dataset.src;
      const srcset = img.dataset.srcset;

      if (src) {
        img.src = src;
        img.removeAttribute('data-src');
      }
      if (srcset) {
        img.srcset = srcset;
        img.removeAttribute('data-srcset');
      }

      img.classList.add('loaded');
    },

    /**
     * 加载 iframe
     */
    loadIframe(iframe) {
      iframe.src = iframe.dataset.src;
      iframe.removeAttribute('data-src');
    },

    /**
     * 加载脚本
     */
    loadScript(element) {
      const src = element.dataset.src;
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      document.head.appendChild(script);
    },

    /**
     * 加载模块
     */
    async loadModule(element) {
      const moduleName = element.dataset.module;
      try {
        if (window.ModuleLoader) {
          await ModuleLoader.lazyLoad(moduleName);
        }
      } catch (error) {
        console.error(`[LazyLoader] Failed to load module ${moduleName}:`, error);
      }
    },

    /**
     * 加载内容
     */
    loadContent(element) {
      const content = element.dataset.content;
      if (content) {
        element.innerHTML = content;
        element.removeAttribute('data-content');
      }
    },

    /**
     * 加载所有（降级处理）
     */
    loadAll() {
      document.querySelectorAll('[data-lazy]').forEach((el) => {
        this.loadElement(el);
      });
    },

    /**
     * 销毁观察器
     */
    destroy() {
      if (this.observer) {
        this.observer.disconnect();
        this.observer = null;
      }
    },
  };

  // ==================== 资源预加载 ====================

  const ResourcePreloader = {
    /**
     * 预加载关键资源
     */
    preload(url, type = 'auto') {
      const link = document.createElement('link');
      link.rel = 'preload';
      link.href = url;
      link.as = type;
      document.head.appendChild(link);
    },

    /**
     * 预获取资源（低优先级）
     */
    prefetch(url) {
      const link = document.createElement('link');
      link.rel = 'prefetch';
      link.href = url;
      document.head.appendChild(link);
    },

    /**
     * DNS 预解析
     */
    dnsPrefetch(domain) {
      const link = document.createElement('link');
      link.rel = 'dns-prefetch';
      link.href = `//${domain}`;
      document.head.appendChild(link);
    },

    /**
     * 预连接
     */
    preconnect(domain) {
      const link = document.createElement('link');
      link.rel = 'preconnect';
      link.href = `//${domain}`;
      link.crossOrigin = 'anonymous';
      document.head.appendChild(link);
    },
  };

  // ==================== 渲染优化 ====================

  const RenderOptimizer = {
    /**
     * 使用 requestIdleCallback 执行低优先级任务
     */
    scheduleIdle(callback, timeout = 2000) {
      if ('requestIdleCallback' in window) {
        return requestIdleCallback(callback, { timeout });
      } 
        // 降级处理
        return setTimeout(callback, 1);
      
    },

    /**
     * 使用 requestAnimationFrame 执行动画
     */
    scheduleAnimation(callback) {
      return requestAnimationFrame(callback);
    },

    /**
     * 批量 DOM 操作
     */
    batchDOMUpdates(updates) {
      return new Promise((resolve) => {
        this.scheduleAnimation(() => {
          updates.forEach((update) => update());
          resolve();
        });
      });
    },

    /**
     * 虚拟滚动（用于长列表）
     */
    createVirtualScroller(container, options = {}) {
      const { itemHeight, overscan = 5, renderItem } = options;
      const items = [];
      let visibleRange = { start: 0, end: 0 };

      const updateVisibleItems = () => {
        const scrollTop = container.scrollTop;
        const containerHeight = container.clientHeight;

        const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
        const endIndex = Math.min(
          items.length,
          Math.ceil((scrollTop + containerHeight) / itemHeight) + overscan
        );

        if (startIndex !== visibleRange.start || endIndex !== visibleRange.end) {
          visibleRange = { start: startIndex, end: endIndex };
          this.renderVisibleItems();
        }
      };

      const renderVisibleItems = () => {
        const fragment = document.createDocumentFragment();

        for (let i = visibleRange.start; i < visibleRange.end; i++) {
          const item = renderItem(items[i], i);
          item.style.position = 'absolute';
          item.style.top = `${i * itemHeight}px`;
          item.style.height = `${itemHeight}px`;
          fragment.appendChild(item);
        }

        container.innerHTML = '';
        container.appendChild(fragment);
      };

      container.addEventListener('scroll', updateVisibleItems, { passive: true });
      updateVisibleItems();

      return {
        setItems: (newItems) => {
          items.length = 0;
          items.push(...newItems);
          updateVisibleItems();
        },
        refresh: updateVisibleItems,
        destroy: () => {
          container.removeEventListener('scroll', updateVisibleItems);
        },
      };
    },

    /**
     * 防抖函数
     */
    debounce(fn, delay) {
      let timeoutId;
      return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
      };
    },

    /**
     * 节流函数
     */
    throttle(fn, limit) {
      let inThrottle;
      return function (...args) {
        if (!inThrottle) {
          fn.apply(this, args);
          inThrottle = true;
          setTimeout(() => (inThrottle = false), limit);
        }
      };
    },
  };

  // ==================== 内存管理 ====================

  const MemoryManager = {
    /**
     * 清理未使用的 DOM 元素
     */
    cleanupDOM() {
      // 清理隐藏的元素
      document.querySelectorAll('.hidden').forEach((el) => {
        if (!el.id || !el.classList.contains('keep-in-dom')) {
          el.remove();
        }
      });

      // 清理事件监听器（需要配合 EventManager 使用）
      if (window.EventManager) {
        EventManager.cleanup();
      }
    },

    /**
     * 建议垃圾回收
     */
    suggestGC() {
      if (window.gc) {
        window.gc();
      }
    },

    /**
     * 获取内存使用情况
     */
    getMemoryInfo() {
      if (performance.memory) {
        return {
          used: performance.memory.usedJSHeapSize,
          total: performance.memory.totalJSHeapSize,
          limit: performance.memory.jsHeapSizeLimit,
        };
      }
      return null;
    },
  };

  // ==================== 初始化 ====================

  function init() {
    // 初始化懒加载
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => LazyLoader.init());
    } else {
      LazyLoader.init();
    }

    // 定期清理内存
    setInterval(() => {
      MemoryManager.cleanupDOM();
    }, 60000); // 每分钟清理一次

    console.log('[Performance] Optimizations initialized');
  }

  // 导出全局 API
  window.PerformanceOptimizer = {
    LazyLoader,
    ResourcePreloader,
    RenderOptimizer,
    MemoryManager,
    init,
  };

  // 自动初始化
  init();
})();
