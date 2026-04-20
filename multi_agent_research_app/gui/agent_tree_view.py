"""Agent tree view - live hierarchy with status icons."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLabel, QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor


class AgentTreeView(QWidget):
    """Live agent hierarchy with status indicators."""
    
    STATUS_COLORS = {
        'idle': '#6272a4',
        'active': '#50fa7b',
        'complete': '#8be9fd',
        'warning': '#f1fa8c',
        'error': '#ff5555',
    }
    
    def __init__(self):
        super().__init__()
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QLabel("Agent Hierarchy")
        header.setStyleSheet("font-size: 13px; font-weight: bold; padding: 8px;")
        layout.addWidget(header)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Agent", "Status", "Action"])
        self.tree.setColumnWidth(0, 250)
        self.tree.setColumnWidth(1, 100)
        self.tree.setAlternatingRowColors(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: none;
                background-color: #282a36;
                color: #f8f8f2;
            }
            QTreeWidget::item { padding: 4px; }
            QTreeWidget::item:selected { background-color: #44475a; }
        """)
        
        layout.addWidget(self.tree)
        
        self._build_tree()
    
    def _build_tree(self):
        """Build the agent hierarchy tree."""
        self.agents = {}
        
        master_item = self._add_item(None, "Master Agent", "idle")
        self.agents['master'] = master_item
        
        frontend_lead = self._add_item(master_item, "Frontend Lead", "idle")
        self.agents['frontend-lead'] = frontend_lead
        self._add_item(frontend_lead, "Wireframe & Layout", "idle")
        self._add_item(frontend_lead, "UI Components Library", "idle")
        self._add_item(frontend_lead, "Color & Style", "idle")
        self._add_item(frontend_lead, "Overall UX/UI/GUI", "idle")
        
        backend_lead = self._add_item(master_item, "Backend Lead", "idle")
        self.agents['backend-lead'] = backend_lead
        self._add_item(backend_lead, "Primary Backend", "idle")
        self._add_item(backend_lead, "Database", "idle")
        self._add_item(backend_lead, "Auth", "idle")
        
        specs_lead = self._add_item(master_item, "Specs Lead", "idle")
        self.agents['specs-lead'] = specs_lead
        self._add_item(specs_lead, "Spec Documents Specialist", "idle")
        self._add_item(specs_lead, "Tech Stack", "idle")
        self._add_item(specs_lead, "Planning", "idle")
        self._add_item(specs_lead, "Architecture", "idle")
        self._add_item(specs_lead, "Best Practices", "idle")
        
        review_lead = self._add_item(master_item, "Review Lead", "idle")
        self.agents['review-lead'] = review_lead
        self._add_item(review_lead, "Review Agent #1", "idle")
        self._add_item(review_lead, "Review Agent #2", "idle")
        self._add_item(review_lead, "Review Agent #3", "idle")
        
        validation_lead = self._add_item(master_item, "Validation Lead", "idle")
        self.agents['validation-lead'] = validation_lead
        self._add_item(validation_lead, "Validation Agent #1", "idle")
        self._add_item(validation_lead, "Validation Agent #2", "idle")
        
        self.tree.expandAll()
    
    def _add_item(self, parent, name, status):
        """Add an item to the tree."""
        item = QTreeWidgetItem(parent or self.tree)
        item.setText(0, name)
        item.setText(1, status.upper())
        item.setText(2, "")
        
        color = self.STATUS_COLORS.get(status, '#6272a4')
        item.setForeground(1, QColor(color))
        
        return item
    
    def update_agent(self, agent_id: str, status: str, action: str = ""):
        """Update agent status."""
        if agent_id in self.agents:
            item = self.agents[agent_id]
            item.setText(1, status.upper())
            item.setText(2, action or "")
            
            color = self.STATUS_COLORS.get(status, '#6272a4')
            item.setForeground(1, QColor(color))
    
    def reset(self):
        """Reset all agents to idle."""
        for agent_id in self.agents:
            self.update_agent(agent_id, "idle", "")