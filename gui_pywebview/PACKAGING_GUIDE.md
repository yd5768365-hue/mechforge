# MechForge AI 打包技术指南

## 📦 打包方案对比

### 1. PyInstaller（当前使用，推荐）

**优点：**
- ✅ 最成熟稳定，社区最大
- ✅ 支持几乎所有 Python 库
- ✅ 配置简单，文档丰富
- ✅ 跨平台支持好（Windows/Mac/Linux）
- ✅ 单文件或文件夹模式可选
- ✅ 自动处理依赖

**缺点：**
- ❌ 打包体积较大（通常 50-200MB）
- ❌ 启动速度较慢（需要解压）
- ❌ 容易被杀毒软件误报

**适用场景：**
- 通用桌面应用
- 需要快速打包
- 依赖复杂的项目

**推荐配置：**
```bash
# 单文件模式（推荐）
python build_optimized.py --mode=single

# 文件夹模式（启动更快）
python build_optimized.py --mode=folder

# 便携版（最小体积）
python build_optimized.py --mode=portable
```

---

### 2. Nuitka（性能优先）

**优点：**
- ✅ 编译为 C++，性能更好
- ✅ 代码保护更强（不是字节码）
- ✅ 启动速度更快
- ✅ 体积可以更小

**缺点：**
- ❌ 编译时间很长（可能几十分钟）
- ❌ 某些库兼容性差
- ❌ 学习曲线较陡
- ❌ 社区相对较小

**适用场景：**
- 对性能要求极高
- 需要代码保护
- 可以接受长编译时间

**使用示例：**
```bash
# 安装
pip install nuitka

# 基础打包
python -m nuitka --standalone --onefile --enable-plugin=tkinter desktop_app.py

# 优化打包
python -m nuitka \
    --standalone \
    --onefile \
    --lto=yes \
    --jobs=4 \
    --include-package=fastapi \
    --include-package=webview \
    desktop_app.py
```

---

### 3. cx_Freeze（跨平台）

**优点：**
- ✅ 更新活跃，支持 Python 3.11+
- ✅ 跨平台支持好
- ✅ 可以创建 MSI 安装包
- ✅ 支持 pip 安装

**缺点：**
- ❌ 配置较复杂
- ❌ 社区比 PyInstaller 小
- ❌ 某些库支持不完善

**适用场景：**
- 需要创建安装包
- 使用较新 Python 版本

**使用示例：**
```python
# setup.py
from cx_Freeze import setup, Executable

setup(
    name="MechForgeAI",
    version="0.5.0",
    description="MechForge AI Desktop App",
    executables=[Executable("desktop_app.py")],
    options={
        "build_exe": {
            "packages": ["fastapi", "webview", "uvicorn"],
            "excludes": ["matplotlib", "numpy"],
        }
    }
)
```

```bash
# 构建
python setup.py build

# 创建 MSI
python setup.py bdist_msi
```

---

### 4. PyOxidizer（现代化）

**优点：**
- ✅ Rust 编写，性能优秀
- ✅ 单文件，启动极快
- ✅ 资源嵌入方式更优
- ✅ 内存占用小

**缺点：**
- ❌ 学习曲线陡峭
- ❌ 文档相对较少
- ❌ 某些 Python 特性支持不完善
- ❌ 调试困难

**适用场景：**
- 追求极致启动速度
- 单文件分发
- 可以接受复杂配置

**使用示例：**
```bash
# 安装
pip install pyoxidizer

# 初始化
pyoxidizer init-config-file pyoxidizer.bzl

# 构建
pyoxidizer build
```

---

### 5. Briefcase（BeeWare）

**优点：**
- ✅ BeeWare 官方工具
- ✅ 支持 iOS/Android（未来）
- ✅ 可以创建原生安装包
- ✅ 支持代码签名

**缺点：**
- ❌ 相对较新，生态小
- ❌ 某些库支持不完善
- ❌ 文档不够完善

**适用场景：**
- 需要移动端支持
- 创建原生安装包

**使用示例：**
```bash
# 安装
pip install briefcase

# 创建项目
briefcase create

# 构建
briefcase build

# 打包
briefcase package
```

---

## 🎯 推荐方案

### 开发阶段
**使用 PyInstaller 文件夹模式**
```bash
python build_optimized.py --mode=folder
```
- 启动快，方便调试
- 可以单独更新资源文件

### 测试阶段
**使用 PyInstaller 单文件模式**
```bash
python build_optimized.py --mode=single
```
- 方便分发给测试人员
- 一个文件，不易出错

### 发布阶段
**方案 A：PyInstaller + UPX（推荐）**
```bash
python build_optimized.py --mode=single --upx
```
- 体积适中（30-80MB）
- 稳定可靠
- 用户熟悉

**方案 B：Nuitka（性能优先）**
```bash
# 需要额外配置
python -m nuitka --standalone --onefile desktop_app.py
```
- 体积更小（20-50MB）
- 启动更快
- 编译时间长

**方案 C：PyInstaller + 安装程序**
```bash
python build_optimized.py --mode=folder --installer
```
- 专业安装体验
- 支持卸载
- 可以创建快捷方式

---

## 📊 体积对比（估算）

| 方案 | 体积 | 启动时间 | 编译时间 | 稳定性 |
|------|------|----------|----------|--------|
| PyInstaller (单文件) | 50-150MB | 3-10s | 2-5min | ⭐⭐⭐⭐⭐ |
| PyInstaller + UPX | 30-80MB | 5-15s | 2-5min | ⭐⭐⭐⭐ |
| Nuitka | 20-50MB | 1-3s | 10-30min | ⭐⭐⭐ |
| cx_Freeze | 50-120MB | 2-5s | 2-5min | ⭐⭐⭐⭐ |
| PyOxidizer | 15-40MB | <1s | 5-10min | ⭐⭐⭐ |

---

## 🔧 优化技巧

### 1. 减小体积

**排除不需要的模块：**
```python
# 在 spec 文件中
excludes=[
    'matplotlib', 'numpy', 'pandas', 'scipy',
    'tkinter', 'unittest', 'pytest',
    'IPython', 'jupyter',
]
```

**使用 UPX 压缩：**
```bash
# 下载 UPX
# https://github.com/upx/upx/releases

# 使用
python build_optimized.py --upx
```

### 2. 加快启动

**使用文件夹模式：**
```bash
python build_optimized.py --mode=folder
```

**优化导入：**
```python
# 延迟导入
if need_feature:
    import heavy_module
```

### 3. 避免杀毒软件误报

**代码签名：**
```bash
python build_optimized.py --sign
```

**使用文件夹模式：**
- 单文件更容易被误报
- 文件夹模式更可信

---

## 🚀 快速开始

### 推荐命令

```bash
# 1. 开发测试（文件夹模式，启动快）
python build_optimized.py --mode=folder --clean

# 2. 内测分发（单文件，方便传输）
python build_optimized.py --mode=single --upx

# 3. 正式发布（单文件 + 安装程序）
python build_optimized.py --mode=single --upx --installer

# 4. 极致精简（便携版）
python build_optimized.py --mode=portable
```

---

## 📋 检查清单

打包前检查：
- [ ] 代码质量检查通过 (`npm run check`)
- [ ] Python 测试通过 (`pytest`)
- [ ] 所有资源文件已更新
- [ ] 版本号已更新
- [ ] 配置文件正确

打包后检查：
- [ ] 程序能正常启动
- [ ] 主要功能正常
- [ ] 没有杀毒软件误报
- [ ] 文件大小合理
- [ ] 在干净环境测试

---

## 🆘 常见问题

### Q: 打包后程序无法启动？
A: 检查是否缺少数据文件，使用 `--mode=folder` 调试

### Q: 体积太大？
A: 使用 `--mode=portable` 或添加更多 `--exclude-module`

### Q: 启动太慢？
A: 使用 `--mode=folder` 或考虑 Nuitka

### Q: 被杀毒软件拦截？
A: 使用文件夹模式，或购买代码签名证书

### Q: 某些库找不到？
A: 在 spec 文件中添加 `hiddenimports`

---

## 📚 相关资源

- [PyInstaller 文档](https://pyinstaller.org/)
- [Nuitka 文档](https://nuitka.net/)
- [cx_Freeze 文档](https://cx-freeze.readthedocs.io/)
- [UPX 官网](https://upx.github.io/)
- [Inno Setup](https://jrsoftware.org/isinfo.php)

---

**建议：继续使用 PyInstaller，它是最稳妥的选择！** ✅
