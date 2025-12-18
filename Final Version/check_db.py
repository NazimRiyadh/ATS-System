"""
Verify if resume data is in the database
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def check_database():
    import asyncpg
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get the connection string from the POSTGRES_URI 
    uri = os.getenv("POSTGRES_URI", "")
    # Convert from asyncpg format to connection params
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "ats_secure_password")
    db = os.getenv("POSTGRES_DB", "ats_db")
    
    print(f"\nConnecting to PostgreSQL: {host}:{port}/{db} as {user}")
    
    try:
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=db
        )
        print("[OK] Connected to database\n")
        
        # List all tables
        tables = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
        print("Tables in database:")
        for t in tables:
            print(f"  - {t['tablename']}")
        
        print("\n" + "="*60)
        print("CHECKING FOR ALEX THOMPSON")
        print("="*60)
        
        # Check full docs
        try:
            result = await conn.fetchrow(
                "SELECT id, content FROM lightrag_doc_full WHERE content ILIKE '%Alex Thompson%' LIMIT 1"
            )
            if result:
                print(f"\n[OK] Found in lightrag_doc_full!")
                print(f"    Doc ID: {result['id'][:60]}...")
                content_preview = result['content'][:200].replace('\n', ' ')
                print(f"    Content: {content_preview}...")
            else:
                print("\n[!] Not found in lightrag_doc_full")
        except Exception as e:
            print(f"\n[!] Error checking lightrag_doc_full: {e}")
        
        # Check chunks
        try:
            chunks = await conn.fetch(
                "SELECT id, content FROM lightrag_doc_chunks WHERE content ILIKE '%Alex Thompson%' LIMIT 3"
            )
            print(f"\n[OK] Found {len(chunks)} chunks containing 'Alex Thompson'")
            for i, chunk in enumerate(chunks):
                preview = chunk['content'][:100].replace('\n', ' ')
                print(f"    Chunk {i+1}: {preview}...")
        except Exception as e:
            print(f"\n[!] Error checking lightrag_doc_chunks: {e}")
        
        # Check entities
        try:
            entities = await conn.fetch(
                "SELECT entity_name FROM lightrag_vdb_entity WHERE entity_name ILIKE '%Alex%' OR entity_name ILIKE '%Thompson%' LIMIT 5"
            )
            print(f"\n[OK] Found {len(entities)} related entities")
            for e in entities:
                print(f"    - {e['entity_name']}")
        except Exception as e:
            print(f"\n[!] Error checking lightrag_vdb_entity: {e}")
        
        # Count total records
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        
        stats = [
            ("lightrag_doc_full", "Full documents"),
            ("lightrag_doc_chunks", "Document chunks"),
            ("lightrag_vdb_entity", "Entities"),
            ("lightrag_vdb_relation", "Relations"),
        ]
        
        for table, desc in stats:
            try:
                count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
                print(f"  {desc}: {count}")
            except:
                print(f"  {desc}: (table not found)")
        
        await conn.close()
        print("\n[OK] Database check complete!")
        
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_database())
