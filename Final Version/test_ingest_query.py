"""
Test a simple ingestion and query - ASCII only for Windows
"""
import asyncio
import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
logging.basicConfig(level=logging.INFO, format='%(name)s - %(message)s')

async def run_test():
    from src.rag_config import get_rag_manager
    from src.ingestion import ingest_resume
    from lightrag import QueryParam
    
    print("\n" + "="*60)
    print("INGESTION TEST")
    print("="*60)
    
    # Initialize RAG
    print("Initializing RAG...")
    manager = get_rag_manager()
    rag = await manager.initialize()
    print("[OK] RAG ready")
    
    # Ingest a test resume
    test_file = Path("data/test_resume/Java_Developer_Rahul_Verma_78a4b1.txt")
    if test_file.exists():
        print(f"\nIngesting: {test_file}")
        result = await ingest_resume(str(test_file))
        print(f"Result: {result.success} - {result.candidate_name}")
        if result.error:
            print(f"Error: {result.error}")
    
    # Test query
    print("\n" + "="*60)
    print("QUERY TEST")  
    print("="*60)
    
    queries = [
        "Find Python developers", 
        "Who is Rahul Verma?",
        "List candidates with Java skills"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        
        # Test naive mode (should work without graph)
        try:
            print("Testing NAIVE mode:")
            response = await rag.aquery(query, param=QueryParam(mode="naive"))
            resp_text = response[:300] + "..." if len(response) > 300 else response
            # Sanitize for Windows terminal
            resp_text = resp_text.encode('ascii', 'replace').decode('ascii')
            print(f"  Response: {resp_text}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Test mix mode
        try:
            print("\nTesting MIX mode:")
            response = await rag.aquery(query, param=QueryParam(mode="mix"))
            resp_text = response[:300] + "..." if len(response) > 300 else response
            resp_text = resp_text.encode('ascii', 'replace').decode('ascii')
            print(f"  Response: {resp_text}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

asyncio.run(run_test())
