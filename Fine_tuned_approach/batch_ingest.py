import os
import asyncio
import argparse
from concurrent.futures import ProcessPoolExecutor
from lightrag import LightRAG
from src.rag_engine import initialize_rag
from src.parser import parse_resume
from src.logger import setup_logger

logger = setup_logger("BatchIngest")

def parse_wrapper(file_path):
    """
    Wrapper to run parse_resume in a separate process.
    Must be a standalone function (top-level) for ProcessPoolExecutor.
    """
    try:
        # Check size first to avoid overhead
        if os.path.getsize(file_path) == 0:
            return None
        return parse_resume(file_path)
    except Exception as e:
        return None

async def batch_ingest(resumes_dir: str, batch_size: int = 10):
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

    # Use a ProcessPool to utilize all CPU cores for Parsing
    # (PDF parsing is CPU heavy, so we need Processes, not Threads)
    loop = asyncio.get_running_loop()
    
    # Process in chunks (e.g., groups of 10) to manage memory and rate limits
    for i in range(0, total_files, batch_size):
        chunk_files = files[i : i + batch_size]
        logger.info(f"--- Processing Batch {i // batch_size + 1} ({len(chunk_files)} files) ---")

        # 1. PARALLEL PARSING
        # We start the parsing tasks for this batch in parallel processes
        parse_tasks = []
        valid_paths = []
        
        with ProcessPoolExecutor() as executor:
            # Create futures for parsing
            futures = []
            for filename in chunk_files:
                file_path = os.path.join(resumes_dir, filename)
                futures.append(loop.run_in_executor(executor, parse_wrapper, file_path))
            
            # Wait for all parsing in this batch to finish
            results = await asyncio.gather(*futures)

        # 2. FILTER VALID TEXTS
        valid_texts = []
        valid_filepaths = []
        
        for idx, text in enumerate(results):
            filename = chunk_files[idx]
            if text and len(text.strip()) > 50:
                valid_texts.append(text)
                valid_filepaths.append(os.path.join(resumes_dir, filename))
            else:
                logger.warning(f"Skipping {filename} (Empty or parsing failed)")

        # 3. BATCH INGESTION
        # Send the whole list to LightRAG at once. 
        # It handles internal parallelism for LLM calls better than we can.
        if valid_texts:
            logger.info(f"Ingesting {len(valid_texts)} documents into LightRAG...")
            try:
                # rag.ainsert supports list input. We must also pass the file_paths so metadata is correct.
                await rag.ainsert(input=valid_texts, file_paths=valid_filepaths) 
                logger.info(f"✅ Batch success")
            except Exception as e:
                logger.error(f"❌ Batch failed: {e}")

    logger.info("Ingestion complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch ingest resumes into LightRAG.")
    parser.add_argument("--dir", type=str, default="./resumes", help="Directory containing resume files")
    parser.add_argument("--batch", type=int, default=10, help="Number of files to process at once")
    args = parser.parse_args()

    asyncio.run(batch_ingest(args.dir, args.batch))