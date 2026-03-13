#!/usr/bin/env python3
"""
MechForge AI 安装脚本
自动检测环境并安装 llama-cpp-python（CPU/GPU 版本）
"""
import subprocess
import sys
import platform


def run_cmd(cmd: list[str]) -> bool:
    """运行命令"""
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr}")
        return False
    return True


def check_cuda() -> bool:
    """检查是否有 CUDA"""
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_llama_cpp() -> bool:
    """安装 llama-cpp-python"""
    print("\n" + "=" * 60)
    print("安装 llama-cpp-python")
    print("=" * 60)

    # 检测 CUDA
    has_cuda = check_cuda()
    system = platform.system()

    if has_cuda:
        print("✓ 检测到 NVIDIA GPU，安装 CUDA 版本...")
        # 使用预编译的 CUDA wheel
        cuda_url = "https://abetlen.github.io/llama-cpp-python/whl/cu121"
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "llama-cpp-python",
            "--extra-index-url",
            cuda_url,
        ]
    else:
        print("✓ 未检测到 NVIDIA GPU，安装 CPU 版本...")
        cmd = [sys.executable, "-m", "pip", "install", "llama-cpp-python"]

    return run_cmd(cmd)


def install_dependencies() -> bool:
    """安装所有依赖"""
    print("\n" + "=" * 60)
    print("安装项目依赖")
    print("=" * 60)

    # 安装基础依赖
    if not run_cmd([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]):
        return False

    # 安装 llama-cpp-python
    if not install_llama_cpp():
        return False

    return True


def verify_installation() -> bool:
    """验证安装"""
    print("\n" + "=" * 60)
    print("验证安装")
    print("=" * 60)

    try:
        import llama_cpp

        print(f"✓ llama-cpp-python 版本: {llama_cpp.__version__}")
    except ImportError as e:
        print(f"✗ llama-cpp-python 安装失败: {e}")
        return False

    try:
        import numpy

        print(f"✓ numpy 版本: {numpy.__version__}")
    except ImportError as e:
        print(f"✗ numpy 安装失败: {e}")
        return False

    return True


def main():
    print("=" * 60)
    print("MechForge AI 安装脚本")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"系统: {platform.system()} {platform.machine()}")

    # 安装依赖
    if not install_dependencies():
        print("\n✗ 安装失败")
        return 1

    # 验证
    if not verify_installation():
        print("\n✗ 验证失败")
        return 1

    print("\n" + "=" * 60)
    print("✓ 安装完成！")
    print("=" * 60)
    print("\n使用方法:")
    print("  1. 下载 GGUF 模型文件（如 qwen2.5-1.5b-instruct-q4_k_m.gguf）")
    print("  2. 将模型放到 models/ 目录")
    print("  3. 运行: python desktop_app.py")
    print("\n推荐模型下载地址:")
    print("  https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF")

    return 0


if __name__ == "__main__":
    sys.exit(main())