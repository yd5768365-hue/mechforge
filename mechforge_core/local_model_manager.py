"""
本地模型管理器

统一管理 Ollama 和 GGUF 本地模型，提供一致的接口。

功能:
- 自动检测可用模型
- 统一模型选择界面
- 自动启动/停止模型服务
- 模型下载管理
"""

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from mechforge_core.config import get_config


@dataclass
class LocalModel:
    """本地模型信息"""

    name: str
    provider: str  # "ollama" or "gguf"
    path: str | None = None  # GGUF 文件路径
    size: int = 0  # 字节
    modified_at: str = ""
    url: str = ""  # 服务地址
    loaded: bool = False


class LocalModelManager:
    """本地模型管理器"""

    def __init__(self):
        self.config = get_config()
        self.ollama_url = self.config.provider.ollama.url
        self.gguf_server_url = "http://127.0.0.1:11435"  # GGUF 服务器默认地址
        self.models: dict[str, LocalModel] = {}

    def scan_models(self) -> list[LocalModel]:
        """扫描所有可用模型"""
        self.models = {}

        # 扫描 Ollama 模型
        self._scan_ollama()

        # 扫描 GGUF 模型
        self._scan_gguf()

        return list(self.models.values())

    def _scan_ollama(self):
        """扫描 Ollama 模型"""
        try:
            resp = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for model in data.get("models", []):
                    name = model.get("name", "")
                    self.models[f"ollama:{name}"] = LocalModel(
                        name=name,
                        provider="ollama",
                        size=model.get("size", 0),
                        modified_at=model.get("modified_at", ""),
                        url=self.ollama_url,
                        loaded=True,
                    )
        except Exception as e:
            print(f"扫描 Ollama 模型失败: {e}")

    def _scan_gguf(self):
        """扫描 GGUF 模型"""
        model_dir = Path(self.config.provider.local.model_dir)

        if not model_dir.exists():
            return

        for gguf_file in model_dir.glob("*.gguf"):
            name = gguf_file.stem
            stat = gguf_file.stat()

            # 检查是否有对应的 GGUF 服务器在运行
            url = self.gguf_server_url
            loaded = self._check_gguf_server(url, name)

            self.models[f"gguf:{name}"] = LocalModel(
                name=name,
                provider="gguf",
                path=str(gguf_file),
                size=stat.st_size,
                modified_at=time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stat.st_mtime)),
                url=url,
                loaded=loaded,
            )

    def _check_gguf_server(self, url: str, model_name: str) -> bool:
        """检查 GGUF 服务器是否运行并加载了指定模型"""
        try:
            resp = requests.get(f"{url}/health", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("model") == model_name
        except Exception:
            pass
        return False

    def get_model(self, model_id: str) -> LocalModel | None:
        """获取模型信息"""
        # 支持多种格式: "ollama:qwen2.5", "gguf:model", "qwen2.5"
        if model_id in self.models:
            return self.models[model_id]

        # 尝试自动添加前缀
        for prefix in ["ollama:", "gguf:"]:
            if f"{prefix}{model_id}" in self.models:
                return self.models[f"{prefix}{model_id}"]

        return None

    def start_gguf_server(self, model_name: str) -> bool:
        """启动 GGUF 模型服务器"""
        model = self.get_model(f"gguf:{model_name}")
        if not model:
            print(f"错误: 未找到 GGUF 模型: {model_name}")
            return False

        if model.loaded:
            print(f"GGUF 服务器已在运行: {model_name}")
            return True

        print(f"正在启动 GGUF 服务器: {model_name}")

        try:
            # 在新进程中启动服务器
            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "mechforge_core.gguf_server",
                    "--model",
                    model.path,
                    "--port",
                    "11435",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # 等待服务器启动
            for _ in range(30):  # 最多等待 30 秒
                time.sleep(1)
                if self._check_gguf_server(self.gguf_server_url, model_name):
                    print("✓ GGUF 服务器启动成功")
                    model.loaded = True
                    return True

            print("错误: GGUF 服务器启动超时")
            return False

        except Exception as e:
            print(f"错误: 启动 GGUF 服务器失败: {e}")
            return False

    def stop_gguf_server(self) -> bool:
        """停止 GGUF 服务器"""
        try:
            # 发送关机请求
            requests.post(f"{self.gguf_server_url}/shutdown", timeout=5)
            return True
        except Exception:
            return False

    def select_model_interactive(self) -> str | None:
        """交互式选择模型"""
        models = self.scan_models()

        if not models:
            print("未找到任何本地模型")
            print("\n建议:")
            print("  1. 安装 Ollama: curl -fsSL https://ollama.com/install.sh | sh")
            print("  2. 下载模型: ollama pull qwen2.5:1.5b")
            print("  3. 或将 GGUF 文件放到 ./models/ 目录")
            return None

        print("\n可用模型:")
        print("-" * 60)

        for i, model in enumerate(models, 1):
            provider_icon = "🦙" if model.provider == "ollama" else "📦"
            status = "✓" if model.loaded else "○"
            size_mb = model.size / (1024 * 1024)

            print(f"{i}. {provider_icon} [{status}] {model.name}")
            print(f"   提供商: {model.provider.upper()}")
            print(f"   大小: {size_mb:.1f} MB")
            print()

        try:
            choice = input("选择模型编号 (或按 Enter 取消): ").strip()
            if not choice:
                return None

            idx = int(choice) - 1
            if 0 <= idx < len(models):
                selected = models[idx]

                # 如果是 GGUF 且未加载，先启动服务器
                if (
                    selected.provider == "gguf"
                    and not selected.loaded
                    and not self.start_gguf_server(selected.name)
                ):
                    return None

                return f"{selected.provider}:{selected.name}"

        except (ValueError, IndexError):
            print("无效选择")

        return None

    def get_model_url(self, model_id: str) -> str | None:
        """获取模型的 API 地址"""
        model = self.get_model(model_id)
        if not model:
            return None
        return model.url

    def get_model_for_config(self, model_id: str) -> tuple[str, str]:
        """
        获取模型配置

        Returns:
            (provider_type, url)
            provider_type: "ollama" or "local" (GGUF)
        """
        model = self.get_model(model_id)
        if not model:
            return "ollama", self.ollama_url

        if model.provider == "ollama":
            return "ollama", model.url
        else:
            # GGUF 作为 local provider，但使用 HTTP API
            return "local", model.url


def main():
    """测试模型管理器"""
    print("🦙 本地模型管理器\n")

    manager = LocalModelManager()
    models = manager.scan_models()

    print(f"找到 {len(models)} 个模型:\n")

    for model in models:
        print(f"  {'🦙' if model.provider == 'ollama' else '📦'} {model.name}")
        print(f"     提供商: {model.provider}")
        print(f"     大小: {model.size / 1024 / 1024:.1f} MB")
        print(f"     状态: {'运行中' if model.loaded else '未加载'}")
        print()

    # 交互式选择
    selected = manager.select_model_interactive()
    if selected:
        print(f"\n已选择: {selected}")
        provider, url = manager.get_model_for_config(selected)
        print(f"提供商: {provider}")
        print(f"API 地址: {url}")


if __name__ == "__main__":
    import sys

    main()
