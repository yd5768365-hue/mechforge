# MechForge AI - Makefile
# 简化常用开发任务

.PHONY: help install install-dev install-all clean test lint format check run gui web

# 默认目标
help:
	@echo "MechForge AI - 可用命令"
	@echo ""
	@echo "环境设置:"
	@echo "  make install      - 安装基础依赖"
	@echo "  make install-dev  - 安装开发依赖"
	@echo "  make install-all  - 安装所有依赖"
	@echo "  make clean        - 清理虚拟环境和缓存"
	@echo ""
	@echo "开发工具:"
	@echo "  make test         - 运行测试"
	@echo "  make lint         - 运行代码检查"
	@echo "  make format       - 格式化代码"
	@echo "  make check        - 运行所有检查"
	@echo ""
	@echo "运行程序:"
	@echo "  make run          - 启动AI对话终端"
	@echo "  make gui          - 启动GUI应用"
	@echo "  make web          - 启动Web服务"
	@echo "  make knowledge    - 启动知识库"
	@echo "  make work         - 启动CAE工作台"

# 环境设置
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

install-all:
	pip install -e ".[all]"

clean:
	rm -rf .venv
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 开发工具
test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=mechforge_core --cov=mechforge_ai --cov=mechforge_knowledge --cov=mechforge_work --cov=mechforge_web

lint:
	ruff check .
	mypy mechforge_core/ mechforge_ai/ mechforge_knowledge/ mechforge_work/ mechforge_web/

format:
	black .
	ruff check . --fix

check: format lint test

# 运行程序
run:
	mechforge

gui:
	mechforge-gui

web:
	mechforge-web

knowledge:
	mechforge-k

work:
	mechforge-work

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose --profile full up -d

docker-down:
	docker-compose down

# 文档
docs-serve:
	mkdocs serve

docs-build:
	mkdocs build

# 打包
build:
	python -m build

build-gui:
	python build_gui_light.py
