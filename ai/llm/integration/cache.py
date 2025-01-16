from typing import Dict, Any, Optional
import json
import hashlib
import time
from pathlib import Path

class LLMCache:
    def __init__(self, cache_dir: str = ".cache/llm", ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = ttl

    def _get_cache_key(self, prompt: str, provider: str, **kwargs) -> str:
        """Generate cache key from prompt and parameters"""
        cache_data = {
            "prompt": prompt,
            "provider": provider,
            **kwargs
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()

    def get(self, prompt: str, provider: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if available and not expired"""
        cache_key = self._get_cache_key(prompt, provider, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)

            if time.time() - cached_data["timestamp"] > self.ttl:
                cache_file.unlink()
                return None

            return cached_data["response"]
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def set(self, prompt: str, provider: str, response: Dict[str, Any], **kwargs) -> None:
        """Cache a response"""
        cache_key = self._get_cache_key(prompt, provider, **kwargs)
        cache_file = self.cache_dir / f"{cache_key}.json"

        cache_data = {
            "timestamp": time.time(),
            "response": response
        }

        with open(cache_file, 'w') as f:
            json.dump(cache_data, f)