"""
MechForge AI GUI 后端服务器
提供 HTTP API 供前端 JavaScript 调用

模块化架构：
- api/chat.py    - 聊天 API
- api/rag.py     - RAG API
- api/config.py  - 配置 API
- api/gguf.py    - GGUF 模型 API
- api/health.py  - 健康检查 API
"""

import logging
import socket
from pathlib import Path
from typing import Union

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

# ── 路径设置 ──────────────────────────────────────────────────────────────────

import sys

# 检测是否在 PyInstaller 打包环境中
def get_gui_dir() -> Path:
    """获取 GUI 目录，兼容 PyInstaller 打包环境"""
    # PyInstaller 会在 sys 中设置 _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        # 打包后的临时目录，所有资源都在这里
        return Path(sys._MEIPASS).resolve()
    else:
        # 开发环境
        return Path(__file__).parent.resolve()

GUI_DIR = get_gui_dir()

# 在打包环境中，GUI_DIR 就是根目录（包含 api/ 等子目录）
# 在开发环境中，需要添加父目录到 Python 路径
if hasattr(sys, '_MEIPASS'):
    # 打包环境：所有资源在 _MEIPASS 目录下
    if str(GUI_DIR) not in sys.path:
        sys.path.insert(0, str(GUI_DIR))
else:
    # 开发环境：添加项目根目录
    project_root = Path(__file__).parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

# ── 日志 ──────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("mechforge.server")

# ── FastAPI 应用 ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="MechForge AI GUI Backend",
    description="Backend API for MechForge AI Desktop GUI",
    version="0.5.0",
    docs_url="/docs",
    redoc_url=None,
)

# ── CORS 中间件 ───────────────────────────────────────────────────────────────

# 注意：在生产环境中应该限制具体的 origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发环境）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 注册 API 路由 ─────────────────────────────────────────────────────────────

from api import (
    chat_router,
    config_router,
    gguf_router,
    health_router,
    rag_router,
)
from api.errors import setup_error_handlers

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(rag_router)
app.include_router(config_router)
app.include_router(gguf_router)

# 配置错误处理器
setup_error_handlers(app)

# ── 静态文件服务 ──────────────────────────────────────────────────────────────


@app.get("/", tags=["静态"], response_model=None)
async def serve_index() -> Union[FileResponse, HTMLResponse]:
    """提供主页面"""
    index_file = GUI_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    return HTMLResponse(
        f"<pre>index.html not found.\nGUI_DIR = {GUI_DIR}</pre>",
        status_code=404,
    )


@app.get("/styles.css", tags=["静态"], response_model=None)
async def serve_styles() -> Union[FileResponse, HTMLResponse]:
    """提供主样式文件"""
    styles_file = GUI_DIR / "styles.css"
    if styles_file.exists():
        return FileResponse(str(styles_file), media_type="text/css")
    return HTMLResponse("styles.css not found", status_code=404)


@app.get("/styles-modular.css", tags=["静态"], response_model=None)
async def serve_styles_modular() -> Union[FileResponse, HTMLResponse]:
    """提供模块化样式入口"""
    styles_file = GUI_DIR / "styles-modular.css"
    if styles_file.exists():
        return FileResponse(str(styles_file), media_type="text/css")
    return HTMLResponse("styles-modular.css not found", status_code=404)


@app.get("/experience.css", tags=["静态"], response_model=None)
async def serve_experience_styles() -> Union[FileResponse, HTMLResponse]:
    """提供 Experience Library 样式"""
    styles_file = GUI_DIR / "experience.css"
    if styles_file.exists():
        return FileResponse(str(styles_file), media_type="text/css")
    return HTMLResponse("experience.css not found", status_code=404)


@app.get("/dj-whale.png", tags=["静态"], response_model=None)
async def serve_whale() -> Union[FileResponse, HTMLResponse]:
    """提供应用图标"""
    icon_file = GUI_DIR / "dj-whale.png"
    if icon_file.exists():
        return FileResponse(str(icon_file), media_type="image/png")
    return HTMLResponse("dj-whale.png not found", status_code=404)


@app.get("/experience.js", tags=["静态"], response_model=None)
async def serve_experience_js() -> Union[FileResponse, HTMLResponse]:
    """提供 Experience Library 脚本"""
    js_file = GUI_DIR / "experience.js"
    if js_file.exists():
        return FileResponse(str(js_file), media_type="application/javascript")
    return HTMLResponse("experience.js not found", status_code=404)


# ── 静态目录挂载 ──────────────────────────────────────────────────────────────

STATIC_DIRS = [
    ("core", GUI_DIR / "core"),
    ("services", GUI_DIR / "services"),
    ("app", GUI_DIR / "app"),
    ("css", GUI_DIR / "css"),
]

for mount_path, dir_path in STATIC_DIRS:
    if dir_path.exists() and dir_path.is_dir():
        app.mount(f"/{mount_path}", StaticFiles(directory=str(dir_path)), name=mount_path)
        logger.debug(f"静态目录已挂载: /{mount_path} -> {dir_path}")
    else:
        logger.warning(f"静态目录不存在，跳过挂载: {dir_path}")


# ── 启动入口 ──────────────────────────────────────────────────────────────────


def find_free_port(start_port: int = 5000, max_attempts: int = 100) -> int:
    """从 start_port 开始查找第一个可用端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"在 {start_port}~{start_port + max_attempts} 范围内找不到可用端口")


def run_server(host: str = "127.0.0.1", port: int = 5000, reload: bool = False) -> None:
    """启动服务器"""
    from api.state import state

    port = find_free_port(port)
    logger.info(f"MechForge AI GUI 后端启动: http://{host}:{port}")
    logger.info(f"GUI 目录: {GUI_DIR}")
    logger.info(f"RAG 启用: {state.config.knowledge.rag.enabled}")

    uvicorn.run(
        "gui_pywebview.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="warning",
    )


if __name__ == "__main__":
    run_server()