"""
Custom dual-level retrieval combining vector search with knowledge graph queries.
Implements fallback mechanisms for robust retrieval.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from lightrag import LightRAG, QueryParam

from .config import settings
from .prompts import CHAT_RESPONSE_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Container for retrieval results with source attribution."""
    response: str
    mode_used: str
    sources: Dict[str, Any]
    fallback_used: bool = False


@dataclass
class CandidateContext:
    """Context for a shortlisted candidate."""
    name: str
    content: str
    score: float
    metadata: Dict[str, Any]


class DualLevelRetrieval:
    """
    Custom dual-level retrieval system combining:
    1. Vector search for semantic similarity
    2. Knowledge graph queries for entity/relationship context
    3. Automatic fallback on mode failures
    """
    
    # Fallback chain from most sophisticated to simplest
    FALLBACK_CHAIN = ["mix", "hybrid", "local", "naive"]
    
    def __init__(self, rag: LightRAG):
        self.rag = rag
    
    async def query_with_mode(
        self,
        query: str,
        mode: str = "mix"
    ) -> Tuple[Optional[str], str]:
        """
        Query using specified mode with error handling.
        
        Args:
            query: Search query
            mode: Retrieval mode
            
        Returns:
            Tuple of (response, mode_used)
        """
        try:
            response = await self.rag.aquery(
                query,
                param=QueryParam(mode=mode)
            )
            if response:
                logger.info(f"✅ Query succeeded with mode: {mode}")
                return response, mode
            else:
                logger.warning(f"Mode '{mode}' returned empty response")
                return None, mode
                
        except Exception as e:
            logger.warning(f"Mode '{mode}' failed: {e}")
            return None, mode
    
    async def query_with_fallback(
        self,
        query: str,
        preferred_mode: str = "mix"
    ) -> RetrievalResult:
        """
        Query with automatic fallback through mode chain.
        
        Args:
            query: Search query
            preferred_mode: Initial mode to try
            
        Returns:
            RetrievalResult with response and metadata
        """
        # Build fallback chain starting with preferred mode
        if preferred_mode in self.FALLBACK_CHAIN:
            start_idx = self.FALLBACK_CHAIN.index(preferred_mode)
            fallback_chain = self.FALLBACK_CHAIN[start_idx:]
        else:
            fallback_chain = [preferred_mode] + self.FALLBACK_CHAIN
        
        sources = {"attempted_modes": [], "errors": []}
        
        for mode in fallback_chain:
            sources["attempted_modes"].append(mode)
            response, used_mode = await self.query_with_mode(query, mode)
            
            if response:
                return RetrievalResult(
                    response=response,
                    mode_used=used_mode,
                    sources=sources,
                    fallback_used=(used_mode != preferred_mode)
                )
        
        # All modes failed - return error
        logger.error("All retrieval modes failed")
        return RetrievalResult(
            response="Unable to retrieve relevant information. Please try rephrasing your query.",
            mode_used="none",
            sources=sources,
            fallback_used=True
        )
    
    async def dual_level_query(
        self,
        query: str,
        candidates: Optional[List[CandidateContext]] = None,
        mode: str = "mix"
    ) -> RetrievalResult:
        """
        Perform dual-level retrieval combining multiple sources.
        
        This method:
        1. Queries LightRAG (which internally uses vector + graph)
        2. Optionally injects candidate context
        3. Aggregates results with source attribution
        
        Args:
            query: User query
            candidates: Optional pre-shortlisted candidates
            mode: Preferred retrieval mode
            
        Returns:
            RetrievalResult with aggregated context
        """
        sources = {
            "vector_context": "",
            "graph_context": "",
            "candidate_context": "",
            "context_lengths": {}
        }
        
        # Step 1: Query LightRAG with fallback
        rag_result = await self.query_with_fallback(query, mode)
        sources["vector_context"] = rag_result.response
        sources["context_lengths"]["rag"] = len(rag_result.response)
        
        # Step 2: Add candidate context if provided
        if candidates:
            candidate_texts = []
            for c in candidates:
                candidate_texts.append(
                    f"**{c.name}** (Score: {c.score:.2f}):\n{c.content[:500]}..."
                )
            sources["candidate_context"] = "\n\n".join(candidate_texts)
            sources["context_lengths"]["candidates"] = len(sources["candidate_context"])
        
        # Step 3: Aggregate context
        total_context = self._aggregate_context(sources)
        sources["context_lengths"]["total"] = len(total_context)
        
        # Log retrieval stats
        self._log_retrieval_stats(sources)
        
        return RetrievalResult(
            response=total_context,
            mode_used=rag_result.mode_used,
            sources=sources,
            fallback_used=rag_result.fallback_used
        )
    
    def _aggregate_context(self, sources: Dict[str, Any]) -> str:
        """Combine multiple context sources into unified context."""
        parts = []
        
        if sources.get("vector_context"):
            parts.append("## Retrieved Information\n" + sources["vector_context"])
        
        if sources.get("candidate_context"):
            parts.append("## Shortlisted Candidates\n" + sources["candidate_context"])
        
        return "\n\n".join(parts)
    
    def _log_retrieval_stats(self, sources: Dict[str, Any]) -> None:
        """Log retrieval statistics."""
        lengths = sources.get("context_lengths", {})
        logger.info(
            f"🔍 Dual-Level Retrieval:\n"
            f"  📊 RAG: {lengths.get('rag', 0)} chars\n"
            f"  📋 Candidates: {lengths.get('candidates', 0)} chars\n"
            f"  ✅ Total: {lengths.get('total', 0)} chars"
        )


async def chat_with_dual_retrieval(
    rag: LightRAG,
    query: str,
    candidates: Optional[List[CandidateContext]] = None,
    mode: str = "mix"
) -> Dict[str, Any]:
    """
    High-level function for chat with dual-level retrieval.
    
    Args:
        rag: LightRAG instance
        query: User question
        candidates: Optional shortlisted candidates
        mode: Retrieval mode
        
    Returns:
        Dict with response and metadata
    """
    retrieval = DualLevelRetrieval(rag)
    result = await retrieval.dual_level_query(query, candidates, mode)
    
    return {
        "response": result.response,
        "mode_used": result.mode_used,
        "fallback_used": result.fallback_used,
        "sources": result.sources.get("context_lengths", {})
    }
