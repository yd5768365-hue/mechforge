#!/bin/bash

# MechForge AI 启动脚本
# 支持: 正常启动、调试模式、服务器模式

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 默认值
MODE="normal"
PORT=5000
DEBUG=""

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --debug)
            MODE="debug"
            DEBUG="--debug"
            shift
            ;;
        --server)
            MODE="server"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help)
            echo ""
            echo "MechForge AI v0.5.0 - 启动脚本"
            echo ""
            echo "用法: ./start.sh [选项]"
            echo ""
            echo "选项:"
            echo "  --debug      以调试模式启动（开启 DevTools）"
            echo "  --server     仅启动后端服务器"
            echo "  --port PORT  指定端口号（默认: 5000）"
            echo "  --help       显示此帮助信息"
            echo ""
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# 打印 Banner
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    MechForge AI v0.5.0                     ║"
echo "║               PyWebView 轻量级桌面应用                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python，请先安装 Python 3.10+"
    exit 1
fi

# 检查依赖
if ! python3 -c "import webview" &> /dev/null; then
    echo "[警告] 缺少依赖，正在安装..."
    pip install -r requirements.txt
fi

# 根据模式启动
case $MODE in
    server)
        echo "[信息] 启动后端服务器（端口: $PORT）..."
        python3 -m uvicorn server:app --host 127.0.0.1 --port $PORT --reload
        ;;
    debug)
        echo "[信息] 以调试模式启动..."
        python3 desktop_app.py $DEBUG
        ;;
    *)
        python3 desktop_app.py
        ;;
esac