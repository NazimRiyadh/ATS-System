"""
Ollama LLM adapter for LightRAG integration.
Provides async LLM function compatible with LightRAG's llm_model_func parameter.
"""

import asyncio
import logging
from typing import Optional, Union, List, Dict, Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings

logger = logging.getLogger(__name__)


class OllamaAdapter:
    """Async adapter for Ollama LLM API."""
    
    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None,
        timeout: float = 120.0
    ):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.llm_model
        self.max_tokens = max_tokens or settings.llm_max_tokens
        self.temperature = temperature or settings.llm_temperature
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(self.timeout)
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text using Ollama API.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters for the API
            
        Returns:
            Generated text response
        """
        client = await self._get_client()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
            }
        }
        
        try:
            response = await client.post("/api/chat", json=payload)
            response.raise_for_status()
            result = response.json()
            
            content = result.get("message", {}).get("content", "")
            logger.debug(f"LLM response length: {len(content)} chars")
            return content
            
        except httpx.HTTPError as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def check_health(self) -> bool:
        """Check if Ollama is available and model is loaded."""
        try:
            client = await self._get_client()
            response = await client.get("/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Check if our model is available
            if any(self.model in name for name in model_names):
                logger.info(f"✅ Ollama healthy, model '{self.model}' available")
                return True
            else:
                logger.warning(f"Model '{self.model}' not found. Available: {model_names}")
                return False
                
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False


# Global adapter instance
_ollama_adapter: Optional[OllamaAdapter] = None


def get_ollama_adapter() -> OllamaAdapter:
    """Get or create global Ollama adapter."""
    global _ollama_adapter
    if _ollama_adapter is None:
        _ollama_adapter = OllamaAdapter()
    return _ollama_adapter


async def ollama_llm_func(
    prompt: str,
    system_prompt: Optional[str] = None,
    history_messages: Optional[List[Dict[str, str]]] = None,
    **kwargs
) -> str:
    """
    LightRAG-compatible LLM function.
    
    This function signature matches what LightRAG expects for llm_model_func.
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt
        history_messages: Optional conversation history (not used currently)
        **kwargs: Additional parameters
        
    Returns:
        Generated text response
    """
    adapter = get_ollama_adapter()
    return await adapter.generate(prompt, system_prompt, **kwargs)


# For synchronous contexts
def ollama_llm_func_sync(
    prompt: str,
    system_prompt: Optional[str] = None,
    **kwargs
) -> str:
    """Synchronous wrapper for ollama_llm_func."""
    return asyncio.run(ollama_llm_func(prompt, system_prompt, **kwargs))
