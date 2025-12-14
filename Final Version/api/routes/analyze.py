"""
Job analysis endpoint for candidate shortlisting.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any

from fastapi import APIRouter, HTTPException

from api.models import (
    JobAnalysisRequest,
    JobAnalysisResponse,
    CandidatePreview
)
from src.rag_config import get_rag, get_query_param
from src.reranker import rerank_func

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["Analysis"])

# In-memory job context storage (use Redis/DB in production)
_job_contexts: Dict[str, Dict[str, Any]] = {}


def get_job_context(job_id: str) -> Dict[str, Any]:
    """Get stored job context."""
    return _job_contexts.get(job_id, {})


def store_job_context(job_id: str, context: Dict[str, Any]) -> None:
    """Store job context for later chat queries."""
    _job_contexts[job_id] = context


@router.post("", response_model=JobAnalysisResponse)
async def analyze_job(request: JobAnalysisRequest):
    """
    Analyze a job description and find top matching candidates.
    
    Stage 1 of the two-stage retrieval process:
    1. Vector search to find semantically similar candidates
    2. Optional reranking for precision
    
    Results are cached for subsequent chat queries.
    """
    start_time = datetime.now()
    
    try:
        # Get RAG instance
        rag = await get_rag()
        
        # Perform initial retrieval using naive mode for speed
        logger.info(f"Analyzing job: {request.job_id}")
        
        # Query using LightRAG's vector search
        response = await rag.aquery(
            request.query,
            param=get_query_param("naive")
        )
        
        # Parse response to extract candidate information
        # Note: In production, you'd have structured data from the vector DB
        candidates = parse_candidates_from_response(response, request.top_k)
        
        # Store context for chat queries
        store_job_context(request.job_id, {
            "query": request.query,
            "candidates": candidates,
            "created_at": datetime.now().isoformat(),
            "top_k": request.top_k
        })
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return JobAnalysisResponse(
            job_id=request.job_id,
            candidates_found=len(candidates),
            candidates=candidates,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Job analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}")
async def get_job_analysis(job_id: str):
    """
    Get stored job analysis results.
    """
    context = get_job_context(job_id)
    
    if not context:
        raise HTTPException(
            status_code=404,
            detail=f"Job analysis not found: {job_id}"
        )
    
    return {
        "job_id": job_id,
        "query": context.get("query", ""),
        "candidates_found": len(context.get("candidates", [])),
        "candidates": context.get("candidates", []),
        "created_at": context.get("created_at")
    }


@router.delete("/{job_id}")
async def delete_job_analysis(job_id: str):
    """
    Delete stored job analysis.
    """
    if job_id in _job_contexts:
        del _job_contexts[job_id]
        return {"message": f"Job analysis deleted: {job_id}"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Job analysis not found: {job_id}"
        )


def parse_candidates_from_response(
    response: str,
    top_k: int
) -> List[CandidatePreview]:
    """
    Parse LightRAG response to extract candidate information.
    
    This is a simplified parser - in production you'd have
    structured data from the vector database.
    """
    candidates = []
    
    if not response:
        return candidates
    
    # Split response into sections (heuristic parsing)
    sections = response.split("\n\n")
    
    for i, section in enumerate(sections[:top_k]):
        if not section.strip():
            continue
        
        # Extract name (first line or default)
        lines = section.strip().split("\n")
        name = lines[0].strip("# *-").strip() if lines else f"Candidate {i+1}"
        
        # Generate score based on position (simplified)
        score = 1.0 - (i * 0.05)  # Decrease by 5% per position
        
        # Extract highlights (remaining lines)
        highlights = [l.strip("- ").strip() for l in lines[1:4] if l.strip()]
        
        candidates.append(CandidatePreview(
            name=name,
            score=round(score, 2),
            highlights=highlights
        ))
    
    return candidates
