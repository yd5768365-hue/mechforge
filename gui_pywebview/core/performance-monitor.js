/**
 * PerformanceMonitor - 性能监控器
 * 监控应用性能指标、内存使用和帧率
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    enabled: true,
    logInterval: 30000, // 日志记录间隔
    slowFrameThreshold: 33, // 慢帧阈值 (30fps)
    memoryWarningThreshold: 0.8, // 内存警告阈值 (80%)
    maxMetricsHistory: 100 // 最大历史记录数
  };

  // ==================== 状态 ====================
  let isRunning = false;
  let frameId = null;
  let logIntervalId = null;
  
  const metrics = {
    fps: [],
    frameTime: [],
    memory: [],
    longTasks: [],
    errors: []
  };

  let lastTime = performance.now();
  let frameCount = 0;
  let lastFpsTime = lastTime;

  // ==================== 核心功能 ====================

  /**
   * 开始监控
   */
  function start() {
    if (isRunning || !config.enabled) return;
    
    isRunning = true;
    lastTime = performance.now();
    lastFpsTime = lastTime;
    frameCount = 0;
    
    measureFrame();
    startMemoryMonitoring();
    startLongTaskMonitoring();
    startLogging();
    
    console.log('[PerformanceMonitor] Started');
  }

  /**
   * 停止监控
   */
  function stop() {
    isRunning = false;
    
    if (frameId) {
      cancelAnimationFrame(frameId);
      frameId = null;
    }
    
    if (logIntervalId) {
      clearInterval(logIntervalId);
      logIntervalId = null;
    }
    
    console.log('[PerformanceMonitor] Stopped');
  }

  /**
   * 测量帧率
   */
  function measureFrame() {
    if (!isRunning) return;

    const now = performance.now();
    const delta = now - lastTime;
    
    frameCount++;
    
    // 每秒计算一次FPS
    if (now - lastFpsTime >= 1000) {
      const fps = Math.round((frameCount * 1000) / (now - lastFpsTime));
      recordMetric('fps', fps);
      
      // 检测慢帧
      if (fps < 30) {
        console.warn(`[PerformanceMonitor] Low FPS detected: ${fps}`);
      }
      
      frameCount = 0;
      lastFpsTime = now;
    }
    
    // 记录帧时间
    if (delta > config.slowFrameThreshold) {
      recordMetric('frameTime', delta);
      if (delta > 100) {
        console.warn(`[PerformanceMonitor] Slow frame: ${delta.toFixed(2)}ms`);
      }
    }
    
    lastTime = now;
    frameId = requestAnimationFrame(measureFrame);
  }

  /**
   * 开始内存监控
   */
  function startMemoryMonitoring() {
    if (!performance.memory) return;
    
    setInterval(() => {
      if (!isRunning) return;
      
      const memory = performance.memory;
      const usedRatio = memory.usedJSHeapSize / memory.jsHeapSizeLimit;
      
      recordMetric('memory', {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit,
        ratio: usedRatio
      });
      
      if (usedRatio > config.memoryWarningThreshold) {
        console.warn(`[PerformanceMonitor] High memory usage: ${(usedRatio * 100).toFixed(1)}%`);
        suggestGC();
      }
    }, 5000);
  }

  /**
   * 开始长任务监控
   */
  function startLongTaskMonitoring() {
    if (!('PerformanceObserver' in window)) return;
    
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) {
            recordMetric('longTasks', {
              duration: entry.duration,
              startTime: entry.startTime,
              name: entry.name
            });
            console.warn(`[PerformanceMonitor] Long task detected: ${entry.duration.toFixed(2)}ms`);
          }
        }
      });
      
      observer.observe({ entryTypes: ['longtask'] });
    } catch (e) {
      // 浏览器不支持 longtask
    }
  }

  /**
   * 开始定期日志记录
   */
  function startLogging() {
    logIntervalId = setInterval(() => {
      if (!isRunning) return;
      logMetrics();
    }, config.logInterval);
  }

  /**
   * 记录指标
   * @param {string} type - 指标类型
   * @param {*} value - 指标值
   */
  function recordMetric(type, value) {
    if (!metrics[type]) return;
    
    metrics[type].push({
      value,
      timestamp: Date.now()
    });
    
    // 限制历史记录数量
    if (metrics[type].length > config.maxMetricsHistory) {
      metrics[type].shift();
    }
  }

  /**
   * 记录错误
   * @param {Error} error - 错误对象
   * @param {string} context - 错误上下文
   */
  function recordError(error, context = '') {
    recordMetric('errors', {
      message: error.message,
      stack: error.stack,
      context,
      timestamp: Date.now()
    });
  }

  /**
   * 获取平均FPS
   */
  function getAverageFPS() {
    if (metrics.fps.length === 0) return 0;
    const sum = metrics.fps.reduce((acc, m) => acc + m.value, 0);
    return Math.round(sum / metrics.fps.length);
  }

  /**
   * 获取内存使用情况
   */
  function getMemoryStats() {
    if (metrics.memory.length === 0) return null;
    const latest = metrics.memory[metrics.memory.length - 1].value;
    return {
      usedMB: (latest.used / 1024 / 1024).toFixed(2),
      totalMB: (latest.total / 1024 / 1024).toFixed(2),
      limitMB: (latest.limit / 1024 / 1024).toFixed(2),
      usagePercent: (latest.ratio * 100).toFixed(1)
    };
  }

  /**
   * 获取性能报告
   */
  function getReport() {
    return {
      fps: {
        average: getAverageFPS(),
        min: metrics.fps.length > 0 ? Math.min(...metrics.fps.map(m => m.value)) : 0,
        max: metrics.fps.length > 0 ? Math.max(...metrics.fps.map(m => m.value)) : 0,
        history: metrics.fps.slice(-10)
      },
      memory: getMemoryStats(),
      longTasks: metrics.longTasks.length,
      errors: metrics.errors.length
    };
  }

  /**
   * 输出指标日志
   */
  function logMetrics() {
    const report = getReport();
    console.log('[PerformanceMonitor] Report:', report);
  }

  /**
   * 建议垃圾回收
   */
  function suggestGC() {
    if (window.gc) {
      console.log('[PerformanceMonitor] Suggesting garbage collection');
      window.gc();
    }
  }

  /**
   * 测量函数执行时间
   * @param {Function} fn - 要测量的函数
   * @param {string} name - 函数名称
   */
  function measure(fn, name) {
    return function(...args) {
      const start = performance.now();
      const result = fn.apply(this, args);
      const duration = performance.now() - start;
      
      if (duration > 16) {
        console.log(`[PerformanceMonitor] ${name} took ${duration.toFixed(2)}ms`);
      }
      
      return result;
    };
  }

  /**
   * 创建性能标记
   * @param {string} name - 标记名称
   */
  function mark(name) {
    if (performance.mark) {
      performance.mark(name);
    }
  }

  /**
   * 测量两个标记之间的时间
   * @param {string} startMark - 开始标记
   * @param {string} endMark - 结束标记
   * @param {string} measureName - 测量名称
   */
  function measureBetween(startMark, endMark, measureName) {
    if (performance.measure) {
      performance.measure(measureName, startMark, endMark);
      const entries = performance.getEntriesByName(measureName);
      if (entries.length > 0) {
        return entries[entries.length - 1].duration;
      }
    }
    return 0;
  }

  /**
   * 清除所有指标
   */
  function clear() {
    Object.keys(metrics).forEach(key => {
      metrics[key] = [];
    });
  }

  // ==================== 导出 ====================
  window.PerformanceMonitor = {
    start,
    stop,
    recordError,
    getAverageFPS,
    getMemoryStats,
    getReport,
    logMetrics,
    measure,
    mark,
    measureBetween,
    clear,
    metrics
  };

})();
