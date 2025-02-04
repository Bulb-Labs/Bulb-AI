# ai/llm/providers/deepseek.py
from typing import Dict, Any, List, Optional
import aiohttp
import json
import asyncio
from ..integration.adapter import LLMAdapter

class DeepSeekAdapter(LLMAdapter):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config["api_key"]
        self.model = config.get("model", "deepseek-67b")
        self.api_base = "https://api.deepseek.com/v1"
        
    async def generate(self, 
                      prompt: str,
                      max_tokens: Optional[int] = None,
                      temperature: float = 0.7,
                      **kwargs) -> Dict[str, Any]:
        """Generate text using DeepSeek"""
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
            
        try:
            async with self.session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"DeepSeek API error: {error_data}")
                return await response.json()
                
        except Exception as e:
            print(f"Error calling DeepSeek: {e}")
            raise
            
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings using DeepSeek"""
        await self._handle_rate_limit()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": f"{self.model}-embed",
            "input": text
        }
        
        try:
            async with self.session.post(
                f"{self.api_base}/embeddings",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_data = await response.json()
                    raise Exception(f"DeepSeek Embedding API error: {error_data}")
                    
                result = await response.json()
                return result["data"][0]["embedding"]
                
        except Exception as e:
            print(f"Error getting embeddings from DeepSeek: {e}")
            raise