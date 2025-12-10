import os
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

from src.rag_engine import initialize_rag
from src.job_manager import process_top_candidates, chat_with_shortlist
from rank_candidates import retrieve_candidates_vector_only
from lightrag.utils import logger
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ATS_API")

# Models
class JobAnalysisRequest(BaseModel):
    query: str
    job_id: str
    top_k: Optional[int] = 20

class JobChatRequest(BaseModel):
    job_id: str
    message: str

class Candidate(BaseModel):
    source_file: str
    resume_text: str
    # Add other fields as necessary

# Context Manager for Startup/Shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
# Startup
    logger.info("Initializing Global LightRAG for Vector Search...")
    global rag_instance
    rag_instance = await initialize_rag()
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(title="LightRAG ATS API", lifespan=lifespan)

@app.post("/analyze_job")
async def analyze_job(request: JobAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Stage 1 & 2 Trigger:
    1. Vector Search (Fast Filter) -> Top 20
    2. Build Ephemeral Graph (Deep Index)
    """
    if not request.query or not request.job_id:
        raise HTTPException(status_code=400, detail="Query and Job ID are required")
        
    try:
        # Stage 1: Fast Filter (Vector Only)
        logger.info(f"Starting Vector Search for Job {request.job_id}...")
        candidates = await retrieve_candidates_vector_only(request.query, top_k=request.top_k)
        
        if not candidates:
            return {"status": "completed", "candidates_found": 0, "message": "No candidates found."}
            
        # Extract texts for Stage 2
        candidate_texts = [c['resume_text'] for c in candidates]
        
        # Stage 2: Deep Index (Background Task or Await?)
        # The user's protocol says "Wait Condition: Ensure indexing is complete... before allowing user queries."
        # So we should await it here to ensure the user can chat immediately after.
        logger.info(f"Starting Deep Indexing for {len(candidates)} candidates...")
        await process_top_candidates(request.job_id, candidate_texts)
        
        return {
            "status": "completed",
            "job_id": request.job_id,
            "candidates_found": len(candidates),
            "candidates_preview": [c['source_file'] for c in candidates],
            "message": "Graph built successfully. You can now use /chat_job."
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat_job")
async def chat_job(request: JobChatRequest):
    """
    Stage 3: Chat Interface (Reasoning)
    """
    try:
        response = await chat_with_shortlist(request.job_id, request.message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat_job: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_resume(file: UploadFile = File(...)):
    """
    Ingest a new resume (Simple save for now, similar to original app)
    """
    save_dir = os.environ.get('RESUMES_DIR', './resumes')
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        
    file_path = os.path.join(save_dir, file.filename)
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
            
        # LIVE INGESTION: Immediately index the file so it is searchable
        if rag_instance:
            logger.info(f"Auto-ingesting {file.filename} into RAG...")
            # We must read the text back to pass it to ainsert
            # (or use the content bytes decoded)
            text_content = content.decode('utf-8', errors='ignore')
            await rag_instance.ainsert(input=text_content, file_paths=[file_path])
            logger.info(f"✅ Auto-ingest complete for {file.filename}")
            
        return {"message": f"Saved and Ingested {file.filename}", "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
