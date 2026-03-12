/**
 * CAEWorkbench - CAE 工作台模块
 * 处理模型加载、网格生成、求解、可视化等功能
 * 
 * 功能：
 * - 模型加载与预览
 * - 网格生成与显示
 * - 求解器控制
 * - 结果可视化
 * - 交互式视图控制
 */

(function () {
  'use strict';

  const { $, debounce, throttle } = Utils;

  // ==================== 日志器 ====================
  const log = window.Logger?.module('CAE') || {
    info: console.log,
    warn: console.warn,
    error: console.error
  };

  // ==================== 状态 ====================
  const state = {
    model: null,
    mesh: null,
    results: null,
    viewMode: 'wireframe', // wireframe, solid, contour
    isProcessing: false,
    camera: {
      rotationX: 0,
      rotationY: 0,
      zoom: 1
    }
  };

  // ==================== DOM 元素 ====================
  let elements = {};

  // ==================== 初始化 ====================

  /**
   * 初始化 CAE 工作台
   */
  function init() {
    // 缓存 DOM 元素
    elements = {
      demoBtn: $('demo-btn'),
      loadModelBtn: $('load-model-btn'),
      meshBtn: $('mesh-btn'),
      solveBtn: $('solve-btn'),
      visualizeBtn: $('visualize-btn'),
      clearBtn: $('clear-btn'),
      caeCanvas: $('cae-canvas'),
      viewportOverlay: $('viewport-overlay'),
      statusText: $('status-text'),
      modelName: $('model-name'),
      elementCount: $('element-count'),
      nodeCount: $('node-count')
    };

    initCanvas();
    setupEventListeners();
    addViewControls();
    refreshBackendStatus();
    
    log.info('CAE Workbench initialized');
  }

  /**
   * 初始化 Canvas
   */
  function initCanvas() {
    if (!elements.caeCanvas) return;

    const resize = debounce(() => {
      const parent = elements.caeCanvas.parentElement;
      if (parent) {
        elements.caeCanvas.width = parent.clientWidth;
        elements.caeCanvas.height = parent.clientHeight;
        redraw();
      }
    }, 100);

    resize();
    window.addEventListener('resize', resize);

    // 鼠标交互
    setupCanvasInteraction();
  }

  /**
   * 设置 Canvas 交互
   */
  function setupCanvasInteraction() {
    if (!elements.caeCanvas) return;

    let isDragging = false;
    let lastX = 0;
    let lastY = 0;

    // 鼠标按下
    elements.caeCanvas.addEventListener('mousedown', (e) => {
      isDragging = true;
      lastX = e.clientX;
      lastY = e.clientY;
      elements.caeCanvas.style.cursor = 'grabbing';
    });

    // 鼠标移动
    elements.caeCanvas.addEventListener('mousemove', throttle((e) => {
      if (!isDragging) return;

      const dx = e.clientX - lastX;
      const dy = e.clientY - lastY;

      state.camera.rotationY += dx * 0.5;
      state.camera.rotationX += dy * 0.5;

      lastX = e.clientX;
      lastY = e.clientY;

      redraw();
    }, 16));

    // 鼠标释放
    window.addEventListener('mouseup', () => {
      isDragging = false;
      if (elements.caeCanvas) {
        elements.caeCanvas.style.cursor = 'grab';
      }
    });

    // 滚轮缩放
    elements.caeCanvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      state.camera.zoom = Math.max(0.1, Math.min(5, state.camera.zoom * delta));
      redraw();
    });

    // 设置初始光标
    elements.caeCanvas.style.cursor = 'grab';
  }

  /**
   * 设置事件监听器
   */
  function setupEventListeners() {
    elements.demoBtn?.addEventListener('click', runDemo);
    elements.loadModelBtn?.addEventListener('click', loadModel);
    elements.meshBtn?.addEventListener('click', generateMesh);
    elements.solveBtn?.addEventListener('click', runSolve);
    elements.visualizeBtn?.addEventListener('click', visualizeResults);
    elements.clearBtn?.addEventListener('click', clearCAE);
  }

  /**
   * 添加视图控制按钮
   */
  function addViewControls() {
    const viewport = elements.caeCanvas?.parentElement;
    if (!viewport) return;

    // 创建视图控制面板
    const controls = document.createElement('div');
    controls.className = 'cae-view-controls';
    controls.innerHTML = `
      <button class="view-btn" data-view="wireframe" title="线框视图">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 22 8.5 22 15.5 12 22 2 15.5 2 8.5 12 2"/>
          <line x1="12" y1="22" x2="12" y2="15.5"/>
          <polyline points="22 8.5 12 15.5 2 8.5"/>
        </svg>
      </button>
      <button class="view-btn" data-view="solid" title="实体视图">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
        </svg>
      </button>
      <button class="view-btn" data-view="contour" title="云图视图">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <circle cx="12" cy="12" r="6"/>
          <circle cx="12" cy="12" r="2"/>
        </svg>
      </button>
      <button class="view-btn" data-action="reset" title="重置视图">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
          <path d="M3 3v5h5"/>
        </svg>
      </button>
    `;

    // 添加样式
    const style = document.createElement('style');
    style.textContent = `
      .cae-view-controls {
        position: absolute;
        top: 10px;
        right: 10px;
        display: flex;
        flex-direction: column;
        gap: 4px;
        z-index: 10;
      }
      .view-btn {
        width: 32px;
        height: 32px;
        border-radius: 4px;
        border: 1px solid rgba(0, 229, 255, 0.2);
        background: rgba(10, 14, 20, 0.9);
        color: var(--text-dim);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
      }
      .view-btn:hover {
        background: rgba(0, 229, 255, 0.1);
        color: var(--accent-primary);
        border-color: rgba(0, 229, 255, 0.4);
      }
      .view-btn.active {
        background: rgba(0, 229, 255, 0.2);
        color: var(--accent-primary);
        border-color: var(--accent-primary);
      }
    `;
    document.head.appendChild(style);

    viewport.appendChild(controls);

    // 绑定事件
    controls.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        const action = btn.dataset.action;

        if (view) {
          state.viewMode = view;
          controls.querySelectorAll('.view-btn[data-view]').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          redraw();
        } else if (action === 'reset') {
          resetCamera();
        }
      });
    });

    // 设置默认激活
    controls.querySelector('[data-view="wireframe"]')?.classList.add('active');
  }

  // ==================== 功能函数 ====================

  /**
   * 从后端获取 CAE 状态，用于首屏提示依赖情况
   */
  async function refreshBackendStatus() {
    if (typeof apiClient === 'undefined') {
      return;
    }
    try {
      const status = await apiClient.get('/cae/status');
      const deps = status.dependencies || {};
      const summary = Object.entries(deps)
        .map(([name, info]) => `${name}:${info.ok ? '✓' : '✗'}`)
        .join('  ');
      updateStatus(summary || '就绪', '系统检查', 0, 0);
    } catch (error) {
      log.warn('Failed to fetch CAE status from backend:', error);
    }
  }

  /**
   * 一键运行悬臂梁 Demo（后端真实求解）
   */
  async function runDemo() {
    if (state.isProcessing) return;
    if (typeof apiClient === 'undefined') {
      log.error('API client not available for CAE demo');
      updateStatus('API 未就绪', 'Demo', 0, 0);
      return;
    }

    log.info('Running cantilever beam demo via backend...');
    state.isProcessing = true;
    updateStatus('运行示例...', 'Cantilever 100x10x10 / 1000N', 0, 0);

    try {
      const result = await apiClient.post('/cae/demo', {});

      if (!result.success) {
        const deps = result.dependencies || {};
        const missing = Object.entries(deps)
          .filter(([, info]) => !info)
          .map(([name]) => name)
          .join(', ');
        const msg = result.message || 'CAE Demo 运行失败';
        const detail = missing ? `${msg}（缺少: ${missing}）` : msg;
        updateStatus(detail, 'Cantilever Demo', 0, 0);
        log.warn('CAE demo failed:', detail);
        return;
      }

      // 使用后端返回的数据构造前端状态（仅用于展示）
      const numElements = result.num_elements || 0;
      const numNodes = result.num_nodes || 0;
      state.model = {
        name: 'Cantilever 100x10x10 / 1000N'
      };
      state.mesh = {
        nodes: new Array(numNodes),
        elements: new Array(numElements)
      };
      state.results = {
        displacement: null,
        stress: null
      };

      const disp = typeof result.max_displacement === 'number'
        ? result.max_displacement.toFixed(4)
        : 'N/A';
      const theory = result.theoretical_displacement?.toFixed
        ? result.theoretical_displacement.toFixed(4)
        : Number(result.theoretical_displacement || 0).toFixed(4);
      const errRatio = typeof result.error_ratio === 'number'
        ? `${(result.error_ratio * 100).toFixed(1)}%`
        : 'N/A';

      let statusLabel = '校核通过';
      if (result.status === 'warn') {
        statusLabel = '建议检查网格/边界条件';
      } else if (result.status === 'error') {
        statusLabel = '求解失败';
      }

      const statusText = `${statusLabel} | δ_calc=${disp}mm, δ_theory=${theory}mm, err=${errRatio}`;
      elements.viewportOverlay?.classList.add('hidden');
      updateStatus(statusText, state.model.name, numElements, numNodes);

      // 运行结束后切换到云图视图，强调“结果解释”
      state.viewMode = 'contour';
      redraw();

      log.info('CAE demo completed:', {
        max_displacement: result.max_displacement,
        theoretical: result.theoretical_displacement,
        error_ratio: result.error_ratio
      });
    } catch (error) {
      log.error('CAE demo error:', error);
      updateStatus('Demo 运行异常，请查看日志', 'Cantilever Demo', 0, 0);
    } finally {
      state.isProcessing = false;
    }
  }

  /**
   * 加载模型
   */
  async function loadModel() {
    if (state.isProcessing) return;

    log.info('Loading model...');
    state.isProcessing = true;
    updateStatus('Loading...', '', 0, 0);

    try {
      // 模拟加载延迟
      await delay(500);

      state.model = {
        name: 'bracket.step',
        vertices: generateRandomVertices(100),
        faces: generateRandomFaces(50)
      };

      elements.viewportOverlay?.classList.add('hidden');
      updateStatus('Model Loaded', state.model.name, 0, 0);

      // 绘制模型预览
      drawModelPreview();

      log.info('Model loaded:', state.model.name);
    } catch (error) {
      log.error('Failed to load model:', error);
      updateStatus('Load Failed', '', 0, 0);
    } finally {
      state.isProcessing = false;
    }
  }

  /**
   * 生成网格
   */
  async function generateMesh() {
    if (state.isProcessing || !state.model) {
      if (!state.model) {
        log.warn('No model loaded');
      }
      return;
    }

    log.info('Generating mesh...');
    state.isProcessing = true;
    updateStatus('Meshing...', state.model?.name || '', 0, 0);

    try {
      // 模拟网格生成
      await delay(1500);

      state.mesh = {
        nodes: generateRandomVertices(486),
        elements: generateRandomElements(1250)
      };

      updateStatus('Mesh Complete', state.model?.name || '', state.mesh.elements.length, state.mesh.nodes.length);
      drawMeshPreview();

      log.info('Mesh generated:', state.mesh.elements.length, 'elements');
    } catch (error) {
      log.error('Mesh generation failed:', error);
      updateStatus('Mesh Failed', '', 0, 0);
    } finally {
      state.isProcessing = false;
    }
  }

  /**
   * 运行求解
   */
  async function runSolve() {
    if (state.isProcessing || !state.mesh) {
      if (!state.mesh) {
        log.warn('No mesh generated');
      }
      return;
    }

    log.info('Starting solver...');
    state.isProcessing = true;
    updateStatus('Solving...', state.model?.name || '', state.mesh?.elements.length || 0, state.mesh?.nodes.length || 0);

    try {
      // 模拟求解过程
      for (let i = 0; i <= 100; i += 10) {
        await delay(300);
        updateStatus(`Solving... ${i}%`, state.model?.name || '', state.mesh?.elements.length || 0, state.mesh?.nodes.length || 0);
      }

      state.results = {
        displacement: generateRandomDisplacement(state.mesh.nodes.length),
        stress: generateRandomStress(state.mesh.elements.length)
      };

      updateStatus('Solve Complete', state.model?.name || '', state.mesh?.elements.length || 0, state.mesh?.nodes.length || 0);

      log.info('Solve complete');
    } catch (error) {
      log.error('Solve failed:', error);
      updateStatus('Solve Failed', '', 0, 0);
    } finally {
      state.isProcessing = false;
    }
  }

  /**
   * 可视化结果
   */
  function visualizeResults() {
    if (!state.results) {
      log.warn('No results to visualize');
      return;
    }

    state.viewMode = 'contour';
    redraw();
    updateStatus('Visualizing', state.model?.name || '', state.mesh?.elements.length || 0, state.mesh?.nodes.length || 0);

    log.info('Visualizing results');
  }

  /**
   * 清空 CAE
   */
  function clearCAE() {
    state.model = null;
    state.mesh = null;
    state.results = null;
    resetCamera();

    elements.viewportOverlay?.classList.remove('hidden');
    updateStatus('Ready', 'None', 0, 0);

    if (elements.caeCanvas) {
      const ctx = elements.caeCanvas.getContext('2d');
      ctx?.clearRect(0, 0, elements.caeCanvas.width, elements.caeCanvas.height);
    }

    log.info('CAE cleared');
  }

  // ==================== 绘图函数 ====================

  /**
   * 重绘视图
   */
  function redraw() {
    if (!elements.caeCanvas) return;

    const ctx = elements.caeCanvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = elements.caeCanvas;

    // 清空画布
    ctx.clearRect(0, 0, width, height);

    // 应用相机变换
    ctx.save();
    ctx.translate(width / 2, height / 2);
    ctx.scale(state.camera.zoom, state.camera.zoom);
    ctx.rotate(state.camera.rotationY * Math.PI / 180);

    // 根据视图模式绘制
    switch (state.viewMode) {
      case 'wireframe':
        drawWireframe(ctx, width, height);
        break;
      case 'solid':
        drawSolid(ctx, width, height);
        break;
      case 'contour':
        drawContour(ctx, width, height);
        break;
    }

    ctx.restore();
  }

  /**
   * 绘制线框视图
   */
  function drawWireframe(ctx, width, height) {
    if (!state.mesh) {
      drawModelPreview();
      return;
    }

    ctx.strokeStyle = 'rgba(0, 229, 255, 0.5)';
    ctx.lineWidth = 0.5;

    // 绘制网格线
    for (let i = 0; i < 200; i++) {
      const x1 = (Math.random() - 0.5) * width * 0.8;
      const y1 = (Math.random() - 0.5) * height * 0.8;
      const x2 = x1 + (Math.random() - 0.5) * 50;
      const y2 = y1 + (Math.random() - 0.5) * 50;

      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }
  }

  /**
   * 绘制实体视图
   */
  function drawSolid(ctx, width, height) {
    ctx.fillStyle = 'rgba(0, 229, 255, 0.1)';
    ctx.strokeStyle = 'rgba(0, 229, 255, 0.3)';
    ctx.lineWidth = 1;

    // 绘制填充多边形
    for (let i = 0; i < 30; i++) {
      const cx = (Math.random() - 0.5) * width * 0.6;
      const cy = (Math.random() - 0.5) * height * 0.6;
      const size = 20 + Math.random() * 40;

      ctx.beginPath();
      ctx.moveTo(cx + size * Math.cos(0), cy + size * Math.sin(0));
      for (let j = 1; j <= 6; j++) {
        const angle = (j * Math.PI * 2) / 6;
        ctx.lineTo(cx + size * Math.cos(angle), cy + size * Math.sin(angle));
      }
      ctx.closePath();
      ctx.fill();
      ctx.stroke();
    }
  }

  /**
   * 绘制云图视图
   */
  function drawContour(ctx, width, height) {
    if (!state.results) {
      drawWireframe(ctx, width, height);
      return;
    }

    // 创建渐变
    const gradient = ctx.createLinearGradient(-width/2, -height/2, width/2, height/2);
    gradient.addColorStop(0, 'rgba(0, 100, 255, 0.6)');
    gradient.addColorStop(0.3, 'rgba(0, 200, 100, 0.6)');
    gradient.addColorStop(0.6, 'rgba(255, 200, 0, 0.6)');
    gradient.addColorStop(1, 'rgba(255, 50, 50, 0.6)');

    ctx.fillStyle = gradient;
    ctx.fillRect(-width/2, -height/2, width, height);

    // 叠加网格
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.lineWidth = 0.5;

    for (let i = 0; i < 50; i++) {
      const x = (Math.random() - 0.5) * width;
      const y = (Math.random() - 0.5) * height;

      ctx.beginPath();
      ctx.arc(x, y, 5 + Math.random() * 10, 0, Math.PI * 2);
      ctx.stroke();
    }
  }

  /**
   * 绘制模型预览
   */
  function drawModelPreview() {
    if (!elements.caeCanvas) return;

    const ctx = elements.caeCanvas.getContext('2d');
    if (!ctx) return;

    const { width, height } = elements.caeCanvas;

    ctx.strokeStyle = 'rgba(0, 229, 255, 0.3)';
    ctx.lineWidth = 1;

    // 绘制简单几何形状
    ctx.beginPath();
    ctx.moveTo(width * 0.3, height * 0.7);
    ctx.lineTo(width * 0.3, height * 0.3);
    ctx.lineTo(width * 0.5, height * 0.2);
    ctx.lineTo(width * 0.7, height * 0.3);
    ctx.lineTo(width * 0.7, height * 0.7);
    ctx.closePath();
    ctx.stroke();

    // 内部结构
    ctx.beginPath();
    ctx.moveTo(width * 0.4, height * 0.5);
    ctx.lineTo(width * 0.6, height * 0.5);
    ctx.stroke();
  }

  // ==================== 辅助函数 ====================

  /**
   * 更新状态栏
   */
  function updateStatus(status, model, elements, nodes) {
    if (elements.statusText) elements.statusText.textContent = status;
    if (elements.modelName) elements.modelName.textContent = model;
    if (elements.elementCount) elements.elementCount.textContent = elements;
    if (elements.nodeCount) elements.nodeCount.textContent = nodes;
  }

  /**
   * 重置相机
   */
  function resetCamera() {
    state.camera = { rotationX: 0, rotationY: 0, zoom: 1 };
    redraw();
  }

  /**
   * 延迟函数
   */
  function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * 生成随机顶点
   */
  function generateRandomVertices(count) {
    return Array.from({ length: count }, () => ({
      x: (Math.random() - 0.5) * 100,
      y: (Math.random() - 0.5) * 100,
      z: (Math.random() - 0.5) * 100
    }));
  }

  /**
   * 生成随机面
   */
  function generateRandomFaces(count) {
    return Array.from({ length: count }, () => [
      Math.floor(Math.random() * 100),
      Math.floor(Math.random() * 100),
      Math.floor(Math.random() * 100)
    ]);
  }

  /**
   * 生成随机单元
   */
  function generateRandomElements(count) {
    return Array.from({ length: count }, () => ({
      nodes: [
        Math.floor(Math.random() * 486),
        Math.floor(Math.random() * 486),
        Math.floor(Math.random() * 486),
        Math.floor(Math.random() * 486)
      ]
    }));
  }

  /**
   * 生成随机位移
   */
  function generateRandomDisplacement(count) {
    return Array.from({ length: count }, () => ({
      dx: (Math.random() - 0.5) * 0.1,
      dy: (Math.random() - 0.5) * 0.1,
      dz: (Math.random() - 0.5) * 0.1
    }));
  }

  /**
   * 生成随机应力
   */
  function generateRandomStress(count) {
    return Array.from({ length: count }, () => ({
      vonMises: Math.random() * 100
    }));
  }

  // ==================== 导出 ====================
  window.CAEWorkbench = {
    init,
    loadModel,
    generateMesh,
    runSolve,
    visualizeResults,
    clearCAE,
    getState: () => ({ ...state })
  };

})();