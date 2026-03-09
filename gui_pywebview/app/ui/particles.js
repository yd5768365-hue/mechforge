/**
 * Particles - 粒子/火花效果模块
 * 处理背景粒子、点击火花、悬停飞溅等视觉效果
 * 
 * 性能优化：
 * - 使用 requestAnimationFrame
 * - 对象池复用
 * - 减少DOM操作
 */

(function () {
  'use strict';

  const { $, random, randomInt, PARTICLE_COUNT } = Utils;

  // ==================== 配置 ====================
  const config = {
    particleCount: PARTICLE_COUNT,
    sparkPoolSize: 50,
    enableParticles: true,
    enableSparks: true
  };

  // ==================== 粒子容器 ====================
  let container = null;
  let particles = [];
  let sparkPool = [];
  let animationId = null;

  // ==================== 初始化 ====================

  /**
   * 初始化粒子系统
   */
  function init() {
    container = $('particles');
    if (!container) return;

    // 创建粒子
    if (config.enableParticles) {
      createParticles();
    }

    // 初始化火花池
    if (config.enableSparks) {
      initSparkPool();
      setupClickSparks();
    }

    console.log('[Particles] Initialized');
  }

  /**
   * 创建背景粒子
   */
  function createParticles() {
    // 使用 DocumentFragment 减少重排
    const fragment = document.createDocumentFragment();

    for (let i = 0; i < config.particleCount; i++) {
      const p = createParticleElement();
      particles.push(p);
      fragment.appendChild(p);
    }

    container.appendChild(fragment);
  }

  /**
   * 创建单个粒子元素
   * @returns {HTMLElement}
   */
  function createParticleElement() {
    const p = document.createElement('div');
    p.className = 'particle';

    const dur = random(15, 35);
    const twk = random(1.5, 3.5);
    const size = random(2, 5);

    p.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${random(0, 100)}%;
      top: ${random(0, 100)}%;
      animation: floatParticle ${dur}s linear ${random(-30, 0)}s infinite,
                 twinkle ${twk}s ease-in-out infinite;
    `;

    return p;
  }

  /**
   * 初始化火花池（对象池模式）
   */
  function initSparkPool() {
    for (let i = 0; i < config.sparkPoolSize; i++) {
      const spark = document.createElement('div');
      spark.className = 'spark-particle';
      spark.style.display = 'none';
      container.appendChild(spark);
      sparkPool.push({
        element: spark,
        active: false,
        timeout: null
      });
    }
  }

  /**
   * 从池中获取火花
   * @returns {Object|null}
   */
  function getSparkFromPool() {
    for (const spark of sparkPool) {
      if (!spark.active) {
        spark.active = true;
        spark.element.style.display = 'block';
        return spark;
      }
    }
    return null;
  }

  /**
   * 归还火花到池
   * @param {Object} spark
   */
  function returnSparkToPool(spark) {
    spark.active = false;
    spark.element.style.display = 'none';
    if (spark.timeout) {
      clearTimeout(spark.timeout);
      spark.timeout = null;
    }
  }

  // ==================== 火花效果 ====================

  /**
   * 设置点击火花效果
   */
  function setupClickSparks() {
    // 使用事件委托
    document.addEventListener('click', handleClick, { passive: true });
  }

  /**
   * 处理点击事件
   * @param {Event} e
   */
  function handleClick(e) {
    const target = e.target;
    if (target.closest('.sidebar-icon, #send-btn, #search-btn, .cae-btn, .window-btn')) {
      createSparks(e.clientX, e.clientY);
    }
  }

  /**
   * 创建点击火花
   * @param {number} x - X 坐标
   * @param {number} y - Y 坐标
   */
  function createSparks(x, y) {
    if (!container || !config.enableSparks) return;

    const count = randomInt(8, 12);

    for (let i = 0; i < count; i++) {
      const spark = getSparkFromPool();
      if (!spark) break;

      const angle = random(0, Math.PI * 2);
      const dist = random(30, 80);
      const dx = Math.cos(angle) * dist;
      const dy = Math.sin(angle) * dist;

      spark.element.style.cssText = `
        left: ${x}px;
        top: ${y}px;
        --dx: ${dx}px;
        --dy: ${dy}px;
        width: ${random(2, 5)}px;
        height: ${random(2, 5)}px;
        display: block;
        animation-duration: 0.8s;
      `;

      // 自动归还
      spark.timeout = setTimeout(() => returnSparkToPool(spark), 800);
    }
  }

  /**
   * 创建悬停飞溅效果
   * @param {number} x - X 坐标
   * @param {number} y - Y 坐标
   */
  function createHoverSplash(x, y) {
    if (!container || !config.enableSparks) return;

    const count = randomInt(5, 8);

    for (let i = 0; i < count; i++) {
      const spark = getSparkFromPool();
      if (!spark) break;

      const angle = (Math.PI * 2 / count) * i + random(0, 0.5);
      const dist = random(20, 50);
      const dx = Math.cos(angle) * dist;
      const dy = Math.sin(angle) * dist;

      spark.element.style.cssText = `
        left: ${x}px;
        top: ${y}px;
        --dx: ${dx}px;
        --dy: ${dy}px;
        width: ${random(2, 4)}px;
        height: ${random(2, 4)}px;
        display: block;
        animation-duration: 0.6s;
      `;

      spark.timeout = setTimeout(() => returnSparkToPool(spark), 600);
    }
  }

  /**
   * 创建发送按钮爆发效果
   * @param {number} x - X 坐标
   * @param {number} y - Y 坐标
   */
  function createSendBurst(x, y) {
    if (!container || !config.enableSparks) return;

    for (let i = 0; i < 20; i++) {
      const spark = getSparkFromPool();
      if (!spark) break;

      const angle = random(0, Math.PI * 2);
      const startD = random(40, 70);
      const endD = random(10, 30);
      const sx = x + Math.cos(angle) * startD;
      const sy = y + Math.sin(angle) * startD;
      const dx = Math.cos(angle) * (endD - startD);
      const dy = Math.sin(angle) * (endD - startD);

      spark.element.style.cssText = `
        left: ${sx}px;
        top: ${sy}px;
        --dx: ${dx}px;
        --dy: ${dy}px;
        width: ${random(2, 5)}px;
        height: ${random(2, 5)}px;
        display: block;
        animation-duration: 0.5s;
        animation-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);
      `;

      spark.timeout = setTimeout(() => returnSparkToPool(spark), 500);
    }
  }

  // ==================== 控制函数 ====================

  /**
   * 暂停粒子动画
   */
  function pause() {
    particles.forEach(p => {
      p.style.animationPlayState = 'paused';
    });
  }

  /**
   * 恢复粒子动画
   */
  function resume() {
    particles.forEach(p => {
      p.style.animationPlayState = 'running';
    });
  }

  /**
   * 设置粒子数量
   * @param {number} count
   */
  function setParticleCount(count) {
    const diff = count - particles.length;

    if (diff > 0) {
      // 添加粒子
      const fragment = document.createDocumentFragment();
      for (let i = 0; i < diff; i++) {
        const p = createParticleElement();
        particles.push(p);
        fragment.appendChild(p);
      }
      container.appendChild(fragment);
    } else if (diff < 0) {
      // 移除粒子
      for (let i = 0; i < -diff; i++) {
        const p = particles.pop();
        p?.remove();
      }
    }

    config.particleCount = count;
  }

  /**
   * 启用/禁用火花效果
   * @param {boolean} enabled
   */
  function setSparksEnabled(enabled) {
    config.enableSparks = enabled;
  }

  /**
   * 清理资源
   */
  function destroy() {
    if (animationId) {
      cancelAnimationFrame(animationId);
    }
    particles.forEach(p => p.remove());
    sparkPool.forEach(s => {
      if (s.timeout) clearTimeout(s.timeout);
      s.element.remove();
    });
    particles = [];
    sparkPool = [];
  }

  // ==================== 导出 ====================
  window.Particles = {
    init,
    createSparks,
    createHoverSplash,
    createSendBurst,
    pause,
    resume,
    setParticleCount,
    setSparksEnabled,
    destroy
  };

})();