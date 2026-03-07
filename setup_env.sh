#!/bin/bash

set -e

echo "=========================================="
echo "MechForge AI - Python环境设置脚本 (Linux/Mac)"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python版本
echo "[1/5] 检查Python版本..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}[OK]${NC} 找到Python $PYTHON_VERSION"
else
    echo -e "${RED}[错误]${NC} 未找到Python3。请安装Python 3.10+"
    exit 1
fi

# 检查Python版本是否>=3.10
REQUIRED_VERSION="3.10"
CURRENT_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$CURRENT_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}[错误]${NC} Python版本过低。需要 >= 3.10，当前 $CURRENT_VERSION"
    exit 1
fi

# 创建虚拟环境
echo ""
echo "[2/5] 创建虚拟环境..."
if [ -d ".venv" ]; then
    echo -e "${YELLOW}[提示]${NC} 虚拟环境已存在，跳过创建"
else
    python3 -m venv .venv
    echo -e "${GREEN}[OK]${NC} 虚拟环境创建完成"
fi

# 激活虚拟环境
echo ""
echo "[3/5] 激活虚拟环境..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[错误]${NC} 无法激活虚拟环境"
    exit 1
fi
echo -e "${GREEN}[OK]${NC} 虚拟环境已激活"

# 升级pip
echo ""
echo "[4/5] 升级pip..."
pip install --upgrade pip setuptools wheel -q
echo -e "${GREEN}[OK]${NC} pip已升级"

# 安装依赖
echo ""
echo "[5/5] 安装项目依赖..."
echo "安装基础依赖..."
pip install -e . -q

echo ""
echo "安装开发依赖..."
pip install -e ".[dev]" -q

echo ""
echo "安装完整功能依赖（这可能需要几分钟）..."
pip install -e ".[all]" -q

echo ""
echo -e "${GREEN}[OK]${NC} 依赖安装完成"

# 验证安装
echo ""
echo "=========================================="
echo "验证安装..."
echo "=========================================="
python -c "import mechforge_core; print('[OK] mechforge_core 导入成功')"
python -c "import mechforge_ai; print('[OK] mechforge_ai 导入成功')"
python -c "import mechforge_knowledge; print('[OK] mechforge_knowledge 导入成功')"
python -c "import mechforge_work; print('[OK] mechforge_work 导入成功')"
python -c "import mechforge_web; print('[OK] mechforge_web 导入成功')"
python -c "import mechforge_gui_ai; print('[OK] mechforge_gui_ai 导入成功')"

echo ""
echo "=========================================="
echo -e "${GREEN}环境设置完成！${NC}"
echo "=========================================="
echo ""
echo "使用方法:"
echo "   1. 激活环境: source .venv/bin/activate"
echo "   2. 运行程序: mechforge"
echo "   3. 运行GUI:  mechforge-gui"
echo "   4. 运行Web:  mechforge-web"
echo ""
echo "常用命令:"
echo "   mechforge --help"
echo "   mechforge-k --help"
echo "   mechforge-work --help"
echo ""
