from typing import Dict, Any, List
from .base_action import BaseAction, ActionContext, ActionResult, ActionStatus

class CommunicateAction(BaseAction):
    def __init__(self):
        super().__init__(
            name="communicate",
            description="Communicate with another agent"
        )
        
    async def validate(self, context: ActionContext) -> bool:
        return context.target is not None
        
    async def execute(self, context: ActionContext) -> ActionResult:
        try:
            # Implement communication logic
            return ActionResult(
                status=ActionStatus.COMPLETED,
                data={
                    "message": context.metadata.get("message", ""),
                    "target": context.target,
                    "type": context.metadata.get("type", "text")
                }
            )
        except Exception as e:
            return ActionResult(
                status=ActionStatus.FAILED,
                data={},
                error=str(e)
            )

class EmoteAction(BaseAction):
    def __init__(self):
        super().__init__(
            name="emote",
            description="Express an emotion or reaction"
        )
        
    async def validate(self, context: ActionContext) -> bool:
        return "emotion" in context.metadata
        
    async def execute(self, context: ActionContext) -> ActionResult:
        try:
            return ActionResult(
                status=ActionStatus.COMPLETED,
                data={
                    "emotion": context.metadata["emotion"],
                    "intensity": context.metadata.get("intensity", 1.0)
                }
            )
        except Exception as e:
            return ActionResult(
                status=ActionStatus.FAILED,
                data={},
                error=str(e)
            )