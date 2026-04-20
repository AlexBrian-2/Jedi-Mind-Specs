"""Spec viewer - tabbed spec document browser."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTextBrowser,
    QLabel, QPushButton, QHBoxLayout,
)
from PySide6.QtCore import Qt


class SpecViewer(QWidget):
    """Tabbed spec document viewer."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QHBoxLayout()
        
        title = QLabel("Spec Documents")
        title.setStyleSheet("font-size: 13px; font-weight: bold; padding: 8px;")
        header.addWidget(title)
        
        header.addStretch()
        
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: #282a36;
            }
            QTabBar::tab {
                background-color: #44475a;
                color: #f8f8f2;
                padding: 8px 16px;
                border: none;
            }
            QTabBar::tab:selected {
                background-color: #282a36;
                border-bottom: 2px solid #50fa7b;
            }
            QTabBar::tab:hover {
                background-color: #6272a4;
            }
        """)
        
        placeholder = QTextBrowser()
        placeholder.setPlainText(
            "No spec documents generated yet.\n\n"
            "Start a research run to generate specification documents."
        )
        placeholder.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: #282a36;
                color: #6272a4;
                font-style: italic;
            }
        """)
        
        self.tabs.addTab(placeholder, "Welcome")
        
        layout.addLayout(header)
        layout.addWidget(self.tabs)
    
    def add_document(self, title: str, content: str):
        """Add a spec document tab."""
        browser = QTextBrowser()
        browser.setMarkdown(content)
        browser.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: #282a36;
                color: #f8f8f2;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
                padding: 10px;
            }
        """)
        
        self.tabs.addTab(browser, title)
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
    
    def clear_documents(self):
        """Clear all document tabs."""
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)
        
        placeholder = QTextBrowser()
        placeholder.setPlainText(
            "No spec documents generated yet.\n\n"
            "Start a research run to generate specification documents."
        )
        placeholder.setStyleSheet("""
            QTextBrowser {
                border: none;
                background-color: #282a36;
                color: #6272a4;
                font-style: italic;
            }
        """)
        
        self.tabs.addTab(placeholder, "Welcome")