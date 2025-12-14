
import asyncio
import os
import logging
from lightrag import LightRAG
from src.rag_config import get_rag

# Setup logging to console
logging.basicConfig(level=logging.DEBUG)

async def main():
    print("🚀 Starting Simple Ingestion Test...")
    
    try:
        # Initialize RAG
        print("🔧 Initializing RAG...")
        rag = await get_rag()
        print("✅ RAG Initialized.")
        
        # Test Data
        test_text = "Jane Doe is a Software Engineer with 5 years of Python experience."
        
        # Insert
        print("📥 Inserting test document...")
        await rag.ainsert(test_text)
        print("✅ Insertion Successful!")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
