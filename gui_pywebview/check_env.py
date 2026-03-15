#!/usr/bin/env python3
"""
MechForge AI - 环境检查脚本
检查Python环境和依赖是否满足要求
"""

import sys
import subprocess
from pathlib import Path


def print_header(text: str) -> None:
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def print_ok(text: str) -> None:
    """打印成功信息"""
    print(f"  ✓ {text}")


def print_error(text: str) -> None:
    """打印错误信息"""
    print(f"  ✗ {text}")


def print_warning(text: str) -> None:
    """打印警告信息"""
    print(f"  ⚠ {text}")


def check_python_version() -> bool:
    """检查Python版本"""
    print_header("Python版本检查")
    
    version = sys.version_info
    current = f"{version.major}.{version.minor}.{version.micro}"
    required = (3, 10)
    
    print(f"  当前版本: {current}")
    print(f"  要求版本: >= 3.10")
    
    if version >= required:
        print_ok(f"Python版本满足要求 ({current})")
        return True
    else:
        print_error(f"Python版本过低 ({current})，需要 >= 3.10")
        return False


def check_virtual_env() -> bool:
    """检查虚拟环境"""
    print_header("虚拟环境检查")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_ok("当前在虚拟环境中运行")
        print(f"  虚拟环境路径: {sys.prefix}")
        return True
    else:
        print_warning("当前不在虚拟环境中运行")
        print("  建议: 运行 setup_env.bat (Windows) 或 ./setup_env.sh (Linux/Mac)")
        return False


def check_module(module_name: str, optional: bool = False) -> bool:
    """检查模块是否安装"""
    try:
        __import__(module_name)
        if optional:
            print_ok(f"{module_name} (可选)")
        else:
            print_ok(f"{module_name}")
        return True
    except ImportError:
        if optional:
            print_warning(f"{module_name} (可选) - 未安装")
        else:
            print_error(f"{module_name} - 未安装")
        return False


def check_core_modules() -> bool:
    """检查核心模块"""
    print_header("核心模块检查")
    
    modules = [
        ("pyyaml", False),
        ("rich", False),
        ("requests", False),
        ("pydantic", False),
    ]
    
    all_ok = True
    for module, optional in modules:
        if not check_module(module, optional):
            all_ok = False
    
    return all_ok


def check_mechforge_modules() -> bool:
    """检查MechForge模块"""
    print_header("MechForge模块检查")
    
    modules = [
        "mechforge_core",
        "mechforge_ai",
        "mechforge_knowledge",
        "mechforge_work",
        "mechforge_web",
        "mechforge_gui_ai",
    ]
    
    all_ok = True
    for module in modules:
        if not check_module(module):
            all_ok = False
    
    return all_ok


def check_optional_modules() -> bool:
    """检查可选模块"""
    print_header("可选模块检查")
    
    modules = [
        ("chromadb", "RAG支持"),
        ("sentence_transformers", "嵌入模型"),
        ("fastapi", "Web服务"),
        ("PySide6", "GUI应用"),
        ("gmsh", "CAE网格"),
        ("pyvista", "CAE可视化"),
        ("llama_cpp", "本地GGUF模型"),
    ]
    
    for module, description in modules:
        check_module(module, optional=True)
    
    return True


def check_commands() -> bool:
    """检查可用命令"""
    print_header("可用命令检查")
    
    commands = [
        "mechforge",
        "mechforge-k",
        "mechforge-work",
        "mechforge-web",
        "mechforge-gui",
        "mechforge-model",
    ]
    
    all_ok = True
    for cmd in commands:
        try:
            result = subprocess.run(
                [cmd, "--help"],
                capture_output=True,
                timeout=5,
                check=False,
            )
            if result.returncode == 0:
                print_ok(f"{cmd}")
            else:
                print_error(f"{cmd} - 命令异常")
                all_ok = False
        except FileNotFoundError:
            print_error(f"{cmd} - 未找到")
            all_ok = False
        except subprocess.TimeoutExpired:
            print_warning(f"{cmd} - 超时")
    
    return all_ok


def check_config() -> bool:
    """检查配置文件"""
    print_header("配置文件检查")
    
    config_files = [
        "config.yaml",
        "pyproject.toml",
    ]
    
    all_ok = True
    for file in config_files:
        path = Path(file)
        if path.exists():
            print_ok(f"{file}")
        else:
            print_warning(f"{file} - 不存在")
    
    return all_ok


def main() -> int:
    """主函数"""
    print("\n" + "=" * 60)
    print(" MechForge AI - 环境检查")
    print("=" * 60)
    
    checks = [
        ("Python版本", check_python_version),
        ("虚拟环境", check_virtual_env),
        ("核心模块", check_core_modules),
        ("MechForge模块", check_mechforge_modules),
        ("可选模块", check_optional_modules),
        ("可用命令", check_commands),
        ("配置文件", check_config),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"检查失败: {e}")
            results.append((name, False))
    
    # 总结
    print_header("检查总结")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status} - {name}")
    
    print(f"\n  总计: {passed}/{total} 项通过")
    
    if passed == total:
        print("\n  🎉 环境检查全部通过！")
        return 0
    elif passed >= total * 0.7:
        print("\n  ⚠ 环境基本可用，但部分功能受限")
        return 0
    else:
        print("\n  ✗ 环境检查未通过，请修复上述问题")
        print("\n  建议:")
        print("    1. 运行 setup_env.bat (Windows) 或 ./setup_env.sh (Linux/Mac)")
        print("    2. 确保Python版本 >= 3.10")
        print("    3. 检查网络连接（安装依赖需要）")
        return 1


if __name__ == "__main__":
    sys.exit(main())
