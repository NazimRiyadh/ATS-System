"""Test query functionality."""
import asyncio
import sys
sys.path.insert(0, '.')
from src.rag_config import get_rag_manager

async def test():
    manager = get_rag_manager()
    rag = await manager.initialize()
    print('RAG initialized')
    
    # Try a simple query
    result = await rag.aquery('Who has Python skills?')
    if result:
        print(f'Query result: {result[:300]}...')
    else:
        print('No result (empty database)')

asyncio.run(test())
