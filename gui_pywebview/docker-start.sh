#!/bin/bash
# MechForge AI - Docker 快速启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# 显示帮助
show_help() {
    echo "MechForge AI - Docker 快速启动脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start [profile]   启动服务 (默认: full)"
    echo "  stop              停止服务"
    echo "  restart           重启服务"
    echo "  logs [service]    查看日志"
    echo "  status            查看状态"
    echo "  pull              拉取最新镜像"
    echo "  update            更新并重启服务"
    echo "  clean             清理所有容器和数据"
    echo ""
    echo "Profiles:"
    echo "  ai      - AI 对话模式"
    echo "  rag     - 知识库 RAG 模式"
    echo "  work    - CAE 工作台模式"
    echo "  web     - Web 服务模式"
    echo "  full    - 完整版 (默认)"
    echo ""
    echo "示例:"
    echo "  $0 start           # 启动完整版"
    echo "  $0 start ai        # 启动 AI 对话模式"
    echo "  $0 logs            # 查看所有日志"
    echo "  $0 logs ollama     # 查看 Ollama 日志"
    echo "  $0 update          # 更新并重启"
}

# 检查依赖
check_dependencies() {
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装，请先安装 Docker"
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose 未安装，请先安装 Docker Compose"
    fi

    # 使用 docker compose 或 docker-compose
    if docker compose version &> /dev/null; then
        COMPOSE="docker compose"
    else
        COMPOSE="docker-compose"
    fi
}

# 创建必要目录
create_directories() {
    mkdir -p knowledge workdir models data logs
}

# 初始化环境文件
init_env() {
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            info "创建 .env 文件..."
            cp .env.example .env
            success ".env 文件已创建"
        else
            warn ".env.example 不存在，跳过"
        fi
    fi
}

# 启动服务
start_service() {
    local profile="${1:-full}"
    info "启动 MechForge AI ($profile 模式)..."
    create_directories
    init_env
    $COMPOSE --profile "$profile" up -d
    success "服务已启动"
    echo ""
    show_access_info "$profile"
}

# 显示访问信息
show_access_info() {
    local profile="$1"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 MechForge AI 已启动！"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    case "$profile" in
        ai)
            echo "  模式: AI 对话"
            echo "  使用: docker-compose exec mechforge-ai python -m mechforge_ai.terminal"
            ;;
        rag)
            echo "  模式: 知识库 RAG"
            echo "  使用: docker-compose exec mechforge-k python -m mechforge_knowledge.cli"
            ;;
        work)
            echo "  模式: CAE 工作台"
            echo "  使用: docker-compose exec mechforge-work python -m mechforge_work.work_cli"
            ;;
        web|full)
            echo "  模式: Web 服务"
            echo "  访问: http://localhost:${WEB_PORT:-8080}"
            echo "  API:  http://localhost:${WEB_PORT:-8080}/docs"
            ;;
    esac
    echo ""
    echo "  查看日志: $0 logs"
    echo "  停止服务: $0 stop"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# 停止服务
stop_service() {
    info "停止服务..."
    $COMPOSE down
    success "服务已停止"
}

# 重启服务
restart_service() {
    info "重启服务..."
    $COMPOSE restart
    success "服务已重启"
}

# 查看日志
view_logs() {
    local service="$1"
    if [ -n "$service" ]; then
        $COMPOSE logs -f "$service"
    else
        $COMPOSE logs -f
    fi
}

# 查看状态
show_status() {
    $COMPOSE ps
}

# 拉取镜像
pull_images() {
    info "拉取最新镜像..."
    $COMPOSE pull
    success "镜像已更新"
}

# 更新并重启
update_service() {
    info "更新服务..."
    pull_images
    stop_service
    $COMPOSE --profile full up -d
    success "服务已更新并重启"
}

# 清理
clean_all() {
    warn "这将删除所有容器、数据卷和数据！"
    read -p "确定要继续吗？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        info "清理中..."
        $COMPOSE down -v --remove-orphans
        docker system prune -f
        success "清理完成"
    else
        info "已取消"
    fi
}

# 主入口
main() {
    check_dependencies

    case "${1:-help}" in
        start)
            start_service "$2"
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        logs)
            view_logs "$2"
            ;;
        status)
            show_status
            ;;
        pull)
            pull_images
            ;;
        update)
            update_service
            ;;
        clean)
            clean_all
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            error "未知命令: $1\n运行 '$0 help' 查看帮助"
            ;;
    esac
}

main "$@"