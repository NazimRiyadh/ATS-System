
import os
import shutil
import asyncio
import json
import re
from typing import List, Dict
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import gpt_4o_complete, gpt_4o_mini_complete
from .config import Config
from .rag_engine import initialize_rag

# Modified Cache: Key: job_id, Value: List[Dict] with 'name' and 'text'
_job_shortlists: Dict[str, List[Dict[str, str]]] = {}

# Global RAG Instance Cache
_global_rag: LightRAG = None

async def get_global_rag() -> LightRAG:
    """
    Returns the singleton Global LightRAG instance.
    """
    global _global_rag
    if _global_rag is None:
        print("Initializing Global RAG instance...")
        _global_rag = await initialize_rag()
    return _global_rag

async def process_top_candidates(job_id: str, top_20_texts: List[str]):
    """
    Stage 2: The "Context Filter".
    Now stores BOTH Name and Resume Text to prevent hallucination.
    """
    print(f"Assigning {len(top_20_texts)} candidates to Job {job_id} context...")
    
    candidates_data = []
    for text in top_20_texts:
        # Extract Name
        match = re.search(r"Name:\s*(.*)", text)
        if match:
            name = match.group(1).strip()
        else:
            name = text[:30].replace('\n', ' ').strip() + "..."
            
        candidates_data.append({"name": name, "text": text})
            
    _job_shortlists[job_id] = candidates_data
    print(f"Job {job_id} Context Set ({len(candidates_data)} profiles cached).")
    
    return "Context Set"

async def chat_with_shortlist(job_id: str, user_question: str, mode: str = "mix") -> str:
    """
    Stage 3: The "Chat Interface".
    Supports multiple retrieval modes with automatic fallback to naive mode.
    
    Args:
        job_id: Unique identifier for the job
        user_question: User's question/query
        mode: Retrieval mode (naive, local, global, hybrid, mix)
        
    Returns:
        LLM-generated response based on retrieved context
    """
    rag = await get_global_rag()
    
    candidates = _job_shortlists.get(job_id, [])
    if not candidates:
        print(f"Warning: No shortlist found for Job {job_id}.")
        context_prompt = ""
    else:
        # Build a robust context block with injected profiles
        context_prompt = "You are an ATS Assistant. Answer strictly based on the following profiles and any retrieved context. Cite which source you used.\n\n"
        context_prompt += "=== INJECTED PROFILES ===\n"
        for c in candidates:
            # Clean text slightly to save tokens
            clean_text = c['text'].replace('\n\n', '\n')[:1000]  # Cap at 1000 chars per candidate
            context_prompt += f"[Source: Injected Profile] NAME: {c['name']}\n{clean_text}\n\n"
        
        context_prompt += "=== END OF INJECTED PROFILES ===\n"
        context_prompt += f"Question: {user_question}\n"
        context_prompt += "Answer:"

    # Validate mode
    valid_modes = ["naive", "local", "global", "hybrid", "mix"]
    if mode not in valid_modes:
        print(f"⚠️  Invalid mode '{mode}', defaulting to 'mix'")
        mode = "mix"
    
    print(f"🔍 Querying with mode='{mode}' ({len(context_prompt)} chars context)...")
    
    try:
        # Attempt query with specified mode
        response = await rag.aquery(context_prompt, param=QueryParam(mode=mode))
        
        if response is None:
            raise ValueError("Query returned None response")
        
        print(f"✅ Query succeeded with mode='{mode}'")
        return response
        
    except Exception as e:
        print(f"⚠️  Mode '{mode}' failed: {e}")
        
        # Automatic fallback to naive mode if mix/hybrid/local/global fails
        if mode != "naive":
            print(f"🔄 Falling back to mode='naive'...")
            try:
                response = await rag.aquery(context_prompt, param=QueryParam(mode="naive"))
                
                if response is None:
                    raise ValueError("Naive mode also returned None")
                
                print(f"✅ Fallback to naive mode succeeded")
                return response
                
            except Exception as fallback_error:
                print(f"❌ Naive mode fallback also failed: {fallback_error}")
                return f"System Error: Unable to generate response. Both {mode} and naive modes failed. Please check the database and ensure data has been ingested."
        else:
            # Even naive mode failed
            return "System Warning: No response generated. This typically happens if the database is empty. Please run ingestion to populate the Knowledge Graph."


async def clear_job_data(job_id: str):
    """
    Cleanup: Just removes the shortlist from memory.
    """
    if job_id in _job_shortlists:
        del _job_shortlists[job_id]
    print(f"Cleared context for Job {job_id}")

