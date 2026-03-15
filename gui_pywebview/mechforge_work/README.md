# MechForge Work - CAE Workbench

轻量级机械工程 CAE 工作台，基于最优开源技术栈。

## 技术栈（2026 最优组合）

| 功能 | 工具 | 安装命令 |
|------|------|----------|
| 几何处理 | **Gmsh** | `pip install gmsh` |
| 网格划分 | **Gmsh Python API** | 已包含 |
| FEA 求解 | **CalculiX (ccx)** | 系统包管理器 |
| 可视化 | **PyVista** | `pip install pyvista` |

## 快速开始

### 1. 安装依赖

```bash
# Python 依赖
pip install mechforge-ai[work]

# 系统依赖（CalculiX）
# Windows: 下载 https://www.calculixforwin.com/
# Linux:   sudo apt install calculix-ccx
# macOS:   brew install calculix
```

### 2. 启动 Work 模式

```bash
# 交互式 CLI
mechforge-work

# 或运行示例
mechforge-work demo
```

### 3. 基本工作流程

```
/demo                    # 运行悬臂梁示例
/mesh --size=2.0         # 生成网格
/material                # 选择材料
/bc                      # 设置边界条件
/solve                   # 执行求解
/show vonmises           # 可视化应力
/export vtk              # 导出结果
```

## 命令参考

### 交互式命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/load <file>` | 加载几何文件 | `/load bracket.step` |
| `/demo` | 运行悬臂梁示例 | `/demo` |
| `/mesh` | 生成网格 | `/mesh --size=5.0` |
| `/material` | 添加材料 | `/material` → 选择 1-4 |
| `/bc` | 设置边界条件 | `/bc` → 交互式向导 |
| `/solve` | 执行求解 | `/solve static` |
| `/show` | 可视化 | `/show vonmises` |
| `/export` | 导出结果 | `/export vtk` |
| `/status` | 显示状态 | `/status` |
| `/clear` | 清屏 | `/clear` |
| `/exit` | 退出 | `/exit` |

### CLI 命令

```bash
# 加载几何并进入交互模式
mechforge-work load model.step

# 直接运行示例
mechforge-work demo

# 仅生成网格
mechforge-work mesh --geo=model.step --size=2.0

# 求解并可视化
mechforge-work solve
mechforge-work show vonmises
```

## 支持的文件格式

### 输入
- **几何**: `.step`, `.stp`, `.iges`, `.igs`, `.stl`, `.brep`
- **网格**: `.msh` (Gmsh), `.inp` (Abaqus/CalculiX)

### 输出
- **结果**: `.vtk`, `.frd` (CalculiX), `.csv`, `.json`
- **报告**: 控制台 + 可视化窗口

## 示例代码

### 程序化 API

```python
from mechforge_work.cae_core import CAEEngine, Material, BoundaryCondition

# 创建引擎
engine = CAEEngine()

# 方法 1: 使用内置示例
engine.setup_cantilever_beam(
    length=100.0,  # mm
    width=10.0,
    height=10.0,
    mesh_size=2.0,
    force=1000.0,  # N
)

# 方法 2: 加载外部几何
engine.load_geometry("bracket.step")
engine.generate_mesh(mesh_size=5.0)

# 添加材料
steel = Material("Steel", E=210000, nu=0.3)
engine.add_material(steel)

# 设置边界条件
engine.add_boundary_condition(BoundaryCondition(
    name="Fixed",
    bc_type="fixed",
    entity="fixed_surface",
))

engine.add_boundary_condition(BoundaryCondition(
    name="Load",
    bc_type="force",
    entity="load_point",
    value=1000.0,
    direction=[0, 0, -1],
))

# 求解
result = engine.solve()
print(f"最大位移: {result.max_displacement:.6f} mm")
print(f"最大应力: {result.max_von_mises:.2f} MPa")

# 可视化
engine.visualize("vonmises")

# 导出
engine.export_results("result.vtk", "vtk")
```

## 材料库

内置常用工程材料：

| 材料 | E (MPa) | ν | ρ (kg/mm³) |
|------|---------|---|------------|
| 结构钢 | 210,000 | 0.30 | 7.85e-6 |
| 铝合金 | 70,000 | 0.33 | 2.70e-6 |
| 钛合金 | 116,000 | 0.31 | 4.50e-6 |
| 自定义 | 用户输入 | 用户输入 | 用户输入 |

## 分析类型

- **Static**: 静力分析（默认）
- **Modal**: 模态分析（频率提取）
- **Thermal**: 热分析（开发中）

## 故障排除

### CalculiX 未找到

```bash
# 检查安装
ccx -v

# Windows: 添加到 PATH
set PATH=%PATH%;C:\Program Files\CalculiX\ccx

# Linux/macOS
export PATH=$PATH:/usr/local/bin
```

### Gmsh 导入错误

```bash
pip install --upgrade gmsh
```

### 可视化失败

```bash
# 安装 PyVista
pip install pyvista

# 无头服务器（无显示器）
export PYVISTA_OFF_SCREEN=true
```

## 性能优化

| 网格尺寸 | 节点数 | 求解时间 | 适用场景 |
|----------|--------|----------|----------|
| 10 mm | ~1,000 | <1s | 快速预览 |
| 5 mm | ~10,000 | 2-5s | 常规分析 |
| 2 mm | ~100,000 | 10-30s | 精细分析 |
| 1 mm | ~1,000,000 | 5-10min | 高精度 |

## 与商业软件对比

| 功能 | MechForge | ANSYS | Abaqus |
|------|-----------|-------|--------|
| 几何导入 | ✓ STEP/IGES | ✓ 全面 | ✓ 全面 |
| 网格 | ✓ 自动/手动 | ✓ 全面 | ✓ 全面 |
| 求解器 | ✓ 基础 | ✓ 全面 | ✓ 全面 |
| 后处理 | ✓ 基础 | ✓ 全面 | ✓ 全面 |
| 成本 | **免费** | $$$$ | $$$$ |
| 体积 | **<100MB** | >10GB | >5GB |

适合：快速验证、教学演示、轻量级分析
不适合：大规模非线性、复杂接触、高级材料

## 许可证

MIT License - 开源免费
