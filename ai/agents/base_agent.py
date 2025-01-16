from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import asyncio
import json
import uuid

class BaseAgent(ABC):
    def __init__(self, name: str, personality_traits: Dict[str, float] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.personality_traits = personality_traits or {}
        self.memory: List[Dict[str, Any]] = []
        self.state = "idle"
        
    @abstractmethod
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process current context and decide next action"""
        pass
    
    @abstractmethod
    async def act(self, action_type: str, **kwargs) -> Dict[str, Any]:
        """Execute an action"""
        pass
    
    def remember(self, event: Dict[str, Any]) -> None:
        """Store an event in agent's memory"""
        self.memory.append({
            "timestamp": asyncio.get_event_loop().time(),
            "event": event
        })
    
    def recall(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent memories"""
        return sorted(self.memory, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def update_personality(self, traits: Dict[str, float]) -> None:
        """Update agent's personality traits"""
        self.personality_traits.update(traits)