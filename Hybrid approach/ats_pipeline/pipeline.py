"""
Main ATS Pipeline Orchestrator
"""
from typing import List, Optional
from .parser import get_parser
from .embeddings import get_embedding_service
from .graph_db import get_graph_db
from .search_engine import get_search_engine
from .ranker import get_ranker
from .models import CandidateProfile, JobRequirement, SearchFilters, CandidateMatch
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ATSPipeline:
    """Main orchestrator for the ATS system"""
    
    def __init__(self):
        self.parser = get_parser()
        self.embedding_service = get_embedding_service()
        self.graph_db = get_graph_db()
        self.search_engine = get_search_engine()
        self.ranker = get_ranker()
        
        # Try to create vector index
        self.vector_index_available = self.graph_db.create_vector_index()
    
    def ingest_candidate(self, resume_text: str) -> str:
        """
        Ingest a candidate from resume text
        
        Args:
            resume_text: Raw resume text
            
        Returns:
            Candidate ID
        """
        logger.info("=" * 60)
        logger.info("CANDIDATE INGESTION PIPELINE")
        logger.info("=" * 60)
        
        # Step 1: Parse resume
        logger.info("Step 1/3: Parsing resume...")
        profile = self.parser.parse_resume(resume_text)
        
        # Step 2: Generate embedding
        logger.info("Step 2/3: Generating embedding...")
        embedding = self.embedding_service.get_embedding(profile.summary)
        
        # Step 3: Store in graph database
        logger.info("Step 3/3: Storing in database...")
        candidate_id = self.graph_db.add_candidate(profile, embedding)
        
        logger.info("=" * 60)
        logger.info(f"✅ INGESTION COMPLETE - ID: {candidate_id}")
        logger.info("=" * 60)
        
        return candidate_id
    
    def search_candidates(
        self,
        job_description: str,
        filters: Optional[SearchFilters] = None,
        use_llm_explanations: bool = True
    ) -> List[CandidateMatch]:
        """
        Search for candidates matching a job description
        
        Args:
            job_description: Job description text
            filters: Optional search filters
            use_llm_explanations: Whether to generate LLM explanations
            
        Returns:
            Ranked list of candidate matches
        """
        logger.info("=" * 60)
        logger.info("CANDIDATE SEARCH PIPELINE")
        logger.info("=" * 60)
        
        # Step 1: Parse job description
        logger.info("Step 1/5: Parsing job description...")
        job_req = self.parser.parse_job_description(job_description)
        
        # Step 2: Create filters from job requirements if not provided
        if filters is None:
            filters = SearchFilters(
                required_skills=job_req.required_skills,
                min_years_experience=job_req.min_years_experience,
                location=job_req.location
            )
        
        # Step 3: Hybrid search
        logger.info("Step 2/5: Performing hybrid search...")
        strategy = "hybrid" if self.vector_index_available else "graph_only"
        matches = self.search_engine.search(
            job_description,
            filters=filters,
            strategy=strategy
        )
        
        if not matches:
            logger.warning("No candidates found matching criteria")
            return []
        
        # Step 4: Calculate final scores
        logger.info("Step 3/5: Calculating scores...")
        matches = self.ranker.calculate_final_scores(matches, job_req)
        
        # Step 5: Add LLM explanations
        if use_llm_explanations:
            logger.info("Step 4/5: Generating explanations...")
            matches = self.ranker.add_llm_explanations(matches, job_description)
        
        logger.info("=" * 60)
        logger.info(f"✅ SEARCH COMPLETE - Found {len(matches)} matches")
        logger.info("=" * 60)
        
        return matches
    
    def batch_ingest(self, resume_texts: List[str]) -> List[str]:
        """
        Ingest multiple candidates in batch
        
        Args:
            resume_texts: List of resume texts
            
        Returns:
            List of candidate IDs
        """
        logger.info("=" * 60)
        logger.info(f"BATCH INGESTION - {len(resume_texts)} candidates")
        logger.info("=" * 60)
        
        candidate_ids = []
        for i, resume_text in enumerate(resume_texts, 1):
            logger.info(f"\nProcessing candidate {i}/{len(resume_texts)}...")
            try:
                candidate_id = self.ingest_candidate(resume_text)
                candidate_ids.append(candidate_id)
            except Exception as e:
                logger.error(f"Failed to ingest candidate {i}: {e}")
                continue
        
        logger.info("=" * 60)
        logger.info(f"✅ BATCH COMPLETE - {len(candidate_ids)}/{len(resume_texts)} successful")
        logger.info("=" * 60)
        
        return candidate_ids
    
    def get_stats(self) -> dict:
        """Get system statistics"""
        db_stats = self.graph_db.get_database_stats()
        cache_stats = self.embedding_service.get_cache_stats()
        
        return {
            "database": db_stats,
            "embedding_cache": cache_stats,
            "vector_index_available": self.vector_index_available
        }
    
    def close(self):
        """Close all connections"""
        self.graph_db.close()
        logger.info("Pipeline closed")

# Global instance
_pipeline: Optional[ATSPipeline] = None

def get_pipeline() -> ATSPipeline:
    """Get or create the global pipeline instance"""
    global _pipeline
    if _pipeline is None:
        _pipeline = ATSPipeline()
    return _pipeline
