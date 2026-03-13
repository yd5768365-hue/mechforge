"""
内置模型下载与管理

首次启动时自动下载一个小型 GGUF 模型，使用户开箱即用。
模型存储在用户数据目录 (~/.mechforge/models/) 中。
"""

import logging
import os
import threading
import time
from pathlib import Path

import requests

logger = logging.getLogger("mechforge.model_downloader")

# ── 内置模型配置 ─────────────────────────────────────────────────────────────

BUNDLED_MODEL = {
    "name": "Qwen2.5-1.5B-Instruct",
    "filename": "qwen2.5-1.5b-instruct-q4_k_m.gguf",
    "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    "size_bytes": 1_118_000_000,  # ~1.04 GB
    "description": "通义千问 2.5 1.5B 指令微调模型 (Q4_K_M 量化)",
}

# 镜像源，用于国内加速
MIRROR_URLS = [
    "https://hf-mirror.com/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
    BUNDLED_MODEL["url"],
]


def get_models_dir() -> Path:
    """获取模型存储目录"""
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path.home() / ".config"
    models_dir = base / "mechforge" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def get_bundled_model_path() -> Path:
    """获取内置模型的完整路径"""
    return get_models_dir() / BUNDLED_MODEL["filename"]


def is_bundled_model_ready() -> bool:
    """检查内置模型是否已下载就绪"""
    path = get_bundled_model_path()
    if not path.exists():
        return False
    actual_size = path.stat().st_size
    return actual_size > BUNDLED_MODEL["size_bytes"] * 0.95


# ── 下载状态 ─────────────────────────────────────────────────────────────────

class DownloadState:
    """下载状态追踪"""

    def __init__(self):
        self.downloading = False
        self.progress = 0.0
        self.downloaded_bytes = 0
        self.total_bytes = 0
        self.speed = 0.0  # bytes/sec
        self.eta = 0  # seconds
        self.error: str | None = None
        self.completed = False
        self._lock = threading.Lock()

    def to_dict(self) -> dict:
        with self._lock:
            return {
                "downloading": self.downloading,
                "progress": round(self.progress, 2),
                "downloaded_mb": round(self.downloaded_bytes / 1024 / 1024, 1),
                "total_mb": round(self.total_bytes / 1024 / 1024, 1),
                "speed_mbps": round(self.speed / 1024 / 1024, 2),
                "eta_seconds": self.eta,
                "error": self.error,
                "completed": self.completed,
            }

    def reset(self):
        with self._lock:
            self.downloading = False
            self.progress = 0.0
            self.downloaded_bytes = 0
            self.total_bytes = 0
            self.speed = 0.0
            self.eta = 0
            self.error = None
            self.completed = False


download_state = DownloadState()


# ── 下载逻辑 ─────────────────────────────────────────────────────────────────

def _download_worker(on_complete=None):
    """后台下载线程"""
    global download_state

    model_path = get_bundled_model_path()
    temp_path = model_path.with_suffix(".gguf.downloading")

    try:
        download_state.downloading = True
        download_state.error = None
        download_state.completed = False

        downloaded = 0
        if temp_path.exists():
            downloaded = temp_path.stat().st_size

        headers = {}
        if downloaded > 0:
            headers["Range"] = f"bytes={downloaded}-"
            logger.info(f"断点续传: 已有 {downloaded / 1024 / 1024:.1f} MB")

        resp = None
        used_url = None
        for url in MIRROR_URLS:
            try:
                logger.info(f"尝试下载: {url}")
                resp = requests.get(url, headers=headers, stream=True, timeout=30)
                if resp.status_code in (200, 206):
                    used_url = url
                    break
                resp.close()
            except requests.RequestException as e:
                logger.warning(f"下载源不可用 {url}: {e}")
                continue

        if resp is None or used_url is None:
            download_state.error = "所有下载源均不可用，请检查网络连接"
            download_state.downloading = False
            return

        if resp.status_code == 200:
            downloaded = 0
            total = int(resp.headers.get("content-length", BUNDLED_MODEL["size_bytes"]))
        else:
            content_range = resp.headers.get("content-range", "")
            if "/" in content_range:
                total = int(content_range.split("/")[-1])
            else:
                total = downloaded + int(
                    resp.headers.get("content-length", BUNDLED_MODEL["size_bytes"] - downloaded)
                )

        download_state.total_bytes = total
        download_state.downloaded_bytes = downloaded

        logger.info(f"开始下载内置模型: {BUNDLED_MODEL['name']} ({total / 1024 / 1024:.0f} MB)")

        mode = "ab" if downloaded > 0 and resp.status_code == 206 else "wb"
        chunk_size = 1024 * 256  # 256KB chunks
        start_time = time.time()
        last_log_time = start_time

        with open(temp_path, mode) as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if not download_state.downloading:
                    logger.info("下载被取消")
                    resp.close()
                    return

                f.write(chunk)
                downloaded += len(chunk)

                with download_state._lock:
                    download_state.downloaded_bytes = downloaded
                    download_state.progress = (downloaded / total * 100) if total > 0 else 0

                    elapsed = time.time() - start_time
                    if elapsed > 0:
                        download_state.speed = downloaded / elapsed
                        remaining = total - downloaded
                        download_state.eta = int(remaining / download_state.speed) if download_state.speed > 0 else 0

                now = time.time()
                if now - last_log_time > 10:
                    logger.info(
                        f"下载进度: {download_state.progress:.1f}% "
                        f"({downloaded / 1024 / 1024:.0f}/{total / 1024 / 1024:.0f} MB) "
                        f"速度: {download_state.speed / 1024 / 1024:.1f} MB/s"
                    )
                    last_log_time = now

        resp.close()

        temp_path.rename(model_path)

        download_state.completed = True
        download_state.progress = 100.0
        download_state.downloading = False

        logger.info(f"内置模型下载完成: {model_path}")

        if on_complete:
            on_complete(str(model_path))

    except Exception as e:
        logger.error(f"模型下载失败: {e}")
        download_state.error = str(e)
        download_state.downloading = False


def start_download(on_complete=None) -> bool:
    """启动后台下载

    Args:
        on_complete: 下载完成后的回调函数，参数为模型路径字符串
    Returns:
        是否成功启动下载
    """
    if download_state.downloading:
        return False

    if is_bundled_model_ready():
        download_state.completed = True
        download_state.progress = 100.0
        return False

    download_state.reset()
    thread = threading.Thread(target=_download_worker, args=(on_complete,), daemon=True)
    thread.start()
    return True


def cancel_download():
    """取消当前下载"""
    download_state.downloading = False


def auto_load_bundled_model():
    """自动加载内置模型（如果已下载）"""
    if not is_bundled_model_ready():
        return False

    model_path = str(get_bundled_model_path())

    from .state import state
    if state.gguf_llm is not None:
        return True

    try:
        from llama_cpp import Llama

        logger.info(f"自动加载内置模型: {BUNDLED_MODEL['name']}")
        state.gguf_llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=max(2, os.cpu_count() // 2 if os.cpu_count() else 2),
            verbose=False,
        )
        state.gguf_model_path = model_path
        state.current_provider = "gguf"
        logger.info("内置模型加载成功")
        return True
    except ImportError:
        logger.warning("llama-cpp-python 未安装，无法加载内置模型")
        return False
    except Exception as e:
        logger.error(f"内置模型加载失败: {e}")
        return False
