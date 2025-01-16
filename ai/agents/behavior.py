from typing import Dict, Any, Callable, List
from enum import Enum
from abc import ABC, abstractmethod

class NodeStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    RUNNING = "running"

class BehaviorNode(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = NodeStatus.FAILURE
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> NodeStatus:
        pass

class Sequence(BehaviorNode):
    def __init__(self, name: str, children: List[BehaviorNode]):
        super().__init__(name)
        self.children = children
        self.current_child = 0
    
    async def execute(self, context: Dict[str, Any]) -> NodeStatus:
        while self.current_child < len(self.children):
            status = await self.children[self.current_child].execute(context)
            
            if status == NodeStatus.FAILURE:
                self.current_child = 0
                return NodeStatus.FAILURE
            
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            
            self.current_child += 1
        
        self.current_child = 0
        return NodeStatus.SUCCESS

class Selector(BehaviorNode):
    def __init__(self, name: str, children: List[BehaviorNode]):
        super().__init__(name)
        self.children = children
        self.current_child = 0
    
    async def execute(self, context: Dict[str, Any]) -> NodeStatus:
        while self.current_child < len(self.children):
            status = await self.children[self.current_child].execute(context)
            
            if status == NodeStatus.SUCCESS:
                self.current_child = 0
                return NodeStatus.SUCCESS
            
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
            
            self.current_child += 1
        
        self.current_child = 0
        return NodeStatus.FAILURE