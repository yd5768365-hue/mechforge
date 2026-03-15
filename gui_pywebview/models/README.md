# GGUF 模型目录

此目录用于存放 GGUF 格式的本地模型文件。

## 下载模型

### 方法 1: 使用下载脚本（推荐）

```bash
# 查看可用模型
python download_model.py --list

# 下载模型
python download_model.py qwen2.5-1.5b
```

### 方法 2: 手动下载

从 HuggingFace 下载 GGUF 模型，放到此目录：

- **Qwen2.5-1.5B**: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
- **Qwen2.5-3B**: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF
- **Llama-3.2**: https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF

## 推荐模型

| 模型 | 大小 | 内存需求 | 适用场景 |
|------|------|----------|----------|
| Qwen2.5-1.5B-Q4_K_M | ~1.1 GB | 2 GB+ | CPU 推理，轻量级 |
| Qwen2.5-3B-Q4_K_M | ~2.0 GB | 4 GB+ | CPU/GPU，平衡型 |
| Qwen2.5-7B-Q4_K_M | ~4.4 GB | 8 GB+ | GPU 推荐，高性能 |

## 使用方法

1. 下载模型到此目录
2. 启动应用: `python desktop_app.py`
3. 在设置中选择 GGUF 模型