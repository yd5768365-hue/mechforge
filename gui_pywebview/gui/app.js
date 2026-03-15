// MechForge AI - Application Logic (Modular Architecture)
(function() {
  'use strict';

  // ==================== Services ====================
  // Services will be initialized after DOM loads

  // ==================== State ====================
  const state = {
    activeTab: 'chat',
    booted: false,
    messages: [],
    knowledgeResults: [],
    caeModel: null,
    meshData: null,
    solveResults: null,
    isAnimating: false,
    // Service instances
    aiService: null,
    configService: null
  };

  // ==================== DOM Elements ====================
  const elements = {
    sidebarIcons: document.querySelectorAll('.sidebar-icon'),
    tabPanels: document.querySelectorAll('.tab-panel'),
    bootSequence: document.getElementById('boot-sequence'),
    chatOutput: document.getElementById('chat-output'),
    chatInput: document.getElementById('chat-input'),
    sendBtn: document.getElementById('send-btn'),
    knowledgeSearch: document.getElementById('knowledge-search'),
    searchBtn: document.getElementById('search-btn'),
    searchResults: document.getElementById('search-results'),
    loadModelBtn: document.getElementById('load-model-btn'),
    meshBtn: document.getElementById('mesh-btn'),
    solveBtn: document.getElementById('solve-btn'),
    visualizeBtn: document.getElementById('visualize-btn'),
    clearBtn: document.getElementById('clear-btn'),
    caeCanvas: document.getElementById('cae-canvas'),
    viewportOverlay: document.getElementById('viewport-overlay'),
    statusText: document.getElementById('status-text'),
    modelName: document.getElementById('model-name'),
    elementCount: document.getElementById('element-count'),
    nodeCount: document.getElementById('node-count'),
    windowBtns: document.querySelectorAll('.window-btn'),
    particlesContainer: document.getElementById('particles'),
    mascotToggle: document.getElementById('mascot-toggle'),
    mascotWhale: document.querySelector('.mascot-whale'),
    defaultGear: document.querySelector('.default-gear')
  };

  // ==================== Boot Sequence ====================
  const bootLines = [
    { text: '[21:04] SYSTEM: Initializing MechForge AI...', delay: 0, color: '#c8d8e0' },
    { text: '> AI Assistant Ready', delay: 600, color: '#00e5ff' },
    { text: 'Model: qwen2.5:3b', delay: 1000, color: '#00e5ff' },
    { text: 'RAG Status: Active', delay: 1200, color: '#00e5ff' },
    { text: 'API: Ollama', delay: 1400, color: '#00e5ff' },
    { text: 'Memory: 42 KB', delay: 1600, color: '#00e5ff' },
    { text: 'Awaiting input...', delay: 2000, color: '#c8d8e0' }
  ];

  // ==================== Initialization ====================
  function init() {
    // Initialize services
    initServices();

    // Run UI initialization
    runBootSequence();
    setupEventListeners();
    initCAECanvas();
    initParticles();
    setupClickSparks();

    // Register event handlers
    registerEventHandlers();
  }

  // Initialize services
  function initServices() {
    // Services are already loaded via script tags
    // Create instances
    state.aiService = new AIService(apiClient, eventBus);
    state.configService = new ConfigService(apiClient, eventBus);

    // Initialize config asynchronously
    state.configService.init().then(({ config, models }) => {
      if (config) {
        updateStatusBar(config);
      }
    }).catch(() => {
      // Use default values
    });
  }

  // Update status bar with config
  function updateStatusBar(config) {
    const modelEl = document.querySelector('[data-status="model"]');
    const apiEl = document.querySelector('[data-status="api"]');

    if (modelEl && config.ai) {
      modelEl.textContent = `Model: ${config.ai.model || 'qwen2.5:3b'}`;
    }
    if (apiEl && config.ai) {
      apiEl.textContent = `API: ${config.ai.provider || 'Ollama'}`;
    }
  }

  // Register event handlers from services
  function registerEventHandlers() {
    // AI message sent
    eventBus.on(Events.AI_MESSAGE_SENT, ({ message }) => {
      console.log('AI Message sent:', message);
    });

    // AI response received
    eventBus.on(Events.AI_RESPONSE_RECEIVED, ({ message }) => {
      console.log('AI Response received:', message);
    });

    // AI error
    eventBus.on(Events.AI_ERROR, ({ error }) => {
      console.error('AI Error:', error);
      addSystemMessage(`Error: ${error}`);
    });

    // Config loaded
    eventBus.on(Events.CONFIG_LOADED, ({ config, models }) => {
      updateStatusBar(config);
    });

    // RAG enabled/disabled
    eventBus.on(Events.RAG_ENABLED, () => {
      updateRAGStatus(true);
    });

    eventBus.on(Events.RAG_DISABLED, () => {
      updateRAGStatus(false);
    });
  }

  function updateRAGStatus(enabled) {
    const ragEl = document.querySelector('[data-status="rag"]');
    if (ragEl) {
      ragEl.textContent = enabled ? 'RAG: ON' : 'RAG: OFF';
      ragEl.classList.toggle('status-on', enabled);
    }
  }

  // ==================== Boot Sequence ====================
  function runBootSequence() {
    bootLines.forEach((line, index) => {
      setTimeout(() => {
        const lineEl = document.createElement('div');
        lineEl.className = 'boot-line';

        // 根据索引添加不同样式
        if (index === 0) {
          lineEl.classList.add('system');
        } else if (index >= 1 && index <= 5) {
          lineEl.classList.add('info');
        } else if (index === bootLines.length - 1) {
          lineEl.classList.add('waiting');
        }

        lineEl.style.color = line.color;
        lineEl.textContent = line.text;
        elements.bootSequence.appendChild(lineEl);

        if (index === bootLines.length - 1) {
          state.booted = true;
          setTimeout(() => {
            const separator = document.createElement('div');
            separator.style.cssText = 'height:1px;background:linear-gradient(90deg,#00e5ff33,transparent);margin:12px 0;';
            elements.bootSequence.appendChild(separator);

            const cursorLine = document.createElement('div');
            cursorLine.className = 'boot-line waiting-cursor';
            cursorLine.innerHTML = '<span class="cursor">_</span>';
            elements.bootSequence.appendChild(cursorLine);
          }, 300);
        }
      }, line.delay);
    });
  }

  // ==================== Event Listeners ====================
  function setupEventListeners() {
    // Tab switching
    elements.sidebarIcons.forEach(icon => {
      icon.addEventListener('click', () => {
        const tab = icon.dataset.tab;
        switchTab(tab);
      });

      icon.addEventListener('mouseenter', (e) => {
        const rect = icon.getBoundingClientRect();
        const centerX = rect.left + rect.width / 2;
        const centerY = rect.top + rect.height / 2;
        createHoverSplash(centerX, centerY);
      });
    });

    // Chat input
    elements.chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
    elements.sendBtn.addEventListener('click', sendMessage);

    // Mascot toggle
    elements.mascotToggle.addEventListener('click', toggleMascot);

    // Knowledge search
    elements.knowledgeSearch.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') performSearch();
    });
    elements.searchBtn.addEventListener('click', performSearch);

    // CAE buttons
    elements.loadModelBtn.addEventListener('click', loadModel);
    elements.meshBtn.addEventListener('click', generateMesh);
    elements.solveBtn.addEventListener('click', runSolve);
    elements.visualizeBtn.addEventListener('click', visualizeResults);
    elements.clearBtn.addEventListener('click', clearCAE);
  }

  // ==================== Tab Switching ====================
  function switchTab(tab) {
    state.activeTab = tab;

    // Update sidebar icons
    elements.sidebarIcons.forEach(icon => {
      icon.classList.toggle('active', icon.dataset.tab === tab);
    });

    // Update panels
    elements.tabPanels.forEach(panel => {
      panel.classList.toggle('active', panel.id === `${tab}-panel`);
    });

    // Emit event
    eventBus.emit(Events.UI_TAB_CHANGED, { tab });
  }

  // ==================== Chat Functions ====================
  async function sendMessage() {
    const text = elements.chatInput.value.trim();
    if (!text || !state.booted || !state.aiService) return;

    // 禁用输入框
    elements.chatInput.disabled = true;
    elements.sendBtn.disabled = true;

    // 点击发送按钮时产生粒子聚集效果
    const btnRect = elements.sendBtn.getBoundingClientRect();
    createSendBurst(btnRect.left + btnRect.width / 2, btnRect.top + btnRect.height / 2);

    const now = new Date();
    const time = `[${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}]`;

    // 添加用户消息
    addMessage('user', text, time);
    elements.chatInput.value = '';

    try {
      // 使用流式模式
      let aiMessageEl = null;
      let lastContent = '';

      await state.aiService.sendMessageStream(text, (content, isDone) => {
        if (!aiMessageEl) {
          // 创建 AI 消息元素
          aiMessageEl = document.createElement('div');
          aiMessageEl.className = 'chat-message ai slide-in';
          aiMessageEl.innerHTML = '<span class="ai-prefix">&gt;</span>';
          elements.chatOutput.appendChild(aiMessageEl);
        }

        // 更新内容（只添加新增部分）
        const newContent = content.slice(lastContent.length);
        if (newContent) {
          const span = document.createElement('span');
          span.textContent = newContent;
          aiMessageEl.appendChild(span);
          lastContent = content;
        }

        // 滚动到底部
        elements.chatOutput.scrollTop = elements.chatOutput.scrollHeight;
      });

    } catch (error) {
      addSystemMessage(`Error: ${error.message}`);
    } finally {
      // 恢复输入框
      elements.chatInput.disabled = false;
      elements.sendBtn.disabled = false;
      elements.chatInput.focus();
    }
  }

  function addMessage(type, text, time) {
    const messageEl = document.createElement('div');
    messageEl.className = `chat-message ${type} slide-in`;

    if (type === 'user') {
      messageEl.innerHTML = `
        <span class="message-time">${time}</span>
        <span class="message-prefix">&gt;</span> ${escapeHtml(text)}
      `;
    } else {
      const lines = text.split('\n');
      messageEl.innerHTML = lines.map(line => {
        if (line.startsWith('>')) {
          return `<div><span class="ai-prefix">${escapeHtml(line)}</span></div>`;
        }
        return `<div>${escapeHtml(line)}</div>`;
      }).join('');
    }

    elements.chatOutput.appendChild(messageEl);
    elements.chatOutput.scrollTop = elements.chatOutput.scrollHeight;
  }

  function addSystemMessage(text) {
    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message ai slide-in';
    messageEl.innerHTML = `<span style="color: #ff4757;">${escapeHtml(text)}</span>`;
    elements.chatOutput.appendChild(messageEl);
    elements.chatOutput.scrollTop = elements.chatOutput.scrollHeight;
  }

  function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'chat-message ai typing-indicator slide-in';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
      <span class="ai-prefix">&gt;</span>
      <span class="typing-text">Thinking</span>
      <span class="typing-cursor"></span>
    `;
    elements.chatOutput.appendChild(indicator);
    elements.chatOutput.scrollTop = elements.chatOutput.scrollHeight;
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
      indicator.remove();
    }
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // ==================== Mascot Toggle ====================
  let mascotVisible = false;

  function toggleMascot() {
    mascotVisible = !mascotVisible;
    elements.mascotToggle.classList.toggle('active', mascotVisible);

    if (mascotVisible) {
      elements.mascotWhale.classList.remove('hidden');
      elements.mascotWhale.classList.add('visible');
      elements.defaultGear.classList.add('hidden');
    } else {
      elements.mascotWhale.classList.remove('visible');
      elements.mascotWhale.classList.add('hidden');
      elements.defaultGear.classList.remove('hidden');
    }
  }

  // ==================== Knowledge Search ====================
  async function performSearch() {
    const query = elements.knowledgeSearch.value.trim();
    if (!query) return;

    elements.searchResults.innerHTML = '<div class="result-placeholder">Searching...</div>';

    try {
      const results = await state.aiService.searchKnowledge(query);
      displaySearchResults(results);
    } catch (error) {
      elements.searchResults.innerHTML = `<div class="result-placeholder">Error: ${error.message}</div>`;
    }
  }

  function displaySearchResults(results) {
    if (!results || results.length === 0) {
      elements.searchResults.innerHTML = '<div class="result-placeholder">No results found</div>';
      return;
    }

    elements.searchResults.innerHTML = results.map((result, index) => `
      <div class="result-item">
        <div class="result-title">${escapeHtml(result.title || `Result ${index + 1}`)}</div>
        <div class="result-snippet">${escapeHtml(result.content || result.snippet || '')}</div>
        <div class="result-meta">
          <span>Score: ${(result.score || 0).toFixed(2)}</span>
          ${result.source ? `<span>Source: ${escapeHtml(result.source)}</span>` : ''}
        </div>
      </div>
    `).join('');
  }

  // ==================== CAE Functions ====================
  function initCAECanvas() {
    const canvas = elements.caeCanvas;
    const ctx = canvas.getContext('2d');

    // Set canvas size
    const resize = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = canvas.parentElement.clientHeight;
    };
    resize();
    window.addEventListener('resize', resize);
  }

  function loadModel() {
    elements.viewportOverlay.classList.add('hidden');
    updateCAEStatus('Model Loaded', 'bracket.step', 0, 0);
  }

  function generateMesh() {
    updateCAEStatus('Meshing...', '', 0, 0);

    setTimeout(() => {
      updateCAEStatus('Mesh Complete', '', 1250, 486);
      drawMeshPreview();
    }, 1000);
  }

  function runSolve() {
    updateCAEStatus('Solving...', '', 1250, 486);

    setTimeout(() => {
      updateCAEStatus('Solve Complete', '', 1250, 486);
    }, 2000);
  }

  function visualizeResults() {
    drawStressContour();
    updateCAEStatus('Visualizing', '', 1250, 486);
  }

  function clearCAE() {
    elements.viewportOverlay.classList.remove('hidden');
    updateCAEStatus('Ready', 'None', 0, 0);

    const canvas = elements.caeCanvas;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }

  function updateCAEStatus(status, model, elementsCount, nodesCount) {
    elements.statusText.textContent = status;
    elements.modelName.textContent = model;
    elements.elementCount.textContent = elementsCount;
    elements.nodeCount.textContent = nodesCount;
  }

  function drawMeshPreview() {
    const canvas = elements.caeCanvas;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    ctx.strokeStyle = 'rgba(0, 229, 255, 0.5)';
    ctx.lineWidth = 0.5;

    // Draw mesh lines
    for (let i = 0; i < 50; i++) {
      const x1 = Math.random() * w;
      const y1 = Math.random() * h;
      const x2 = x1 + (Math.random() - 0.5) * 100;
      const y2 = y1 + (Math.random() - 0.5) * 100;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }
  }

  function drawStressContour() {
    const canvas = elements.caeCanvas;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;

    // Draw stress contour
    const gradient = ctx.createLinearGradient(0, 0, w, h);
    gradient.addColorStop(0, 'rgba(0, 100, 255, 0.3)');
    gradient.addColorStop(0.5, 'rgba(0, 255, 100, 0.3)');
    gradient.addColorStop(1, 'rgba(255, 50, 50, 0.3)');

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, w, h);
  }

  // ==================== Particle Effects ====================
  function initParticles() {
    const container = elements.particlesContainer;
    const particleCount = 15;

    for (let i = 0; i < particleCount; i++) {
      createParticle(container);
    }
  }

  function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';

    const size = Math.random() * 3 + 2;
    const startX = Math.random() * 100;
    const startY = Math.random() * 100;
    const duration = Math.random() * 20 + 15;
    const delay = Math.random() * -30;
    const twinkleDuration = Math.random() * 2 + 1.5;

    particle.style.cssText = `
      width: ${size}px;
      height: ${size}px;
      left: ${startX}%;
      top: ${startY}%;
      animation: floatParticle ${duration}s linear ${delay}s infinite,
                 twinkle ${twinkleDuration}s ease-in-out infinite;
    `;

    if (Math.random() > 0.5) {
      particle.style.animation += ', particleTrail 1.5s ease-out infinite';
    }

    container.appendChild(particle);
  }

  function setupClickSparks() {
    document.addEventListener('click', (e) => {
      if (e.target.closest('.sidebar-icon') ||
          e.target.closest('#send-btn') ||
          e.target.closest('#search-btn') ||
          e.target.closest('.cae-btn') ||
          e.target.closest('.window-btn')) {
        createSparks(e.clientX, e.clientY);
      }
    });
  }

  function createSparks(x, y) {
    const container = elements.particlesContainer;
    const sparkCount = 8 + Math.floor(Math.random() * 5);

    for (let i = 0; i < sparkCount; i++) {
      const spark = document.createElement('div');
      spark.className = 'spark-particle';

      const angle = Math.random() * Math.PI * 2;
      const distance = 30 + Math.random() * 50;
      const dx = Math.cos(angle) * distance;
      const dy = Math.sin(angle) * distance;

      spark.style.cssText = `
        left: ${x}px;
        top: ${y}px;
        --dx: ${dx}px;
        --dy: ${dy}px;
        width: ${2 + Math.random() * 3}px;
        height: ${2 + Math.random() * 3}px;
      `;

      container.appendChild(spark);
      setTimeout(() => spark.remove(), 800);
    }
  }

  function createHoverSplash(x, y) {
    const container = elements.particlesContainer;
    const splashCount = 5 + Math.floor(Math.random() * 4);

    for (let i = 0; i < splashCount; i++) {
      const splash = document.createElement('div');
      splash.className = 'spark-particle';

      const angle = (Math.PI * 2 / splashCount) * i + Math.random() * 0.5;
      const distance = 20 + Math.random() * 30;
      const dx = Math.cos(angle) * distance;
      const dy = Math.sin(angle) * distance;

      splash.style.cssText = `
        left: ${x}px;
        top: ${y}px;
        --dx: ${dx}px;
        --dy: ${dy}px;
        width: ${2 + Math.random() * 2}px;
        height: ${2 + Math.random() * 2}px;
        animation-duration: 0.6s;
      `;

      container.appendChild(splash);
      setTimeout(() => splash.remove(), 600);
    }
  }

  function createSendBurst(x, y) {
    const container = elements.particlesContainer;
    const particleCount = 20;

    for (let i = 0; i < particleCount; i++) {
      const particle = document.createElement('div');
      particle.className = 'spark-particle';

      const angle = Math.random() * Math.PI * 2;
      const startDist = 40 + Math.random() * 30;
      const endDist = 10 + Math.random() * 20;
      const startX = x + Math.cos(angle) * startDist;
      const startY = y + Math.sin(angle) * startDist;
      const dx = Math.cos(angle) * (endDist - startDist);
      const dy = Math.sin(angle) * (endDist - startDist);

      particle.style.cssText = `
        left: ${startX}px;
        top: ${startY}px;
        --dx: ${dx}px;
        --dy: ${dy}px;
        width: ${2 + Math.random() * 3}px;
        height: ${2 + Math.random() * 3}px;
        animation-duration: 0.5s;
        animation-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);
      `;

      container.appendChild(particle);
      setTimeout(() => particle.remove(), 500);
    }
  }

  // ==================== Start Application ====================
  // Wait for DOM and services to load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
