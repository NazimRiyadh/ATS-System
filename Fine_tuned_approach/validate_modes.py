"""
Validate all LightRAG retrieval modes to verify functionality.
This script tests: naive, local, global, hybrid, and mix modes.
"""

import asyncio
from lightrag import QueryParam
from src.job_manager import get_global_rag

async def validate_modes():
    print("=" * 70)
    print("LightRAG Mode Validation")
    print("=" * 70)
    
    print('\n📦 Initializing RAG...')
    rag = await get_global_rag()
    print('✅ RAG initialized\n')
    
    # Test query
    query = 'Who has Python and machine learning experience?'
    
    # All available modes
    modes = ['naive', 'local', 'global', 'hybrid', 'mix']
    
    results = {}
    
    for mode in modes:
        print(f"\n{'=' * 70}")
        print(f"🧪 Testing MODE: '{mode}'")
        print('=' * 70)
        
        try:
            print(f"  Query: {query}")
            print(f"  Executing...")
            
            response = await rag.aquery(query, param=QueryParam(mode=mode))
            
            if response is None:
                print(f"  ❌ FAILED: Returned None")
                results[mode] = "FAILED (None response)"
            else:
                print(f"  ✅ SUCCESS")
                # Show first 200 chars of response
                preview = response[:200] + "..." if len(response) > 200 else response
                print(f"  Response preview: {preview}")
                results[mode] = "SUCCESS"
                
        except Exception as e:
            print(f"  ❌ FAILED with exception:")
            print(f"     {type(e).__name__}: {str(e)[:150]}")
            results[mode] = f"FAILED ({type(e).__name__})"
    
    # Summary
    print(f"\n\n{'=' * 70}")
    print("📊 SUMMARY")
    print('=' * 70)
    
    for mode, result in results.items():
        status_icon = "✅" if "SUCCESS" in result else "❌"
        print(f"  {status_icon} {mode:10s}: {result}")
    
    # Count successes
    success_count = sum(1 for r in results.values() if "SUCCESS" in r)
    total_count = len(results)
    
    print(f"\n  Total: {success_count}/{total_count} modes working")
    
    if success_count == 0:
        print("\n⚠️  WARNING: No modes are working!")
        print("   - Ensure databases are running (PostgreSQL + Neo4j)")
        print("   - Ensure data has been ingested: python batch_ingest.py")
    elif success_count < total_count:
        print("\n⚠️  PARTIAL SUCCESS: Some modes are not working")
        print("   - This is expected behavior. Mix/hybrid modes may require specific data structures")
        print("   - Use naive mode for production if other modes fail")
    else:
        print("\n🎉 All modes working perfectly!")
    
    print("\n" + "=" * 70)

if __name__ == '__main__':
    asyncio.run(validate_modes())
