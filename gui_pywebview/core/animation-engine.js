/**
 * AnimationEngine - 动画引擎
 * 提供高性能的动画系统，支持 CSS 动画、Web Animations API 和自定义动画
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    useWebAnimationsAPI: true,
    useRequestAnimationFrame: true,
    defaultEasing: 'cubic-bezier(0.4, 0, 0.2, 1)',
    defaultDuration: 300,
    fpsLimit: 60
  };

  // ==================== 缓动函数 ====================
  const easings = {
    linear: t => t,
    easeIn: t => t * t,
    easeOut: t => 1 - (1 - t) * (1 - t),
    easeInOut: t => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2,
    easeInCubic: t => t * t * t,
    easeOutCubic: t => 1 - Math.pow(1 - t, 3),
    easeInOutCubic: t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
    easeInQuart: t => t * t * t * t,
    easeOutQuart: t => 1 - Math.pow(1 - t, 4),
    easeInBack: t => 2.70158 * t * t * t - 1.70158 * t * t,
    easeOutBack: t => 1 + 2.70158 * Math.pow(t - 1, 3) + 1.70158 * Math.pow(t - 1, 2),
    elastic: t => {
      const c4 = (2 * Math.PI) / 3;
      return t === 0 ? 0 : t === 1 ? 1 : -Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * c4);
    },
    bounce: t => {
      const n1 = 7.5625;
      const d1 = 2.75;
      if (t < 1 / d1) {
        return n1 * t * t;
      } else if (t < 2 / d1) {
        return n1 * (t -= 1.5 / d1) * t + 0.75;
      } else if (t < 2.5 / d1) {
        return n1 * (t -= 2.25 / d1) * t + 0.9375;
      } 
        return n1 * (t -= 2.625 / d1) * t + 0.984375;
      
    }
  };

  // ==================== 动画状态管理 ====================
  const activeAnimations = new Map();
  let animationIdCounter = 0;

  // ==================== 核心动画函数 ====================

  /**
   * 使用 Web Animations API 创建动画
   * @param {HTMLElement} element - 目标元素
   * @param {Array} keyframes - 关键帧
   * @param {Object} options - 动画选项
   * @returns {Animation}
   */
  function animate(element, keyframes, options = {}) {
    if (!element) return null;

    const {
      duration = config.defaultDuration,
      easing = config.defaultEasing,
      delay = 0,
      iterations = 1,
      direction = 'normal',
      fill = 'forwards',
      onComplete,
      onUpdate
    } = options;

    // 使用 Web Animations API
    if (config.useWebAnimationsAPI && element.animate) {
      const animation = element.animate(keyframes, {
        duration,
        easing,
        delay,
        iterations,
        direction,
        fill
      });

      if (onComplete) {
        animation.onfinish = onComplete;
      }

      return animation;
    }

    // 降级到自定义动画
    return customAnimate(element, keyframes, options);
  }

  /**
   * 自定义动画实现（降级方案）
   * @param {HTMLElement} element - 目标元素
   * @param {Array} keyframes - 关键帧
   * @param {Object} options - 动画选项
   * @returns {Object}
   */
  function customAnimate(element, keyframes, options) {
    const {
      duration = config.defaultDuration,
      easing = 'easeInOut',
      onComplete
    } = options;

    const id = ++animationIdCounter;
    const startTime = performance.now();
    const easingFn = easings[easing] || easings.easeInOut;

    const animation = {
      id,
      element,
      keyframes,
      duration,
      easing: easingFn,
      startTime,
      onComplete,
      isRunning: true
    };

    activeAnimations.set(id, animation);

    if (activeAnimations.size === 1) {
      startAnimationLoop();
    }

    return {
      id,
      cancel: () => cancelAnimation(id)
    };
  }

  /**
   * 动画循环
   */
  function startAnimationLoop() {
    let lastTime = performance.now();

    function loop(currentTime) {
      if (activeAnimations.size === 0) return;

      const deltaTime = currentTime - lastTime;
      lastTime = currentTime;

      activeAnimations.forEach((animation, id) => {
        if (!animation.isRunning) return;

        const elapsed = currentTime - animation.startTime;
        const progress = Math.min(elapsed / animation.duration, 1);
        const easedProgress = animation.easing(progress);

        // 应用关键帧插值
        applyKeyframe(animation.element, animation.keyframes, easedProgress);

        if (progress >= 1) {
          animation.isRunning = false;
          activeAnimations.delete(id);
          if (animation.onComplete) {
            animation.onComplete();
          }
        }
      });

      if (activeAnimations.size > 0) {
        requestAnimationFrame(loop);
      }
    }

    requestAnimationFrame(loop);
  }

  /**
   * 应用关键帧
   * @param {HTMLElement} element - 目标元素
   * @param {Array} keyframes - 关键帧
   * @param {number} progress - 进度 (0-1)
   */
  function applyKeyframe(element, keyframes, progress) {
    if (keyframes.length < 2) return;

    // 找到当前进度对应的关键帧
    const totalFrames = keyframes.length - 1;
    const frameProgress = progress * totalFrames;
    const frameIndex = Math.floor(frameProgress);
    const localProgress = frameProgress - frameIndex;

    const startFrame = keyframes[frameIndex];
    const endFrame = keyframes[Math.min(frameIndex + 1, totalFrames)];

    // 插值计算
    const styles = {};
    for (const [prop, startValue] of Object.entries(startFrame)) {
      if (prop === 'offset') continue;

      const endValue = endFrame[prop];
      if (typeof startValue === 'number' && typeof endValue === 'number') {
        styles[prop] = startValue + (endValue - startValue) * localProgress;
      } else {
        styles[prop] = localProgress < 0.5 ? startValue : endValue;
      }
    }

    // 应用样式
    Object.assign(element.style, styles);
  }

  /**
   * 取消动画
   * @param {number} id - 动画 ID
   */
  function cancelAnimation(id) {
    const animation = activeAnimations.get(id);
    if (animation) {
      animation.isRunning = false;
      activeAnimations.delete(id);
    }
  }

  // ==================== 预设动画 ====================

  /**
   * 淡入
   * @param {HTMLElement} element - 目标元素
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function fadeIn(element, options = {}) {
    const { duration = 300, easing = 'easeOut' } = options;

    return new Promise(resolve => {
      element.style.opacity = '0';
      element.style.display = options.display || 'block';

      animate(element, [
        { opacity: 0 },
        { opacity: 1 }
      ], {
        duration,
        easing,
        onComplete: resolve
      });
    });
  }

  /**
   * 淡出
   * @param {HTMLElement} element - 目标元素
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function fadeOut(element, options = {}) {
    const { duration = 300, easing = 'easeIn' } = options;

    return new Promise(resolve => {
      animate(element, [
        { opacity: 1 },
        { opacity: 0 }
      ], {
        duration,
        easing,
        onComplete: () => {
          element.style.display = 'none';
          resolve();
        }
      });
    });
  }

  /**
   * 滑动进入
   * @param {HTMLElement} element - 目标元素
   * @param {string} direction - 方向 (up|down|left|right)
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function slideIn(element, direction = 'up', options = {}) {
    const { duration = 400, easing = 'easeOutBack', distance = 50 } = options;

    const transforms = {
      up: { y: distance },
      down: { y: -distance },
      left: { x: distance },
      right: { x: -distance }
    };

    const offset = transforms[direction] || transforms.up;

    return new Promise(resolve => {
      element.style.display = options.display || 'block';

      animate(element, [
        { opacity: 0, transform: `translate(${offset.x || 0}px, ${offset.y || 0}px)` },
        { opacity: 1, transform: 'translate(0, 0)' }
      ], {
        duration,
        easing,
        onComplete: resolve
      });
    });
  }

  /**
   * 缩放动画
   * @param {HTMLElement} element - 目标元素
   * @param {number} from - 起始缩放
   * @param {number} to - 结束缩放
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function scale(element, from = 0, to = 1, options = {}) {
    const { duration = 300, easing = 'easeOutBack' } = options;

    return new Promise(resolve => {
      element.style.display = options.display || 'block';

      animate(element, [
        { transform: `scale(${from})`, opacity: from === 0 ? 0 : 1 },
        { transform: `scale(${to})`, opacity: 1 }
      ], {
        duration,
        easing,
        onComplete: resolve
      });
    });
  }

  /**
   * 脉冲动画
   * @param {HTMLElement} element - 目标元素
   * @param {Object} options - 选项
   */
  function pulse(element, options = {}) {
    const { duration = 1000, scale = 1.05 } = options;

    return animate(element, [
      { transform: 'scale(1)' },
      { transform: `scale(${scale})` },
      { transform: 'scale(1)' }
    ], {
      duration,
      iterations: Infinity
    });
  }

  /**
   * 抖动动画
   * @param {HTMLElement} element - 目标元素
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function shake(element, options = {}) {
    const { duration = 500, intensity = 10 } = options;

    return new Promise(resolve => {
      animate(element, [
        { transform: 'translateX(0)' },
        { transform: `translateX(-${intensity}px)` },
        { transform: `translateX(${intensity}px)` },
        { transform: `translateX(-${intensity}px)` },
        { transform: `translateX(${intensity}px)` },
        { transform: 'translateX(0)' }
      ], {
        duration,
        onComplete: resolve
      });
    });
  }

  /**
   * 翻转动画
   * @param {HTMLElement} element - 目标元素
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function flip(element, options = {}) {
    const { duration = 600, axis = 'Y' } = options;

    return new Promise(resolve => {
      animate(element, [
        { transform: `${axis === 'Y' ? 'rotateY' : 'rotateX'}(0deg)` },
        { transform: `${axis === 'Y' ? 'rotateY' : 'rotateX'}(180deg)` },
        { transform: `${axis === 'Y' ? 'rotateY' : 'rotateX'}(360deg)` }
      ], {
        duration,
        onComplete: resolve
      });
    });
  }

  /**
   * 打字机效果
   * @param {HTMLElement} element - 目标元素
   * @param {string} text - 文本内容
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function typewriter(element, text, options = {}) {
    const { speed = 50, cursor = true } = options;

    return new Promise(resolve => {
      let index = 0;
      element.textContent = cursor ? '|' : '';

      const interval = setInterval(() => {
        if (index < text.length) {
          element.textContent = text.slice(0, index + 1) + (cursor ? '|' : '');
          index++;
        } else {
          clearInterval(interval);
          if (cursor) {
            element.textContent = text;
          }
          resolve();
        }
      }, speed);
    });
  }

  /**
   * 数字滚动动画
   * @param {HTMLElement} element - 目标元素
   * @param {number} from - 起始值
   * @param {number} to - 结束值
   * @param {Object} options - 选项
   * @returns {Promise}
   */
  function countUp(element, from = 0, to = 100, options = {}) {
    const { duration = 1000, easing = 'easeOut' } = options;
    const easingFn = easings[easing] || easings.easeOut;

    return new Promise(resolve => {
      const startTime = performance.now();

      function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const easedProgress = easingFn(progress);
        const current = from + (to - from) * easedProgress;

        element.textContent = Math.round(current).toLocaleString();

        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          resolve();
        }
      }

      requestAnimationFrame(update);
    });
  }

  /**
   * 交错动画
   * @param {Array<HTMLElement>} elements - 元素数组
   * @param {Function} animationFn - 动画函数
   * @param {Object} options - 选项
   */
  function stagger(elements, animationFn, options = {}) {
    const { stagger = 100, ...animOptions } = options;

    elements.forEach((element, index) => {
      setTimeout(() => {
        animationFn(element, animOptions);
      }, index * stagger);
    });
  }

  /**
   * 创建动画序列
   * @param {Array} steps - 动画步骤
   * @returns {Promise}
   */
  async function sequence(steps) {
    for (const step of steps) {
      const { fn, args, delay = 0 } = step;
      if (delay) {
        await new Promise(r => setTimeout(r, delay));
      }
      await fn(...args);
    }
  }

  // ==================== 导出 ====================
  window.AnimationEngine = {
    config,
    easings,
    animate,
    fadeIn,
    fadeOut,
    slideIn,
    scale,
    pulse,
    shake,
    flip,
    typewriter,
    countUp,
    stagger,
    sequence,
    cancelAnimation
  };

})();
