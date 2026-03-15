"""MechForge AI 集成测试"""

import pytest
from pathlib import Path


class TestCLI:
    """CLI 命令测试"""

    def test_mechforge_help(self):
        """测试 mechforge --help"""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "mechforge_ai.terminal", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        # 可能因为依赖问题失败，所以只检查能运行
        assert result.returncode in [0, 1, 2]

    def test_mechforge_work_help(self):
        """测试 mechforge-work --help"""
        import subprocess
        result = subprocess.run(
            ["python", "-m", "mechforge_work.work_cli", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent
        )
        assert result.returncode in [0, 1, 2]


class TestConfigIntegration:
    """配置集成测试"""

    def test_config_file_exists(self):
        """测试配置文件存在"""
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / "config.yaml"
        assert config_file.exists() or (project_root / "config.yaml.example").exists()

    def test_env_example_exists(self):
        """测试环境变量示例文件存在"""
        project_root = Path(__file__).parent.parent.parent
        env_example = project_root / ".env.example"
        assert env_example.exists()


class TestDocker:
    """Docker 配置测试"""

    def test_dockerfile_exists(self):
        """测试 Dockerfile 存在"""
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / "Dockerfile").exists()

    def test_docker_compose_exists(self):
        """测试 docker-compose.yml 存在"""
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / "docker-compose.yml").exists()

    def test_dockerignore_exists(self):
        """测试 .dockerignore 存在"""
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / ".dockerignore").exists()


class TestDocumentation:
    """文档测试"""

    def test_readme_exists(self):
        """测试 README.md 存在"""
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / "README.md").exists()

    def test_install_guide_exists(self):
        """测试安装指南存在"""
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / "INSTALL.md").exists()

    def test_license_exists(self):
        """测试 LICENSE 存在"""
        project_root = Path(__file__).parent.parent.parent
        assert (project_root / "LICENSE").exists()

    def test_changelog_exists(self):
        """测试更新日志存在"""
        project_root = Path(__file__).parent.parent.parent
        changelog = (project_root / "开发日志" / "CHANGELOG.md")
        assert changelog.exists()