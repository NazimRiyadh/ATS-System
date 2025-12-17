import asyncio
import os
import asyncpg
from tabulate import tabulate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get DB config from env or use defaults (matching docker-compose)
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "ats_db")

DSN = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

async def inspect():
    print(f"\n🔌 Connecting to {DSN}...")
    try:
        conn = await asyncpg.connect(DSN)
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Ensure 'docker-compose up -d' is running.")
        return

    print("✅ Connected!\n")

    # 1. List all tables
    print("📋 TABLES IN DATABASE:")
    tables = await conn.fetch("""
        SELECT schemaname, tablename 
        FROM pg_catalog.pg_tables 
        WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';
    """)
    print(tabulate(tables, headers=["Schema", "Table"], tablefmt="simple"))
    print("-" * 40)

    # 2. Check Row Counts & Vector Dimensions
    print("📊 TABLE STATISTICS:")
    stats = []
    
    # Check for known tables (adjust if your schema differs)
    target_tables = ["lightrag_docs", "lightrag_text_chunks", "lightrag_entities", "lightrag_relationships"]
    
    for table in tables:
        t_name = table['tablename']
        try:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {t_name}")
            stats.append([t_name, count])
        except Exception:
            pass
            
    print(tabulate(stats, headers=["Table", "Row Count"], tablefmt="grid"))
    print("-" * 40)

    # 3. Sample Vector Data (if chunks exist)
    print("👀 SAMPLE VECTOR DATA (lightrag_text_chunks):")
    try:
        # Check if table exists
        exists = await conn.fetchval("SELECT to_regclass('lightrag_text_chunks')")
        if exists:
            # Get one row with vector preview
            row = await conn.fetchrow("""
                SELECT substring(content for 50) as snippet, 
                       vector_dims(embedding) as dims 
                FROM lightrag_text_chunks 
                LIMIT 1
            """)
            if row:
                print(f"Snippet: {row['snippet']}...")
                print(f"Vector Dimensions: {row['dims']}")
            else:
                print("Table is empty.")
        else:
            print("Table 'lightrag_text_chunks' not found.")
    except Exception as e:
        print(f"Error reading vectors: {e}")

    await conn.close()

if __name__ == "__main__":
    asyncio.run(inspect())
