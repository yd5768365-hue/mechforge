#!/usr/bin/env python3
"""
MechForge AI 模型下载脚本
自动下载推荐的 GGUF 模型
"""
import argparse
import sys
from pathlib import Path

# 推荐模型列表
RECOMMENDED_MODELS = {
    "qwen2.5-1.5b": {
        "name": "Qwen2.5-1.5B-Instruct (Q4_K_M)",
        "url": "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf",
        "size": "~1.1 GB",
        "description": "轻量级模型，适合 CPU 推理",
    },
    "qwen2.5-3b": {
        "name": "Qwen2.5-3B-Instruct (Q4_K_M)",
        "url": "https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF/resolve/main/qwen2.5-3b-instruct-q4_k_m.gguf",
        "size": "~2.0 GB",
        "description": "中等模型，平衡性能与速度",
    },
    "qwen2.5-7b": {
        "name": "Qwen2.5-7B-Instruct (Q4_K_M)",
        "url": "https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF/resolve/main/qwen2.5-7b-instruct-q4_k_m.gguf",
        "size": "~4.4 GB",
        "description": "大模型，需要 GPU 或大内存",
    },
    "llama-3.2-1b": {
        "name": "Llama-3.2-1B-Instruct (Q4_K_M)",
        "url": "https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF/resolve/main/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
        "size": "~0.8 GB",
        "description": "Meta Llama 轻量级模型",
    },
    "llama-3.2-3b": {
        "name": "Llama-3.2-3B-Instruct (Q4_K_M)",
        "url": "https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF/resolve/main/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
        "size": "~2.0 GB",
        "description": "Meta Llama 中等模型",
    },
}


def download_model(model_key: str, output_dir: Path) -> bool:
    """下载模型"""
    import requests

    if model_key not in RECOMMENDED_MODELS:
        print(f"未知模型: {model_key}")
        return False

    model = RECOMMENDED_MODELS[model_key]
    output_dir.mkdir(parents=True, exist_ok=True)

    # 从 URL 提取文件名
    filename = model["url"].split("/")[-1]
    output_path = output_dir / filename

    if output_path.exists():
        print(f"模型已存在: {output_path}")
        return True

    print(f"\n下载模型: {model['name']}")
    print(f"大小: {model['size']}")
    print(f"保存到: {output_path}")
    print(f"URL: {model['url']}")
    print("\n开始下载...")

    try:
        response = requests.get(model["url"], stream=True, timeout=30)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))
        downloaded = 0

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(
                            f"\r进度: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)",
                            end="",
                            flush=True,
                        )

        print(f"\n\n✓ 下载完成: {output_path}")
        return True

    except Exception as e:
        print(f"\n✗ 下载失败: {e}")
        if output_path.exists():
            output_path.unlink()
        return False


def list_models():
    """列出可用模型"""
    print("\n可用模型:")
    print("-" * 60)
    for key, model in RECOMMENDED_MODELS.items():
        print(f"\n  {key}:")
        print(f"    名称: {model['name']}")
        print(f"    大小: {model['size']}")
        print(f"    描述: {model['description']}")
    print("\n")


def main():
    parser = argparse.ArgumentParser(description="下载 GGUF 模型")
    parser.add_argument("model", nargs="?", help="模型名称 (如 qwen2.5-1.5b)")
    parser.add_argument(
        "-o",
        "--output",
        default="models",
        help="输出目录 (默认: models)",
    )
    parser.add_argument("-l", "--list", action="store_true", help="列出可用模型")

    args = parser.parse_args()

    if args.list:
        list_models()
        return 0

    if not args.model:
        print("用法: python download_model.py <模型名称>")
        print("示例: python download_model.py qwen2.5-1.5b")
        print("\n运行 'python download_model.py --list' 查看可用模型")
        return 1

    output_dir = Path(args.output)
    success = download_model(args.model, output_dir)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())