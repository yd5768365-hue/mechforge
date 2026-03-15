"""
PyInstaller hook for llama-cpp-python
收集 llama-cpp-python 的动态库和依赖
"""
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

# 收集 llama-cpp-python 的所有文件（包括动态库）
datas, binaries, hiddenimports = collect_all("llama_cpp")

# 额外收集动态库
binaries += collect_dynamic_libs("llama_cpp")

# 隐藏导入
hiddenimports += [
    "llama_cpp",
    "llama_cpp.llama",
    "llama_cpp.llama_chat_format",
    "llama_cpp.llama_grammar",
    "llama_cpp.llama_types",
    "llama_cpp.llama_tokenizer",
    "llama_cpp.llama_cache",
]