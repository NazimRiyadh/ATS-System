import logging
# Suppress noisy loggers
logging.getLogger("lightrag").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

import asyncio
from rank_candidates import retrieve_candidates_vector_only


from src.job_manager import process_top_candidates, chat_with_shortlist, clear_job_data

async def run_scenario():
    job_id = "job_12345"
    print(f"=== SCENARIO TEST: {job_id} ===")
    
    # Step 1: Initial Search
    query = "Senior Python Developer with AWS experience"
    print(f"\n[Step 1] Analyze Query: '{query}'")

    
    candidates = await retrieve_candidates_vector_only(query, top_k=5)
    for c in candidates:
        print(f"   Candidate File: {c['source_file']}")
        print(f"   Snippet: {c['resume_text'][:100]}...")


    if not candidates:
        print("❌ No candidates found.")
        return

    # Simulate /analyze_job backend logic
    await clear_job_data(job_id)
    full_texts = [c['resume_text'] for c in candidates]
    await process_top_candidates(job_id, full_texts)
    
    # Step 2: Chat Question
    question = "Who can work as a team lead and better suit for the role?"
    print(f"\n[Step 2] Chat Query: '{question}'")
    
    response = await chat_with_shortlist(job_id, question)
    print(f"\n[LLM Response]:\n{response}")


if __name__ == "__main__":
    asyncio.run(run_scenario())
