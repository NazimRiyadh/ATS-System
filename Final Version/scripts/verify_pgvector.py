
import asyncio
import asyncpg
import sys

async def check_pgvector():
    print("🔌 Connecting to database (localhost:5432, user:postgres, db:ats_db)...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='admin',
            host='127.0.0.1',
            port=5432,
            database='ats_db'
        )
        print("✅ CONNECTED to database!")
        
        # Check pgvector extension
        vector_version = await conn.fetchval("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        if vector_version:
            print(f"✅ PGVECTOR is installed! Version: {vector_version}")
            
            # Test vector operation
            dim = await conn.fetchval("SELECT vector_dims('[1,2,3]'::vector)")
            print(f"✅ Vector math test passed! Dims: {dim}")

            # Check table counts
            count = await conn.fetchval("SELECT COUNT(*) FROM LIGHTRAG_DOC_FULL")
            print(f"📊 LIGHTRAG_DOC_FULL Rows: {count}")
            
            chunk_count = await conn.fetchval("SELECT COUNT(*) FROM LIGHTRAG_DOC_CHUNKS")
            print(f"📊 LIGHTRAG_DOC_CHUNKS Rows: {chunk_count}")
        else:
            print("❌ PGVECTOR extension is NOT installed in this database.")

        await conn.close()
    except Exception as e:
        print(f"❌ FAILED to connect: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_pgvector())
