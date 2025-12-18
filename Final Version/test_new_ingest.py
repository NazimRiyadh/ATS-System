"""
Test ingestion of a new resume and verify in database
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_ingest_and_verify():
    import logging
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')
    
    from src.rag_config import get_rag_manager
    from src.ingestion import ingest_resume
    
    print("\n" + "="*60)
    print("INGESTION TEST FOR NEW RESUME")
    print("="*60)
    
    # Initialize RAG
    print("\n[1] Initializing RAG...")
    manager = get_rag_manager()
    rag = await manager.initialize()
    print("[OK] RAG initialized")
    
    # Ingest the new test resume
    test_file = Path("test_resume_alex.txt")
    if not test_file.exists():
        print(f"[ERROR] Test file not found: {test_file}")
        return
    
    print(f"\n[2] Ingesting: {test_file}")
    result = await ingest_resume(str(test_file))
    
    print(f"\n[3] INGESTION RESULT:")
    print(f"    Success: {result.success}")
    print(f"    Candidate Name: {result.candidate_name}")
    if result.error:
        print(f"    Error: {result.error}")
    
    # Verify by querying
    print("\n" + "="*60)
    print("VERIFICATION - QUERY FOR NEW CANDIDATE")
    print("="*60)
    
    from lightrag import QueryParam
    
    queries = [
        "Who is Alex Thompson?",
        "Find Python developers with FastAPI experience",
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        try:
            response = await rag.aquery(query, param=QueryParam(mode="naive"))
            # Sanitize for Windows terminal
            resp_text = response[:500] if len(response) <= 500 else response[:500] + "..."
            resp_text = resp_text.encode('ascii', 'replace').decode('ascii')
            print(f"Response: {resp_text}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Check database directly
    print("\n" + "="*60)
    print("DATABASE VERIFICATION")
    print("="*60)
    
    try:
        import asyncpg
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        conn = await asyncpg.connect(os.getenv("POSTGRES_CONNECTION_STRING"))
        
        # Check if Alex Thompson is in the database
        result = await conn.fetchrow(
            "SELECT id, content FROM lightrag_doc_full WHERE content ILIKE '%Alex Thompson%' LIMIT 1"
        )
        
        if result:
            print("[OK] Found 'Alex Thompson' in lightrag_doc_full table!")
            print(f"    Document ID: {result['id'][:50]}...")
        else:
            print("[!] 'Alex Thompson' NOT found in lightrag_doc_full")
        
        # Check vector chunks
        chunk_count = await conn.fetchval(
            "SELECT COUNT(*) FROM lightrag_doc_chunks WHERE content ILIKE '%Alex Thompson%'"
        )
        print(f"    Chunks containing 'Alex Thompson': {chunk_count}")
        
        # Check entities
        entity_count = await conn.fetchval(
            "SELECT COUNT(*) FROM lightrag_vdb_entity WHERE entity_name ILIKE '%Alex Thompson%'"
        )
        print(f"    Entities matching 'Alex Thompson': {entity_count}")
        
        await conn.close()
        
    except Exception as e:
        print(f"[ERROR] Database check failed: {e}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_ingest_and_verify())
