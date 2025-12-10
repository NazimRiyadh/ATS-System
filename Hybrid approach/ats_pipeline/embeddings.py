"""
Vector embedding service with caching support
"""
from typing import List, Dict, Optional
import hashlib
import json
from openai import OpenAI
from .config import Config

class EmbeddingService:
    """Service for generating and caching text embeddings"""
    
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.cache: Dict[str, List[float]] = {}
        self.model = Config.EMBEDDING_MODEL
        
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Get embedding for a single text
        
        Args:
            text: Text to embed
            use_cache: Whether to use cache
            
        Returns:
            List of floats representing the embedding
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Check cache
        if use_cache and Config.ENABLE_CACHE:
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                return self.cache[cache_key]
        
        # Generate embedding
        response = self.client.embeddings.create(
            input=text,
            model=self.model
        )
        
        embedding = response.data[0].embedding
        
        # Cache result
        if use_cache and Config.ENABLE_CACHE:
            self.cache[cache_key] = embedding
        
        return embedding
    
    def get_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """
        Get embeddings for multiple texts in batch
        
        Args:
            texts: List of texts to embed
            use_cache: Whether to use cache
            
        Returns:
            List of embeddings
        """
        if not texts:
            return []
        
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            if use_cache and Config.ENABLE_CACHE:
                cache_key = self._get_cache_key(text)
                if cache_key in self.cache:
                    embeddings.append(self.cache[cache_key])
                    continue
            
            texts_to_embed.append(text)
            indices_to_embed.append(i)
            embeddings.append(None)  # Placeholder
        
        # Generate embeddings for uncached texts
        if texts_to_embed:
            response = self.client.embeddings.create(
                input=texts_to_embed,
                model=self.model
            )
            
            for i, embedding_data in enumerate(response.data):
                original_index = indices_to_embed[i]
                embedding = embedding_data.embedding
                embeddings[original_index] = embedding
                
                # Cache result
                if use_cache and Config.ENABLE_CACHE:
                    cache_key = self._get_cache_key(texts_to_embed[i])
                    self.cache[cache_key] = embedding
        
        return embeddings
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cached_embeddings": len(self.cache),
            "cache_size_mb": len(json.dumps(self.cache)) / (1024 * 1024)
        }

# Global instance
_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    """Get or create the global embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
