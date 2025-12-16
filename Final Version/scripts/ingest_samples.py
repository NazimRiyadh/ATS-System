import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion import ingest_resumes_from_directory

# Point to samples directory
DATA_DIR = r"D:\KT Informatik\ATS project\Final Version\data\sample_resumes"

async def main():
    print(f"🚀 Starting Sample Ingestion from {DATA_DIR}...")
    
    if not os.path.exists(DATA_DIR):
        print(f"❌ Directory not found: {DATA_DIR}")
        return

    try:
        # Run batch ingestion
        # batch_size=1 for stability
        result = await ingest_resumes_from_directory(DATA_DIR, batch_size=1)
        
        print("\n" + "="*50)
        print("Ingestion Complete")
        print("="*50)
        print(f"Total Files: {result.total_files}")
        print(f"Successful:  {result.successful}")
        print(f"Failed:      {result.failed}")
        print(f"Total Time:  {result.total_time:.2f}s")
        
        if result.failed > 0:
            print("\nFailed files:")
            for r in result.results:
                if not r.success:
                    print(f" - {r.file_path}: {r.error}")

    except Exception as e:
        print(f"❌ Ingestion error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
