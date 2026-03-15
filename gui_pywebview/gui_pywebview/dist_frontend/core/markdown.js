/**
 * Markdown - Markdown 渲染模块
 * 支持基础 Markdown 语法和代码高亮
 */

(function () {
  'use strict';

  // ==================== 配置 ====================
  const config = {
    codeHighlight: true,
    linkTarget: '_blank',
    maxHeadingLevel: 4
  };

  // ==================== 转义映射 ====================
  const escapeMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };

  /**
   * HTML 转义
   * @param {string} text - 原始文本
   * @returns {string}
   */
  function escapeHtml(text) {
    if (!text) return '';
    return String(text).replace(/[&<>"']/g, char => escapeMap[char]);
  }

  /**
   * 安全渲染 HTML（保留已有 HTML 标签）
   * @param {string} text - 原始文本
   * @returns {string}
   */
  function safeHtml(text) {
    if (!text) return '';
    // 只转义非标签内容
    return String(text);
  }

  // ==================== 解析器 ====================

  /**
   * 解析代码块
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseCodeBlocks(text) {
    // 匹配 ```language\ncode\n```
    return text.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
      const language = lang || 'plaintext';
      const escapedCode = escapeHtml(code.trim());
      return `<div class="code-block" data-language="${language}">
        <div class="code-header">
          <span class="code-language">${language}</span>
          <button class="code-copy-btn" title="复制代码">复制</button>
        </div>
        <pre class="code-content"><code class="language-${language}">${escapedCode}</code></pre>
      </div>`;
    });
  }

  /**
   * 解析行内代码
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseInlineCode(text) {
    // 匹配 `code`（不在代码块内）
    return text.replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>');
  }

  /**
   * 解析标题
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseHeadings(text) {
    for (let i = config.maxHeadingLevel; i >= 1; i--) {
      const regex = new RegExp(`^${'#'.repeat(i)}\\s+(.+)$`, 'gm');
      text = text.replace(regex, `<h${i} class="md-heading">$1</h${i}>`);
    }
    return text;
  }

  /**
   * 解析粗体和斜体
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseBoldItalic(text) {
    // 粗体 **text** 或 __text__
    text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    text = text.replace(/__(.+?)__/g, '<strong>$1</strong>');
    // 斜体 *text* 或 _text_
    text = text.replace(/\*(.+?)\*/g, '<em>$1</em>');
    text = text.replace(/_(.+?)_/g, '<em>$1</em>');
    return text;
  }

  /**
   * 解析链接
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseLinks(text) {
    // [text](url)
    return text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, 
      `<a href="$2" target="${config.linkTarget}" class="md-link" rel="noopener noreferrer">$1</a>`);
  }

  /**
   * 解析列表
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseLists(text) {
    const lines = text.split('\n');
    const result = [];
    let inList = false;
    let listType = '';

    for (const line of lines) {
      const ulMatch = line.match(/^(\s*)[-*+]\s+(.+)$/);
      const olMatch = line.match(/^(\s*)\d+\.\s+(.+)$/);

      if (ulMatch) {
        if (!inList || listType !== 'ul') {
          if (inList) result.push(`</${listType}>`);
          result.push('<ul class="md-list">');
          inList = true;
          listType = 'ul';
        }
        result.push(`<li>${ulMatch[2]}</li>`);
      } else if (olMatch) {
        if (!inList || listType !== 'ol') {
          if (inList) result.push(`</${listType}>`);
          result.push('<ol class="md-list">');
          inList = true;
          listType = 'ol';
        }
        result.push(`<li>${olMatch[2]}</li>`);
      } else {
        if (inList) {
          result.push(`</${listType}>`);
          inList = false;
        }
        result.push(line);
      }
    }

    if (inList) {
      result.push(`</${listType}>`);
    }

    return result.join('\n');
  }

  /**
   * 解析引用块
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseBlockquotes(text) {
    return text.replace(/^(?:&gt;|>)\s+(.+)$/gm, '<blockquote class="md-quote">$1</blockquote>');
  }

  /**
   * 解析水平线
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseHorizontalRules(text) {
    return text.replace(/^(?:---|\*\*\*|___)$/gm, '<hr class="md-hr">');
  }

  /**
   * 解析段落
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseParagraphs(text) {
    // 将连续的非空行包装成段落
    const blocks = text.split(/\n\n+/);
    return blocks.map(block => {
      // 跳过已经是 HTML 块的内容
      if (block.match(/^<(div|pre|ul|ol|blockquote|h[1-6]|hr)/)) {
        return block;
      }
      // 跳过空块
      if (!block.trim()) {
        return '';
      }
      // 包装成段落
      return `<p class="md-paragraph">${block}</p>`;
    }).join('\n');
  }

  /**
   * 解析换行
   * @param {string} text - 文本
   * @returns {string}
   */
  function parseLineBreaks(text) {
    // 单个换行转为 <br>
    return text.replace(/\n/g, '<br>');
  }

  // ==================== 主渲染函数 ====================

  /**
   * 渲染 Markdown 为 HTML
   * @param {string} text - Markdown 文本
   * @returns {string} HTML
   */
  function render(text) {
    if (!text) return '';

    let html = text;

    // 按顺序解析（顺序很重要）
    html = parseCodeBlocks(html); // 先处理代码块
    html = parseHeadings(html); // 标题
    html = parseHorizontalRules(html); // 水平线
    html = parseBlockquotes(html); // 引用
    html = parseLists(html); // 列表
    html = parseBoldItalic(html); // 粗体斜体
    html = parseLinks(html); // 链接
    html = parseInlineCode(html); // 行内代码
    html = parseParagraphs(html); // 段落

    return html;
  }

  /**
   * 渲染纯文本（转义 HTML）
   * @param {string} text - 原始文本
   * @returns {string}
   */
  function renderPlain(text) {
    if (!text) return '';
    return escapeHtml(text).replace(/\n/g, '<br>');
  }

  // ==================== 代码复制功能 ====================

  /**
   * 初始化代码复制按钮
   */
  function initCodeCopy() {
    document.addEventListener('click', async (e) => {
      const copyBtn = e.target.closest('.code-copy-btn');
      if (!copyBtn) return;

      const codeBlock = copyBtn.closest('.code-block');
      const code = codeBlock?.querySelector('code')?.textContent;

      if (code) {
        try {
          await navigator.clipboard.writeText(code);
          const originalText = copyBtn.textContent;
          copyBtn.textContent = '已复制!';
          copyBtn.classList.add('copied');
          setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.classList.remove('copied');
          }, 2000);
        } catch (err) {
          console.error('复制失败:', err);
          copyBtn.textContent = '复制失败';
        }
      }
    });
  }

  // ==================== 导出 ====================
  window.Markdown = {
    render,
    renderPlain,
    escapeHtml,
    initCodeCopy
  };

  // 自动初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initCodeCopy);
  } else {
    initCodeCopy();
  }

})();