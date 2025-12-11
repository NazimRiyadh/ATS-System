
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

async def chat_with_shortlist(job_id: str, user_question: str) -> str:
    """
    Stage 3: The "Chat Interface".
    Injects FULL RESUME TEXT into the prompt to force grounded answers.
    """
    rag = await get_global_rag()
    
    candidates = _job_shortlists.get(job_id, [])
    if not candidates:
        print(f"Warning: No shortlist found for Job {job_id}.")
        context_prompt = ""
    else:
        # Build a robust context block
        context_prompt = "You are an ATS Assistant. Answer strictly based on the following profiles and any retrieved context. Cite which source you used.\n\n"
        context_prompt += "=== INJECTED PROFILES ===\n"
        for c in candidates:
            # Clean text slightly to save tokens if needed
            clean_text = c['text'].replace('\n\n', '\n')[:1000] # Cap at 1000 chars per cand for hybrid mode
            context_prompt += f"[Source: Injected Profile] NAME: {c['name']}\n{clean_text}\n\n"
        
        context_prompt += "=== END OF INJECTED PROFILES ===\n"
        context_prompt += f"Question: {user_question}\n"
        context_prompt += "Answer:"

    # We bypass the 'hybrid' search for the context part because we INJECTED it.
    # But we still use RAG query to let it use the LLM.
    # Actually, if we inject context, we just need a direct LLM call?
    # No, keep using rag.aquery because it handles the LLM connection nicely, 
    # but we might want 'local' mode or just direct prompt.
    # Let's use 'naive' mode which relies mostly on the prompt we verify?
    # Or just prepend the context to the query and let it run.
    
    # Use 'mix' mode which combines knowledge graph + vector retrieval
    # Unlike 'hybrid', 'mix' doesn't require global community summaries
    print(f"Querying with Injected Context ({len(context_prompt)} chars) using Mix Mode (Graph + Vector)...")
    response = await rag.aquery(context_prompt, param=QueryParam(mode="mix"))
    
    if response is None:
        return "System Warning: No response generated. This typically happens if the database is empty. Please run ingestion to populate the Knowledge Graph."
        
    return response


async def clear_job_data(job_id: str):
    """
    Cleanup: Just removes the shortlist from memory.
    """
    if job_id in _job_shortlists:
        del _job_shortlists[job_id]
    print(f"Cleared context for Job {job_id}")

