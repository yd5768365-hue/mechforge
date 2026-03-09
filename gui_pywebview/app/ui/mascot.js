/**
 * Mascot - 吉祥物与共鸣效果模块
 * 处理鲸鱼吉祥物显示、符文共鸣、思考波纹等效果
 */

(function () {
  'use strict';

  const { $, escapeHtml, random, randomInt, RUNE_CHARS, RUNE_COUNT, WHALE_SPEECH_MAX_LEN } = Utils;

  // ==================== 状态 ====================
  let visible = false;
  let runeElements = [];
  let resonanceInterval = null;

  // ==================== DOM 元素 ====================
  let mascotToggle = null;
  let mascotWhale = null;
  let defaultGear = null;
  let runeContainer = null;
  let whaleSpeech = null;

  /**
   * 初始化吉祥物模块
   */
  function init() {
    mascotToggle = $('mascot-toggle');
    mascotWhale = document.querySelector('.mascot-whale');
    defaultGear = document.querySelector('.default-gear');
    runeContainer = $('rune-container');
    whaleSpeech = $('whale-speech');

    mascotToggle?.addEventListener('click', toggle);
  }

  /**
   * 切换吉祥物显示状态
   */
  function toggle() {
    visible = !visible;
    mascotToggle?.classList.toggle('active', visible);

    if (visible) {
      mascotWhale?.classList.remove('hidden');
      mascotWhale?.classList.add('visible');
      defaultGear?.classList.add('hidden');
    } else {
      mascotWhale?.classList.remove('visible');
      mascotWhale?.classList.add('hidden');
      defaultGear?.classList.remove('hidden');
    }
  }

  /**
   * 检查吉祥物是否可见
   * @returns {boolean}
   */
  function isVisible() {
    return visible;
  }

  // ==================== 数据共鸣效果 ====================

  /**
   * 开始共鸣效果
   */
  function startResonance() {
    if (!visible) return;

    mascotWhale?.classList.add('resonating');

    if (runeContainer) {
      runeContainer.classList.add('active');
      generateRunes();
    }

    resonanceInterval = setInterval(updateRunes, 500);
  }

  /**
   * 停止共鸣效果
   */
  function stopResonance() {
    mascotWhale?.classList.remove('resonating');
    runeContainer?.classList.remove('active');

    if (resonanceInterval) {
      clearInterval(resonanceInterval);
      resonanceInterval = null;
    }

    if (whaleSpeech) {
      whaleSpeech.classList.remove('active');
      whaleSpeech.textContent = '';
    }
  }

  /**
   * 生成符文元素
   */
  function generateRunes() {
    if (!runeContainer) return;

    // 清除旧符文
    runeElements.forEach(el => el.remove());
    runeElements = [];

    for (let i = 0; i < RUNE_COUNT; i++) {
      const rune = document.createElement('div');
      rune.className = 'rune-char';

      const angle = (i / RUNE_COUNT) * Math.PI * 2 - Math.PI / 2;
      const r = 160 + random(0, 40);

      rune.style.left = `${Math.cos(angle) * r + 200}px`;
      rune.style.top = `${Math.sin(angle) * r + 200}px`;
      rune.style.animationDelay = `${i * 0.1}s`;
      rune.textContent = RUNE_CHARS[randomInt(0, RUNE_CHARS.length - 1)];

      runeContainer.appendChild(rune);
      runeElements.push(rune);
    }
  }

  /**
   * 更新符文（随机变化）
   */
  function updateRunes() {
    runeElements.forEach(rune => {
      if (Math.random() > 0.7) {
        rune.textContent = RUNE_CHARS[randomInt(0, RUNE_CHARS.length - 1)];
      }
    });
  }

  /**
   * 更新鲸鱼语音气泡
   * @param {string} text - 显示文本
   */
  function updateWhaleSpeech(text) {
    if (!whaleSpeech || !visible) return;

    whaleSpeech.classList.add('active');

    const display = text.length > WHALE_SPEECH_MAX_LEN
      ? text.substring(0, WHALE_SPEECH_MAX_LEN) + '...'
      : text;

    whaleSpeech.innerHTML = `${escapeHtml(display)}<span class="typing-cursor"></span>`;
  }

  // ==================== 导出 ====================
  window.Mascot = {
    init,
    toggle,
    isVisible,
    startResonance,
    stopResonance,
    updateWhaleSpeech
  };

})();