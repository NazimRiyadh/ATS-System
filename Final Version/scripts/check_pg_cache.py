
import asyncio
import asyncpg
import sys

async def check_llm_cache():
    print(f"🔌 Checking Postgres LIGHTRAG_LLM_CACHE...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='admin',
            database='ats_db',
            host='localhost',
            port=5432
        )
        try:
            count = await conn.fetchval("SELECT count(*) FROM lightrag_llm_cache")
            print(f"📊 Rows in LIGHTRAG_LLM_CACHE: {count}")
        except Exception as e:
            print(f"⚠️ Could not query table: {e}")
            
        await conn.close()
    except Exception as e:
        print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_llm_cache())
