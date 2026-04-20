from abc import ABC, abstractmethod
from typing import Any, Optional
import asyncio

from ..rate_limiter import RateLimitedGatewayClient
from ..run_context import RunContext, AgentStatus
from ..message_bus import AgentMessage, MessageBus


class BaseAgent(ABC):
    """Abstract base agent - all LLM calls MUST go through llm_call()."""
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        run_context: RunContext,
        message_bus: MessageBus,
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.ctx = run_context
        self.message_bus = message_bus
        self._client = RateLimitedGatewayClient.get_instance()
    
    async def llm_call(
        self,
        messages: list[dict],
        model: str = "kilo/auto-free",
    ) -> str:
        """All LLM calls MUST go through this method - never call litellm directly."""
        
        async def _call():
            import litellm
            resp = await litellm.acompletion(
                model=f"openai/{model}",
                messages=messages,
                api_base="https://api.kilo.ai/api/gateway",
                # api_key can be "anonymous" or a token
            )
            return resp.choices[0].message.content
        
        self.ctx.api_call_count += 1
        result = await self._client.call(_call)
        return result
    
    @abstractmethod
    async def run(self, task: dict) -> dict:
        """Each agent implements its specific research/review/validation logic."""
        pass
    
    async def receive_message(self) -> Optional[AgentMessage]:
        """Receive next message from message bus."""
        return await self.message_bus.receive(self.agent_id)
    
    async def send_message(self, recipient_id: str, message: AgentMessage):
        """Send a message to another agent."""
        self.message_bus.send(message)
    
    def update_status(self, status: AgentStatus, action: Optional[str] = None):
        """Update agent status in run context."""
        agent = self.ctx.agents.get(self.agent_id)
        if agent:
            agent.status = status
            agent.current_action = action
    
    def add_log(self, message: str, level: str = 'info'):
        """Add a log entry."""
        self.ctx.add_log(self.agent_id, self.name, message, level)
    
    async def wait_for_messages(self, timeout: float = 30.0) -> Optional[AgentMessage]:
        """Wait for incoming messages with timeout."""
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            msg = await self.receive_message()
            if msg:
                return msg
            await asyncio.sleep(0.1)
        return None


class ResearchAgent(BaseAgent):
    """Base class for research agents."""
    
    async def run(self, task: dict) -> dict:
        """Execute research task."""
        query = task.get('query', '')
        project_type = task.get('project_type', '')
        
        research_queries = self._generate_research_queries(query, project_type)
        
        results = []
        for rq in research_queries:
            if self.ctx.has_visited_url(rq):
                continue
            
            result = await self._perform_research(rq)
            results.append(result)
            self.ctx.add_visited_url(rq)
        
        content = self._compile_results(results)
        
        return {
            'content': content,
            'confidence': 'medium',
            'sources': [],
        }
    
    def _generate_research_queries(self, query: str, project_type: str) -> list[str]:
        """Generate research queries based on task."""
        return [f"{project_type} {query} best practices"]
    
    async def _perform_research(self, query: str) -> dict:
        """Perform actual research (web search + fetch)."""
        return {
            'query': query,
            'summary': f'Research results for: {query}',
            'sources': [],
        }
    
    def _compile_results(self, results: list[dict]) -> str:
        """Compile research results into markdown."""
        lines = ["# Research Results\n"]
        for r in results:
            lines.append(f"## {r['query']}\n")
            lines.append(f"{r['summary']}\n\n")
        return "\n".join(lines)


class ReviewAgent(BaseAgent):
    """Base class for review agents."""
    
    async def run(self, task: dict) -> dict:
        """Execute review task."""
        documents = task.get('documents', [])
        
        review_content = await self._review_documents(documents)
        
        score = self._calculate_score(review_content)
        passed = score >= 0.7
        
        return {
            'content': review_content,
            'score': score,
            'passed': passed,
            'recommendations': [],
        }
    
    async def _review_documents(self, documents: list[dict]) -> str:
        """Review documents and provide feedback."""
        return "All documents meet quality standards."
    
    def _calculate_score(self, review_content: str) -> float:
        """Calculate review score."""
        return 0.85


class ValidationAgent(BaseAgent):
    """Base class for validation agents."""
    
    async def run(self, task: dict) -> dict:
        """Execute validation task."""
        documents = task.get('documents', [])
        
        validation_result = await self._validate_documents(documents)
        
        return {
            'passed': validation_result['passed'],
            'issues': validation_result.get('issues', []),
            'recommendations': validation_result.get('recommendations', []),
        }
    
    async def _validate_documents(self, documents: list[dict]) -> dict:
        """Validate documents."""
        return {
            'passed': True,
            'issues': [],
            'recommendations': [],
        }
