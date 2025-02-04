from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ActionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ActionContext:
    agent_id: str
    timestamp: float
    environment: Dict[str, Any]
    target: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class ActionResult:
    status: ActionStatus
    data: Dict[str, Any]
    error: Optional[str] = None

class BaseAction(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = ActionStatus.PENDING
        
    @abstractmethod
    async def execute(self, context: ActionContext) -> ActionResult:
        """Execute the action with given context"""
        pass
    
    @abstractmethod
    async def validate(self, context: ActionContext) -> bool:
        """Validate if the action can be executed"""
        pass
    
    def can_interrupt(self) -> bool:
        """Whether the action can be interrupted"""
        return False