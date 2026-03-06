"""
GGUF 模型服务器

提供类似 Ollama 的 HTTP API 服务，让本地 GGUF 模型可以通过网络访问。

用法:
    python -m mechforge_core.gguf_server --model ./models/qwen2.5-1.5b.gguf

API 端点:
    GET  /api/tags          - 列出可用模型
    POST /api/generate      - 生成文本（非流式）
    POST /api/chat          - 聊天（支持流式）
    GET  /health            - 健康检查
"""

import argparse
import json
import sys
import time
from collections.abc import Generator
from pathlib import Path

try:
    from llama_cpp import Llama
except ImportError:
    print("错误: 需要安装 llama-cpp-python")
    print("pip install llama-cpp-python")
    sys.exit(1)


class GGUFModelServer:
    """GGUF 模型服务器"""

    def __init__(
        self,
        model_path: str,
        host: str = "127.0.0.1",
        port: int = 11435,  # 默认用 11435，避免和 Ollama 冲突
        n_ctx: int = 2048,
        n_gpu_layers: int = 0,
    ):
        self.model_path = Path(model_path)
        self.host = host
        self.port = port
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers

        self.model: Llama | None = None
        self.model_info = {
            "name": self.model_path.stem,
            "path": str(self.model_path),
            "size": self.model_path.stat().st_size if self.model_path.exists() else 0,
            "loaded": False,
        }

    def load_model(self) -> bool:
        """加载模型"""
        if not self.model_path.exists():
            print(f"错误: 模型文件不存在: {self.model_path}")
            return False

        print(f"正在加载模型: {self.model_path.name}")
        print(f"  上下文长度: {self.n_ctx}")
        print(f"  GPU 层数: {self.n_gpu_layers}")

        try:
            self.model = Llama(
                model_path=str(self.model_path),
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False,
            )
            self.model_info["loaded"] = True
            print("✓ 模型加载成功")
            return True
        except Exception as e:
            print(f"错误: 模型加载失败: {e}")
            return False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Generator[str, None, None]:
        """生成文本"""
        if not self.model:
            raise RuntimeError("模型未加载")

        if stream:
            # 流式生成
            for chunk in self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            ):
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    text = chunk["choices"][0].get("text", "")
                    if text:
                        yield text
        else:
            # 非流式生成
            output = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
            )
            if "choices" in output and len(output["choices"]) > 0:
                yield output["choices"][0].get("text", "")

    def chat(
        self,
        messages: list[dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> Generator[str, None, None]:
        """聊天生成"""
        if not self.model:
            raise RuntimeError("模型未加载")

        if stream:
            for chunk in self.model.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            ):
                if "choices" in chunk and len(chunk["choices"]) > 0:
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
        else:
            output = self.model.create_chat_completion(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False,
            )
            if "choices" in output and len(output["choices"]) > 0:
                message = output["choices"][0].get("message", {})
                yield message.get("content", "")

    def run_http_server(self):
        """运行 HTTP 服务器"""
        try:
            from flask import Flask, Response, jsonify, request, stream_with_context
        except ImportError:
            print("错误: 需要安装 Flask")
            print("pip install flask")
            sys.exit(1)

        app = Flask(__name__)

        @app.route("/api/tags", methods=["GET"])
        def list_models():
            """列出可用模型"""
            return jsonify(
                {
                    "models": [
                        {
                            "name": self.model_info["name"],
                            "modified_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                            "size": self.model_info["size"],
                        }
                    ]
                }
            )

        @app.route("/api/generate", methods=["POST"])
        def generate():
            """生成文本"""
            data = request.json
            prompt = data.get("prompt", "")
            stream = data.get("stream", False)
            max_tokens = data.get("max_tokens", 2048)
            temperature = data.get("temperature", 0.7)

            if not self.model_info["loaded"]:
                return jsonify({"error": "模型未加载"}), 503

            if stream:

                def generate_stream():
                    for chunk in self.generate(prompt, max_tokens, temperature, stream=True):
                        yield json.dumps({"response": chunk}) + "\n"

                return Response(
                    stream_with_context(generate_stream()),
                    mimetype="application/x-ndjson",
                )
            else:
                response_text = ""
                for chunk in self.generate(prompt, max_tokens, temperature, stream=False):
                    response_text += chunk

                return jsonify(
                    {
                        "response": response_text,
                        "done": True,
                    }
                )

        @app.route("/api/chat", methods=["POST"])
        def chat():
            """聊天"""
            data = request.json
            messages = data.get("messages", [])
            stream = data.get("stream", False)
            max_tokens = data.get("max_tokens", 2048)
            temperature = data.get("temperature", 0.7)

            if not self.model_info["loaded"]:
                return jsonify({"error": "模型未加载"}), 503

            if stream:

                def chat_stream():
                    for chunk in self.chat(messages, max_tokens, temperature, stream=True):
                        yield (
                            json.dumps({"message": {"role": "assistant", "content": chunk}}) + "\n"
                        )

                    # 发送完成标记
                    yield json.dumps({"done": True}) + "\n"

                return Response(
                    stream_with_context(chat_stream()),
                    mimetype="application/x-ndjson",
                )
            else:
                response_text = ""
                for chunk in self.chat(messages, max_tokens, temperature, stream=False):
                    response_text += chunk

                return jsonify(
                    {
                        "message": {
                            "role": "assistant",
                            "content": response_text,
                        },
                        "done": True,
                    }
                )

        @app.route("/health", methods=["GET"])
        def health():
            """健康检查"""
            return jsonify(
                {
                    "status": "healthy" if self.model_info["loaded"] else "loading",
                    "model": self.model_info["name"],
                }
            )

        print("\n🚀 GGUF 模型服务器启动")
        print(f"   模型: {self.model_info['name']}")
        print(f"   地址: http://{self.host}:{self.port}")
        print(f"   API 文档: http://{self.host}:{self.port}/health\n")

        app.run(host=self.host, port=self.port, threaded=True)


def main():
    parser = argparse.ArgumentParser(description="GGUF 模型服务器")
    parser.add_argument("--model", "-m", required=True, help="GGUF 模型文件路径")
    parser.add_argument("--host", "-H", default="127.0.0.1", help="服务器地址 (默认: 127.0.0.1)")
    parser.add_argument("--port", "-p", type=int, default=11435, help="服务器端口 (默认: 11435)")
    parser.add_argument("--ctx", "-c", type=int, default=2048, help="上下文长度 (默认: 2048)")
    parser.add_argument(
        "--gpu-layers", "-g", type=int, default=0, help="GPU 层数 (默认: 0, CPU only)"
    )

    args = parser.parse_args()

    server = GGUFModelServer(
        model_path=args.model,
        host=args.host,
        port=args.port,
        n_ctx=args.ctx,
        n_gpu_layers=args.gpu_layers,
    )

    if server.load_model():
        server.run_http_server()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
