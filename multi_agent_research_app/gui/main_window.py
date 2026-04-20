"""Main window - PySide6 three-panel layout."""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QStatusBar,
    QMenuBar,
    QMenu,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

from .project_form import ProjectForm
from .agent_tree_view import AgentTreeView
from .activity_log import ActivityLog
from .spec_viewer import SpecViewer
from .rate_limit_widget import RateLimitWidget


class MainWindow(QMainWindow):
    """Main application window with three-panel layout."""
    
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self._setup_ui()
        self._setup_menu()
        self._connect_signals()
    
    def _setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Research Orchestrator - Multi-Agent System")
        self.setMinimumSize(1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        header = self._create_header()
        main_layout.addWidget(header)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.project_form = ProjectForm(self.controller)
        splitter.addWidget(self.project_form)
        
        center_splitter = QSplitter(Qt.Vertical)
        
        self.agent_tree = AgentTreeView()
        center_splitter.addWidget(self.agent_tree)
        
        self.activity_log = ActivityLog()
        center_splitter.addWidget(self.activity_log)
        
        center_splitter.setSizes([400, 200])
        splitter.addWidget(center_splitter)
        
        self.spec_viewer = SpecViewer()
        splitter.addWidget(self.spec_viewer)
        
        splitter.setSizes([250, 500, 450])
        
        main_layout.addWidget(splitter)
        
        self.status_bar = self._create_status_bar()
        self.setStatusBar(self.status_bar)
    
    def _create_header(self) -> QWidget:
        """Create header widget."""
        from PySide6.QtWidgets import QFrame, QLabel
        from PySide6.QtCore import QSize
        
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #1e1e2e; color: white;")
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Research Orchestrator")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        
        subtitle = QLabel("Hierarchical Multi-Agent System")
        subtitle.setStyleSheet("font-size: 11px; color: #a0a0b0;")
        
        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.setSpacing(2)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        self.run_status = QLabel("Ready")
        self.run_status.setStyleSheet(
            "background-color: #2d2d3d; padding: 6px 16px; "
            "border-radius: 12px; font-size: 12px;"
        )
        
        layout.addWidget(self.run_status)
        
        return header
    
    def _create_status_bar(self) -> QStatusBar:
        """Create status bar with rate limit widget."""
        status = QStatusBar()
        
        self.rate_limit_widget = RateLimitWidget()
        status.addPermanentWidget(self.rate_limit_widget)
        
        status.showMessage("Ready")
        
        return status
    
    def _setup_menu(self):
        """Set up menu bar."""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Run", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """Connect signals to slots."""
        pass
    
    def update_run_status(self, is_running: bool):
        """Update run status display."""
        if is_running:
            self.run_status.setText("Running")
            self.run_status.setStyleSheet(
                "background-color: #2d4a3e; padding: 6px 16px; "
                "border-radius: 12px; font-size: 12px; color: #50fa7b;"
            )
        else:
            self.run_status.setText("Ready")
            self.run_status.setStyleSheet(
                "background-color: #2d2d3d; padding: 6px 16px; "
                "border-radius: 12px; font-size: 12px;"
            )
    
    def update_workflow_state(self, state: str):
        """Update workflow state display."""
        self.status_bar.showMessage(f"State: {state}")
    
    def get_project_form(self) -> 'ProjectForm':
        return self.project_form
    
    def get_agent_tree(self) -> 'AgentTreeView':
        return self.agent_tree
    
    def get_activity_log(self) -> 'ActivityLog':
        return self.activity_log
    
    def get_spec_viewer(self) -> 'SpecViewer':
        return self.spec_viewer
    
    def get_rate_limit_widget(self) -> 'RateLimitWidget':
        return self.rate_limit_widget