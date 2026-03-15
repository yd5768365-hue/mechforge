"""
对话框组件
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from mechforge_gui_ai.theme import THEME, get_stylesheet

if TYPE_CHECKING:
    from mechforge_ai.llm_client import LLMClient


class ModelConfigDialog(QDialog):
    """模型配置对话框"""
    
    def __init__(self, config, llm_client: "LLMClient", parent=None):
        super().__init__(parent)
        self.config = config
        self.llm_client = llm_client
        
        self.setWindowTitle("模型配置")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(get_stylesheet())
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标签页
        tabs = QTabWidget()
        
        # Provider 选择
        provider_tab = QWidget()
        provider_layout = QFormLayout(provider_tab)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["ollama", "openai", "anthropic", "local"])
        self.provider_combo.setCurrentText(self.config.provider.default)
        provider_layout.addRow("默认 Provider:", self.provider_combo)
        
        tabs.addTab(provider_tab, "Provider")
        
        # Ollama 配置
        ollama_tab = QWidget()
        ollama_layout = QFormLayout(ollama_tab)
        
        self.ollama_url = QLineEdit(self.config.provider.ollama.url)
        ollama_layout.addRow("Ollama 地址:", self.ollama_url)
        
        self.ollama_model = QLineEdit(self.config.provider.ollama.model)
        ollama_layout.addRow("默认模型:", self.ollama_model)
        
        tabs.addTab(ollama_tab, "Ollama")
        
        # OpenAI 配置
        openai_tab = QWidget()
        openai_layout = QFormLayout(openai_tab)
        
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.Password)
        if self.config.provider.openai.api_key:
            self.openai_key.setText(self.config.provider.openai.api_key)
        openai_layout.addRow("API Key:", self.openai_key)
        
        self.openai_model = QLineEdit(self.config.provider.openai.model)
        openai_layout.addRow("模型:", self.openai_model)
        
        tabs.addTab(openai_tab, "OpenAI")
        
        # Anthropic 配置
        anthropic_tab = QWidget()
        anthropic_layout = QFormLayout(anthropic_tab)
        
        self.anthropic_key = QLineEdit()
        self.anthropic_key.setEchoMode(QLineEdit.Password)
        if self.config.provider.anthropic.api_key:
            self.anthropic_key.setText(self.config.provider.anthropic.api_key)
        anthropic_layout.addRow("API Key:", self.anthropic_key)
        
        self.anthropic_model = QLineEdit(self.config.provider.anthropic.model)
        anthropic_layout.addRow("模型:", self.anthropic_model)
        
        tabs.addTab(anthropic_tab, "Anthropic")
        
        # 本地模型配置
        local_tab = QWidget()
        local_layout = QFormLayout(local_tab)
        
        self.local_model_dir = QLineEdit(self.config.provider.local.model_dir)
        local_layout.addRow("模型目录:", self.local_model_dir)
        
        self.local_llm_model = QLineEdit(self.config.provider.local.llm_model)
        local_layout.addRow("LLM 模型:", self.local_llm_model)
        
        self.local_n_ctx = QSpinBox()
        self.local_n_ctx.setRange(512, 32768)
        self.local_n_ctx.setValue(self.config.provider.local.n_ctx)
        local_layout.addRow("上下文长度:", self.local_n_ctx)
        
        self.local_n_gpu = QSpinBox()
        self.local_n_gpu.setRange(0, 100)
        self.local_n_gpu.setValue(self.config.provider.local.n_gpu_layers)
        local_layout.addRow("GPU 层数:", self.local_n_gpu)
        
        tabs.addTab(local_tab, "本地模型")
        
        layout.addWidget(tabs)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _on_accept(self):
        """确认"""
        from mechforge_core.config import save_config, reload_config
        import os
        
        # 更新配置
        self.config.provider.default = self.provider_combo.currentText()
        self.config.provider.ollama.url = self.ollama_url.text()
        self.config.provider.ollama.model = self.ollama_model.text()
        
        if self.openai_key.text():
            self.config.provider.openai.api_key = self.openai_key.text()
            os.environ["OPENAI_API_KEY"] = self.openai_key.text()
        self.config.provider.openai.model = self.openai_model.text()
        
        if self.anthropic_key.text():
            self.config.provider.anthropic.api_key = self.anthropic_key.text()
            os.environ["ANTHROPIC_API_KEY"] = self.anthropic_key.text()
        self.config.provider.anthropic.model = self.anthropic_model.text()
        
        self.config.provider.local.model_dir = self.local_model_dir.text()
        self.config.provider.local.llm_model = self.local_llm_model.text()
        self.config.provider.local.n_ctx = self.local_n_ctx.value()
        self.config.provider.local.n_gpu_layers = self.local_n_gpu.value()
        
        # 保存配置
        save_config(self.config)
        self.config = reload_config()
        
        # 更新 LLM 客户端
        if self.llm_client:
            self.llm_client._provider = None
        
        self.accept()


class RAGConfigDialog(QDialog):
    """RAG 配置对话框"""
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        
        self.setWindowTitle("RAG 配置")
        self.setMinimumSize(400, 300)
        self.setStyleSheet(get_stylesheet())
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QFormLayout(self)
        
        # RAG 开关
        from PySide6.QtWidgets import QCheckBox
        self.rag_enabled = QCheckBox()
        self.rag_enabled.setChecked(self.config.knowledge.rag.enabled)
        layout.addRow("启用 RAG:", self.rag_enabled)
        
        # 知识库路径
        self.kb_path = QLineEdit(self.config.knowledge.path)
        layout.addRow("知识库路径:", self.kb_path)
        
        # Top K
        self.top_k = QSpinBox()
        self.top_k.setRange(1, 20)
        self.top_k.setValue(self.config.knowledge.rag.top_k)
        layout.addRow("Top K:", self.top_k)
        
        # 嵌入模型
        self.embedding_model = QLineEdit(self.config.knowledge.rag.embedding_model)
        layout.addRow("嵌入模型:", self.embedding_model)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def _on_accept(self):
        """确认"""
        from mechforge_core.config import save_config, reload_config
        
        self.config.knowledge.rag.enabled = self.rag_enabled.isChecked()
        self.config.knowledge.path = self.kb_path.text()
        self.config.knowledge.rag.top_k = self.top_k.value()
        self.config.knowledge.rag.embedding_model = self.embedding_model.text()
        
        save_config(self.config)
        self.config = reload_config()
        
        self.accept()