from ..integration.adapter import LLMAdapter
from typing import Dict, Any, List, Optional

class GPT4Adapter(LLMAdapter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config["api_key"]
        self.model = config.get("model", "gpt-4-turbo-preview")
        self.api_base = "https://api.openai.com/v1"
        
    async def generate(self,
                      prompt: str,
                      max_tokens: Optional[int] = None,
                      temperature: float = 0.7,
                      **kwargs) -> Dict[str, Any]:
        await self._handle_rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
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
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=data
        ) as response:
            if response.status != 200:
                error_data = await response.json()
                raise Exception(f"OpenAI API error: {error_data}")
            return await response.json()
            
    async def embed(self, text: str) -> List[float]:
        await self._handle_rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "text-embedding-3-large",
            "input": text
        }
        
        async with self.session.post(
            f"{self.api_base}/embeddings",
            headers=headers,
            json=data
        ) as response:
            if response.status != 200:
                error_data = await response.json()
                raise Exception(f"OpenAI API error: {error_data}")
            result = await response.json()
            return result["data"][0]["embedding"]
