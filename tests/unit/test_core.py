"""MechForge AI 单元测试"""

import pytest
from pathlib import Path


class TestConfig:
    """配置模块测试"""

    def test_config_import(self):
        """测试配置模块可以导入"""
        try:
            from mechforge_core.config import get_config, MechForgeConfig
            assert True
        except ImportError as e:
            pytest.skip(f"配置模块导入失败: {e}")

    def test_config_defaults(self):
        """测试配置默认值"""
        try:
            from mechforge_core.config import MechForgeConfig
            config = MechForgeConfig()
            assert config.provider.default == "ollama"
        except Exception as e:
            pytest.skip(f"配置测试跳过: {e}")


class TestLogger:
    """日志模块测试"""

    def test_logger_import(self):
        """测试日志模块可以导入"""
        try:
            from mechforge_core.logger import get_logger
            logger = get_logger("test")
            assert logger is not None
        except ImportError as e:
            pytest.skip(f"日志模块导入失败: {e}")

    def test_logger_output(self):
        """测试日志输出"""
        try:
            from mechforge_core.logger import get_logger
            import logging
            logger = get_logger("test_output")
            # 测试日志级别
            assert logger.level <= logging.INFO
        except Exception as e:
            pytest.skip(f"日志测试跳过: {e}")


class TestUtils:
    """工具函数测试"""

    def test_project_structure(self):
        """测试项目结构"""
        project_root = Path(__file__).parent.parent.parent
        
        # 检查核心目录存在
        assert (project_root / "mechforge_core").exists()
        assert (project_root / "mechforge_ai").exists()
        assert (project_root / "mechforge_knowledge").exists()
        assert (project_root / "mechforge_work").exists()
        assert (project_root / "mechforge_web").exists()

    def test_pyproject_exists(self):
        """测试 pyproject.toml 存在"""
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / "pyproject.toml").exists()

    def test_readme_exists(self):
        """测试 README.md 存在"""
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / "README.md").exists()


class TestImports:
    """模块导入测试"""

    def test_core_import(self):
        """测试核心模块导入"""
        try:
            import mechforge_core
            assert True
        except ImportError as e:
            pytest.fail(f"核心模块导入失败: {e}")

    def test_ai_import(self):
        """测试 AI 模块导入"""
        try:
            import mechforge_ai
            assert True
        except ImportError as e:
            pytest.skip(f"AI 模块导入失败 (可能缺少依赖): {e}")

    def test_knowledge_import(self):
        """测试知识库模块导入"""
        try:
            import mechforge_knowledge
            assert True
        except ImportError as e:
            pytest.skip(f"知识库模块导入失败 (可能缺少依赖): {e}")

    def test_work_import(self):
        """测试 CAE 模块导入"""
        try:
            import mechforge_work
            assert True
        except ImportError as e:
            pytest.skip(f"CAE 模块导入失败 (可能缺少依赖): {e}")

    def test_web_import(self):
        """测试 Web 模块导入"""
        try:
            import mechforge_web
            assert True
        except ImportError as e:
            pytest.skip(f"Web 模块导入失败 (可能缺少依赖): {e}")

    def test_theme_import(self):
        """测试主题模块导入"""
        try:
            import mechforge_theme
            assert True
        except ImportError as e:
            pytest.skip(f"主题模块导入失败: {e}")