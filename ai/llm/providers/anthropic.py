from ..integration.adapter import LLMAdapter
from typing import Dict, Any, List, Optional
import json

class ClaudeAdapter(LLMAdapter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config["api_key"]
        self.model = config.get("model", "claude-3-opus-20240229")
        self.api_base = "https://api.anthropic.com/v1"
        
    async def generate(self, 
                      prompt: str,
                      max_tokens: Optional[int] = None,
                      temperature: float = 0.7,
                      **kwargs) -> Dict[str, Any]:
        await self._handle_rate_limit()
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            data["max_tokens"] = max_tokens
            
        async with self.session.post(
            f"{self.api_base}/messages",
            headers=headers,
            json=data
        ) as response:
            if response.status != 200:
                error_data = await response.json()
                raise Exception(f"Claude API error: {error_data}")
            return await response.json()
            
    async def embed(self, text: str) -> List[float]:
        raise NotImplementedError("Claude embeddings not yet available")
