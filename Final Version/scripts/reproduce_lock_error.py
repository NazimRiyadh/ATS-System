
import asyncio
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_config import get_rag_manager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def reproduce():
    print("Reproducing LightRAG Lock Error...")
    try:
        manager = get_rag_manager()
        # This calls initialize(), which calls initialize_storages()
        rag = await manager.initialize()
        
        print("RAG initialized. Attempting ainsert...")
        # This might trigger the lock error if not properly initialized
        await rag.ainsert("Test content for reproduction")
        print("ainsert successful")
    except Exception as e:
        print(f"CAPTURED ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(reproduce())
