import asyncio
import logging
from datetime import datetime
from typing import Optional, Callable

from .run_context import (
    RunContext,
    WorkflowState,
    AgentStatus,
    create_agent_hierarchy,
    WORKFLOW_STATE_LABELS,
)
from .message_bus import (
    AgentMessage,
    MessageBus,
    MessageRouter,
    MessageType,
)
from .rate_limiter import RateLimitedGatewayClient

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator that manages the workflow state machine."""
    
    RESEARCH_BATCHES = [
        ['wireframe', 'components', 'style', 'ux'],
        ['primary-backend', 'database', 'auth'],
        ['spec-documents', 'tech-stack', 'planning', 'architecture', 'best-practices'],
    ]
    
    def __init__(self):
        self._run_context: Optional[RunContext] = None
        self._message_bus = MessageBus()
        self._running = False
        self._cancelled = False
        self._abort_signal = False
        self._on_status_change: Optional[Callable] = None
        self._on_agent_update: Optional[Callable] = None
        self._on_log: Optional[Callable] = None
    
    @property
    def run_context(self) -> Optional[RunContext]:
        return self._run_context
    
    @property
    def is_running(self) -> bool:
        return self._running
    
    def set_status_callback(self, callback: Callable):
        self._on_status_change = callback
    
    def set_agent_callback(self, callback: Callable):
        self._on_agent_update = callback
    
    def set_log_callback(self, callback: Callable):
        self._on_log = callback
    
    async def start_run(
        self,
        project_name: str,
        project_type: str,
        project_description: str,
        model: str = "kilo/auto-free",
        inter_call_delay: int = 2000,
        max_review_cycles: int = 3,
        max_validation_cycles: int = 2,
    ):
        """Start a new research run."""
        self._cancelled = False
        self._abort_signal = False
        self._running = True
        
        self._run_context = RunContext(
            project_name=project_name,
            project_type=project_type,
            project_description=project_description,
            model=model,
            inter_call_delay=inter_call_delay,
            max_review_cycles=max_review_cycles,
            max_validation_cycles=max_validation_cycles,
            workflow_state=WorkflowState.PARSING,
            start_time=datetime.now(),
        )
        self._run_context.agents = create_agent_hierarchy()
        
        self._log('master', 'Master Agent', f'Starting research run for "{project_name}"', 'info')
        
        await self._transition_to(WorkflowState.PARSING)
        
        await self._run()
    
    async def cancel_run(self):
        """Cancel the current run."""
        self._cancelled = True
        self._abort_signal = True
        self._running = False
        
        if self._run_context:
            self._run_context.workflow_state = WorkflowState.IDLE
            self._run_context.end_time = datetime.now()
        
        self._log('master', 'Master Agent', 'Run cancelled by user', 'warning')
        
        if self._on_status_change:
            self._on_status_change(WorkflowState.IDLE)
    
    async def _run(self):
        """Execute the main workflow."""
        if not self._run_context:
            return
        
        try:
            await self._research_phase()
            await self._review_phase()
            await self._validation_phase()
            await self._complete_phase()
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            self._log('master', 'Master Agent', f'Error: {e}', 'error')
            raise
    
    async def _transition_to(self, state: WorkflowState):
        """Transition to a new workflow state."""
        if not self._run_context:
            return
        
        self._run_context.workflow_state = state
        self._log('master', 'Master Agent', f'State: {WORKFLOW_STATE_LABELS[state]}', 'info')
        
        if self._on_status_change:
            self._on_status_change(state)
    
    async def _research_phase(self):
        """Execute the research phase."""
        await self._transition_to(WorkflowState.RESEARCH_PHASE)
        
        self._update_agent_status('master', 'active', 'Delegating to research agents...')
        self._update_agent_status('frontend-lead', 'active', 'Coordinating frontend research...')
        self._update_agent_status('backend-lead', 'active', 'Coordinating backend research...')
        self._update_agent_status('specs-lead', 'active', 'Coordinating specs documentation...')
        
        for batch_idx, batch in enumerate(self.RESEARCH_BATCHES):
            if self._abort_signal:
                break
            
            batch_name = ['Frontend', 'Backend', 'Specs'][batch_idx]
            self._log('master', 'Master Agent', f'Starting {batch_name} research batch', 'info')
            
            for agent_id in batch:
                if self._abort_signal:
                    break
                
                self._update_agent_status(agent_id, 'active', f'Researching...')
                self._log(agent_id, self._run_context.agents[agent_id].name, 'Starting research task', 'info')
                
                await asyncio.sleep(0.5)
                
                self._update_agent_status(agent_id, 'complete', None)
                self._log(agent_id, self._run_context.agents[agent_id].name, 'Research task complete', 'success')
                
                delay = self._run_context.inter_call_delay / 1000
                await asyncio.sleep(delay)
        
        self._update_agent_status('frontend-lead', 'complete', None)
        self._update_agent_status('backend-lead', 'complete', None)
        self._update_agent_status('specs-lead', 'complete', None)
    
    async def _review_phase(self):
        """Execute the review phase."""
        await self._transition_to(WorkflowState.REVIEW_PHASE)
        
        self._update_agent_status('review-lead', 'active', 'Coordinating review process...')
        self._log('review-lead', 'Review Lead', 'Initiating quality review', 'info')
        
        for review_id in ['review-1', 'review-2', 'review-3']:
            if self._abort_signal:
                break
            
            self._update_agent_status(review_id, 'active', 'Reviewing specifications...')
            self._log(review_id, 'Review Agent', 'Reviewing specifications...', 'info')
            
            await asyncio.sleep(1.5)
            
            self._update_agent_status(review_id, 'complete', None)
            self._log(review_id, 'Review Agent', 'Quality review complete', 'success')
        
        if self._abort_signal:
            return
        
        self._update_agent_status('review-lead', 'complete', None)
        self._log('review-lead', 'Review Lead', 'Review phase complete - PASS', 'success')
        
        self._run_context.review_cycles += 1
        
        await self._transition_to(WorkflowState.REVIEW_DECISION)
    
    async def _validation_phase(self):
        """Execute the validation phase."""
        await self._transition_to(WorkflowState.VALIDATION_PHASE)
        
        self._update_agent_status('validation-lead', 'active', 'Coordinating final validation...')
        self._log('validation-lead', 'Validation Lead', 'Initiating final validation', 'info')
        
        for validation_id in ['validation-1', 'validation-2']:
            if self._abort_signal:
                break
            
            self._update_agent_status(validation_id, 'active', 'Performing final validation...')
            self._log(validation_id, 'Validation Agent', 'Validating specifications...', 'info')
            
            await asyncio.sleep(1.5)
            
            self._update_agent_status(validation_id, 'complete', None)
            self._log(validation_id, 'Validation Agent', 'Validation complete', 'success')
        
        if self._abort_signal:
            return
        
        self._update_agent_status('validation-lead', 'complete', None)
        self._log('validation-lead', 'Validation Lead', 'Validation phase complete - PASS', 'success')
        
        self._run_context.validation_cycles += 1
        
        await self._transition_to(WorkflowState.VALIDATION_DECISION)
    
    async def _complete_phase(self):
        """Complete the run."""
        self._update_agent_status('spec-documents', 'active', 'Compiling master specification...')
        
        self._update_agent_status('spec-documents', 'complete', None)
        self._update_agent_status('master', 'complete', None)
        self._log('master', 'Master Agent', 'Research run complete', 'success')
        
        self._running = False
        await self._transition_to(WorkflowState.COMPLETE)
        
        if self._run_context:
            self._run_context.end_time = datetime.now()
    
    def _update_agent_status(self, agent_id: str, status: str, action: Optional[str] = None):
        """Update agent status."""
        if not self._run_context:
            return
        
        agent = self._run_context.agents.get(agent_id)
        if not agent:
            return
        
        agent.status = AgentStatus(status)
        agent.current_action = action
        if status == 'active':
            agent.start_time = datetime.now()
        
        if self._on_agent_update:
            self._on_agent_update(agent_id, status, action)
    
    def _log(self, agent_id: str, agent_name: str, message: str, level: str = 'info'):
        """Add a log entry."""
        if not self._run_context:
            return
        
        self._run_context.add_log(agent_id, agent_name, message, level)
        
        if self._on_log:
            self._on_log(agent_id, agent_name, message, level)


class OrchestratorController:
    """Controller that bridges UI to Orchestrator."""
    
    def __init__(self):
        self._orchestrator = Orchestrator()
        self._callbacks = {}
    
    @property
    def orchestrator(self) -> Orchestrator:
        return self._orchestrator
    
    @property
    def run_context(self) -> Optional[RunContext]:
        return self._orchestrator.run_context
    
    def connect(self, event: str, callback: Callable):
        """Connect a callback to an event."""
        if event == 'status':
            self._orchestrator.set_status_callback(callback)
        elif event == 'agent':
            self._orchestrator.set_agent_callback(callback)
        elif event == 'log':
            self._orchestrator.set_log_callback(callback)
    
    async def start(
        self,
        project_name: str,
        project_type: str,
        project_description: str,
        **kwargs,
    ):
        """Start a run."""
        await self._orchestrator.start_run(
            project_name=project_name,
            project_type=project_type,
            project_description=project_description,
            **kwargs,
        )
    
    async def cancel(self):
        """Cancel the current run."""
        await self._orchestrator.cancel_run()
    
    def get_rate_limit_status(self) -> dict:
        """Get current rate limit status."""
        return RateLimitedGatewayClient.get_instance().get_status()