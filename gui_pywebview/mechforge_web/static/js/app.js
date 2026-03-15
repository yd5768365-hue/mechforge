/**
 * MechForge Web - 前端应用
 */

// ==================== 全局状态 ====================

const state = {
    currentMode: 'chat',
    ws: null,
    messageHistory: [],
    ragEnabled: false,
    currentFile: null,
    caeData: {
        mesh: null,
        results: null
    }
};

// ==================== WebSocket 连接 ====================

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat`;

    state.ws = new WebSocket(wsUrl);

    state.ws.onopen = () => {
        console.log('WebSocket 连接成功');
        updateStatus('online', '已连接');
    };

    state.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    state.ws.onclose = () => {
        console.log('WebSocket 连接关闭');
        updateStatus('offline', '已断开');
        // 尝试重连
        setTimeout(connectWebSocket, 3000);
    };

    state.ws.onerror = (error) => {
        console.error('WebSocket 错误:', error);
        updateStatus('error', '连接错误');
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'message':
            appendMessage(data.role, data.content, data.messageId);
            break;
        case 'stream':
            updateStreamingMessage(data.messageId, data.content);
            break;
        case 'stream_end':
            finishStreamingMessage(data.messageId);
            break;
        case 'error':
            showError(data.message);
            break;
        case 'status':
            updateStatus(data.status, data.message);
            break;
    }
}

function sendWebSocketMessage(message) {
    if (state.ws && state.ws.readyState === WebSocket.OPEN) {
        state.ws.send(JSON.stringify({
            type: 'chat',
            message: message,
            rag: state.ragEnabled,
            model: document.getElementById('model-select')?.value || 'ollama'
        }));
    } else {
        showError('WebSocket 未连接');
    }
}

// ==================== UI 交互 ====================

// 切换模式
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
        const mode = item.dataset.mode;
        switchMode(mode);
    });
});

function switchMode(mode) {
    state.currentMode = mode;

    // 更新导航
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.toggle('active', item.dataset.mode === mode);
    });

    // 更新内容
    document.querySelectorAll('.mode-content').forEach(content => {
        content.classList.toggle('active', content.id === `${mode}-mode`);
    });
}

// 聊天功能
const chatInput = document.getElementById('chat-input');
if (chatInput) {
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message) return;

    // 添加用户消息
    appendMessage('user', message);

    // 清空输入
    input.value = '';
    input.style.height = 'auto';

    // 发送消息
    sendWebSocketMessage(message);

    // 显示加载中
    showLoadingMessage();
}

function sendQuickMessage(message) {
    document.getElementById('chat-input').value = message;
    sendMessage();
}

function appendMessage(role, content, messageId = null) {
    const container = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    if (messageId) {
        messageDiv.id = `msg-${messageId}`;
    }

    const avatar = role === 'user' ?
        '<div class="avatar user"><i class="fas fa-user"></i></div>' :
        '<div class="avatar bot"><i class="fas fa-robot"></i></div>';

    const contentHtml = role === 'assistant' ?
        `<div class="content markdown">${marked.parse(content)}</div>` :
        `<div class="content">${escapeHtml(content)}</div>`;

    messageDiv.innerHTML = `
        ${avatar}
        <div class="message-body">
            ${contentHtml}
            <div class="message-actions">
                <button onclick="copyMessage(this)" title="复制"><i class="fas fa-copy"></i></button>
                ${role === 'assistant' ? '<button onclick="regenerateMessage(this)" title="重新生成"><i class="fas fa-redo"></i></button>' : ''}
            </div>
        </div>
    `;

    container.appendChild(messageDiv);
    scrollToBottom();

    // 代码高亮
    messageDiv.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
    });
}

function updateStreamingMessage(messageId, content) {
    const messageDiv = document.getElementById(`msg-${messageId}`);
    if (messageDiv) {
        const contentDiv = messageDiv.querySelector('.content');
        contentDiv.innerHTML = marked.parse(content);
        scrollToBottom();
    }
}

function finishStreamingMessage(messageId) {
    const messageDiv = document.getElementById(`msg-${messageId}`);
    if (messageDiv) {
        messageDiv.querySelectorAll('pre code').forEach((block) => {
            hljs.highlightBlock(block);
        });
    }
    hideLoadingMessage();
}

function showLoadingMessage() {
    const container = document.getElementById('chat-messages');
    const existing = document.getElementById('loading-message');
    if (existing) return;

    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-message';
    loadingDiv.className = 'message assistant loading';
    loadingDiv.innerHTML = `
        <div class="avatar bot"><i class="fas fa-robot"></i></div>
        <div class="message-body">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    container.appendChild(loadingDiv);
    scrollToBottom();
}

function hideLoadingMessage() {
    const loading = document.getElementById('loading-message');
    if (loading) {
        loading.remove();
    }
}

function clearChat() {
    if (confirm('确定要清空对话历史吗？')) {
        document.getElementById('chat-messages').innerHTML = '';
        state.messageHistory = [];
    }
}

function copyMessage(btn) {
    const content = btn.closest('.message-body').querySelector('.content').innerText;
    navigator.clipboard.writeText(content).then(() => {
        showToast('已复制到剪贴板');
    });
}

// ==================== 知识库功能 ====================

function searchKnowledge() {
    const query = document.getElementById('knowledge-search-input').value.trim();
    if (!query) return;

    const resultsContainer = document.getElementById('knowledge-results');
    resultsContainer.innerHTML = '<div class="searching"><i class="fas fa-spinner fa-spin"></i> 搜索中...</div>';

    fetch('/api/knowledge/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 5 })
    })
    .then(res => res.json())
    .then(data => {
        displayKnowledgeResults(data.results);
    })
    .catch(err => {
        resultsContainer.innerHTML = `<div class="error">搜索失败: ${err.message}</div>`;
    });
}

function displayKnowledgeResults(results) {
    const container = document.getElementById('knowledge-results');

    if (!results || results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-search"></i>
                <p>未找到相关结果</p>
            </div>
        `;
        return;
    }

    container.innerHTML = results.map((result, index) => `
        <div class="knowledge-result">
            <div class="result-header">
                <span class="result-num">${index + 1}</span>
                <span class="result-title">${result.title}</span>
                <span class="result-score">${(result.score * 100).toFixed(1)}%</span>
            </div>
            <div class="result-content">${result.content}</div>
            <div class="result-source">${result.source}</div>
        </div>
    `).join('');
}

// 回车搜索
document.getElementById('knowledge-search-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchKnowledge();
});

// ==================== CAE 功能 ====================

function loadCaeDemo() {
    showLoading('正在加载示例...');

    fetch('/api/cae/demo', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                state.caeData = data;
                updateCaeViewer(data);
                showToast('示例加载成功');
            } else {
                showError(data.message);
            }
        })
        .catch(err => {
            hideLoading();
            showError(err.message);
        });
}

function generateMesh() {
    if (!state.caeData.geometry) {
        showError('请先加载几何模型');
        return;
    }

    const size = document.getElementById('mesh-size').value;
    showLoading('正在生成网格...');

    fetch('/api/cae/mesh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ size: parseFloat(size) })
    })
    .then(res => res.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            state.caeData.mesh = data.mesh;
            document.getElementById('node-count').textContent = data.mesh.nodes.toLocaleString();
            document.getElementById('element-count').textContent = data.mesh.elements.toLocaleString();
            document.getElementById('mesh-info').style.display = 'block';
            showToast('网格生成成功');
        } else {
            showError(data.message);
        }
    })
    .catch(err => {
        hideLoading();
        showError(err.message);
    });
}

function runSolver() {
    if (!state.caeData.mesh) {
        showError('请先生成网格');
        return;
    }

    showLoading('正在求解...');

    const config = {
        analysis_type: document.getElementById('analysis-type').value,
        material: document.getElementById('cae-material').value
    };

    fetch('/api/cae/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
    })
    .then(res => res.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            state.caeData.results = data.results;
            document.getElementById('max-disp').textContent = data.results.max_displacement + ' mm';
            document.getElementById('max-stress').textContent = data.results.max_von_mises + ' MPa';
            document.getElementById('results-placeholder').style.display = 'none';
            document.getElementById('results-content').style.display = 'block';
            showToast('求解完成');
        } else {
            showError(data.message);
        }
    })
    .catch(err => {
        hideLoading();
        showError(err.message);
    });
}

function updateCaeViewer(data) {
    const placeholder = document.getElementById('viewer-placeholder');
    if (placeholder && data.geometry) {
        placeholder.innerHTML = `
            <div class="model-loaded">
                <i class="fas fa-check-circle"></i>
                <p>模型已加载</p>
                <span>${data.geometry.filename}</span>
            </div>
        `;
    }
}

// CAE 标签切换
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        document.getElementById(`tab-${tab}`).classList.add('active');
    });
});

// ==================== 工具函数 ====================

function toggleRag() {
    state.ragEnabled = !state.ragEnabled;
    const badge = document.getElementById('rag-badge');
    if (badge) {
        badge.textContent = state.ragEnabled ? 'ON' : 'OFF';
        badge.classList.toggle('active', state.ragEnabled);
    }
    showToast(state.ragEnabled ? '知识库检索已开启' : '知识库检索已关闭');
}

function toggleSettings() {
    const modal = document.getElementById('settings-modal');
    modal.classList.toggle('active');
}

function saveSettings() {
    const settings = {
        model: document.getElementById('setting-model').value,
        ollamaUrl: document.getElementById('setting-ollama-url').value,
        theme: document.getElementById('setting-theme').value
    };

    localStorage.setItem('mechforge-settings', JSON.stringify(settings));
    toggleSettings();
    showToast('设置已保存');
}

function loadSettings() {
    const settings = JSON.parse(localStorage.getItem('mechforge-settings') || '{}');
    if (settings.model) {
        document.getElementById('setting-model').value = settings.model;
        document.getElementById('model-select').value = settings.model;
    }
    if (settings.ollamaUrl) {
        document.getElementById('setting-ollama-url').value = settings.ollamaUrl;
    }
    if (settings.theme) {
        document.getElementById('setting-theme').value = settings.theme;
        document.body.setAttribute('data-theme', settings.theme);
    }
}

function updateStatus(status, message) {
    const dot = document.querySelector('.status-dot');
    const text = document.querySelector('.status-text');

    dot.className = 'status-dot ' + status;
    text.textContent = message;
}

function showLoading(text = '处理中...') {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
}

function showError(message) {
    showToast(message, 'error');
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function scrollToBottom() {
    const container = document.getElementById('chat-messages');
    if (container) {
        container.scrollTop = container.scrollHeight;
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
    loadSettings();

    // 文件上传处理
    document.getElementById('file-input')?.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            showToast(`已选择文件: ${file.name}`);
            // TODO: 上传文件到服务器
        }
    });

    document.getElementById('cae-file-input')?.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            showToast(`已加载模型: ${file.name}`);
            state.caeData.geometry = { filename: file.name };
            updateCaeViewer(state.caeData);
        }
    });
});

// 页面关闭时清理
window.addEventListener('beforeunload', () => {
    if (state.ws) {
        state.ws.close();
    }
});
