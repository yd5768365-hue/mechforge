/**
 * MechForge AI — Daily Feed (经验库内嵌版)
 * 功能：在经验库界面内显示每日推送，手动触发
 *
 * 改进:
 * - 自动加载已有内容
 * - 使用 gen_id 轮询区分新旧内容
 * - 实时进度指示
 * - 历史浏览功能
 * - 详细错误反馈
 */
(function () {
  'use strict';

  const API_URL = '/api/daily';
  const REFRESH_URL = '/api/daily/refresh';
  const HISTORY_URL = '/api/daily/history';

  const SEV_COLOR = {
    warning: '#ffa502',
    info:    '#00e5ff',
    tip:     '#2ed573',
    error:   '#ff4757',
  };

  const TYPE_CFG = {
    failure_case:      { fields: ['phenomenon','root_cause','prevention','reference'] },
    standard_spotlight:{ fields: ['scope','key_requirements','query_points','source_url'] },
    calc_tip:          { fields: ['scenario','formula','example','notes'] },
    tool_tip:          { fields: ['purpose','steps','pitfall','doc_url'] },
    material_insight:  { fields: ['properties','applications','notes'] },
    industry_news:     { fields: ['summary','impacts','keywords','outlook'] },
  };

  const FIELD_LABEL = {
    phenomenon: '故障现象', root_cause: '根本原因', prevention: '预防措施',
    reference: '参考标准', scope: '适用范围', key_requirements: '技术要求',
    query_points: '查询要点', source_url: '标准来源', scenario: '适用场景',
    formula: '核心公式', example: '计算示例', notes: '注意事项',
    purpose: '主要用途', steps: '操作步骤', pitfall: '常见坑',
    doc_url: '文档链接', properties: '核心性能', applications: '应用场景',
    equivalents: '等效牌号', summary: '内容摘要', impacts: '影响',
    keywords: '关键词', outlook: '展望', grade: '材料牌号',
  };

  let feedCache = null;
  let isLoading = false;
  let pendingGenId = null;
  let renderedCount = 0;

  // ══════════════════════════════════════════════════════════
  //  CSS 注入
  // ══════════════════════════════════════════════════════════
  function injectCSS() {
    if (document.getElementById('df-embedded-style')) return;
    const style = document.createElement('style');
    style.id = 'df-embedded-style';
    style.textContent = `
/* ── Daily Feed 嵌入经验库样式 ── */

.df-embedded-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 229, 255, 0.1);
}

.df-embedded-title {
  font-family: 'Orbitron', 'Courier New', monospace;
  font-size: 12px;
  color: #00e5ff;
  letter-spacing: 2px;
}

.df-embedded-date {
  font-family: monospace;
  font-size: 10px;
  color: rgba(200, 216, 224, 0.4);
}

.df-embedded-actions {
  display: flex;
  gap: 10px;
}

.df-embedded-btn {
  font-family: 'Orbitron', monospace;
  font-size: 9px;
  letter-spacing: 1.5px;
  padding: 6px 12px;
  border: 1px solid rgba(0, 229, 255, 0.3);
  background: rgba(0, 229, 255, 0.05);
  color: #00e5ff;
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s;
}

.df-embedded-btn:hover {
  background: rgba(0, 229, 255, 0.12);
  border-color: rgba(0, 229, 255, 0.5);
}

.df-embedded-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.df-embedded-btn.primary {
  border-color: rgba(255, 165, 2, 0.4);
  background: rgba(255, 165, 2, 0.08);
  color: #ffa502;
}

.df-embedded-btn.primary:hover {
  background: rgba(255, 165, 2, 0.15);
}

.df-embedded-btn.history {
  border-color: rgba(46, 213, 115, 0.3);
  background: rgba(46, 213, 115, 0.05);
  color: #2ed573;
}

.df-embedded-btn.history:hover {
  background: rgba(46, 213, 115, 0.12);
}

#daily-feed-section {
  margin: 16px 20px;
  padding: 16px;
  background: rgba(0, 229, 255, 0.03);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 8px;
}

.df-generate-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin: 16px auto 8px;
  padding: 14px 28px;
  font-family: 'Orbitron', monospace;
  font-size: 13px;
  letter-spacing: 2px;
  color: #0d1117;
  background: linear-gradient(135deg, #00e5ff 0%, #00a8ff 100%);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3);
}

.df-generate-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 229, 255, 0.4);
}

.df-generate-btn:active {
  transform: translateY(0);
}

.df-generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.df-generate-btn .btn-icon {
  font-size: 16px;
}

.df-generate-hint {
  font-size: 11px;
  color: rgba(200, 216, 224, 0.4);
  text-align: center;
  margin-top: 8px;
}

.df-embedded-content {
  display: block;
}

.df-embedded-empty {
  text-align: center;
  padding: 24px;
  color: rgba(200, 216, 224, 0.3);
}

.df-embedded-empty-icon {
  font-size: 32px;
  margin-bottom: 8px;
  opacity: 0.5;
}

.df-embedded-empty-text {
  font-family: 'Orbitron', monospace;
  font-size: 11px;
  letter-spacing: 1px;
}

.df-embedded-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.df-embedded-card {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 229, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
  transition: border-color 0.2s;
}

.df-embedded-card:hover {
  border-color: rgba(0, 229, 255, 0.25);
}

.df-embedded-card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  cursor: pointer;
  border-bottom: 1px solid transparent;
  transition: border-color 0.2s;
}

.df-embedded-card.open .df-embedded-card-header {
  border-bottom-color: rgba(0, 229, 255, 0.1);
}

.df-embedded-card-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.df-embedded-card-type {
  font-family: 'Orbitron', monospace;
  font-size: 8px;
  letter-spacing: 1px;
  padding: 2px 6px;
  border-radius: 2px;
  border: 1px solid;
  flex-shrink: 0;
}

.df-embedded-card-title {
  font-family: 'Orbitron', monospace;
  font-size: 11px;
  color: #c8d8e0;
  font-weight: 600;
  flex: 1;
  line-height: 1.4;
}

.df-embedded-card-chevron {
  font-size: 10px;
  color: rgba(0, 229, 255, 0.4);
  transition: transform 0.25s;
  flex-shrink: 0;
}

.df-embedded-card.open .df-embedded-card-chevron {
  transform: rotate(90deg);
}

.df-embedded-card-body {
  display: none;
  padding: 14px;
}

.df-embedded-card.open .df-embedded-card-body {
  display: block;
  animation: dfEmbeddedBodyIn 0.2s ease;
}

@keyframes dfEmbeddedBodyIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: none; }
}

.df-embedded-field {
  margin-bottom: 10px;
}

.df-embedded-field:last-child {
  margin-bottom: 0;
}

.df-embedded-field-label {
  font-family: 'Orbitron', monospace;
  font-size: 8px;
  color: rgba(0, 229, 255, 0.5);
  letter-spacing: 1.5px;
  margin-bottom: 4px;
  text-transform: uppercase;
}

.df-embedded-field-text {
  font-size: 12px;
  color: rgba(200, 216, 224, 0.75);
  line-height: 1.6;
}

.df-embedded-field-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.df-embedded-field-list li {
  font-size: 12px;
  color: rgba(200, 216, 224, 0.7);
  line-height: 1.5;
  padding-left: 12px;
  position: relative;
}

.df-embedded-field-list li::before {
  content: '›';
  position: absolute;
  left: 0;
  color: rgba(0, 229, 255, 0.5);
}

.df-embedded-field-code {
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 229, 255, 0.1);
  border-left: 3px solid rgba(0, 229, 255, 0.35);
  border-radius: 0 3px 3px 0;
  padding: 10px 12px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  color: #a8c8d4;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.df-embedded-field-link {
  font-family: monospace;
  font-size: 11px;
  color: rgba(0, 229, 255, 0.7);
  text-decoration: none;
  border-bottom: 1px dashed rgba(0, 229, 255, 0.3);
  transition: color 0.18s;
}

.df-embedded-field-link:hover {
  color: #00e5ff;
  border-bottom-style: solid;
}

.df-embedded-field-kw {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.df-embedded-field-kw span {
  font-family: monospace;
  font-size: 10px;
  color: rgba(0, 229, 255, 0.6);
  background: rgba(0, 229, 255, 0.05);
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: 3px;
  padding: 2px 7px;
}

/* 加载 & 进度 */
.df-embedded-loading {
  text-align: center;
  padding: 24px;
  color: rgba(200, 216, 224, 0.4);
}

.df-embedded-loading::after {
  content: '';
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 229, 255, 0.2);
  border-top-color: #00e5ff;
  border-radius: 50%;
  animation: dfSpin 1s linear infinite;
  margin-left: 8px;
  vertical-align: middle;
}

@keyframes dfSpin {
  to { transform: rotate(360deg); }
}

.df-progress-bar {
  width: 100%;
  height: 3px;
  background: rgba(0, 229, 255, 0.1);
  border-radius: 2px;
  margin-top: 12px;
  overflow: hidden;
}

.df-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #00e5ff, #00a8ff);
  border-radius: 2px;
  transition: width 0.5s ease;
}

.df-progress-text {
  font-family: monospace;
  font-size: 10px;
  color: rgba(200, 216, 224, 0.4);
  text-align: center;
  margin-top: 6px;
}

.df-provider-info {
  font-family: monospace;
  font-size: 9px;
  color: rgba(200, 216, 224, 0.25);
  text-align: center;
  margin-top: 6px;
  letter-spacing: 0.5px;
}

/* 历史选择器 */
.df-history-selector {
  display: none;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 12px;
  padding: 10px 12px;
  background: rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(46, 213, 115, 0.1);
  border-radius: 4px;
}

.df-history-selector.active {
  display: flex;
}

.df-history-chip {
  font-family: monospace;
  font-size: 10px;
  padding: 4px 10px;
  border: 1px solid rgba(46, 213, 115, 0.2);
  background: rgba(46, 213, 115, 0.05);
  color: rgba(46, 213, 115, 0.7);
  border-radius: 3px;
  cursor: pointer;
  transition: all 0.2s;
}

.df-history-chip:hover {
  background: rgba(46, 213, 115, 0.12);
  border-color: rgba(46, 213, 115, 0.4);
}

.df-history-chip.active {
  background: rgba(46, 213, 115, 0.15);
  border-color: #2ed573;
  color: #2ed573;
}

.df-history-empty {
  font-family: monospace;
  font-size: 10px;
  color: rgba(200, 216, 224, 0.3);
  padding: 4px;
}

/* 卡片入场动画 */
.df-card-enter {
  animation: dfCardSlideIn 0.4s cubic-bezier(0.22, 1, 0.36, 1) both;
}

@keyframes dfCardSlideIn {
  from {
    opacity: 0;
    transform: translateY(12px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

/* 内联进度指示器 */
.df-inline-progress {
  padding: 12px 14px;
  background: rgba(0, 229, 255, 0.03);
  border: 1px dashed rgba(0, 229, 255, 0.12);
  border-radius: 4px;
  animation: dfPulseGlow 2s ease-in-out infinite;
}

@keyframes dfPulseGlow {
  0%, 100% { border-color: rgba(0, 229, 255, 0.08); }
  50% { border-color: rgba(0, 229, 255, 0.25); }
}
`;
    document.head.appendChild(style);
  }

  // ══════════════════════════════════════════════════════════
  //  DOM 绑定
  // ══════════════════════════════════════════════════════════
  function bindEvents() {
    const genBtn = document.getElementById('df-generate-btn');
    const refreshBtn = document.getElementById('df-refresh-btn');
    const historyBtn = document.getElementById('df-history-btn');

    if (genBtn) {
      genBtn.addEventListener('click', generateFeed);
    } else {
      console.warn('[DailyFeed] 未找到 df-generate-btn');
    }

    if (refreshBtn) {
      refreshBtn.addEventListener('click', refreshFeed);
    }

    if (historyBtn) {
      historyBtn.addEventListener('click', toggleHistory);
    }

    return !!genBtn;
  }

  // ══════════════════════════════════════════════════════════
  //  自动加载已有内容
  // ══════════════════════════════════════════════════════════
  async function autoLoadExisting() {
    try {
      const resp = await fetch(API_URL);
      if (!resp.ok) return;

      feedCache = await resp.json();

      if (feedCache.status === 'ok' && feedCache.items && feedCache.items.length > 0) {
        showFeedContent();
        console.log('[DailyFeed] 已自动加载现有内容:', feedCache.date);
      }
    } catch (e) {
      console.warn('[DailyFeed] 自动加载失败:', e);
    }
  }

  // ══════════════════════════════════════════════════════════
  //  生成内容
  // ══════════════════════════════════════════════════════════
  async function generateFeed() {
    if (isLoading) return;
    isLoading = true;
    renderedCount = 0;

    const emptyEl = document.getElementById('df-embedded-empty');
    const listEl = document.getElementById('df-embedded-list');
    const genBtn = document.getElementById('df-generate-btn');
    const actionsBar = document.getElementById('df-actions-bar');

    if (genBtn) genBtn.disabled = true;
    if (listEl) { listEl.innerHTML = ''; listEl.style.display = 'none'; }

    if (emptyEl) {
      emptyEl.innerHTML = `
        <div class="df-embedded-loading">AI 正在生成内容，请稍候...</div>
        <div class="df-progress-bar"><div class="df-progress-fill" id="df-progress-fill" style="width:5%"></div></div>
        <div class="df-progress-text" id="df-progress-text">准备中...</div>
        <div style="margin-top:8px;font-size:11px;color:rgba(200,216,224,.35);">首次生成可能需要 10-30 秒</div>
      `;
    }

    try {
      const resp = await fetch(REFRESH_URL, { method: 'POST' });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);

      const data = await resp.json();
      pendingGenId = data.gen_id;

      let elapsed = 0;
      const maxWait = 300000;
      const pollInterval = 3000;

      while (elapsed < maxWait) {
        await sleep(pollInterval);
        elapsed += pollInterval;

        const checkResp = await fetch(API_URL);
        if (!checkResp.ok) continue;

        feedCache = await checkResp.json();

        if (feedCache.items && feedCache.items.length > renderedCount) {
          appendNewCards(feedCache.items, emptyEl, listEl);
        }

        if (feedCache.status === 'generating' && feedCache.progress) {
          updateProgress(feedCache.progress);
        }

        if (feedCache.gen_id === pendingGenId && feedCache.status !== 'generating') {
          removeInlineProgress();
          if (feedCache.items && feedCache.items.length > 0) {
            appendNewCards(feedCache.items, emptyEl, listEl);
            showFeedContent();
          } else {
            showError(feedCache.error_detail || '生成失败，请检查 LLM 配置');
          }
          return;
        }
      }

      throw new Error('生成超时（5分钟），请检查 LLM 是否在运行');

    } catch (e) {
      console.error('[DailyFeed] 生成失败:', e);
      removeInlineProgress();
      showError(e.message || '生成失败');
    } finally {
      isLoading = false;
      pendingGenId = null;
    }
  }

  function appendNewCards(items, emptyEl, listEl) {
    if (!listEl) return;
    var newItems = items.slice(renderedCount);
    if (newItems.length === 0) return;

    if (renderedCount === 0) {
      if (emptyEl) emptyEl.style.display = 'none';
      listEl.style.display = 'flex';
    }

    newItems.forEach(function(item) {
      var card = buildCard(item, renderedCount === 0 && items.length === 1);
      card.classList.add('df-card-enter');
      listEl.appendChild(card);
      renderedCount++;
    });

    ensureInlineProgress(listEl);
  }

  function ensureInlineProgress(listEl) {
    var existing = document.getElementById('df-inline-progress');
    if (existing) existing.remove();

    var el = document.createElement('div');
    el.id = 'df-inline-progress';
    el.className = 'df-inline-progress';
    el.innerHTML =
      '<div class="df-progress-bar"><div class="df-progress-fill" id="df-progress-fill" style="width:50%"></div></div>' +
      '<div class="df-progress-text" id="df-progress-text">正在生成下一条...</div>';
    listEl.appendChild(el);
  }

  function removeInlineProgress() {
    var el = document.getElementById('df-inline-progress');
    if (el) el.remove();
  }

  function updateProgress(progress) {
    const fill = document.getElementById('df-progress-fill');
    const text = document.getElementById('df-progress-text');
    if (!fill || !text) return;

    const pct = Math.round((progress.current / progress.total) * 100);
    fill.style.width = pct + '%';
    text.textContent = `正在生成: ${progress.current_type} (${progress.current}/${progress.total})`;
  }

  function showError(message) {
    const emptyEl = document.getElementById('df-embedded-empty');
    if (!emptyEl) return;

    let providerHint = '';
    if (feedCache && feedCache.provider) {
      const p = feedCache.provider;
      providerHint = `<div class="df-provider-info">当前 Provider: ${escHtml(p.provider)} / ${escHtml(p.model)}</div>`;
    }

    emptyEl.innerHTML = `
      <div class="df-embedded-empty-icon">⚠</div>
      <div class="df-embedded-empty-text">${escHtml(message)}</div>
      ${providerHint}
      <button class="df-generate-btn" id="df-retry-btn" style="margin-top:16px;">
        <span class="btn-icon">↻</span>
        <span class="btn-text">重试</span>
      </button>
    `;
    const retryBtn = document.getElementById('df-retry-btn');
    if (retryBtn) retryBtn.addEventListener('click', generateFeed);
  }

  function showFeedContent() {
    const emptyEl = document.getElementById('df-embedded-empty');
    const listEl = document.getElementById('df-embedded-list');
    const dateEl = document.getElementById('df-embedded-date');
    const actionsBar = document.getElementById('df-actions-bar');

    if (dateEl) {
      dateEl.textContent = feedCache.date ? '── ' + feedCache.date + ' ──' : '── 今日推送 ──';
    }

    if (feedCache.items && feedCache.items.length > 0) {
      renderFeed(feedCache.items);
      if (emptyEl) emptyEl.style.display = 'none';
      if (listEl) listEl.style.display = 'flex';
      if (actionsBar) actionsBar.style.display = 'flex';
    }

    // 显示 provider 信息
    if (feedCache.provider) {
      let infoEl = document.getElementById('df-provider-tag');
      if (!infoEl) {
        infoEl = document.createElement('div');
        infoEl.id = 'df-provider-tag';
        infoEl.className = 'df-provider-info';
        if (actionsBar) actionsBar.appendChild(infoEl);
      }
      const p = feedCache.provider;
      infoEl.textContent = p.provider + ' / ' + p.model;
    }
  }

  async function refreshFeed() {
    if (isLoading) return;
    isLoading = true;
    renderedCount = 0;

    const refreshBtn = document.getElementById('df-refresh-btn');
    const listEl = document.getElementById('df-embedded-list');
    const emptyEl = document.getElementById('df-embedded-empty');

    if (refreshBtn) {
      refreshBtn.disabled = true;
      refreshBtn.textContent = '⟳ 生成中...';
    }
    if (listEl) { listEl.innerHTML = ''; listEl.style.opacity = '1'; }

    try {
      const resp = await fetch(REFRESH_URL, { method: 'POST' });
      if (!resp.ok) throw new Error('HTTP ' + resp.status);

      const data = await resp.json();
      pendingGenId = data.gen_id;

      ensureInlineProgress(listEl);

      let elapsed = 0;
      const maxWait = 300000;
      const pollInterval = 3000;

      while (elapsed < maxWait) {
        await sleep(pollInterval);
        elapsed += pollInterval;

        const checkResp = await fetch(API_URL);
        if (!checkResp.ok) continue;

        const newCache = await checkResp.json();

        if (newCache.items && newCache.items.length > renderedCount) {
          feedCache = newCache;
          appendNewCards(newCache.items, emptyEl, listEl);
        }

        if (newCache.status === 'generating' && newCache.progress) {
          updateProgress(newCache.progress);
        }

        if (newCache.gen_id === pendingGenId && newCache.status !== 'generating') {
          feedCache = newCache;
          removeInlineProgress();
          if (feedCache.items && feedCache.items.length > 0) {
            appendNewCards(feedCache.items, emptyEl, listEl);
          }
          return;
        }
      }

      throw new Error('生成超时（5分钟），请检查 LLM 是否在运行');

    } catch (e) {
      console.error('[DailyFeed] 刷新失败:', e);
      removeInlineProgress();
      alert('生成失败: ' + e.message);
    } finally {
      isLoading = false;
      pendingGenId = null;
      if (refreshBtn) {
        refreshBtn.disabled = false;
        refreshBtn.textContent = '⟳ 重新生成';
      }
    }
  }

  // ══════════════════════════════════════════════════════════
  //  历史浏览
  // ══════════════════════════════════════════════════════════
  async function toggleHistory() {
    const selector = document.getElementById('df-history-selector');
    if (!selector) return;

    if (selector.classList.contains('active')) {
      selector.classList.remove('active');
      return;
    }

    selector.innerHTML = '<div class="df-history-empty">加载中...</div>';
    selector.classList.add('active');

    try {
      const resp = await fetch(HISTORY_URL + '?days=14');
      if (!resp.ok) throw new Error('HTTP ' + resp.status);

      const data = await resp.json();
      const history = data.history || [];

      if (history.length === 0) {
        selector.innerHTML = '<div class="df-history-empty">暂无历史记录</div>';
        return;
      }

      selector.innerHTML = history.map(function(h) {
        const isToday = h.date === new Date().toISOString().slice(0, 10);
        return '<span class="df-history-chip' + (isToday ? ' active' : '') + '" data-date="' +
          escHtml(h.date) + '">' + escHtml(h.date) + ' (' + (h.total || 0) + '条)</span>';
      }).join('');

      selector.querySelectorAll('.df-history-chip').forEach(function(chip) {
        chip.addEventListener('click', function() {
          loadHistoryDate(chip.dataset.date);
          selector.querySelectorAll('.df-history-chip').forEach(function(c) {
            c.classList.remove('active');
          });
          chip.classList.add('active');
        });
      });

    } catch (e) {
      console.error('[DailyFeed] 加载历史失败:', e);
      selector.innerHTML = '<div class="df-history-empty">加载失败</div>';
    }
  }

  async function loadHistoryDate(dateStr) {
    try {
      const resp = await fetch(HISTORY_URL + '/' + dateStr);
      if (!resp.ok) throw new Error('HTTP ' + resp.status);

      const data = await resp.json();

      if (data.items && data.items.length > 0) {
        feedCache = data;
        showFeedContent();
      } else {
        alert('该日期没有推送记录');
      }
    } catch (e) {
      console.error('[DailyFeed] 加载历史日期失败:', e);
      alert('加载失败: ' + e.message);
    }
  }

  // ══════════════════════════════════════════════════════════
  //  渲染 Feed
  // ══════════════════════════════════════════════════════════
  function renderFeed(items) {
    const listEl = document.getElementById('df-embedded-list');
    if (!listEl) return;
    listEl.innerHTML = '';

    items.forEach(function(item, idx) {
      var card = buildCard(item, idx === 0);
      listEl.appendChild(card);
    });
  }

  function buildCard(item, defaultOpen) {
    var color = SEV_COLOR[item.severity] || '#00e5ff';
    var cfg = TYPE_CFG[item.type] || { fields: [] };
    var title = getTitle(item);

    var card = document.createElement('div');
    card.className = 'df-embedded-card' + (defaultOpen ? ' open' : '');
    card.style.setProperty('--card-color', color);

    var header = document.createElement('div');
    header.className = 'df-embedded-card-header';
    header.innerHTML =
      '<span class="df-embedded-card-icon">' + item.icon + '</span>' +
      '<span class="df-embedded-card-type" style="color:' + color + ';border-color:' + color + '40;background:' + color + '10">' + item.type_cn + '</span>' +
      '<span class="df-embedded-card-title">' + escHtml(title) + '</span>' +
      '<span class="df-embedded-card-chevron">›</span>';
    header.addEventListener('click', function() { card.classList.toggle('open'); });

    var body = document.createElement('div');
    body.className = 'df-embedded-card-body';
    cfg.fields.forEach(function(field) {
      var val = item.data && item.data[field];
      if (!val) return;
      var fieldEl = buildField(field, val, color);
      if (fieldEl) body.appendChild(fieldEl);
    });

    if (item.generated_at) {
      var ts = document.createElement('div');
      ts.style.cssText = 'margin-top:10px;font-family:monospace;font-size:9px;color:rgba(200,216,224,.25);letter-spacing:1px';
      ts.textContent = 'GENERATED ' + item.generated_at;
      body.appendChild(ts);
    }

    card.appendChild(header);
    card.appendChild(body);
    return card;
  }

  function buildField(field, val, accentColor) {
    var label = FIELD_LABEL[field] || field;
    var wrapper = document.createElement('div');
    wrapper.className = 'df-embedded-field';

    var labelEl = document.createElement('div');
    labelEl.className = 'df-embedded-field-label';
    labelEl.textContent = label;
    wrapper.appendChild(labelEl);

    if ((field === 'source_url' || field === 'doc_url') && typeof val === 'string') {
      var a = document.createElement('a');
      a.className = 'df-embedded-field-link';
      a.href = val;
      a.target = '_blank';
      a.rel = 'noopener noreferrer';
      a.textContent = val;
      wrapper.appendChild(a);
      return wrapper;
    }

    if (Array.isArray(val)) {
      if (field === 'keywords') {
        var kw = document.createElement('div');
        kw.className = 'df-embedded-field-kw';
        val.forEach(function(k) {
          var s = document.createElement('span');
          s.textContent = k;
          kw.appendChild(s);
        });
        wrapper.appendChild(kw);
      } else {
        var ul = document.createElement('ul');
        ul.className = 'df-embedded-field-list';
        val.forEach(function(v) {
          var li = document.createElement('li');
          li.textContent = v;
          ul.appendChild(li);
        });
        wrapper.appendChild(ul);
      }
      return wrapper;
    }

    if (field === 'formula' || field === 'example') {
      var code = document.createElement('div');
      code.className = 'df-embedded-field-code';
      code.textContent = val;
      wrapper.appendChild(code);
      return wrapper;
    }

    if (typeof val === 'object' && val !== null) {
      var ul2 = document.createElement('ul');
      ul2.className = 'df-embedded-field-list';
      Object.entries(val).forEach(function(entry) {
        var li = document.createElement('li');
        li.textContent = entry[0] + ': ' + entry[1];
        ul2.appendChild(li);
      });
      wrapper.appendChild(ul2);
      return wrapper;
    }

    var p = document.createElement('p');
    p.className = 'df-embedded-field-text';
    p.textContent = String(val);
    wrapper.appendChild(p);
    return wrapper;
  }

  function getTitle(item) {
    var d = item.data || {};
    return d.title || d.tt
      || (d.std_no && (d.std_no + ' ' + (d.std_name || '')).trim())
      || d.name
      || (d.grade && (d.grade + ' ' + (d.name_cn || '')).trim())
      || d.headline || item.type_cn;
  }

  function escHtml(s) {
    var d = document.createElement('div');
    d.textContent = String(s || '');
    return d.innerHTML;
  }

  function sleep(ms) {
    return new Promise(function(resolve) { setTimeout(resolve, ms); });
  }

  // ══════════════════════════════════════════════════════════
  //  入口
  // ══════════════════════════════════════════════════════════
  function init() {
    console.log('[DailyFeed] 初始化开始...');
    injectCSS();

    var section = document.getElementById('daily-feed-section');
    var genBtn = document.getElementById('df-generate-btn');
    console.log('[DailyFeed] daily-feed-section:', section ? '存在' : '不存在');
    console.log('[DailyFeed] df-generate-btn:', genBtn ? '存在' : '不存在');

    var ok = bindEvents();
    if (ok) {
      console.log('[DailyFeed] 已绑定事件');
    } else {
      console.warn('[DailyFeed] 绑定事件失败');
    }

    // 自动加载已有内容
    autoLoadExisting();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.DailyFeed = { refresh: refreshFeed, loadHistory: loadHistoryDate };
})();
