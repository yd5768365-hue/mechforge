"""
Pytest 配置和共享夹具
"""

import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_config(temp_dir):
    """创建测试配置"""
    config_data = {
        "provider": {
            "default": "ollama",
            "ollama": {
                "url": "http://localhost:11434",
                "model": "test-model",
                "auto_start": False,
            },
        },
        "knowledge": {
            "path": str(temp_dir / "knowledge"),
            "rag": {
                "enabled": True,
                "top_k": 3,
            },
        },
        "ui": {
            "theme": "dark",
            "color": False,
        },
    }

    config_file = temp_dir / "config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    return config_file


@pytest.fixture
def sample_knowledge_base(temp_dir):
    """创建示例知识库"""
    kb_dir = temp_dir / "knowledge"
    kb_dir.mkdir()

    # 创建测试文档
    (kb_dir / "bearings.md").write_text(
        """# 轴承手册

## 深沟球轴承 6205

- 内径: 25mm
- 外径: 52mm
- 宽度: 15mm
- 额定动载荷: 14.0 kN
- 额定静载荷: 7.85 kN

## 深沟球轴承 6206

- 内径: 30mm
- 外径: 62mm
- 宽度: 16mm
- 额定动载荷: 19.5 kN
- 额定静载荷: 11.3 kN
""",
        encoding="utf-8",
    )

    (kb_dir / "bolts.md").write_text(
        """# 螺栓标准

## GB/T 5782 六角头螺栓

### M8×20
- 螺纹直径: 8mm
- 长度: 20mm
- 强度等级: 8.8
- 拧紧力矩: 25 N·m

### M10×30
- 螺纹直径: 10mm
- 长度: 30mm
- 强度等级: 8.8
- 拧紧力矩: 50 N·m
""",
        encoding="utf-8",
    )

    return kb_dir


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """每个测试后重置配置单例"""
    yield
    # 重置配置单例
    import mechforge_core.config as config_module

    config_module._default_config = None
