"""Entry point - qasync event loop bridge."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
import qasync
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon

from gui.main_window import MainWindow
from core.orchestrator import OrchestratorController
from core.run_context import PROJECT_TYPE_LABELS, ProjectType, WorkflowState


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ResearchOrchestratorApp:
    """Main application class."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Research Orchestrator")
        self.app.setApplicationVersion("1.0.0")
        
        self.loop = qasync.QEventLoop(self.app)
        asyncio.set_event_loop(self.loop)
        
        self.controller = OrchestratorController()
        self.window = MainWindow(self.controller)
        
        self._connect_signals()
    
    def _connect_signals(self):
        """Connect signals between components."""
        form = self.window.get_project_form()
        form.run_started.connect(self._on_run_started)
        form.run_cancelled.connect(self._on_run_cancelled)
        
        self.controller.connect('status', self._on_status_change)
        self.controller.connect('agent', self._on_agent_update)
        self.controller.connect('log', self._on_log)
    
    async def _on_run_started(self, config: dict):
        """Handle run started."""
        logger.info(f"Starting run: {config['project_name']}")
        
        self.window.update_run_status(True)
        self.window.get_agent_tree().reset()
        self.window.get_activity_log().clear()
        self.window.get_spec_viewer().clear_documents()
        
        project_type = ProjectType(config['project_type'])
        
        await self.controller.start(
            project_name=config['project_name'],
            project_type=project_type,
            project_description=config['project_description'],
            model=config.get('model', 'kilo/auto-free'),
            inter_call_delay=config.get('inter_call_delay', 2000),
            max_review_cycles=config.get('max_review_cycles', 3),
            max_validation_cycles=config.get('max_validation_cycles', 2),
        )
    
    async def _on_run_cancelled(self):
        """Handle run cancelled."""
        logger.info("Cancelling run")
        await self.controller.cancel()
    
    def _on_status_change(self, state: WorkflowState):
        """Handle workflow state change."""
        state_name = state.value.replace('_', ' ').title()
        self.window.update_workflow_state(state_name)
        
        if state == WorkflowState.COMPLETE or state == WorkflowState.IDLE:
            self.window.update_run_status(False)
            self.window.get_project_form().set_running(False)
    
    def _on_agent_update(self, agent_id: str, status: str, action: str):
        """Handle agent status update."""
        self.window.get_agent_tree().update_agent(agent_id, status, action)
    
    def _on_log(self, agent_id: str, agent_name: str, message: str, level: str):
        """Handle log entry."""
        self.window.get_activity_log().append_log(agent_name, message, level)
    
    def run(self):
        """Run the application."""
        self.window.show()
        
        with self.loop:
            self.loop.run_forever()


def main():
    """Main entry point."""
    app = ResearchOrchestratorApp()
    app.run()


if __name__ == "__main__":
    main()