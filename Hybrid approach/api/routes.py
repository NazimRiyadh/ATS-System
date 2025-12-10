"""
API Routes for ATS Pipeline
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from ats_pipeline import get_pipeline, SearchFilters, CandidateMatch
from ats_pipeline.feedback import get_feedback_system
from ats_pipeline.rag import get_rag_chatbot
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Request Models
class SearchRequest(BaseModel):
    query: str
    filters: Optional[SearchFilters] = None
    use_llm_explanations: bool = True

class IngestRequest(BaseModel):
    text: str

class FeedbackRequest(BaseModel):
    candidate_id: str
    query: str
    action: str  # "click", "like", "dislike"

class ChatRequest(BaseModel):
    candidate_id: str
    message: str

# Routes
@router.post("/search", response_model=List[CandidateMatch])
async def search_candidates(request: SearchRequest):
    """Search for candidates"""
    try:
        pipeline = get_pipeline()
        matches = pipeline.search_candidates(
            request.query,
            filters=request.filters,
            use_llm_explanations=request.use_llm_explanations
        )
        return matches
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ingest")
async def ingest_candidate(request: IngestRequest):
    """Ingest a candidate from text"""
    try:
        pipeline = get_pipeline()
        candidate_id = pipeline.ingest_candidate(request.text)
        return {"status": "success", "candidate_id": candidate_id}
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback"""
    try:
        feedback_sys = get_feedback_system()
        feedback_sys.record_feedback(
            request.candidate_id, 
            request.query, 
            request.action
        )
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        logger.error(f"Feedback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_candidate(request: ChatRequest):
    """Chat with a candidate's profile"""
    try:
        rag = get_rag_chatbot()
        response = rag.chat(request.candidate_id, request.message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
