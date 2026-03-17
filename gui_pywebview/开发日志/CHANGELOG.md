# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-03-17

### Added
- **模块化框架** - 将 index.html 中的硬编码 HTML 抽取为独立 JS 模块
  - `app/layout/sidebar.js` - 侧边栏模块
  - `app/chat/chat-panel.js` + `.html` - 对话面板模块
  - `app/knowledge/knowledge-panel.js` + `.html` - 知识库面板模块
  - `app/cae/cae-panel.js` + `.html` - CAE 工作台模块
  - `app/experience/experience-panel.js` + `.html` - 经验库模块
  - `app/settings/settings-panel.js` + `.html` - 设置面板模块

### Changed
- **知识库界面完善**
  - 添加「我的知识库」用户书籍管理区块
  - 支持添加书籍、刷新列表功能
  - 详情抽屉展示、标签筛选、搜索功能
  - 工业风格 UI 优化

### Added Files
- `css/knowledge.css` - 知识库样式
- `css/experience.css` - 经验库样式

## [0.4.0] - 2026-03-02

### Added
- **CAE Work Mode** - Complete CAE workbench with Gmsh integration
  - Interactive file selection for geometry files
  - Mesh generation with progress display
  - Result visualization with ASCII stress cloud map
  - Support for STEP/IGES/STL/OBJ file formats
- **Textual TUI** - Interactive terminal UI for CAE workbench
  - File selection modal
  - Progress screen with step indicators
  - Result display modal with mesh statistics
- **Three main modes**:
  - `mechforge-ai` - AI chat mode
  - `mechforge-k` - Knowledge base lookup mode
  - `mechforge-work` - CAE workbench mode
- New command: `mechforge-work --tui` to launch TUI interface
- **Real Gmsh Engine** (`mesh_engine.py`)
  - Load STEP/IGES/STL/OBJ/BREP geometry files
  - Create demo models (block, bracket, cylinder, plate, bearing, rod)
  - Generate tetrahedral/hexahedral meshes
  - Mesh optimization with Netgen algorithm
  - Export to MSH, VTK, STL, INP formats
- **CalculiX Solver Engine** (`solver_engine.py`)
  - Local CalculiX integration
  - **API remote solving** - Submit jobs to remote CalculiX API
  - Simulation mode when CalculiX not available
  - INP file generation
  - Material library (Steel, Aluminum, Copper, Titanium)
  - Boundary condition support
- **PyVista Visualization Engine** (`viz_engine.py`)
  - Interactive 3D stress/displacement visualization
  - ASCII fallback visualization
  - VTK export support
- **New CLI Commands**
  - `/api <url>` - Set/check CalculiX API endpoint
  - `/status` - View available solvers status
  - `/solve --api` - Use API for remote solving
- **Test Models** - Added `test_models/test_bracket.step`

### Changed
- Improved `/mesh` command workflow with interactive file selection
- Updated Gmsh version to 4.15.1
- Updated PyVista version to 0.47.1
- Updated Trimesh version to 4.11.2
- Fixed `rich.box` import issue in work_cli.py
- Enhanced `get_solver_engine()` to accept optional `api_endpoint` parameter

### Fixed
- Import error: `cannot import name 'box' from 'rich.box'`
- Pylance import resolution for packages

## [0.3.0] - 2025-12-15

### Added
- Knowledge base lookup mode
- RAG (Retrieval Augmented Generation) support
- Multiple AI provider support (OpenAI, Anthropic, Ollama, Local)
- Configuration management with YAML and environment variables

### Changed
- Restructured project with packages directory
- Improved CLI interface with Rich formatting

## [0.2.0] - 2025-11-01

### Added
- AI chat mode with terminal interface
- Support for local Ollama models
- Basic command handling

## [0.1.0] - 2025-10-01

### Added
- Initial project structure
- Basic CLI framework
- Configuration system