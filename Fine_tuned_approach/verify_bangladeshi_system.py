
import asyncio
import os
import time
from rank_candidates import retrieve_candidates_vector_only
from src.job_manager import process_top_candidates, chat_with_shortlist, clear_job_data

async def verify_system():
    print("=== VERIFYING BANGLADESHI ATS SYSTEM ===")
    

    # Query 1: Find a specific role (HR/Media likely ingested first)
    query = "HR Manager or Digital Media Specialist"
    print(f"\nQuery 1: '{query}'")
    
    candidates = await retrieve_candidates_vector_only(query, top_k=5)

    print(f"Found {len(candidates)} candidates.")
    for i, c in enumerate(candidates):
        print(f"  {i+1}. {c['source_file']}")
        
    if not candidates:
        print("❌ No candidates found. Ingestion might still be running.")
        return

    # Create Graph for top candidates
    job_id = "verify_bd_001"
    await clear_job_data(job_id)
    
    texts = [c['resume_text'] for c in candidates]
    print(f"\nBuilding Graph for Job {job_id}...")
    await process_top_candidates(job_id, texts)
    
    # Query 2: Chat Reason
    question = "Who are the candidates? List their names."
    print(f"\nQuery 2 (Chat): '{question}'")
    response = await chat_with_shortlist(job_id, question)
    print(f"🤖 Response:\n{response}")
    
    # Query 3: Specific comparison
    question_2 = "Compare the experience of the top 2 candidates."
    print(f"\nQuery 3 (Chat): '{question_2}'")
    response_2 = await chat_with_shortlist(job_id, question_2)
    print(f"🤖 Response:\n{response_2}")
    
    print("\n=== VERIFICATION COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(verify_system())
