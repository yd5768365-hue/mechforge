/**
 * ModelDownload - 内置模型下载管理
 * 检查内置模型状态，提示下载，显示进度
 */

(function () {
  'use strict';

  const { $ } = Utils;

  let banner = null;
  let pollTimer = null;
  let dismissed = false;

  async function init() {
    banner = $('model-download-banner');
    if (!banner) return;

    const downloadBtn = $('mdb-download-btn');
    const dismissBtn = $('mdb-dismiss-btn');

    downloadBtn?.addEventListener('click', startDownload);
    dismissBtn?.addEventListener('click', dismiss);

    await checkBundledModel();
  }

  async function checkBundledModel() {
    try {
      const resp = await fetch('/api/gguf/bundled/status');
      if (!resp.ok) return;
      const data = await resp.json();

      if (data.loaded) {
        hideBanner();
        return;
      }

      if (data.ready && !data.loaded) {
        showLoadingState();
        return;
      }

      if (data.download?.downloading) {
        showBanner();
        showProgress();
        startPolling();
        return;
      }

      if (!data.ready && !dismissed) {
        showBanner();
      }
    } catch (e) {
      console.warn('[ModelDownload] Status check failed:', e);
    }
  }

  function showBanner() {
    if (banner) banner.style.display = 'flex';
  }

  function hideBanner() {
    if (banner) banner.style.display = 'none';
    stopPolling();
  }

  function dismiss() {
    dismissed = true;
    hideBanner();
  }

  async function startDownload() {
    try {
      const resp = await fetch('/api/gguf/bundled/download', { method: 'POST' });
      const data = await resp.json();

      if (data.already_ready) {
        showComplete(data.loaded);
        return;
      }

      if (data.success) {
        showProgress();
        startPolling();
      }
    } catch (e) {
      console.error('[ModelDownload] Download start failed:', e);
      showError('下载启动失败，请检查网络');
    }
  }

  function showProgress() {
    const wrap = $('mdb-progress-wrap');
    const actions = $('mdb-actions');
    const desc = $('mdb-desc');

    if (wrap) wrap.style.display = 'flex';
    if (actions) {
      actions.innerHTML = '<button class="mdb-btn secondary" id="mdb-cancel-btn">取消</button>';
      $('mdb-cancel-btn')?.addEventListener('click', cancelDownload);
    }
    if (desc) desc.textContent = '正在下载模型，请耐心等待...';
  }

  function startPolling() {
    stopPolling();
    pollTimer = setInterval(pollProgress, 1500);
  }

  function stopPolling() {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
  }

  async function pollProgress() {
    try {
      const resp = await fetch('/api/gguf/bundled/progress');
      if (!resp.ok) return;
      const data = await resp.json();

      const fill = $('mdb-progress-fill');
      const text = $('mdb-progress-text');

      if (fill) fill.style.width = `${data.progress}%`;

      if (text) {
        if (data.speed_mbps > 0) {
          const eta = data.eta_seconds > 0
            ? (data.eta_seconds > 60
              ? `${Math.floor(data.eta_seconds / 60)}分${data.eta_seconds % 60}秒`
              : `${data.eta_seconds}秒`)
            : '';
          text.textContent = `${data.downloaded_mb}/${data.total_mb} MB (${data.speed_mbps} MB/s) ${eta ? '剩余 ' + eta : ''}`;
        } else {
          text.textContent = `${data.progress}%`;
        }
      }

      if (data.completed) {
        stopPolling();
        showComplete(true);
      }

      if (data.error) {
        stopPolling();
        showError(data.error);
      }

      if (!data.downloading && !data.completed && !data.error) {
        stopPolling();
      }
    } catch (e) {
      console.warn('[ModelDownload] Poll failed:', e);
    }
  }

  async function cancelDownload() {
    try {
      await fetch('/api/gguf/bundled/cancel', { method: 'POST' });
      stopPolling();
      resetBanner();
    } catch (e) {
      console.warn('[ModelDownload] Cancel failed:', e);
    }
  }

  function showComplete(loaded) {
    const desc = $('mdb-desc');
    const actions = $('mdb-actions');
    const wrap = $('mdb-progress-wrap');
    const fill = $('mdb-progress-fill');

    if (fill) fill.style.width = '100%';
    if (desc) desc.textContent = loaded ? '模型已就绪，可以开始对话' : '模型下载完成，正在加载...';
    if (actions) {
      actions.innerHTML = loaded
        ? '<button class="mdb-btn primary" id="mdb-close-btn">开始使用</button>'
        : '<button class="mdb-btn primary" id="mdb-load-btn">加载模型</button>';

      $('mdb-close-btn')?.addEventListener('click', () => {
        hideBanner();
        if (window.aiService) window.aiService.setProvider('gguf');
        if (window.eventBus) window.eventBus.emit('model-loaded');
        if (window.StatusBarManager?.updateAPIUI) {
          window.StatusBarManager.updateAPIUI();
          window.StatusBarManager.updateModelUI();
        }
      });

      $('mdb-load-btn')?.addEventListener('click', async () => {
        try {
          const resp = await fetch('/api/gguf/bundled/load', { method: 'POST' });
          const data = await resp.json();
          if (data.success) showComplete(true);
        } catch (e) {
          showError('模型加载失败');
        }
      });
    }

    setTimeout(() => {
      if (loaded) hideBanner();
    }, 5000);
  }

  function showLoadingState() {
    showBanner();
    const desc = $('mdb-desc');
    const actions = $('mdb-actions');
    if (desc) desc.textContent = '内置模型已下载，点击加载即可使用';
    if (actions) {
      actions.innerHTML = `
        <button class="mdb-btn primary" id="mdb-load-btn">加载模型</button>
        <button class="mdb-btn secondary" id="mdb-dismiss-btn2">稍后</button>
      `;
      $('mdb-load-btn')?.addEventListener('click', async () => {
        if (desc) desc.textContent = '正在加载模型...';
        try {
          const resp = await fetch('/api/gguf/bundled/load', { method: 'POST' });
          const data = await resp.json();
          if (data.success) showComplete(true);
          else showError('加载失败');
        } catch (e) {
          showError('加载失败');
        }
      });
      $('mdb-dismiss-btn2')?.addEventListener('click', dismiss);
    }
  }

  function showError(msg) {
    const desc = $('mdb-desc');
    const actions = $('mdb-actions');
    if (desc) desc.textContent = msg;
    if (actions) {
      actions.innerHTML = `
        <button class="mdb-btn primary" id="mdb-retry-btn">重试</button>
        <button class="mdb-btn secondary" id="mdb-dismiss-btn3">关闭</button>
      `;
      $('mdb-retry-btn')?.addEventListener('click', startDownload);
      $('mdb-dismiss-btn3')?.addEventListener('click', dismiss);
    }
  }

  function resetBanner() {
    const desc = $('mdb-desc');
    const actions = $('mdb-actions');
    const wrap = $('mdb-progress-wrap');
    const fill = $('mdb-progress-fill');

    if (desc) desc.textContent = '下载 Qwen2.5-1.5B 模型 (~1 GB)，即可离线使用 AI 对话';
    if (wrap) wrap.style.display = 'none';
    if (fill) fill.style.width = '0%';
    if (actions) {
      actions.innerHTML = `
        <button class="mdb-btn primary" id="mdb-download-btn">开始下载</button>
        <button class="mdb-btn secondary" id="mdb-dismiss-btn4">稍后</button>
      `;
      $('mdb-download-btn')?.addEventListener('click', startDownload);
      $('mdb-dismiss-btn4')?.addEventListener('click', dismiss);
    }
  }

  window.ModelDownload = { init, checkBundledModel };
})();
