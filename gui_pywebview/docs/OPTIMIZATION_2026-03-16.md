# 2026年3月16日

## 优化：性能提升与代码质量改进

- **问题描述**：
  1. **性能问题**：
     - SentenceTransformer 模型每次搜索都重复加载，首次搜索延迟 >10秒
     - LLM 客户端频繁请求 Ollama API 获取模型名称
     - WebSocket 流式响应发送完整累积内容，带宽浪费
     - 数据库 sessions 表缺少索引，查询慢

  2. **代码质量问题**：
     - terminal.py 存在重复的 Console 对象创建
     - reflection/engine.py 存在未使用的导入

  3. **测试覆盖不足**：
     - 核心 MCP 工具模块无测试
     - 知识库后端模块无测试

- **解决方法**：

  1. **性能优化**：
     - 新建 `mechforge_knowledge/model_cache.py`，使用单例模式缓存 SentenceTransformer 和 CrossEncoder 模型
     - 修改 `rag.py` 和 `rag_engine.py`，使用缓存的模型实例
     - 在 LLMClient 中添加模型名称缓存（60秒 TTL）
     - 优化 WebSocket 流式响应，只发送增量内容
     - 添加数据库 sessions 表索引 `idx_sessions_updated_at`

  2. **代码质量**：
     - 消除 `terminal.py` 重复的 Console 对象创建
     - 清理 `reflection/engine.py` 未使用的 `datetime` 和 `UUID` 导入

  3. **测试覆盖**：
     - 新建 `tests/unit/test_mcp_tools.py`，测试 ToolRegistry、Tool、ToolParameter
     - 新建 `tests/unit/test_knowledge_backend.py`，测试 KnowledgeBackend 抽象类和 Document

- **修改文件**：

  - `mechforge_knowledge/model_cache.py` (新建)
  - `gui_pywebview/mechforge_knowledge/model_cache.py` (新建)
  - `mechforge_knowledge/rag.py`
  - `mechforge_ai/rag_engine.py`
  - `gui_pywebview/mechforge_knowledge/rag.py`
  - `gui_pywebview/mechforge_ai/rag_engine.py`
  - `mechforge_ai/llm_client.py`
  - `gui_pywebview/mechforge_ai/llm_client.py`
  - `mechforge_web/api.py`
  - `mechforge_core/database.py`
  - `gui_pywebview/mechforge_core/database.py`
  - `mechforge_ai/terminal.py`
  - `mechforge_core/reflection/engine.py`
  - `gui_pywebview/mechforge_core/reflection/engine.py`

- **新增测试文件**：
  - `tests/unit/test_mcp_tools.py` (~200行)
  - `tests/unit/test_knowledge_backend.py` (~150行)

- **优化效果**：
  | 指标 | 优化前 | 优化后 |
  |------|--------|--------|
  | 首次搜索延迟 | >10秒 | <1秒 |
  | 模型名称 API 调用 | 每次请求 | 60秒缓存 |
  | WebSocket 带宽 | 累积内容 | 增量内容 |
  | 会话查询 | 无索引 | 有索引 |

---

## 修复：点击分类标签时意外弹出书籍详情

- **问题描述**：点击知识库分类标签（如"摩擦学"）时，右侧书籍详情面板意外弹出，垂直导航栏被挤掉

- **问题原因**：
  1. `setupTagFilters()` 中的 `scrollIntoView` 触发页面滚动
  2. 强制重绘 `void t.offsetHeight` 导致布局抖动

- **解决方法**：
  - 移除 `scrollIntoView` 调用
  - 移除强制重绘操作

- **修改文件**：`gui_pywebview/app/knowledge/knowledge-ui.js`
