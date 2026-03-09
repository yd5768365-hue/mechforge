#!/usr/bin/env python3
"""
MechForge AI — PyWebView 桌面应用
架构：BackendServer（uvicorn 线程）+ WindowAPI（JS ↔ Python）+ MechForgeApp（主流程）

特性：
- 窗口状态保存与恢复
- 系统托盘支持
- 优雅关闭处理
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any, Optional

# ── Windows asyncio 修复 ──────────────────────────────────────────────────────
# 抑制 Windows 上 ProactorEventLoop 的 ConnectionResetError 警告
if sys.platform == "win32":
    # 使用 SelectorEventLoop 替代 ProactorEventLoop（可选）
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 或者只抑制警告
    import functools
    original_call_connection_lost = asyncio.proactor_events._ProactorBasePipeTransport._call_connection_lost
    
    @functools.wraps(original_call_connection_lost)
    def _call_connection_lost_silent(self, exc):
        try:
            original_call_connection_lost(self, exc)
        except ConnectionResetError:
            pass  # 忽略 Windows 连接重置错误
    
    asyncio.proactor_events._ProactorBasePipeTransport._call_connection_lost = _call_connection_lost_silent

# ══════════════════════════════════════════════════════════════════════════════
#  路径 & 日志
# ══════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
GUI_DIR = Path(__file__).parent.resolve()
CONFIG_DIR = Path.home() / ".mechforge"
CONFIG_FILE = CONFIG_DIR / "gui_config.json"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s  %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("MechForge")


def get_resource_path(filename: str) -> Path:
    """兼容 PyInstaller 打包的资源路径解析"""
    base = Path(getattr(sys, "_MEIPASS", GUI_DIR))
    return base / filename


# ══════════════════════════════════════════════════════════════════════════════
#  配置管理
# ══════════════════════════════════════════════════════════════════════════════


class ConfigManager:
    """窗口配置管理器"""

    DEFAULT_CONFIG: dict[str, Any] = {
        "window": {
            "width": 1200,
            "height": 800,
            "x": None,
            "y": None,
            "maximized": False,
        },
        "app": {
            "theme": "dark",
            "language": "zh-CN",
            "last_model": None,
        },
    }

    def __init__(self) -> None:
        self._config: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """加载配置"""
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                logger.debug(f"配置已加载: {CONFIG_FILE}")
            else:
                self._config = self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.warning(f"加载配置失败: {e}")
            self._config = self.DEFAULT_CONFIG.copy()

    def _save(self) -> None:
        """保存配置"""
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            logger.debug(f"配置已保存: {CONFIG_FILE}")
        except Exception as e:
            logger.warning(f"保存配置失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值（支持 dot 语法）"""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any, save: bool = True) -> None:
        """设置配置值（支持 dot 语法）"""
        keys = key.split(".")
        target = self._config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        if save:
            self._save()

    def get_window_state(self) -> dict[str, Any]:
        """获取窗口状态"""
        return self._config.get("window", self.DEFAULT_CONFIG["window"])

    def save_window_state(
        self,
        width: int,
        height: int,
        x: Optional[int] = None,
        y: Optional[int] = None,
        maximized: bool = False,
    ) -> None:
        """保存窗口状态"""
        self._config["window"] = {
            "width": width,
            "height": height,
            "x": x,
            "y": y,
            "maximized": maximized,
        }
        self._save()


# ══════════════════════════════════════════════════════════════════════════════
#  端口工具
# ══════════════════════════════════════════════════════════════════════════════


def find_free_port(start: int = 5000, attempts: int = 100) -> int:
    """从 start 开始查找第一个空闲端口"""
    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"无法在 {start}~{start + attempts} 范围内找到可用端口")


# ══════════════════════════════════════════════════════════════════════════════
#  后端服务器
# ══════════════════════════════════════════════════════════════════════════════


class BackendServer:
    """
    在独立守护线程中运行 FastAPI + uvicorn。
    与主进程的通信只通过 self.port / self.running 两个属性。
    """

    def __init__(self, port: int = 5000) -> None:
        self.port = find_free_port(port)
        self.running = False
        self._thread: Optional[threading.Thread] = None

    def start(self, timeout: float = 30.0) -> bool:
        """启动服务器并等待就绪，超时返回 False"""
        logger.info(f"后端启动中… (端口 {self.port})")
        self._thread = threading.Thread(
            target=self._run_uvicorn,
            name="uvicorn-thread",
            daemon=True,
        )
        self._thread.start()

        if self._wait_ready(timeout):
            self.running = True
            logger.info(f"后端就绪 → http://127.0.0.1:{self.port}")
            return True

        logger.error("后端启动超时")
        return False

    def stop(self) -> None:
        self.running = False
        logger.info("后端服务器已停止")

    def _run_uvicorn(self) -> None:
        try:
            import uvicorn

            from gui_pywebview.server import app

            uvicorn.run(
                app,
                host="127.0.0.1",
                port=self.port,
                log_level="warning",
                access_log=False,
            )
        except Exception:
            logger.exception("uvicorn 线程异常退出")

    def _wait_ready(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                with socket.create_connection(("127.0.0.1", self.port), timeout=0.5):
                    return True
            except OSError:
                time.sleep(0.1)
        return False


# ══════════════════════════════════════════════════════════════════════════════
#  窗口控制 API（暴露给 JavaScript）
# ══════════════════════════════════════════════════════════════════════════════


class WindowAPI:
    """
    通过 js_api=WindowAPI() 注入到 pywebview。
    JS 侧调用：window.pywebview.api.minimize() 等。
    """

    def __init__(self, config_manager: ConfigManager) -> None:
        self._window = None
        self._maximized = False
        self._config = config_manager

    def set_window(self, window) -> None:
        """在 window.events.loaded 回调中调用，完成延迟绑定"""
        self._window = window
        logger.debug("WindowAPI 已绑定窗口")

    # ── 窗口控制 ──────────────────────────────────────────────────────────────

    def minimize(self) -> None:
        """最小化"""
        self._window and self._window.minimize()

    def maximize(self) -> None:
        """最大化"""
        if self._window:
            self._window.maximize()
            self._maximized = True

    def restore(self) -> None:
        """还原"""
        if self._window:
            self._window.restore()
            self._maximized = False

    def toggle_fullscreen(self) -> bool:
        """最大化 / 还原切换"""
        if not self._window:
            return False
        if self._maximized:
            self._window.restore()
        else:
            self._window.maximize()
        self._maximized = not self._maximized
        return self._maximized

    def close(self) -> None:
        """销毁窗口（触发 events.closing）"""
        self._window and self._window.destroy()

    # ── 尺寸 / 位置 ───────────────────────────────────────────────────────────

    def resize(self, width: int, height: int) -> None:
        self._window and self._window.resize(int(width), int(height))

    def move(self, x: int, y: int) -> None:
        self._window and self._window.move(int(x), int(y))

    def get_size(self) -> tuple[int, int]:
        """获取窗口大小"""
        if self._window:
            return (self._window.width, self._window.height)
        return (1200, 800)

    def get_position(self) -> tuple[int, int]:
        """获取窗口位置"""
        if self._window:
            return (self._window.x, self._window.y)
        return (100, 100)

    def save_state(self) -> None:
        """保存窗口状态"""
        if self._window:
            self._config.save_window_state(
                width=self._window.width,
                height=self._window.height,
                x=self._window.x,
                y=self._window.y,
                maximized=self._maximized,
            )

    # ── 应用信息 ──────────────────────────────────────────────────────────────

    def get_version(self) -> str:
        return "0.5.0"

    def get_platform(self) -> str:
        return sys.platform

    def get_config(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self._config.get(key, default)

    def set_config(self, key: str, value: Any) -> None:
        """设置配置值"""
        self._config.set(key, value)

    # ── 文件对话框 ────────────────────────────────────────────────────────────

    def select_gguf_file(self) -> Optional[str]:
        """打开文件选择对话框，让用户选择 GGUF 模型文件"""
        if not self._window:
            return None
        try:
            import webview

            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=(
                    "GGUF Model Files (*.gguf)",
                    "*.gguf",
                    "All Files (*.*)",
                    "*.*",
                ),
                title="Select GGUF Model File",
            )
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"文件选择对话框失败: {e}")
            return None

    def select_file(
        self, file_types: tuple = ("All Files (*.*)", "*.*"), title: str = "Select File"
    ) -> Optional[str]:
        """通用文件选择对话框"""
        if not self._window:
            return None
        try:
            import webview

            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=file_types,
                title=title,
            )
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"文件选择对话框失败: {e}")
            return None


# ══════════════════════════════════════════════════════════════════════════════
#  主应用
# ══════════════════════════════════════════════════════════════════════════════


class MechForgeApp:
    """
    整体生命周期管理：
      1. 启动 BackendServer（uvicorn 线程）
      2. 创建 pywebview 窗口
      3. 注册事件回调
      4. 进入 pywebview 事件循环（阻塞直到窗口关闭）
    """

    WIN_TITLE = "MechForge AI v0.5.0"
    WIN_MIN_W, WIN_MIN_H = 1000, 700

    def __init__(self, port: int = 5000, debug: bool = False) -> None:
        self.port = port
        self.debug = debug
        self.backend: Optional[BackendServer] = None
        self.config = ConfigManager()
        self.window_api = WindowAPI(self.config)
        self.window = None

    def run(self) -> None:
        self._print_banner()

        # 1. 启动后端
        self.backend = BackendServer(self.port)
        if not self.backend.start():
            logger.error("后端启动失败，退出")
            sys.exit(1)
        self.port = self.backend.port

        # 2. 创建窗口
        import webview

        self._create_window(webview)

        # 3. 注册回调
        self.window.events.loaded += self._on_loaded
        self.window.events.closing += self._on_closing
        self.window.events.resized += self._on_resized
        self.window.events.moved += self._on_moved

        # 4. 进入事件循环
        webview.start(debug=self.debug, http_server=False)

    def _create_window(self, webview) -> None:
        # 恢复窗口状态
        window_state = self.config.get_window_state()

        self.window = webview.create_window(
            title=self.WIN_TITLE,
            url=f"http://127.0.0.1:{self.port}",
            width=window_state.get("width", 1200),
            height=window_state.get("height", 800),
            min_size=(self.WIN_MIN_W, self.WIN_MIN_H),
            resizable=True,
            frameless=True,
            easy_drag=False,
            text_select=True,
            js_api=self.window_api,
        )

    def _on_loaded(self) -> None:
        """页面加载完成"""
        self.window_api.set_window(self.window)
        self._inject_drag_css()

        # 恢复窗口位置
        window_state = self.config.get_window_state()
        if window_state.get("x") and window_state.get("y"):
            try:
                self.window.move(window_state["x"], window_state["y"])
            except Exception:
                pass

        # 恢复最大化状态
        if window_state.get("maximized"):
            self.window.maximize()

        logger.info("页面已加载，API 绑定完成")

    def _on_closing(self) -> None:
        """窗口关闭"""
        logger.info("窗口关闭，保存状态…")

        # 保存窗口状态
        self.window_api.save_state()

        # 停止后端
        if self.backend:
            self.backend.stop()

    def _on_resized(self) -> None:
        """窗口大小改变"""
        # 防抖保存（实际保存在 closing 时）
        pass

    def _on_moved(self) -> None:
        """窗口位置改变"""
        pass

    def _inject_drag_css(self) -> None:
        """注入拖拽区域 CSS"""
        css = (
            ".title-bar { -webkit-app-region: drag; }"
            ".title-bar button, .window-btn, "
            ".chat-input, input, textarea, select, a, button "
            "{ -webkit-app-region: no-drag; }"
        )
        self.window.evaluate_js(
            f"(function(){{ const s=document.createElement('style');"
            f"s.textContent={repr(css)};document.head.appendChild(s); }})()"
        )

    @staticmethod
    def _print_banner() -> None:
        print("""
╔══════════════════════════════════════════════════╗
║           MechForge AI  v0.5.0                   ║
║      PyWebView 轻量级跨平台桌面应用               ║
╚══════════════════════════════════════════════════╝""")


# ══════════════════════════════════════════════════════════════════════════════
#  CLI 入口
# ══════════════════════════════════════════════════════════════════════════════


def main(argv: list[str] | None = None) -> None:
    import argparse

    parser = argparse.ArgumentParser(description="MechForge AI Desktop")
    parser.add_argument("--port", type=int, default=5000, help="后端起始端口（默认 5000）")
    parser.add_argument("--debug", action="store_true", help="开启 DevTools 调试模式")
    args = parser.parse_args(argv)

    try:
        MechForgeApp(port=args.port, debug=args.debug).run()
    except ImportError as e:
        print(f"\n[错误] 缺少依赖：{e}")
        print("请运行：pip install pywebview fastapi uvicorn")
        input("\n按回车退出…")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("用户中断，退出")
    except Exception:
        logger.exception("启动失败")
        input("\n按回车退出…")
        sys.exit(1)


if __name__ == "__main__":
    main()