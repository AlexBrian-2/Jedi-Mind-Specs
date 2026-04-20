from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid

from .message_bus import AgentMessage, MessageType


class AgentStatus(Enum):
    IDLE = "idle"
    ACTIVE = "active"
    COMPLETE = "complete"
    WARNING = "warning"
    ERROR = "error"


class WorkflowState(Enum):
    IDLE = "idle"
    PARSING = "parsing"
    RESEARCH_PHASE = "research_phase"
    REVIEW_PHASE = "review_phase"
    REVIEW_DECISION = "review_decision"
    REVISION_PHASE = "revision_phase"
    VALIDATION_PHASE = "validation_phase"
    VALIDATION_DECISION = "validation_decision"
    COMPLETE = "complete"


class ProjectType(Enum):
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    API_BACKEND = "api_backend"
    CLI_TOOL = "cli_tool"
    DATA_PIPELINE = "data_pipeline"
    ML_SYSTEM = "ml_system"
    OTHER = "other"


PROJECT_TYPE_LABELS = {
    ProjectType.WEB_APP: "Web Application",
    ProjectType.MOBILE_APP: "Mobile Application",
    ProjectType.DESKTOP_APP: "Desktop Application",
    ProjectType.API_BACKEND: "API / Backend Service",
    ProjectType.CLI_TOOL: "CLI Tool",
    ProjectType.DATA_PIPELINE: "Data Pipeline",
    ProjectType.ML_SYSTEM: "ML / AI System",
    ProjectType.OTHER: "Other",
}


class AgentTier(Enum):
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


@dataclass
class Agent:
    """Agent definition."""
    id: str
    name: str
    role: str
    tier: AgentTier
    parent_id: Optional[str]
    status: AgentStatus = AgentStatus.IDLE
    current_action: Optional[str] = None
    start_time: Optional[datetime] = None
    output_artifact: Optional[str] = None
    tools: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'tier': self.tier.value,
            'parent_id': self.parent_id,
            'status': self.status.value,
            'current_action': self.current_action,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'output_artifact': self.output_artifact,
            'tools': self.tools,
        }


@dataclass
class SpecDocument:
    """Research specification document."""
    id: str
    type: str
    title: str
    agent_id: str
    agent_name: str
    content: str
    confidence: str
    confidence_rationale: str
    sources: list[dict]
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'content': self.content,
            'confidence': self.confidence,
            'confidence_rationale': self.confidence_rationale,
            'sources': self.sources,
            'generated_at': self.generated_at.isoformat(),
        }


@dataclass
class LogEntry:
    """Log entry for activity tracking."""
    id: str
    timestamp: datetime
    agent_id: str
    agent_name: str
    message: str
    level: str
    
    @classmethod
    def create(cls, agent_id: str, agent_name: str, message: str, level: str = 'info') -> 'LogEntry':
        return cls(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            agent_id=agent_id,
            agent_name=agent_name,
            message=message,
            level=level,
        )


@dataclass
class RunContext:
    """Single source of truth for a research run."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str = ""
    project_type: ProjectType = ProjectType.WEB_APP
    project_description: str = ""
    workflow_state: WorkflowState = WorkflowState.IDLE
    agents: dict[str, Agent] = field(default_factory=dict)
    documents: list[SpecDocument] = field(default_factory=list)
    visited_urls: set = field(default_factory=set)
    api_call_count: int = 0
    review_cycles: int = 0
    validation_cycles: int = 0
    max_review_cycles: int = 3
    max_validation_cycles: int = 2
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    logs: list[LogEntry] = field(default_factory=list)
    messages: list[AgentMessage] = field(default_factory=list)
    
    model: str = "kilo/auto-free"
    inter_call_delay: int = 2000
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'project_name': self.project_name,
            'project_type': self.project_type.value,
            'project_description': self.project_description,
            'workflow_state': self.workflow_state.value,
            'agents': {k: v.to_dict() for k, v in self.agents.items()},
            'documents': [d.to_dict() for d in self.documents],
            'visited_urls': list(self.visited_urls),
            'api_call_count': self.api_call_count,
            'review_cycles': self.review_cycles,
            'validation_cycles': self.validation_cycles,
            'max_review_cycles': self.max_review_cycles,
            'max_validation_cycles': self.max_validation_cycles,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'logs': [
                {
                    'id': l.id,
                    'timestamp': l.timestamp.isoformat(),
                    'agent_id': l.agent_id,
                    'agent_name': l.agent_name,
                    'message': l.message,
                    'level': l.level,
                }
                for l in self.logs
            ],
            'model': self.model,
            'inter_call_delay': self.inter_call_delay,
        }
    
    def add_log(self, agent_id: str, agent_name: str, message: str, level: str = 'info'):
        """Add a log entry."""
        entry = LogEntry.create(agent_id, agent_name, message, level)
        self.logs.append(entry)
    
    def add_visited_url(self, url: str):
        """Add a visited URL for deduplication."""
        self.visited_urls.add(url)
    
    def has_visited_url(self, url: str) -> bool:
        """Check if URL was already visited."""
        return url in self.visited_urls
    
    def add_document(self, document: SpecDocument):
        """Add a spec document."""
        self.documents.append(document)
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID."""
        return self.agents.get(agent_id)
    
    def get_children(self, parent_id: str) -> list[Agent]:
        """Get all children of an agent."""
        return [a for a in self.agents.values() if a.parent_id == parent_id]


def create_agent_hierarchy() -> dict[str, Agent]:
    """Create the full agent hierarchy."""
    agents = {}
    
    agents['master'] = Agent(
        id='master',
        name='Master Agent',
        role='Orchestrates all; sole user-facing interface; no research',
        tier=AgentTier.TIER_1,
        parent_id=None,
        output_artifact='Final report + all spec docs',
        tools=['Task decomposition', 'Result aggregation'],
    )
    
    agents['frontend-lead'] = Agent(
        id='frontend-lead',
        name='Frontend Lead',
        role='Delegates UI/UX research; synthesizes Tier-3 outputs',
        tier=AgentTier.TIER_2,
        parent_id='master',
        output_artifact='Frontend spec summary',
        tools=['Sub-agent management'],
    )
    agents['wireframe'] = Agent(
        id='wireframe',
        name='Wireframe & Layout',
        role='Researches wireframing patterns for the project type',
        tier=AgentTier.TIER_3,
        parent_id='frontend-lead',
        output_artifact='wireframe_spec.md',
        tools=['Web search', 'Layout analysis'],
    )
    agents['components'] = Agent(
        id='components',
        name='UI Components Library',
        role='Researches component libraries relevant to project',
        tier=AgentTier.TIER_3,
        parent_id='frontend-lead',
        output_artifact='components_spec.md',
        tools=['Web search'],
    )
    agents['style'] = Agent(
        id='style',
        name='Color & Style',
        role='Researches design systems and color theory',
        tier=AgentTier.TIER_3,
        parent_id='frontend-lead',
        output_artifact='style_spec.md',
        tools=['Web search'],
    )
    agents['ux'] = Agent(
        id='ux',
        name='Overall UX/UI/GUI',
        role='Synthesizes UX best practices across sources',
        tier=AgentTier.TIER_3,
        parent_id='frontend-lead',
        output_artifact='ux_spec.md',
        tools=['Web search', 'Synthesis'],
    )
    
    agents['backend-lead'] = Agent(
        id='backend-lead',
        name='Backend Lead',
        role='Delegates backend research; synthesizes Tier-3 outputs',
        tier=AgentTier.TIER_2,
        parent_id='master',
        output_artifact='Backend spec summary',
        tools=['Sub-agent management'],
    )
    agents['primary-backend'] = Agent(
        id='primary-backend',
        name='Primary Backend',
        role='Researches backend architecture patterns',
        tier=AgentTier.TIER_3,
        parent_id='backend-lead',
        output_artifact='backend_spec.md',
        tools=['Web search'],
    )
    agents['database'] = Agent(
        id='database',
        name='Database',
        role='Researches DB options and schema patterns',
        tier=AgentTier.TIER_3,
        parent_id='backend-lead',
        output_artifact='database_spec.md',
        tools=['Web search'],
    )
    agents['auth'] = Agent(
        id='auth',
        name='Auth',
        role='Researches auth patterns and libraries',
        tier=AgentTier.TIER_3,
        parent_id='backend-lead',
        output_artifact='auth_spec.md',
        tools=['Web search'],
    )
    
    agents['specs-lead'] = Agent(
        id='specs-lead',
        name='Specs Lead',
        role='Delegates documentation; synthesizes all spec docs',
        tier=AgentTier.TIER_2,
        parent_id='master',
        output_artifact='All spec documents',
        tools=['Sub-agent management'],
    )
    agents['spec-documents'] = Agent(
        id='spec-documents',
        name='Spec Documents Specialist',
        role='Compiles and formats all spec docs into master',
        tier=AgentTier.TIER_3,
        parent_id='specs-lead',
        output_artifact='master_spec.md',
        tools=['Document generation'],
    )
    agents['tech-stack'] = Agent(
        id='tech-stack',
        name='Tech Stack',
        role='Researches and recommends technology choices',
        tier=AgentTier.TIER_3,
        parent_id='specs-lead',
        output_artifact='techstack_spec.md',
        tools=['Web search', 'Comparison'],
    )
    agents['planning'] = Agent(
        id='planning',
        name='Planning',
        role='Creates project timeline and milestones',
        tier=AgentTier.TIER_3,
        parent_id='specs-lead',
        output_artifact='planning_spec.md',
        tools=['Analysis'],
    )
    agents['architecture'] = Agent(
        id='architecture',
        name='Architecture',
        role='Designs system architecture',
        tier=AgentTier.TIER_3,
        parent_id='specs-lead',
        output_artifact='architecture_spec.md',
        tools=['Web search', 'Diagramming'],
    )
    agents['best-practices'] = Agent(
        id='best-practices',
        name='Best Practices',
        role='Researches coding standards and patterns',
        tier=AgentTier.TIER_3,
        parent_id='specs-lead',
        output_artifact='bestpractices_spec.md',
        tools=['Web search'],
    )
    
    agents['review-lead'] = Agent(
        id='review-lead',
        name='Review Lead',
        role='Coordinates 3 review agents; manages consensus',
        tier=AgentTier.TIER_2,
        parent_id='master',
        output_artifact='Review report',
        tools=['Consensus management'],
    )
    agents['review-1'] = Agent(
        id='review-1',
        name='Review Agent #1',
        role='Independent quality review pass',
        tier=AgentTier.TIER_3,
        parent_id='review-lead',
        output_artifact='review1_report.md',
        tools=['Analysis', 'Scoring'],
    )
    agents['review-2'] = Agent(
        id='review-2',
        name='Review Agent #2',
        role='Independent quality review pass',
        tier=AgentTier.TIER_3,
        parent_id='review-lead',
        output_artifact='review2_report.md',
        tools=['Analysis', 'Scoring'],
    )
    agents['review-3'] = Agent(
        id='review-3',
        name='Review Agent #3',
        role='Independent quality review pass',
        tier=AgentTier.TIER_3,
        parent_id='review-lead',
        output_artifact='review3_report.md',
        tools=['Analysis', 'Scoring'],
    )
    
    agents['validation-lead'] = Agent(
        id='validation-lead',
        name='Validation Lead',
        role='Coordinates 2 validation agents; final gate',
        tier=AgentTier.TIER_2,
        parent_id='master',
        output_artifact='Validation report',
        tools=['Final gate management'],
    )
    agents['validation-1'] = Agent(
        id='validation-1',
        name='Validation Agent #1',
        role='Final validation check',
        tier=AgentTier.TIER_3,
        parent_id='validation-lead',
        output_artifact='validation1_report.md',
        tools=['Analysis'],
    )
    agents['validation-2'] = Agent(
        id='validation-2',
        name='Validation Agent #2',
        role='Final validation check',
        tier=AgentTier.TIER_3,
        parent_id='validation-lead',
        output_artifact='validation2_report.md',
        tools=['Analysis'],
    )
    
    return agents


WORKFLOW_STATE_LABELS = {
    WorkflowState.IDLE: "Ready",
    WorkflowState.PARSING: "Analyzing Request",
    WorkflowState.RESEARCH_PHASE: "Research Phase",
    WorkflowState.REVIEW_PHASE: "Review Phase",
    WorkflowState.REVIEW_DECISION: "Review Decision",
    WorkflowState.REVISION_PHASE: "Revision Phase",
    WorkflowState.VALIDATION_PHASE: "Validation Phase",
    WorkflowState.VALIDATION_DECISION: "Validation Decision",
    WorkflowState.COMPLETE: "Complete",
}
