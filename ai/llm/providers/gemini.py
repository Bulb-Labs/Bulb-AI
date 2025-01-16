from ..integration.adapter import LLMAdapter
from typing import Dict, Any, List, Optional

class GeminiAdapter(LLMAdapter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config["api_key"]
        self.model = config.get("model", "gemini-pro")
        self.api_base = "https://generativelanguage.googleapis.com/v1beta"
        
    async def generate(self,
                      prompt: str,
                      max_tokens: Optional[int] = None,
                      temperature: float = 0.7,
                      **kwargs) -> Dict[str, Any]:
        await self._handle_rate_limit()
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": temperature,
                **kwargs
            }
        }
        
        if max_tokens:
            data["generationConfig"]["maxOutputTokens"] = max_tokens
            
        url = f"{self.api_base}/models/{self.model}:generateContent?key={self.api_key}"
        
        async with self.session.post(
            url,
            headers=headers,
            json=data
        ) as response:
            if response.status != 200:
                error_data = await response.json()
                raise Exception(f"Gemini API error: {error_data}")
            return await response.json()
            
    async def embed(self, text: str) -> List[float]:
        await self._handle_rate_limit()
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "models/embedding-001",
            "text": text
        }
        
        url = f"{self.api_base}/models/embedding-001:embedText?key={self.api_key}"
        
        async with self.session.post(
            url,
            headers=headers,
            json=data
        ) as response:
            if response.status != 200:
                error_data = await response.json()
                raise Exception(f"Gemini API error: {error_data}")
            result = await response.json()
            return result["embedding"]["values"]