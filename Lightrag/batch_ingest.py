import os
import asyncio
import argparse
from lightrag import LightRAG
from src.rag_engine import initialize_rag
from src.parser import parse_resume

from src.logger import setup_logger

logger = setup_logger("BatchIngest")

async def batch_ingest(resumes_dir: str):
    """
    Iterate through a directory of resumes, parse them, and ingest into LightRAG.
    """
    if not os.path.exists(resumes_dir):
        logger.error(f"Directory not found: {resumes_dir}")
        return

    logger.info(f"Initializing LightRAG...")
    try:
        rag = await initialize_rag()
    except Exception as e:
        logger.critical(f"Failed to initialize LightRAG: {e}")
        return

    files = [f for f in os.listdir(resumes_dir) if os.path.isfile(os.path.join(resumes_dir, f))]
    total_files = len(files)
    logger.info(f"Found {total_files} files in {resumes_dir}")

    success_count = 0
    fail_count = 0

    for i, filename in enumerate(files):
        file_path = os.path.join(resumes_dir, filename)
        logger.info(f"[{i+1}/{total_files}] Processing {filename}...")
        
        # Validation: Check file size
        if os.path.getsize(file_path) == 0:
            logger.warning(f"  Skipping {filename}: File is empty.")
            fail_count += 1
            continue

        try:
            # Extract text using our parser
            text = parse_resume(file_path)
            
            if not text or len(text.strip()) < 50: # Increased threshold
                logger.warning(f"  Skipping {filename}: Insufficient text extracted (<50 chars).")
                fail_count += 1
                continue

            # Ingest into LightRAG
            await rag.ainsert(input=text, file_paths=[file_path])
            logger.info(f"  Successfully ingested {filename}")
            success_count += 1
            
        except Exception as e:
            logger.error(f"  Failed to ingest {filename}: {e}")
            fail_count += 1

    logger.info("Batch ingestion complete.")
    logger.info(f"Summary: {success_count} succeeded, {fail_count} failed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch ingest resumes into LightRAG.")
    parser.add_argument("--dir", type=str, default="./resumes", help="Directory containing resume files")
    args = parser.parse_args()

    asyncio.run(batch_ingest(args.dir))
