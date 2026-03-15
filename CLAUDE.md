# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MechForge AI is a mechanical engineering AI assistant that combines LLM chat, RAG-based knowledge retrieval, and CAE (Computer-Aided Engineering) capabilities. It provides real engineering calculations with tool calls and avoids AI hallucinations by grounding responses in actual knowledge.

## Common Commands

### Installation

```bash
# From PyPI (recommended)
pip install mechforge-ai

# Full installation (all features)
pip install mechforge-ai[all]

# From source
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge
pip install -e ".[all]"
```

### Running the Application

```bash
mechforge              # Start AI chat mode
mechforge-k            # Start knowledge base mode
mechforge-work         # Start CAE workbench
mechforge-work --tui   # Start CAE TUI interface
mechforge-web          # Start Web interface (port 8080)
mechforge-model        # Model management CLI
```

### Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run specific test file
pytest tests/unit/test_config.py

# Lint and format
ruff check .
ruff check --fix .
black --check .

# Type checking
mypy mechforge_*/
```

### Docker

```bash
# Docker Compose (full stack)
docker-compose --profile full up -d

# Specific profiles
docker-compose --profile ai up -d      # AI chat
docker-compose --profile rag up -d     # Knowledge base
docker-compose --profile work up -d   # CAE workbench
docker-compose --profile web up -d     # Web interface
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MechForge AI v0.4.0                    │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  AI 对话     │  知识库      │  CAE 工作台  │  Web 界面      │
├──────────────┼──────────────┼──────────────┼────────────────┤
│ LLM Client   │ RAG Engine   │ Gmsh 4.15+   │ FastAPI        │
│ MCP Tools    │ BM25/Rerank  │ CalculiX     │ WebSocket      │
│ Streaming    │ ChromaDB     │ PyVista      │ Security       │
├──────────────┴──────────────┴──────────────┴────────────────┤
│              Core (Config / MCP / Local Model Manager)       │
├─────────────────────────────────────────────────────────────┤
│  🦙 Ollama  │  📦 GGUF HTTP  │  🔧 MCP Servers               │
└─────────────────────────────────────────────────────────────┘
```

### Key Modules

| Module | Purpose |
|--------|---------|
| `mechforge_ai/` | LLM client, terminal UI, command handling |
| `mechforge_core/` | Config, MCP protocol, local model management, cache, security |
| `mechforge_knowledge/` | RAG engine with local/RAGFlow backends |
| `mechforge_work/` | CAE workbench: mesh, solver, visualization engines |
| `mechforge_web/` | FastAPI web interface with WebSocket |
| `mechforge_theme/` | Terminal theming and colors |

### MCP Tool System

The MCP (Model Context Protocol) system in `mechforge_core/mcp/tools.py` provides built-in engineering calculation tools:
- `calculate_cantilever_deflection` - Beam deflection calculations
- `query_material_properties` - Material database lookup
- `spring_design` - Spring design calculations

Tools are registered via `ToolRegistry` and expose JSON Schema for LLM function calling.

### Knowledge Backend Architecture

Two backends are supported (configured in `config.yaml`):
- **local**: ChromaDB + BM25 hybrid search with sentence-transformers embeddings
- **ragflow**: RAGFlow API integration for advanced document parsing (OCR, tables)

## Configuration

Main configuration in `config.yaml`:
- AI provider: `openai`, `anthropic`, `ollama`, or `local` (GGUF)
- Knowledge backend: `local` or `ragflow`
- MCP servers can be added under `mcp.servers`

Environment variables take precedence:
- `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- `OLLAMA_URL`, `OLLAMA_MODEL`

## Dependencies

Optional dependency groups (in `pyproject.toml`):
- `llm`: llama-cpp-python for GGUF inference
- `rag`: ChromaDB, sentence-transformers, rank-bm25
- `work`: Gmsh, PyVista, NumPy (CAE features)
- `web`: FastAPI, uvicorn, websockets
- `gui`: PySide6 (desktop GUI)
- `dev`: pytest, ruff, black, mypy

## Code Style

- Line length: 100 (via Black)
- Type checking: MyPy strict mode enabled
- Linting: Ruff with pycodestyle, isort, flake8-bugbear
- Test framework: pytest with async support
