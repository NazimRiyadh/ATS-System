import asyncio
import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def check_progress():
    DB_USER = os.getenv("POSTGRES_USER", "postgres")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
    DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB", "ats_db")
    
    DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    try:
        conn = await asyncpg.connect(DSN)
        
        # Count processed docs
        row = await conn.fetchrow("SELECT count(*) FROM lightrag_doc_status")
        processed_count = row[0]
        
        # Count total chunks (optional interest)
        row_chunks = await conn.fetchrow("SELECT count(*) FROM lightrag_doc_chunks")
        chunks_count = row_chunks[0]
        
        # Last active time
        row_time = await conn.fetchrow("SELECT created_at FROM lightrag_doc_status ORDER BY created_at DESC LIMIT 1")
        last_time = row_time[0] if row_time else "Never"
        
        # Total expected
        total_files = 65 # Based on data/resumes count
        
        print("\n" + "="*40)
        print("📊 INGESTION PROGRESS")
        print("="*40)
        print(f"Processed Documents: {processed_count} / {total_files}")
        print(f"Total Chunks Stored: {chunks_count}")
        print(f"Last Document Finished: {last_time}")
        
        pct = (processed_count / total_files) * 100
        bar = "█" * int(pct // 5) + "░" * (20 - int(pct // 5))
        print(f"Progress: [{bar}] {pct:.1f}%")
        
        await conn.close()
        
    except Exception as e:
        print(f"Error checking progress: {e}")

if __name__ == "__main__":
    asyncio.run(check_progress())
