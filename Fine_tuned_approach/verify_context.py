
import asyncio
import os
import shutil

# Basic setup to trigger the LLM
from rank_candidates import retrieve_candidates_vector_only
from src.job_manager import process_top_candidates, chat_with_shortlist, clear_job_data

async def prove_context_usage():
    job_id = "proof_001"
    print(f"=== PROVING CONTEXT USAGE FOR JOB {job_id} ===\n")
    
    # 1. Retrieve candidates (Vector Search)
    query = "Java Developer with focus on Security"
    print(f"Querying: '{query}'")
    candidates = await retrieve_candidates_vector_only(query, top_k=3)
    
    if not candidates:
        print("No candidates found! (Check ingestion?)")
        return

    print(f"\n[Retrieved {len(candidates)} candidates via Vector Search]")
    for c in candidates:
        print(f" - {c['source_file']}")
        
    # 2. Build Context (Pass to Job Manager)
    await clear_job_data(job_id)
    texts = [c['resume_text'] for c in candidates]
    await process_top_candidates(job_id, texts)
    
    # 3. Ask Question (Triggers LLM)
    # This call will hit 'ollama_model_complete' which now PRINTS the prompt.
    question = "Who is the strongest security candidate and why?"
    print(f"\n[Asking LLM]: '{question}'")
    print("(Watch below for the 'PROMPT SENT TO LLM' block...)\n")
    
    response = await chat_with_shortlist(job_id, question)
    print(f"\n[LLM Final Answer]:\n{response}")

if __name__ == "__main__":
    asyncio.run(prove_context_usage())
