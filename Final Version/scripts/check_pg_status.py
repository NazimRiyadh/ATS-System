
import asyncio
import asyncpg
import sys

async def check_doc_status():
    print(f"🔌 Checking Postgres LIGHTRAG_DOC_STATUS...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='admin',
            database='ats_db',
            host='localhost',
            port=5432
        )
        
        # Check table existence
        tables = await conn.fetch("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'")
        print(f"📊 Tables found: {[t['tablename'] for t in tables]}")
        
        if any(t['tablename'] == 'lightrag_doc_status' for t in tables):
            rows = await conn.fetch("SELECT * FROM lightrag_doc_status")
            print(f"\n📄 Documents in LIGHTRAG_DOC_STATUS: {len(rows)}")
            for row in rows:
                print(f"   - {dict(row)}")
        else:
            print("⚠️ LIGHTRAG_DOC_STATUS table not found!")
            
        await conn.close()
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_doc_status())
