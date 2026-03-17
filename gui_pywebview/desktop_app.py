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
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Any

# ── 配置 ──────────────────────────────────────────────────────────────────────

# cspell:ignore MECHFORGE MEIPASS pywebview gguf frameless cw5n1h2txyewy creationflags msgbox

# 从环境变量读取配置，提供默认值
DEFAULT_HOST = os.getenv("MECHFORGE_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.getenv("MECHFORGE_PORT", "5000"))
DEFAULT_WINDOW_WIDTH = int(os.getenv("MECHFORGE_WINDOW_WIDTH", "1200"))
DEFAULT_WINDOW_HEIGHT = int(os.getenv("MECHFORGE_WINDOW_HEIGHT", "800"))
DEFAULT_MIN_WIDTH = int(os.getenv("MECHFORGE_WINDOW_MIN_WIDTH", "1000"))
DEFAULT_MIN_HEIGHT = int(os.getenv("MECHFORGE_WINDOW_MIN_HEIGHT", "700"))
CONFIG_DIR = Path(os.getenv("MECHFORGE_CONFIG_DIR", Path.home() / ".mechforge"))
CONFIG_FILE = CONFIG_DIR / "gui_config.json"

# ── Windows asyncio 修复 ──────────────────────────────────────────────────────
# 抑制 Windows 上 ProactorEventLoop 的 ConnectionResetError 警告
if sys.platform == "win32":
    # 使用 SelectorEventLoop 替代 ProactorEventLoop（可选）
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # 或者只抑制警告
    import functools

    # cspell:ignore Proactor
    original_call_connection_lost = (
        asyncio.proactor_events._ProactorBasePipeTransport._call_connection_lost  # type: ignore[attr-defined]
    )

    @functools.wraps(original_call_connection_lost)
    def _call_connection_lost_silent(self, exc):
        try:
            original_call_connection_lost(self, exc)
        except ConnectionResetError:
            pass  # 忽略 Windows 连接重置错误

    asyncio.proactor_events._ProactorBasePipeTransport._call_connection_lost = (  # type: ignore[attr-defined]
        _call_connection_lost_silent
    )

# ══════════════════════════════════════════════════════════════════════════════
#  路径 & 日志
# ══════════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
GUI_DIR = Path(__file__).parent.resolve()

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
            "width": DEFAULT_WINDOW_WIDTH,
            "height": DEFAULT_WINDOW_HEIGHT,
            "x": None,
            "y": None,
            "maximized": False,
        },
        "app": {
            "theme": os.getenv("MECHFORGE_THEME", "dark"),
            "language": os.getenv("MECHFORGE_LANGUAGE", "zh-CN"),
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
                with open(CONFIG_FILE, encoding="utf-8") as f:
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
        x: int | None = None,
        y: int | None = None,
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


def find_free_port(start: int = None, attempts: int = 100) -> int:
    """从 start 开始查找第一个空闲端口

    Args:
        start: 起始端口，默认从环境变量 MECHFORGE_PORT 读取
        attempts: 最大尝试次数
    """
    if start is None:
        start = DEFAULT_PORT

    for port in range(start, start + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((DEFAULT_HOST, port))
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

    def __init__(self, port: int = None) -> None:
        self.port = find_free_port(port)
        self.host = DEFAULT_HOST
        self.running = False
        self._thread: threading.Thread | None = None

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
            logger.info(f"后端就绪 → http://{self.host}:{self.port}")
            return True

        logger.error("后端启动超时")
        return False

    def stop(self) -> None:
        self.running = False
        logger.info("后端服务器已停止")

    def _run_uvicorn(self) -> None:
        try:
            # 动态导入 server 模块（兼容 PyInstaller 打包）
            import sys
            from pathlib import Path

            import uvicorn

            # 获取正确的 GUI 目录（资源文件所在目录）
            if hasattr(sys, "_MEIPASS"):
                gui_dir = Path(sys._MEIPASS)
            else:
                # 开发环境使用 desktop_app.py 所在目录
                gui_dir = Path(__file__).parent

            # 添加到 Python 路径，确保可以导入 api 模块
            gui_dir_str = str(gui_dir)
            if gui_dir_str not in sys.path:
                sys.path.insert(0, gui_dir_str)

            # 添加父项目目录到路径，以便导入 mechforge_core 和 mechforge_ai
            parent_dir = gui_dir.parent
            parent_dir_str = str(parent_dir)
            if parent_dir_str not in sys.path:
                sys.path.insert(0, parent_dir_str)
                logger.info(f"添加父项目路径: {parent_dir_str}")

            logger.info(f"Uvicorn 加载路径: {gui_dir_str}")
            logger.info(f"目录内容: {list(gui_dir.glob('*'))[:10]}")

            from server import app

            uvicorn.run(
                app,
                host=self.host,
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
                with socket.create_connection((self.host, self.port), timeout=0.5):
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

    # ── 向导 ─────────────────────────────────────────────────────────────────

    def open_wizard(self, page: str) -> None:
        import webview

        if self._window:
            # 在新窗口中打开向导
            wizard_window = webview.create_window(
                "RAGFlow 安装向导",
                url=page,
                width=720,
                height=720,
                resizable=False,
            )
            wizard_window.events.closed += lambda: None
            webview.windows.append(wizard_window)

    def close_wizard(self) -> None:
        """关闭向导并刷新主窗口"""
        import webview

        # 关闭除了主窗口外的所有窗口
        for window in webview.windows[:]:
            if window != self._window:
                window.destroy()
        # 刷新主窗口
        if self._window:
            self._window.evaluate_js('location.reload()')

    def open_url(self, url: str) -> None:
        """打开外部 URL"""
        import webbrowser

        webbrowser.open(url)

    # ── 文件对话框 ────────────────────────────────────────────────────────────

    def select_gguf_file(self) -> str | None:
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
            )
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"文件选择对话框失败: {e}")
            return None

    def select_file(
        self, file_types: tuple = ("All Files (*.*)", "*.*"), title: str = "Select File"
    ) -> str | None:
        """通用文件选择对话框"""
        if not self._window:
            return None
        try:
            import webview

            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                file_types=file_types,
            )
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"文件选择对话框失败: {e}")
            return None

    def select_folder(self, title: str = "选择目录") -> str | None:
        """目录选择对话框"""
        if not self._window:
            return None
        try:
            import webview

            result = self._window.create_file_dialog(
                webview.FOLDER_DIALOG,
            )
            if result and len(result) > 0:
                return result[0]
            return None
        except Exception as e:
            logger.error(f"目录选择对话框失败: {e}")
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

    WIN_TITLE = os.getenv("MECHFORGE_WINDOW_TITLE", "MechForge AI v0.5.0")
    WIN_MIN_W = DEFAULT_MIN_WIDTH
    WIN_MIN_H = DEFAULT_MIN_HEIGHT

    def __init__(self, port: int = None, debug: bool = None) -> None:
        self.port = port
        self.debug = (
            debug if debug is not None else os.getenv("MECHFORGE_DEBUG", "false").lower() == "true"
        )
        self.backend: BackendServer | None = None
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
            url=f"http://{DEFAULT_HOST}:{self.port}",
            width=window_state.get("width", DEFAULT_WINDOW_WIDTH),
            height=window_state.get("height", DEFAULT_WINDOW_HEIGHT),
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


def ensure_loopback_exemption() -> bool:
    """
    Windows WebView2 默认禁止访问 localhost，需添加回环豁免。
    以管理员运行 CheckNetIsolation 可修复「网站无法访问」问题。
    """
    if sys.platform != "win32":
        return True
    try:
        result = subprocess.run(
            [
                "CheckNetIsolation.exe",
                "LoopbackExempt",
                "-a",
                '-n="Microsoft.Win32WebViewHost_cw5n1h2txyewy"',
            ],
            capture_output=True,
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
        )
        if result.returncode == 0:
            logger.info("localhost 回环豁免已启用")
            return True
        # 已存在或需管理员权限
        stderr_bytes = result.stderr or b""
        stderr_text = stderr_bytes.decode("utf-8", errors="ignore").lower()
        if "already" in stderr_text or "已" in stderr_text:
            return True
        logger.warning("localhost 回环豁免未设置（需管理员权限）。若页面空白，请以管理员运行 fix_localhost.bat")
        return False
    except Exception as e:
        logger.debug(f"回环豁免检查跳过: {e}")
        return False


def check_webview2() -> bool:
    """Check if WebView2 runtime is installed"""
    if sys.platform != "win32":
        return True
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
        )
        winreg.CloseKey(key)
        return True
    except FileNotFoundError:
        return False


def show_webview2_error():
    """Show WebView2 error dialog"""
    msg = (
        "MechForge AI requires Microsoft Edge WebView2 Runtime.\n\n"
        "Please download and install it from:\n"
        "https://go.microsoft.com/fwlink/p/?LinkId=2124703"
    )
    try:
        import tkinter as tk
        import tkinter.messagebox as msgbox

        root = tk.Tk()
        root.withdraw()
        msgbox.showerror("MechForge AI - Error", msg)
    except Exception:
        print(msg, file=sys.stderr)
        input("\nPress Enter to exit...")


def main(argv: list[str] | None = None) -> None:
    import argparse

    # Check WebView2 runtime
    if not check_webview2():
        show_webview2_error()
        sys.exit(1)

    # Windows: 尝试启用 localhost 回环豁免（解决「网站无法访问」）
    if sys.platform == "win32":
        ensure_loopback_exemption()

    # Fix PyInstaller --windowed mode - 创建日志文件
    log_file = None
    if getattr(sys, "frozen", False):
        log_dir = Path.home() / ".mechforge" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "mechforge.log"
        # 追加模式打开日志文件
        file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "[%(asctime)s] %(levelname)s  %(name)s — %(message)s", datefmt="%H:%M:%S"
            )
        )
        logger.addHandler(file_handler)
        # 获取 GUI_DIR 用于日志
        gui_dir = Path(getattr(sys, "_MEIPASS", GUI_DIR))
        logger.info(f"日志文件: {log_file}")
        logger.info(f"GUI_DIR: {gui_dir}")
        logger.info(f"_MEIPASS: {getattr(sys, '_MEIPASS', 'Not set')}")

    parser = argparse.ArgumentParser(description="MechForge AI Desktop")
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help=f"后端起始端口（默认 {DEFAULT_PORT}）"
    )
    parser.add_argument("--debug", action="store_true", help="开启 DevTools 调试模式")
    args = parser.parse_args(argv)

    try:
        MechForgeApp(port=args.port, debug=args.debug).run()
    except ImportError as e:
        logger.error(f"缺少依赖：{e}")
        logger.error("请运行：pip install pywebview fastapi uvicorn")
        if log_file:
            print(f"错误日志已保存到: {log_file}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("用户中断，退出")
    except Exception:
        logger.exception("启动失败")
        if log_file:
            print(f"错误日志已保存到: {log_file}", file=sys.stderr)
        input("\n按回车键退出...")  # 让用户看到错误信息
        sys.exit(1)


if __name__ == "__main__":
    main()
