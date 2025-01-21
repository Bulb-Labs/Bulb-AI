from typing import Dict, Any, List, Optional
import aiohttp
import json
import asyncio
  from ..integration.adapter import LLMAdapter

class Llama3Adapter(LLMAdapter):
    def __init__(self, config: Dict[str, Any]):
super().__init__(config)
self.base_url = config.get('base_url', 'http://localhost:8080')
self.batch_size = config.get('batch_size', 32)
self.api_key = config['api_key']
self.model = config.get('model', 'llama3-7b')
        
    async def generate(self,
  prompt: str,
  max_tokens: Optional[int] = None,
  temperature: float = 0.7,
                      ** kwargs) -> Dict[str, Any]:
"""Generate text using Llama3"""
await self._handle_rate_limit()

headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {self.api_key}'
        }

data = {
  'prompt': prompt,
  'temperature': temperature,
  'model': self.model,
  'stream': False
}

if max_tokens:
  data['max_tokens'] = max_tokens

if kwargs.get('top_p'):
  data['top_p'] = kwargs['top_p']

if kwargs.get('frequency_penalty'):
  data['frequency_penalty'] = kwargs['frequency_penalty']

if kwargs.get('presence_penalty'):
  data['presence_penalty'] = kwargs['presence_penalty']

if kwargs.get('stop'):
  data['stop'] = kwargs['stop']

try:
            async with self.session.post(
  f"{self.base_url}/v1/completions",
  headers = headers,
  json = data
) as response:
if response.status != 200:
  error_data = await response.json()
                    raise Exception(f"Llama3 API error: {error_data}")

return await response.json()
                
        except Exception as e:
print(f"Error calling Llama3: {e}")
raise
            
    async def embed(self, text: str) -> List[float]:
"""Generate embeddings using Llama3"""
await self._handle_rate_limit()

headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {self.api_key}'
        }

data = {
  'input': text,
  'model': f"{self.model}-embedding"
        }

try:
            async with self.session.post(
  f"{self.base_url}/v1/embeddings",
  headers = headers,
  json = data
) as response:
if response.status != 200:
  error_data = await response.json()
                    raise Exception(f"Llama3 Embedding API error: {error_data}")

result = await response.json()
return result['embeddings'][0]
                
        except Exception as e:
print(f"Error getting embeddings from Llama3: {e}")
raise
            
    async def batch_process(self, texts: List[str]) -> List[Dict[str, Any]]:
"""Process multiple texts in batches"""
results = []
for i in range(0, len(texts), self.batch_size):
  batch = texts[i: i + self.batch_size]
batch_results = await asyncio.gather(
                * [self.generate(text) for text in batch],
return_exceptions = True
            )
            
            # Filter out any errors from the batch
valid_results = [
  result for result in batch_results 
                if not isinstance(result, Exception)
            ]
results.extend(valid_results)

return results
        
    async def stream_generate(self, prompt: str, ** kwargs) -> AsyncIterator[str]:
"""Stream generation results"""
headers = {
  'Content-Type': 'application/json',
  'Authorization': f'Bearer {self.api_key}'
        }

data = {
  'prompt': prompt,
  'model': self.model,
  'stream': True,
            ** kwargs
        }
        
        async with self.session.post(
    f"{self.base_url}/v1/completions",
    headers = headers,
    json = data
  ) as response:
            async for line in response.content:
  if line:
    try:
chunk = json.loads(line.decode('utf-8'))
if chunk.get('choices'):
  yield chunk['choices'][0]['text']
                    except json.JSONDecodeError:
continue

# Example usage:
"""
config = {
  'api_key': 'your-api-key',
  'base_url': 'http://localhost:8080',
  'model': 'llama3-7b',
  'batch_size': 32
}

async def main():
llama = Llama3Adapter(config)
    
    # Single generation
response = await llama.generate(
  prompt = "What is artificial intelligence?",
  max_tokens = 100,
  temperature = 0.7
)
print(response['choices'][0]['text'])
    
    # Batch processing
texts = [
  "What is machine learning?",
  "Explain neural networks",
  "Describe deep learning"
]
batch_results = await llama.batch_process(texts)
    
    # Streaming generation
    async for chunk in llama.stream_generate(
  prompt = "Tell me a story",
  max_tokens = 200
):
  print(chunk, end = '', flush = True)

if __name__ == "__main__":
  asyncio.run(main())
"""