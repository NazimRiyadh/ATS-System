"""
Debug script to test LightRAG modes and understand why local/global fail.
This will help us implement proper dual-level retrieval.
"""

import asyncio
import traceback
from lightrag import QueryParam
from src.job_manager import get_global_rag

async def debug_modes():
    print("=" * 70)
    print("LightRAG Mode Debugging")
    print("=" * 70)
    
    print('\nInitializing RAG...')
    rag = await get_global_rag()
    print('RAG initialized\n')
    
    query = 'Who has Python experience?'
    
    # Test each mode with detailed error info
    modes_to_test = ['naive', 'local', 'global', 'mix']
    
    for mode in modes_to_test:
        print(f"\n{'=' * 70}")
        print(f"Testing MODE: '{mode}'")
        print('=' * 70)
        
        try:
            print(f"Query: {query}")
            print(f"Mode: {mode}")
            print("Executing...")
            
            response = await rag.aquery(query, param=QueryParam(mode=mode))
            
            if response is None:
                print(f"RESULT: None (no error, but empty response)")
            else:
                print(f"SUCCESS!")
                print(f"Response length: {len(response)} chars")
                print(f"Preview: {response[:200]}...")
                
        except Exception as e:
            print(f"FAILED with exception:")
            print(f"  Type: {type(e).__name__}")
            print(f"  Message: {str(e)}")
            print(f"\nFull traceback:")
            traceback.print_exc()
    
    print(f"\n{'=' * 70}")
    print("Debug Complete")
    print('=' * 70)

if __name__ == '__main__':
    asyncio.run(debug_modes())
