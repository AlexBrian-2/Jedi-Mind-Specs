"""Rate limit widget - status bar rate limit monitor."""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QProgressBar,
)
from PySide6.QtCore import QTimer, Qt


class RateLimitWidget(QWidget):
    """Rate limit status widget for status bar."""
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_status)
        self._timer.start(5000)
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(15)
        
        api_label = QLabel("API:")
        api_label.setStyleSheet("color: #6272a4; font-size: 11px;")
        layout.addWidget(api_label)
        
        self.usage_label = QLabel("0/180")
        self.usage_label.setStyleSheet("color: #f8f8f2; font-size: 11px; font-family: monospace;")
        layout.addWidget(self.usage_label)
        
        self.progress = QProgressBar()
        self.progress.setFixedWidth(100)
        self.progress.setFixedHeight(8)
        self.progress.setTextVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #44475a;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #50fa7b;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress)
        
        remaining_label = QLabel("Remaining:")
        remaining_label.setStyleSheet("color: #6272a4; font-size: 11px;")
        layout.addWidget(remaining_label)
        
        self.remaining_label = QLabel("180")
        self.remaining_label.setStyleSheet("color: #50fa7b; font-size: 11px; font-family: monospace;")
        layout.addWidget(self.remaining_label)
        
        reset_label = QLabel("Reset:")
        reset_label.setStyleSheet("color: #6272a4; font-size: 11px;")
        layout.addWidget(reset_label)
        
        self.reset_label = QLabel("--:--")
        self.reset_label.setStyleSheet("color: #8be9fd; font-size: 11px; font-family: monospace;")
        layout.addWidget(self.reset_label)
        
        tokens_label = QLabel("Tokens:")
        tokens_label.setStyleSheet("color: #6272a4; font-size: 11px;")
        layout.addWidget(tokens_label)
        
        self.tokens_label = QLabel("10")
        self.tokens_label.setStyleSheet("color: #f1fa8c; font-size: 11px; font-family: monospace;")
        layout.addWidget(self.tokens_label)
    
    def _update_status(self):
        """Update rate limit status."""
        try:
            from core.rate_limiter import RateLimitedGatewayClient
            
            status = RateLimitedGatewayClient.get_instance().get_status()
            
            self.usage_label.setText(
                f"{status['requests_this_hour']}/{status['soft_limit']}"
            )
            
            percentage = (status['requests_this_hour'] / status['soft_limit']) * 100
            self.progress.setValue(int(percentage))
            
            if percentage > 80:
                self.progress.setStyleSheet("""
                    QProgressBar {
                        border: none;
                        background-color: #44475a;
                        border-radius: 4px;
                    }
                    QProgressBar::chunk {
                        background-color: #ff5555;
                        border-radius: 4px;
                    }
                """)
            elif percentage > 60:
                self.progress.setStyleSheet("""
                    QProgressBar {
                        border: none;
                        background-color: #44475a;
                        border-radius: 4px;
                    }
                    QProgressBar::chunk {
                        background-color: #f1fa8c;
                        border-radius: 4px;
                    }
                """)
            else:
                self.progress.setStyleSheet("""
                    QProgressBar {
                        border: none;
                        background-color: #44475a;
                        border-radius: 4px;
                    }
                    QProgressBar::chunk {
                        background-color: #50fa7b;
                        border-radius: 4px;
                    }
                """)
            
            self.remaining_label.setText(str(status['remaining']))
            
            minutes = status['next_reset_seconds'] // 60
            seconds = status['next_reset_seconds'] % 60
            self.reset_label.setText(f"{minutes}m {seconds}s")
            
            self.tokens_label.setText(str(status['tokens_available']))
            
        except Exception as e:
            pass
    
    def stop(self):
        """Stop the update timer."""
        self._timer.stop()