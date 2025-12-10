
import asyncio
import os
import shutil
import warnings
from src.job_manager import process_top_candidates, chat_with_shortlist, clear_job_data
from src.config import Config
from rank_candidates import retrieve_candidates_vector_only

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

async def test_workflow():
    print("=== STARTING WORKFLOW TEST ===")
    
    query = "Python Developer with Machine Learning experience"
    job_id = "test_job_123"
    
    # Clean previous test run
    await clear_job_data(job_id)
    
    # 1. Test Stage 1: Vector Search
    print("\n--- STAGE 1: Vector Search (Fast Filter) ---")
    try:
        candidates = await retrieve_candidates_vector_only(query, top_k=5)
        print(f"Candidates found: {len(candidates)}")
        if not candidates:
            print("❌ No candidates found! Ensure resumes are ingested.")
            return
        print(f"Top 1: {candidates[0]['source_file']}")
    except Exception as e:
        print(f"❌ Stage 1 Failed with error: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. Test Stage 2: Deep Index
    print("\n--- STAGE 2: Deep Index (Graph Building) ---")
    try:
        texts = [c['resume_text'] for c in candidates]
        await process_top_candidates(job_id, texts)
        
        # Check if directory exists
        path = os.path.join(Config.RAG_DIR, f"job_{job_id}")
        if os.path.exists(path):
            print(f"✅ Graph storage created at {path}")
        else:
            print("❌ Graph storage NOT found!")
    except Exception as e:
        print(f"❌ Stage 2 Failed: {e}")
        return

    # 3. Test Stage 3: Chat Interface
    print("\n--- STAGE 3: Chat Interface (Reasoning) ---")
    try:
        question = "Which candidate has the most relevant ML experience? Explain why."
        response = await chat_with_shortlist(job_id, question)
        print(f"🤖 Response:\n{response}")
    except Exception as e:
        print(f"❌ Stage 3 Failed: {e}")
        return

    print("\n=== WORKFLOW TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    asyncio.run(test_workflow())
