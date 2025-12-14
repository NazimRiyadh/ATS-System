"""
LightRAG configuration and initialization.
Sets up LightRAG with PostgreSQL vector storage and Neo4j graph storage.
"""

import os
import logging
from typing import Optional

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc

from .config import settings
from .llm_adapter import ollama_llm_func
from .embedding import embedding_func, get_embedding_model
from .reranker import rerank_func
from .prompts import ATS_ENTITY_EXTRACTION_PROMPT

logger = logging.getLogger(__name__)


def _setup_environment():
    """Set environment variables for LightRAG storage backends."""
    # Neo4j configuration via environment variables
    os.environ["NEO4J_URI"] = settings.neo4j_uri
    os.environ["NEO4J_USERNAME"] = settings.neo4j_username
    os.environ["NEO4J_PASSWORD"] = settings.neo4j_password
    
    # PostgreSQL configuration
    os.environ["POSTGRES_HOST"] = settings.postgres_host
    os.environ["POSTGRES_PORT"] = str(settings.postgres_port)
    os.environ["POSTGRES_USER"] = settings.postgres_user
    os.environ["POSTGRES_PASSWORD"] = settings.postgres_password
    os.environ["POSTGRES_DATABASE"] = settings.postgres_db


class RAGManager:
    """Manages LightRAG instance lifecycle."""
    
    def __init__(self):
        self._rag: Optional[LightRAG] = None
        self._initialized = False
    
    async def initialize(self) -> LightRAG:
        """Initialize LightRAG with dual storage configuration."""
        if self._initialized and self._rag is not None:
            return self._rag
        
        logger.info("Initializing LightRAG...")
        
        # Ensure working directory exists
        os.makedirs(settings.rag_working_dir, exist_ok=True)
        
        # Create embedding function wrapper for LightRAG
        embedding_model = get_embedding_model()
        
        async def _embedding_func(texts):
            """Wrapper to match LightRAG's expected signature."""
            return await embedding_func(texts)
        
        try:
            # Set up environment variables for database connections
            _setup_environment()
            
            # Initialize LightRAG with PostgreSQL (vectors) and Neo4j (graph)
            self._rag = LightRAG(
                working_dir=settings.rag_working_dir,
                
                # LLM Configuration (Ollama)
                llm_model_func=ollama_llm_func,
                
                # Embedding Configuration
                embedding_func=EmbeddingFunc(
                    embedding_dim=settings.embedding_dim,
                    max_token_size=settings.embedding_max_tokens,
                    func=_embedding_func
                ),
                
                # Storage Configuration - Use PostgreSQL and Neo4j
                kv_storage="PGKVStorage",                    # PostgreSQL for key-value
                vector_storage="PGVectorStorage",            # PostgreSQL + pgvector for vectors
                graph_storage="Neo4JStorage",                # Neo4j for knowledge graph
                
                # Chunking Configuration
                chunk_token_size=settings.chunk_token_size,
                chunk_overlap_token_size=settings.chunk_overlap_size,
            )
            
            # CRITICAL: Must call initialize_storages() before any operations
            # This initializes the _storage_lock and other async resources
            await self._rag.initialize_storages()
            
            self._initialized = True
            
            logger.info("✅ LightRAG initialized with PostgreSQL + Neo4j storage")
            return self._rag
            
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG: {e}")
            raise
    
    @property
    def rag(self) -> LightRAG:
        """Get the LightRAG instance (must be initialized first)."""
        if not self._initialized or self._rag is None:
            raise RuntimeError("RAG not initialized. Call initialize() first.")
        return self._rag
    
    async def close(self):
        """Cleanup resources."""
        if self._rag is not None:
            # Close any open connections
            self._initialized = False
            self._rag = None
            logger.info("LightRAG resources cleaned up")


# Global RAG manager instance
_rag_manager: Optional[RAGManager] = None


def get_rag_manager() -> RAGManager:
    """Get or create global RAG manager."""
    global _rag_manager
    if _rag_manager is None:
        _rag_manager = RAGManager()
    return _rag_manager


async def get_rag() -> LightRAG:
    """Get initialized RAG instance."""
    manager = get_rag_manager()
    return await manager.initialize()


# Query parameter presets for different use cases
QUERY_PRESETS = {
    "naive": QueryParam(mode="naive"),
    "local": QueryParam(mode="local"),
    "global": QueryParam(mode="global"),
    "hybrid": QueryParam(mode="hybrid"),
    "mix": QueryParam(mode="mix"),
}


def get_query_param(mode: str = "mix") -> QueryParam:
    """Get QueryParam for specified mode."""
    return QUERY_PRESETS.get(mode, QUERY_PRESETS["mix"])
