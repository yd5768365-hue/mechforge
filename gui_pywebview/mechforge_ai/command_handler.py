"""
命令处理器模块 - 负责处理用户命令
"""

import os

from rich.console import Console

from mechforge_core.config import reload_config, save_config

console = Console()


class CommandHandler:
    """命令处理器"""

    def __init__(self, config):
        self.config = config

    def handle(self, command: str, terminal) -> bool:
        """
        处理命令
        返回 True 表示退出程序
        """
        cmd = command.lower()

        # RAG 命令
        if cmd.startswith("/rag"):
            self._handle_rag(terminal)
            return False

        # 帮助
        if cmd in ["/help", "/h"]:
            terminal.ui.print_command_help()
            return False

        # 状态
        if cmd == "/status":
            # 获取知识库路径（不触发 RAG 引擎加载）
            kb_path = None
            if terminal.rag_enabled:
                kb_path = terminal.rag_engine.knowledge_path
            else:
                from pathlib import Path

                config_path = Path(terminal.config.knowledge.path)
                if config_path.exists():
                    kb_path = config_path

            terminal.ui.print_dashboard(
                api_type=terminal.llm.get_api_type(),
                model_name=terminal.llm.get_current_model_name(),
                rag_enabled=terminal.rag_enabled,
                kb_path=kb_path,
                top_k=self.config.knowledge.rag.top_k,
                msg_count=len(terminal.conversation_history),
            )
            return False

        # 会话信息
        if cmd == "/info":
            # 获取知识库路径（不触发 RAG 引擎加载）
            kb_path = None
            if terminal.rag_enabled:
                kb_path = terminal.rag_engine.knowledge_path
            else:
                from pathlib import Path

                config_path = Path(terminal.config.knowledge.path)
                if config_path.exists():
                    kb_path = config_path

            terminal.ui.print_session_info(
                conversation_count=len(terminal.conversation_history),
                command_count=len(terminal.command_history),
                rag_enabled=terminal.rag_enabled,
                provider=self.config.get_active_provider(),
                kb_path=kb_path,
            )
            return False

        # 对话历史
        if cmd == "/history":
            terminal.ui.print_conversation_history(terminal.conversation_history)
            return False

        # 重新加载配置
        if cmd == "/reload":
            self._reload_config(terminal)
            return False

        # 清除对话
        if cmd == "/clear":
            terminal.conversation_history.clear()
            print("✓ 对话历史已清除")
            return False

        # 模型配置
        if cmd == "/model":
            self._configure_model(terminal)
            return False

        # 退出
        if cmd in ["/exit", "/quit", "/q"]:
            return True

        print(f"未知命令: {command}")
        return False

    def _handle_rag(self, terminal):
        """处理 RAG 命令"""
        # 检查知识库是否可用（延迟加载）
        if not terminal.rag_engine.is_available:
            print("✗ 未找到知识库")
            return

        # Toggle 切换
        terminal.rag_enabled = not terminal.rag_enabled
        if terminal.rag_enabled:
            print(f"✓ RAG 已启用，知识库: {terminal.rag_engine.knowledge_path}")
        else:
            print("✓ RAG 已禁用")

    def _reload_config(self, terminal):
        """重新加载配置"""
        terminal.config = reload_config()
        terminal.rag_enabled = terminal.config.knowledge.rag.enabled
        # 重置 RAG 引擎（延迟加载）
        terminal._rag_engine = None
        print("✓ 配置已重新加载")

        # 获取知识库路径（不触发 RAG 引擎加载）
        kb_path = None
        if terminal.rag_enabled:
            kb_path = terminal.rag_engine.knowledge_path
        else:
            from pathlib import Path

            config_path = Path(terminal.config.knowledge.path)
            if config_path.exists():
                kb_path = config_path

        terminal.ui.print_dashboard(
            api_type=terminal.llm.get_api_type(),
            model_name=terminal.llm.get_current_model_name(),
            rag_enabled=terminal.rag_enabled,
            kb_path=kb_path,
            top_k=self.config.knowledge.rag.top_k,
            msg_count=len(terminal.conversation_history),
        )

    def _configure_model(self, terminal):
        """配置 AI 模型"""
        print("""
+================================================================+
|           MechForge AI - 模型配置                           |
+================================================================+
|  1. OpenAI (GPT-4o, GPT-4o-mini, etc.)                   |
|  2. Anthropic (Claude-3.5, Claude-3, etc.)               |
|  3. Ollama (本地模型)                                     |
|  4. 本地 GGUF 模型                                        |
|  5. 设为默认 Provider                                     |
|  6. 查看当前配置                                           |
|  7. 测试连接                                               |
|  0. 退出                                                   |
+================================================================+
""")

        choice = console.input("[spring_green3]选择 [0-7]:[/spring_green3] ").strip()

        if choice == "0":
            return
        elif choice == "3":
            self._config_ollama(terminal)
        elif choice == "4":
            self._config_local(terminal)
        elif choice == "1":
            self._config_openai(terminal)
        elif choice == "2":
            self._config_anthropic(terminal)
        elif choice == "5":
            self._set_default_provider(terminal)
        elif choice == "6":
            self._show_config(terminal)
        elif choice == "7":
            self._test_connection(terminal)

    def _config_ollama(self, terminal):
        """配置 Ollama"""
        print("\n[Ollama 本地模型配置]")
        print(f"默认地址: {terminal.config.provider.ollama.url}\n")

        url = console.input("[spring_green3]输入 Ollama 地址 [默认]:[/spring_green3] ").strip()
        if url:
            terminal.config.provider.ollama.url = url

        print("测试连接中...")
        import requests

        try:
            resp = requests.get(f"{terminal.config.provider.ollama.url}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                if models:
                    self._save_config(
                        terminal, "ollama", url or terminal.config.provider.ollama.url
                    )
                    print("\n✓ Ollama 连接成功!")
                    print(f"  可用模型: {len(models)} 个")
                    for m in models[:5]:
                        print(f"    - {m.get('name', 'unknown')}")
                else:
                    print("\n✗ 未找到任何模型，请先下载模型")
                    print("  命令: ollama pull qwen2.5:1.5b")
            else:
                print(f"\n✗ 连接失败: {resp.status_code}")
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            print("\n请确保 Ollama 已启动: ollama serve")

    def _config_local(self, terminal):
        """配置本地 GGUF 模型"""
        print("\n[本地 GGUF 模型配置]")
        cfg = terminal.config.provider.local

        print(f"模型目录: {cfg.model_dir}")
        print(f"LLM 模型: {cfg.llm_model}")
        print(f"嵌入模型: {cfg.embedding_model}")
        print(f"上下文长度: {cfg.n_ctx}")
        print(f"GPU 层数: {cfg.n_gpu_layers}\n")

        print("1. 修改 LLM 模型文件名")
        print("2. 修改模型目录")
        print("3. 修改上下文长度")
        print("4. 修改 GPU 层数")
        print("0. 返回\n")

        choice = console.input("[spring_green3]选择 [0-4]:[/spring_green3] ").strip()

        if choice == "1":
            model = console.input(
                f"[spring_green3]输入 GGUF 模型文件名 [{cfg.llm_model}]:[/spring_green3] "
            ).strip()
            if model:
                cfg.llm_model = model
                self._save_config(terminal, "local", model, "llm_model")
                print(f"\n✓ LLM 模型已设置为: {model}")
        elif choice == "2":
            model_dir = console.input(
                f"[spring_green3]输入模型目录 [{cfg.model_dir}]:[/spring_green3] "
            ).strip()
            if model_dir:
                cfg.model_dir = model_dir
                self._save_config(terminal, "local", model_dir, "model_dir")
                print(f"\n✓ 模型目录已设置为: {model_dir}")
        elif choice == "3":
            n_ctx = console.input(
                f"[spring_green3]输入上下文长度 [{cfg.n_ctx}]:[/spring_green3] "
            ).strip()
            if n_ctx and n_ctx.isdigit():
                cfg.n_ctx = int(n_ctx)
                self._save_config(terminal, "local", int(n_ctx), "n_ctx")
                print(f"\n✓ 上下文长度已设置为: {n_ctx}")
        elif choice == "4":
            n_gpu = console.input(
                f"[spring_green3]输入 GPU 层数 (0=CPU) [{cfg.n_gpu_layers}]:[/spring_green3] "
            ).strip()
            if n_gpu and n_gpu.isdigit():
                cfg.n_gpu_layers = int(n_gpu)
                self._save_config(terminal, "local", int(n_gpu), "n_gpu_layers")
                print(f"\n✓ GPU 层数已设置为: {n_gpu}")

    def _set_default_provider(self, terminal):
        """设置默认 Provider"""
        print("\n[设置默认 Provider]")
        print("当前默认:", terminal.config.provider.default)
        print("可选: openai, anthropic, ollama, local\n")

        provider = (
            console.input("[spring_green3]输入默认 Provider [ollama]:[/spring_green3] ").strip()
            or "ollama"
        )
        if provider in ["openai", "anthropic", "ollama", "local"]:
            self._save_config(terminal, "default", provider)
            print(f"\n✓ 默认 Provider 已设置为: {provider}")
        else:
            print("\n✗ 无效的 Provider")

    def _config_openai(self, terminal):
        """配置 OpenAI"""
        api_key = console.input("[spring_green3]输入 OpenAI API Key:[/spring_green3] ").strip()
        if not api_key:
            print("取消")
            return

        print("测试连接中...")
        import requests

        try:
            resp = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                self._save_config(terminal, "openai", api_key)
                terminal.llm._api_type = "openai"
                print("\n✓ OpenAI 配置成功!")
            else:
                print(f"\n✗ 连接失败: {resp.status_code}")
        except Exception as e:
            print(f"\n✗ 错误: {e}")

    def _config_anthropic(self, terminal):
        """配置 Anthropic"""
        api_key = console.input("[spring_green3]输入 Anthropic API Key:[/spring_green3] ").strip()
        if not api_key:
            print("取消")
            return

        print("测试连接中...")
        import requests

        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": "hi"}],
                },
                timeout=10,
            )
            if resp.status_code == 200:
                self._save_config(terminal, "anthropic", api_key)
                terminal.llm._api_type = "anthropic"
                print("\n✓ Anthropic 配置成功!")
            else:
                print(f"\n✗ 连接失败: {resp.status_code}")
        except Exception as e:
            print(f"\n✗ 错误: {e}")

    def _show_config(self, terminal):
        """显示配置"""
        print("\n当前配置:")
        cfg = terminal.config.provider

        if cfg.openai.api_key:
            key = cfg.openai.api_key
            print(f"  OpenAI: {key[:8]}...{key[-4:]} (模型: {cfg.openai.model})")

        if cfg.anthropic.api_key:
            key = cfg.anthropic.api_key
            print(f"  Anthropic: {key[:8]}...{key[-4:]} (模型: {cfg.anthropic.model})")

        print(f"  Ollama: {cfg.ollama.url} (默认模型: {cfg.ollama.model})")
        print(f"  Local GGUF: {cfg.local.llm_model}")
        print(f"\n  默认 Provider: {cfg.default}")
        print(f"  当前激活: {terminal.config.get_active_provider()}")
        print()

    def _test_connection(self, terminal):
        """测试连接"""
        import requests

        cfg = terminal.config.provider

        # OpenAI
        if cfg.openai.api_key:
            try:
                resp = requests.get(
                    f"{cfg.openai.base_url}/models",
                    headers={"Authorization": f"Bearer {cfg.openai.api_key}"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    print("✓ OpenAI 连接正常")
            except Exception as e:
                print(f"✗ OpenAI 连接错误: {e}")

        # Anthropic
        if cfg.anthropic.api_key:
            try:
                resp = requests.post(
                    f"{cfg.anthropic.base_url}/v1/messages",
                    headers={
                        "x-api-key": cfg.anthropic.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": cfg.anthropic.model,
                        "max_tokens": 10,
                        "messages": [{"role": "user", "content": "hi"}],
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    print("✓ Anthropic 连接正常")
            except Exception as e:
                print(f"✗ Anthropic 连接错误: {e}")

        # Ollama
        try:
            resp = requests.get(f"{cfg.ollama.url}/api/tags", timeout=10)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                print(f"✓ Ollama 连接正常 ({len(models)} 个模型)")
        except Exception as e:
            print(f"✗ Ollama 连接错误: {e}")

    def _save_config(self, terminal, provider: str, value, field: str = None):
        """保存配置"""
        if provider == "openai":
            terminal.config.provider.openai.api_key = value
            os.environ["OPENAI_API_KEY"] = value
        elif provider == "anthropic":
            terminal.config.provider.anthropic.api_key = value
            os.environ["ANTHROPIC_API_KEY"] = value
        elif provider == "ollama":
            terminal.config.provider.ollama.url = value
        elif provider == "default":
            terminal.config.provider.default = value
        elif provider == "local":
            if field == "llm_model":
                terminal.config.provider.local.llm_model = value
            elif field == "model_dir":
                terminal.config.provider.local.model_dir = value
            elif field == "n_ctx":
                terminal.config.provider.local.n_ctx = value
            elif field == "n_gpu_layers":
                terminal.config.provider.local.n_gpu_layers = value

        save_config(terminal.config)
        terminal.config = reload_config()
