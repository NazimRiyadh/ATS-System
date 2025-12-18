"""
Ingest a specific resume and verify in database
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def ingest_and_verify():
    import logging
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')
    
    from src.rag_config import get_rag_manager
    from src.ingestion import ingest_resume
    from lightrag import QueryParam
    
    print("\n" + "="*60)
    print("INGESTING: Sarah Mitchell Resume")
    print("="*60)
    
    # Initialize RAG
    print("\n[1] Initializing RAG...")
    manager = get_rag_manager()
    rag = await manager.initialize()
    print("[OK] RAG initialized")
    
    # Ingest the new resume
    resume_path = Path("data/resumes/Software_Engineer_Sarah_Mitchell_2024.txt")
    print(f"\n[2] Ingesting: {resume_path}")
    
    result = await ingest_resume(str(resume_path))
    
    print(f"\n[3] RESULT:")
    print(f"    Success: {result.success}")
    print(f"    Candidate: {result.candidate_name}")
    if result.error:
        print(f"    Error: {result.error}")
    
    # Query to verify
    print("\n" + "="*60)
    print("VERIFICATION QUERIES")
    print("="*60)
    
    queries = [
        "Who is Sarah Mitchell?",
        "Find engineers with Kubernetes experience",
    ]
    
    for q in queries:
        print(f"\nQuery: '{q}'")
        print("-" * 40)
        try:
            resp = await rag.aquery(q, param=QueryParam(mode="mix"))
            preview = resp[:400].encode('ascii', 'replace').decode('ascii')
            print(f"Response: {preview}...")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "="*60)
    print("DONE!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(ingest_and_verify())
