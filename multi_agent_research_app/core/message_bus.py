from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import uuid


class MessageType(Enum):
    TASK_ASSIGNMENT = "task_assignment"
    RESULT_SUBMISSION = "result_submission"
    STATUS_UPDATE = "status_update"
    ESCALATION = "escalation"


@dataclass
class AgentMessage:
    """Message for inter-agent communication.
    
    Communication topology is strictly enforced:
    - Human User ↔ Master Agent only
    - Master Agent ↔ Tier-2 Leads only
    - Tier-2 Leads ↔ their own Tier-3 specialists only
    - No Tier-3 agent ever addresses Master Agent or a sibling subtree
    """
    sender_id: str
    recipient_id: str
    message_type: MessageType
    payload: Any
    run_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> dict:
        return {
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'message_type': self.message_type.value,
            'payload': self.payload,
            'run_id': self.run_id,
            'timestamp': self.timestamp.isoformat(),
        }
    
    @classmethod
    def create_task_assignment(
        cls,
        sender_id: str,
        recipient_id: str,
        run_id: str,
        task: dict,
    ) -> 'AgentMessage':
        """Create a task assignment message."""
        return cls(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.TASK_ASSIGNMENT,
            payload=task,
            run_id=run_id,
        )
    
    @classmethod
    def create_result_submission(
        cls,
        sender_id: str,
        recipient_id: str,
        run_id: str,
        result: dict,
    ) -> 'AgentMessage':
        """Create a result submission message."""
        return cls(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.RESULT_SUBMISSION,
            payload=result,
            run_id=run_id,
        )
    
    @classmethod
    def create_status_update(
        cls,
        sender_id: str,
        recipient_id: str,
        run_id: str,
        status: dict,
    ) -> 'AgentMessage':
        """Create a status update message."""
        return cls(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.STATUS_UPDATE,
            payload=status,
            run_id=run_id,
        )
    
    @classmethod
    def create_escalation(
        cls,
        sender_id: str,
        recipient_id: str,
        run_id: str,
        escalation: dict,
    ) -> 'AgentMessage':
        """Create an escalation message (review/validation failure)."""
        return cls(
            sender_id=sender_id,
            recipient_id=recipient_id,
            message_type=MessageType.ESCALATION,
            payload=escalation,
            run_id=run_id,
        )


class MessageRouter:
    """Routes messages between agents based on topology rules."""
    
    ALLOWED_ROUTES = {
        'user': ['master'],
        'master': ['frontend-lead', 'backend-lead', 'specs-lead', 'review-lead', 'validation-lead'],
        'frontend-lead': ['wireframe', 'components', 'style', 'ux'],
        'backend-lead': ['primary-backend', 'database', 'auth'],
        'specs-lead': ['spec-documents', 'tech-stack', 'planning', 'architecture', 'best-practices'],
        'review-lead': ['review-1', 'review-2', 'review-3'],
        'validation-lead': ['validation-1', 'validation-2'],
    }
    
    @classmethod
    def can_route(cls, from_id: str, to_id: str) -> bool:
        """Check if routing from one agent to another is allowed."""
        allowed = cls.ALLOWED_ROUTES.get(from_id, [])
        return to_id in allowed
    
    @classmethod
    def get_allowed_recipients(cls, from_id: str) -> list[str]:
        """Get list of agents that can receive messages from from_id."""
        return cls.ALLOWED_ROUTES.get(from_id, [])
    
    @classmethod
    def route_message(cls, message: AgentMessage) -> bool:
        """Route a message if allowed. Returns True if routed."""
        if cls.can_route(message.sender_id, message.recipient_id):
            return True
        raise ValueError(
            f"Invalid route: {message.sender_id} -> {message.recipient_id}. "
            f"Allowed: {cls.get_allowed_recipients(message.sender_id)}"
        )


class MessageBus:
    """Async message bus for agent communication."""
    
    def __init__(self):
        self._queue: dict[str, list[AgentMessage]] = {}
        self._subscribers: dict[str, list] = {}
    
    async def send(self, message: AgentMessage):
        """Send a message to recipient's queue."""
        recipient = message.recipient_id
        if recipient not in self._queue:
            self._queue[recipient] = []
        self._queue[recipient].append(message)
        
        if recipient in self._subscribers:
            for callback in self._subscribers[recipient]:
                await callback(message)
    
    async def receive(self, agent_id: str) -> Optional[AgentMessage]:
        """Receive next message from queue."""
        if agent_id in self._queue and self._queue[agent_id]:
            return self._queue[agent_id].pop(0)
        return None
    
    async def peek(self, agent_id: str) -> Optional[AgentMessage]:
        """Peek at next message without removing."""
        if agent_id in self._queue and self._queue[agent_id]:
            return self._queue[agent_id][0]
        return None
    
    def subscribe(self, agent_id: str, callback):
        """Subscribe to messages for an agent."""
        if agent_id not in self._subscribers:
            self._subscribers[agent_id] = []
        self._subscribers[agent_id].append(callback)
    
    def unsubscribe(self, agent_id: str, callback):
        """Unsubscribe from messages."""
        if agent_id in self._subscribers:
            self._subscribers[agent_id].remove(callback)
    
    def get_queue_depth(self, agent_id: str) -> int:
        """Get number of pending messages."""
        return len(self._queue.get(agent_id, []))
    
    def clear_queue(self, agent_id: str):
        """Clear all pending messages for an agent."""
        if agent_id in self._queue:
            self._queue[agent_id].clear()