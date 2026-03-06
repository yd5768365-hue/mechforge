"""
配置模块单元测试
"""

import pytest
import yaml

from mechforge_core.config import (
    MechForgeConfig,
    ProviderConfig,
    get_config,
    save_config,
)


class TestProviderConfig:
    """测试 Provider 配置"""

    def test_default_provider(self):
        """测试默认 Provider"""
        config = ProviderConfig()
        assert config.default == "ollama"

    def test_openai_config_env(self, monkeypatch):
        """测试 OpenAI 配置从环境变量读取"""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key-123")
        config = MechForgeConfig()
        assert config.provider.openai.api_key == "test-key-123"

    def test_anthropic_config_env(self, monkeypatch):
        """测试 Anthropic 配置从环境变量读取"""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-456")
        config = MechForgeConfig()
        assert config.provider.anthropic.api_key == "test-key-456"


class TestMechForgeConfig:
    """测试主配置类"""

    def test_default_values(self):
        """测试默认值"""
        config = MechForgeConfig()
        assert config.provider.default == "ollama"
        assert config.knowledge.rag.enabled is False
        assert config.ui.theme == "dark"
        assert config.chat.temperature == 0.7

    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效的温度值
        config = MechForgeConfig(chat={"temperature": 0.5})
        assert config.chat.temperature == 0.5

        # 测试无效的温度值会被 Pydantic 捕获
        with pytest.raises(ValueError):
            MechForgeConfig(chat={"temperature": 3.0})  # 超出范围

    def test_env_overrides(self, monkeypatch):
        """测试环境变量覆盖"""
        monkeypatch.setenv("OLLAMA_URL", "http://test:11434")
        monkeypatch.setenv("OLLAMA_MODEL", "test-model")
        monkeypatch.setenv("MECHFORGE_RAG", "true")

        config = MechForgeConfig()
        assert config.provider.ollama.url == "http://test:11434"
        assert config.provider.ollama.model == "test-model"
        assert config.knowledge.rag.enabled is True


class TestConfigFileOperations:
    """测试配置文件操作"""

    def test_save_and_load(self, temp_dir):
        """测试保存和加载配置"""
        config = MechForgeConfig(
            provider=ProviderConfig(default="openai"),
            chat={"temperature": 0.8},
        )

        config_file = temp_dir / "test_config.yaml"
        save_config(config, config_file)

        assert config_file.exists()

        loaded = MechForgeConfig.from_file(config_file)
        assert loaded.provider.default == "openai"
        assert loaded.chat.temperature == 0.8

    def test_load_nonexistent_file(self):
        """测试加载不存在的文件返回默认配置"""
        config = MechForgeConfig.from_file("/nonexistent/config.yaml")
        assert config.provider.default == "ollama"


class TestGetConfig:
    """测试 get_config 函数"""

    def test_singleton(self, temp_dir):
        """测试配置单例"""
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"provider": {"default": "anthropic"}}, f)

        config1 = get_config(config_file)
        config2 = get_config(config_file)

        assert config1 is config2

    def test_force_reload(self, temp_dir):
        """测试强制重载"""
        config_file = temp_dir / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump({"provider": {"default": "ollama"}}, f)

        config1 = get_config(config_file)

        # 修改文件
        with open(config_file, "w") as f:
            yaml.dump({"provider": {"default": "openai"}}, f)

        config2 = get_config(config_file, force_reload=True)

        assert config1 is not config2
        assert config2.provider.default == "openai"
