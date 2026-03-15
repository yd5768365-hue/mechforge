# MechForge AI - 多阶段构建 Dockerfile
# 提供多种镜像变体以满足不同部署需求
#
# 可用镜像变体:
#   - dev:      开发环境 (包含所有开发工具)
#   - ai:       AI 对话模式 (轻量级)
#   - rag:      知识库 RAG 模式
#   - work:     CAE 工作台模式
#   - full:     完整版 (包含所有功能)
#   - web:      Web 服务模式 (API + Web UI)
#
# 构建示例:
#   docker build -t mechforge-ai:latest --target ai .
#   docker build -t mechforge-full:latest --target full .

# ==================== 基础阶段 ====================
FROM python:3.11-slim as base

# 镜像元数据
LABEL maintainer="MechForge Team"
LABEL org.opencontainers.image.title="MechForge AI"
LABEL org.opencontainers.image.description="Mechanical Engineering AI Assistant"
LABEL org.opencontainers.image.url="https://github.com/yd5768365-hue/mechforge"
LABEL org.opencontainers.image.source="https://github.com/yd5768365-hue/mechforge"
LABEL org.opencontainers.image.licenses="MIT"

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    # MechForge 特定环境变量
    MECHFORGE_HOME=/app \
    MECHFORGE_DATA=/app/data \
    MECHFORGE_KNOWLEDGE=/app/knowledge

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 创建非 root 用户
RUN groupadd --gid 1000 mechforge \
    && useradd --uid 1000 --gid mechforge --shell /bin/bash --create-home mechforge

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY --chown=mechforge:mechforge pyproject.toml README.md LICENSE ./
COPY --chown=mechforge:mechforge packages/ ./packages/

# ==================== 开发阶段 ====================
FROM base as dev

LABEL org.opencontainers.image.title="MechForge AI (Development)"
LABEL org.opencontainers.image.description="Development environment with all tools"

# 安装开发依赖
RUN pip install -e ".[dev]"

# 复制源代码
COPY --chown=mechforge:mechforge . .

# 切换到非 root 用户
USER mechforge

# 设置入口点
CMD ["bash"]

# ==================== AI 模式阶段 ====================
FROM base as ai

LABEL org.opencontainers.image.title="MechForge AI (AI Mode)"
LABEL org.opencontainers.image.description="Lightweight AI chat mode"

# 安装 AI 模式依赖
RUN pip install --no-cache-dir -e "."

# 复制源代码
COPY --chown=mechforge:mechforge . .

# 创建数据目录
RUN mkdir -p /app/data /app/knowledge \
    && chown -R mechforge:mechforge /app/data /app/knowledge

# 切换到非 root 用户
USER mechforge

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from mechforge_ai.terminal import MechForgeTerminal; print('healthy')" || exit 1

# 设置入口点
ENTRYPOINT ["python", "-m", "mechforge_ai.terminal"]

# ==================== RAG 模式阶段 ====================
FROM base as rag

LABEL org.opencontainers.image.title="MechForge AI (RAG Mode)"
LABEL org.opencontainers.image.description="Knowledge base with RAG capabilities"

# 安装 RAG 依赖
RUN pip install --no-cache-dir -e ".[rag]"

# 复制源代码
COPY --chown=mechforge:mechforge . .

# 创建知识库目录
RUN mkdir -p /app/knowledge /app/data /app/.cache/rag \
    && chown -R mechforge:mechforge /app/knowledge /app/data /app/.cache

# 切换到非 root 用户
USER mechforge

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "from mechforge_knowledge.cli import main; print('healthy')" || exit 1

# 设置入口点
ENTRYPOINT ["python", "-m", "mechforge_knowledge.cli"]

# ==================== CAE 工作台阶段 ====================
FROM python:3.11-slim as work

LABEL maintainer="MechForge Team"
LABEL org.opencontainers.image.title="MechForge AI (CAE Workbench)"
LABEL org.opencontainers.image.description="CAE workbench for mechanical engineering"

# 安装系统依赖（包括 CAE 工具依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libgl1-mesa-glx \
    libxrender1 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MECHFORGE_HOME=/app \
    MECHFORGE_WORKDIR=/app/workdir

# 创建非 root 用户
RUN groupadd --gid 1000 mechforge \
    && useradd --uid 1000 --gid mechforge --shell /bin/bash --create-home mechforge

WORKDIR /app

# 复制项目文件
COPY --chown=mechforge:mechforge pyproject.toml README.md LICENSE ./
COPY --chown=mechforge:mechforge packages/ ./packages/

# 安装 CAE 依赖
RUN pip install --no-cache-dir -e ".[work]"

# 复制源代码
COPY --chown=mechforge:mechforge . .

# 创建工作目录
RUN mkdir -p /app/workdir /app/models /app/data \
    && chown -R mechforge:mechforge /app/workdir /app/models /app/data

# 切换到非 root 用户
USER mechforge

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import mechforge_work; print('healthy')" || exit 1

# 设置入口点
ENTRYPOINT ["python", "-m", "mechforge_work.work_cli"]

# ==================== Web 服务阶段 ====================
FROM base as web

LABEL org.opencontainers.image.title="MechForge AI (Web Service)"
LABEL org.opencontainers.image.description="Web API and UI service"

# 安装 Web 依赖
RUN pip install --no-cache-dir -e ".[web]"

# 复制源代码
COPY --chown=mechforge:mechforge . .

# 创建必要目录
RUN mkdir -p /app/data /app/knowledge /app/logs \
    && chown -R mechforge:mechforge /app/data /app/knowledge /app/logs

# 暴露端口
EXPOSE 8080

# 切换到非 root 用户
USER mechforge

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 设置入口点
ENTRYPOINT ["python", "-m", "mechforge_web.main"]
CMD ["--host", "0.0.0.0", "--port", "8080"]

# ==================== 完整版阶段 ====================
FROM python:3.11-slim as full

LABEL maintainer="MechForge Team"
LABEL org.opencontainers.image.title="MechForge AI (Full)"
LABEL org.opencontainers.image.description="Complete MechForge AI with all features"

# 安装所有系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libgl1-mesa-glx \
    libxrender1 \
    libxext6 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    MECHFORGE_HOME=/app \
    MECHFORGE_DATA=/app/data \
    MECHFORGE_KNOWLEDGE=/app/knowledge \
    MECHFORGE_WORKDIR=/app/workdir

# 创建非 root 用户
RUN groupadd --gid 1000 mechforge \
    && useradd --uid 1000 --gid mechforge --shell /bin/bash --create-home mechforge

WORKDIR /app

# 复制项目文件
COPY --chown=mechforge:mechforge pyproject.toml README.md LICENSE ./
COPY --chown=mechforge:mechforge packages/ ./packages/

# 安装所有依赖
RUN pip install --no-cache-dir -e ".[all]"

# 复制源代码
COPY --chown=mechforge:mechforge . .

# 创建必要目录
RUN mkdir -p /app/data /app/knowledge /app/workdir /app/models /app/logs /app/.cache \
    && chown -R mechforge:mechforge /app/data /app/knowledge /app/workdir /app/models /app/logs /app/.cache

# 暴露端口（用于 Web UI）
EXPOSE 8080

# 切换到非 root 用户
USER mechforge

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health 2>/dev/null || python -c "from mechforge_ai.terminal import MechForgeTerminal; print('healthy')" || exit 1

# 默认启动 Web 服务
CMD ["python", "-m", "mechforge_web.main", "--host", "0.0.0.0", "--port", "8080"]