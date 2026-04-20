"""Activity log - timestamped event messages."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPlainTextEdit, QLabel,
)
from PySide6.QtCore import Qt


class ActivityLog(QWidget):
    """Real-time activity log."""
    
    LEVEL_COLORS = {
        'info': '#8be9fd',
        'success': '#50fa7b',
        'warning': '#f1fa8c',
        'error': '#ff5555',
    }
    
    LEVEL_PREFIXES = {
        'info': 'ℹ',
        'success': '✓',
        'warning': '⚠',
        'error': '✗',
    }
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Activity Log")
        header.setStyleSheet("font-size: 13px; font-weight: bold; padding: 8px;")
        layout.addWidget(header)
        
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(1000)
        self.log_view.setStyleSheet("""
            QPlainTextEdit {
                border: none;
                background-color: #282a36;
                color: #f8f8f2;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        
        layout.addWidget(self.log_view)
    
    def append_log(self, agent_name: str, message: str, level: str = 'info'):
        """Append a log entry."""
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = self.LEVEL_PREFIXES.get(level, 'ℹ')
        color = self.LEVEL_COLORS.get(level, '#8be9fd')
        
        line = f"[{timestamp}] {prefix} {agent_name}: {message}"
        
        self.log_view.appendHtml(
            f'<span style="color: #6272a4;">[{timestamp}]</span> '
            f'<span style="color: {color};">{prefix}</span> '
            f'<span style="color: #f8f8f2;">{agent_name}:</span> '
            f'<span style="color: #bd93f9;">{message}</span>'
        )
    
    def clear(self):
        """Clear the log."""
        self.log_view.clear()