from typing import Dict, Any, Optional, List
from .adapter import LLMAdapter
import random
import logging

logger = logging.getLogger(__name__)

class LLMRouter:
    def __init__(self):
        self.providers: Dict[str, LLMAdapter] = {}
        self.default_provider = None
        self.fallback_providers: List[str] = []

    def register_provider(self, 
                         name: str, 
                         adapter: LLMAdapter, 
                         is_default: bool = False,
                         is_fallback: bool = False) -> None:
        """Register a new LLM provider"""
        self.providers[name] = adapter
        
        if is_default:
            self.default_provider = name
        if is_fallback:
            self.fallback_providers.append(name)

    async def generate(self,
                      prompt: str,
                      provider: Optional[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """Generate text using specified or default provider with fallback"""
        errors = []
        
        # Try specified provider
        if provider:
            if provider not in self.providers:
                raise ValueError(f"Unknown provider: {provider}")
            try:
                return await self.providers[provider].generate(prompt, **kwargs)
            except Exception as e:
                errors.append((provider, str(e)))
                logger.warning(f"Failed to generate with {provider}: {e}")
        
        # Try default provider
        if self.default_provider:
            try:
                return await self.providers[self.default_provider].generate(prompt, **kwargs)
            except Exception as e:
                errors.append((self.default_provider, str(e)))
                logger.warning(f"Failed to generate with default provider {self.default_provider}: {e}")
        
        # Try fallback providers
        for fallback in self.fallback_providers:
            try:
                return await self.providers[fallback].generate(prompt, **kwargs)
            except Exception as e:
                errors.append((fallback, str(e)))
                logger.warning(f"Failed to generate with fallback provider {fallback}: {e}")
        
        raise RuntimeError(f"All providers failed: {errors}")

    async def embed(self,
                   text: str,
                   provider: Optional[str] = None) -> List[float]:
        """Generate embeddings using specified or default provider"""
        if provider:
            if provider not in self.providers:
                raise ValueError(f"Unknown provider: {provider}")
            return await self.providers[provider].embed(text)
        
        if self.default_provider:
            return await self.providers[self.default_provider].embed(text)
        
        raise ValueError("No provider specified and no default provider set")
