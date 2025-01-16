from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import aiohttp
import json
import asyncio
from datetime import datetime, timedelta

class LLMAdapter(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request: Optional[datetime] = None
        self.rate_limit = config.get('rate_limit', 60)  # requests per minute
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    @abstractmethod
    async def generate(self, 
                      prompt: str, 
                      max_tokens: Optional[int] = None,
                      temperature: float = 0.7,
                      **kwargs) -> Dict[str, Any]:
        """Generate text using the LLM"""
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embeddings for text"""
        pass

    async def _handle_rate_limit(self):
        """Handle rate limiting between requests"""
        if self.last_request:
            elapsed = datetime.now() - self.last_request
            if elapsed < timedelta(seconds=60/self.rate_limit):
                await asyncio.sleep((60/self.rate_limit) - elapsed.total_seconds())
        self.last_request = datetime.now()