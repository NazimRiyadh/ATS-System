"""
Batch resume ingestion CLI script.
"""

import asyncio
import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def main(args):
    """Run batch ingestion."""
    from src.ingestion import ingest_resumes_from_directory
    from src.rag_config import get_rag_manager
    
    print("\n" + "="*50)
    print("📄 LightRAG ATS - Resume Ingestion")
    print("="*50 + "\n")
    
    # Validate directory
    directory = Path(args.dir)
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        return False
    
    print(f"📁 Source: {directory}")
    print(f"📦 Batch size: {args.batch_size}")
    print()
    
    # Initialize RAG first
    print("🔧 Initializing RAG system...")
    try:
        manager = get_rag_manager()
        await manager.initialize()
        print("✅ RAG initialized\n")
    except Exception as e:
        print(f"❌ RAG initialization failed: {e}")
        return False
    
    # Run ingestion
    print("🚀 Starting ingestion...\n")
    
    result = await ingest_resumes_from_directory(
        directory=str(directory),
        batch_size=args.batch_size
    )
    
    # Print summary
    print("\n" + "="*50)
    print("📊 Ingestion Complete")
    print("="*50)
    print(f"  📁 Total files: {result.total_files}")
    print(f"  ✅ Successful: {result.successful}")
    print(f"  ❌ Failed: {result.failed}")
    print(f"  ⏱️ Time: {result.total_time:.2f}s")
    
    if result.total_files > 0:
        rate = result.total_files / result.total_time
        print(f"  📈 Rate: {rate:.2f} files/sec")
    
    if result.failed > 0:
        print("\n⚠️ Failed files:")
        for r in result.results:
            if not r.success:
                print(f"  - {r.file_path}: {r.error}")
    
    return result.failed == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ingest resumes from a directory into LightRAG"
    )
    parser.add_argument(
        "--dir", "-d",
        required=True,
        help="Directory containing resume files"
    )
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=5,
        help="Batch size for concurrent processing (default: 5)"
    )
    
    args = parser.parse_args()
    success = asyncio.run(main(args))
    sys.exit(0 if success else 1)
