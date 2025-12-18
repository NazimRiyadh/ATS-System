"""
Test Mix Mode specifically
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_mix_mode():
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    from src.rag_config import get_rag_manager
    from lightrag import QueryParam
    
    print("\n" + "="*60)
    print("MIX MODE TEST")
    print("="*60)
    
    manager = get_rag_manager()
    rag = await manager.initialize()
    print("[OK] RAG initialized\n")
    
    queries = [
        "Who is Alex Thompson and what are his skills?",
        "Find Python developers",
        "List candidates with experience at TechCorp",
    ]
    
    for query in queries:
        print(f"Query: '{query}'")
        print("-" * 50)
        
        try:
            response = await rag.aquery(query, param=QueryParam(mode="mix"))
            # Clean for terminal
            resp = response[:600] if len(response) <= 600 else response[:600] + "..."
            resp = resp.encode('ascii', 'replace').decode('ascii')
            print(f"MIX Response:\n{resp}\n")
            print("[OK] Mix mode worked!\n")
        except Exception as e:
            print(f"[ERROR] Mix mode failed: {e}\n")
    
    print("="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_mix_mode())
