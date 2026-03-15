# MechForge AI - Docker 部署指南

本指南帮助您快速部署 MechForge AI。

## 📦 镜像变体

| 镜像 | 大小 | 描述 | 适用场景 |
|------|------|------|----------|
| `mechforge-ai` | ~200MB | AI 对话模式 | 轻量级 AI 助手 |
| `mechforge-rag` | ~500MB | 知识库 RAG 模式 | 文档检索、知识问答 |
| `mechforge-work` | ~400MB | CAE 工作台模式 | 机械工程计算 |
| `mechforge-web` | ~300MB | Web 服务模式 | API 服务 |
| `mechforge-full` | ~800MB | 完整版 | 所有功能 |

## 🚀 快速开始

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/yd5768365-hue/mechforge.git
cd mechforge

# 2. 复制环境配置
cp .env.example .env

# 3. 编辑配置（可选）
# vim .env

# 4. 启动服务
# 完整版（推荐）
docker-compose --profile full up -d

# 或单独启动某个模式
docker-compose --profile ai up -d      # AI 对话
docker-compose --profile rag up -d     # 知识库
docker-compose --profile work up -d    # CAE 工作台
docker-compose --profile web up -d     # Web 服务

# 5. 查看日志
docker-compose logs -f

# 6. 停止服务
docker-compose down
```

### 方式二：直接使用镜像

```bash
# 从 GitHub Container Registry 拉取
docker pull ghcr.io/yd5768365-hue/mechforge:latest

# 或从 Docker Hub 拉取
docker pull docker.io/yd5768365-hue/mechforge:latest

# 运行容器
docker run -it --rm \
  -v ./knowledge:/app/knowledge \
  -v ./data:/app/data \
  ghcr.io/yd5768365-hue/mechforge:latest
```

## ⚙️ 配置说明

### 环境变量

创建 `.env` 文件配置环境变量：

```bash
# 复制模板
cp .env.example .env
```

主要配置项：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `OLLAMA_URL` | `http://ollama:11434` | Ollama 服务地址 |
| `OLLAMA_MODEL` | `qwen2.5:1.5b` | 默认使用的模型 |
| `LOG_LEVEL` | `INFO` | 日志级别 |
| `WEB_PORT` | `8080` | Web 服务端口 |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | RAG 嵌入模型 |

### 目录挂载

```yaml
volumes:
  - ./knowledge:/app/knowledge:ro  # 知识库文档（只读）
  - ./workdir:/app/workdir          # 工作目录
  - ./models:/app/models:ro         # 模型文件（只读）
  - ./data:/app/data                # 数据持久化
  - ./logs:/app/logs                # 日志目录
```

## 🌐 服务访问

启动后可通过以下方式访问：

- **Web UI**: http://localhost:8080
- **API 文档**: http://localhost:8080/docs
- **健康检查**: http://localhost:8080/health

## 📋 常用命令

```bash
# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f [服务名]

# 重启服务
docker-compose restart [服务名]

# 进入容器
docker-compose exec mechforge-full bash

# 更新镜像
docker-compose pull
docker-compose up -d

# 清理数据（注意：会删除所有数据）
docker-compose down -v
```

## 🔧 高级配置

### GPU 支持

编辑 `docker-compose.yml`，取消 GPU 配置注释：

```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 使用外部 Ollama

如果已有 Ollama 服务，修改 `.env`：

```bash
OLLAMA_URL=http://your-ollama-host:11434
```

然后在 `docker-compose.yml` 中移除 `ollama` 服务依赖。

### 自定义模型

```bash
# 进入 Ollama 容器拉取模型
docker-compose exec ollama ollama pull llama3

# 修改 .env 使用新模型
OLLAMA_MODEL=llama3
```

## 🐛 故障排除

### 容器无法启动

```bash
# 检查日志
docker-compose logs mechforge-full

# 检查健康状态
docker inspect --format='{{.State.Health.Status}}' mechforge-full
```

### Ollama 连接失败

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 检查网络
docker network ls
docker network inspect mechforge_network
```

### 权限问题

```bash
# 修复目录权限
sudo chown -R 1000:1000 ./data ./knowledge ./workdir
```

## 📚 相关文档

- [主文档](../README.md)
- [配置指南](./CONFIGURATION.md)
- [API 文档](./API.md)