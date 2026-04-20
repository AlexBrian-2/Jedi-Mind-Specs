"""Project submission form - left panel."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QSpinBox,
    QPushButton, QGroupBox, QCheckBox, QScrollArea,
)
from PySide6.QtCore import Signal


class ProjectForm(QWidget):
    """Project configuration form."""
    
    run_started = Signal(dict)
    run_cancelled = Signal()
    
    PROJECT_TYPES = [
        ("web_app", "Web Application"),
        ("mobile_app", "Mobile Application"),
        ("desktop_app", "Desktop Application"),
        ("api_backend", "API / Backend Service"),
        ("cli_tool", "CLI Tool"),
        ("data_pipeline", "Data Pipeline"),
        ("ml_system", "ML / AI System"),
        ("other", "Other"),
    ]
    
    MODELS = [
        ("kilo/auto-free", "Kilo Auto Free (Recommended)"),
        ("openai/nvidia/llama-3.1-nemotron-super-49b-v1", "NVIDIA Nemotron 3 Super"),
        ("openai/qwen/qwen3-coder-32b", "Qwen3 Coder"),
        ("anthropic/claude-sonnet-4", "Claude Sonnet 4"),
    ]
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self._is_running = False
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the form UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        title = QLabel("Project Configuration")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        form = QFormLayout()
        form.setSpacing(10)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("My Awesome Project")
        self.name_input.setStyleSheet("padding: 8px; border-radius: 4px;")
        form.addRow("Project Name:", self.name_input)
        
        self.type_combo = QComboBox()
        for value, label in self.PROJECT_TYPES:
            self.type_combo.addItem(label, value)
        form.addRow("Project Type:", self.type_combo)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Describe your project in detail. Include the target audience, "
            "key features, technical requirements, and any specific constraints..."
        )
        self.description_input.setMinimumHeight(150)
        self.description_input.setStyleSheet("padding: 8px; border-radius: 4px;")
        form.addRow("Description:", self.description_input)
        
        layout.addLayout(form)
        
        self.advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout()
        
        self.model_combo = QComboBox()
        for value, label in self.MODELS:
            self.model_combo.addItem(label, value)
        advanced_layout.addRow("Model:", self.model_combo)
        
        self.max_review_spin = QSpinBox()
        self.max_review_spin.setRange(1, 5)
        self.max_review_spin.setValue(3)
        self.max_review_spin.setSuffix(" cycles")
        advanced_layout.addRow("Max Review Cycles:", self.max_review_spin)
        
        self.max_validation_spin = QSpinBox()
        self.max_validation_spin.setRange(1, 3)
        self.max_validation_spin.setValue(2)
        self.max_validation_spin.setSuffix(" cycles")
        advanced_layout.addRow("Max Validation Cycles:", self.max_validation_spin)
        
        self.delay_spin = QSpinBox()
        self.delay_spin.setRange(500, 5000)
        self.delay_spin.setValue(2000)
        self.delay_spin.setSuffix(" ms")
        self.delay_spin.setSingleStep(500)
        advanced_layout.addRow("Inter-call Delay:", self.delay_spin)
        
        self.advanced_group.setLayout(advanced_layout)
        layout.addWidget(self.advanced_group)
        
        layout.addStretch()
        
        button_layout = QVBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = QPushButton("Start Research Run")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #50fa7b;
                color: #282a36;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5ffb8f; }
            QPushButton:disabled { background-color: #44475a; color: #6272a4; }
        """)
        self.start_button.clicked.connect(self._on_start_clicked)
        button_layout.addWidget(self.start_button)
        
        self.cancel_button = QPushButton("Cancel Run")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                color: white;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #ff6e6e; }
        """)
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _on_start_clicked(self):
        """Handle start button click."""
        config = self.get_config()
        if self._validate_config(config):
            self._is_running = True
            self.start_button.setEnabled(False)
            self.cancel_button.setEnabled(True)
            self.run_started.emit(config)
    
    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self._is_running = False
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.run_cancelled.emit()
    
    def _validate_config(self, config: dict) -> bool:
        """Validate the configuration."""
        if not config.get('project_name', '').strip():
            return False
        if len(config.get('project_description', '').strip()) < 100:
            return False
        return True
    
    def get_config(self) -> dict:
        """Get the current configuration."""
        return {
            'project_name': self.name_input.text(),
            'project_type': self.type_combo.currentData(),
            'project_description': self.description_input.toPlainText(),
            'model': self.model_combo.currentData(),
            'max_review_cycles': self.max_review_spin.value(),
            'max_validation_cycles': self.max_validation_spin.value(),
            'inter_call_delay': self.delay_spin.value(),
        }
    
    def set_running(self, is_running: bool):
        """Set running state."""
        self._is_running = is_running
        self.start_button.setEnabled(not is_running)
        self.cancel_button.setEnabled(is_running)
        self.name_input.setEnabled(not is_running)
        self.type_combo.setEnabled(not is_running)
        self.description_input.setEnabled(not is_running)
    
    def reset(self):
        """Reset the form."""
        self.name_input.clear()
        self.type_combo.setCurrentIndex(0)
        self.description_input.clear()
        self._is_running = False
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)