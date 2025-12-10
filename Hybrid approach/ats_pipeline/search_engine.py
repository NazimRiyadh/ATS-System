"""
Hybrid Search Engine combining Vector and Graph approaches
"""
from typing import List, Dict, Any, Optional
from .config import Config
from .models import SearchFilters, CandidateMatch, JobRequirement
from .graph_db import get_graph_db
from .embeddings import get_embedding_service
import logging

logger = logging.getLogger(__name__)

class HybridSearchEngine:
    """Combines vector similarity search with graph-based filtering"""
    
    def __init__(self):
        self.graph_db = get_graph_db()
        self.embedding_service = get_embedding_service()
    
    def search(
        self,
        query_text: str,
        filters: Optional[SearchFilters] = None,
        strategy: str = "hybrid"
    ) -> List[CandidateMatch]:
        """
        Search for candidates using hybrid approach
        
        Args:
            query_text: Job description or search query
            filters: Optional search filters
            strategy: Search strategy - "hybrid", "vector_only", or "graph_only"
            
        Returns:
            List of candidate matches with scores
        """
        if strategy == "vector_only":
            return self._vector_only_search(query_text)
        elif strategy == "graph_only":
            return self._graph_only_search(filters or SearchFilters())
        else:
            return self._hybrid_search(query_text, filters)
    
    def _hybrid_search(
        self,
        query_text: str,
        filters: Optional[SearchFilters]
    ) -> List[CandidateMatch]:
        """
        Hybrid search: Vector search first, then graph filtering
        """
        logger.info("🔍 Starting hybrid search...")
        
        # Step 1: Vector similarity search
        query_embedding = self.embedding_service.get_embedding(query_text)
        vector_results = self.graph_db.vector_search(
            query_embedding,
            top_k=Config.VECTOR_TOP_K
        )
        
        if not vector_results:
            logger.warning("No results from vector search, falling back to graph search")
            if filters:
                return self._graph_only_search(filters)
            return []
        
        logger.info(f"  Vector search found {len(vector_results)} candidates")
        
        # Step 2: Apply graph filters if provided
        if filters:
            filtered_results = self._apply_graph_filters(vector_results, filters)
            logger.info(f"  After graph filtering: {len(filtered_results)} candidates")
        else:
            filtered_results = vector_results
        
        # Step 3: Convert to CandidateMatch objects
        matches = []
        for result in filtered_results:
            # Get candidate skills for matching
            skills = self.graph_db.get_candidate_skills(result['id'])
            
            match = CandidateMatch(
                candidate_id=result['id'],
                name=result['name'],
                summary=result['summary'],
                total_experience=result.get('total_experience', 0.0),
                matched_skills=skills,
                vector_score=result.get('vector_score', 0.0)
            )
            matches.append(match)
        
        # Step 4: Calculate additional scores
        if filters and filters.required_skills:
            for match in matches:
                match.skill_match_score = self._calculate_skill_match(
                    match.matched_skills,
                    filters.required_skills
                )
        
        # Sort by vector score
        matches.sort(key=lambda x: x.vector_score, reverse=True)
        
        return matches[:Config.FINAL_TOP_K]
    
    def _vector_only_search(self, query_text: str) -> List[CandidateMatch]:
        """Vector similarity search only"""
        logger.info("🔍 Vector-only search...")
        
        query_embedding = self.embedding_service.get_embedding(query_text)
        results = self.graph_db.vector_search(query_embedding, top_k=Config.FINAL_TOP_K)
        
        matches = []
        for result in results:
            skills = self.graph_db.get_candidate_skills(result['id'])
            match = CandidateMatch(
                candidate_id=result['id'],
                name=result['name'],
                summary=result['summary'],
                total_experience=result.get('total_experience', 0.0),
                matched_skills=skills,
                vector_score=result.get('vector_score', 0.0)
            )
            matches.append(match)
        
        return matches
    
    def _graph_only_search(self, filters: SearchFilters) -> List[CandidateMatch]:
        """Graph-based search only"""
        logger.info("🔍 Graph-only search...")
        
        results = self.graph_db.graph_search(filters, limit=Config.FINAL_TOP_K)
        
        matches = []
        for result in results:
            skills = self.graph_db.get_candidate_skills(result['id'])
            
            match = CandidateMatch(
                candidate_id=result['id'],
                name=result['name'],
                summary=result['summary'],
                total_experience=result.get('total_experience', 0.0),
                matched_skills=skills
            )
            
            if filters.required_skills:
                match.skill_match_score = self._calculate_skill_match(
                    skills,
                    filters.required_skills
                )
            
            matches.append(match)
        
        return matches
    
    def _apply_graph_filters(
        self,
        vector_results: List[Dict[str, Any]],
        filters: SearchFilters
    ) -> List[Dict[str, Any]]:
        """Apply graph-based filters to vector search results"""
        filtered = []
        
        for result in vector_results:
            # Experience filter
            if filters.min_years_experience > 0:
                if result.get('total_experience', 0) < filters.min_years_experience:
                    continue
            
            if filters.max_years_experience:
                if result.get('total_experience', 0) > filters.max_years_experience:
                    continue
            
            # Location filter
            if filters.location:
                candidate_location = result.get('location', '').lower()
                if filters.location.lower() not in candidate_location:
                    continue
            
            # Skills filter
            if filters.required_skills:
                candidate_skills = self.graph_db.get_candidate_skills(result['id'])
                candidate_skills_lower = [s.lower() for s in candidate_skills]
                
                # Check if candidate has all required skills
                has_all_skills = all(
                    any(req.lower() in skill for skill in candidate_skills_lower)
                    for req in filters.required_skills
                )
                
                if not has_all_skills:
                    continue
            
            filtered.append(result)
        
        return filtered
    
    def _calculate_skill_match(
        self,
        candidate_skills: List[str],
        required_skills: List[str]
    ) -> float:
        """Calculate skill match percentage"""
        if not required_skills:
            return 1.0
        
        candidate_skills_lower = [s.lower() for s in candidate_skills]
        matched = 0
        
        for req_skill in required_skills:
            if any(req_skill.lower() in skill for skill in candidate_skills_lower):
                matched += 1
        
        return matched / len(required_skills)

# Global instance
_search_engine: Optional[HybridSearchEngine] = None

def get_search_engine() -> HybridSearchEngine:
    """Get or create the global search engine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = HybridSearchEngine()
    return _search_engine
