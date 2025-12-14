
import asyncio
import asyncpg
import sys

async def check_version():
    print("🔌 Connecting to database...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='password',
            host='127.0.0.1',
            port=5432,
            database='postgres'
        )
        version = await conn.fetchval("SELECT version();")
        print(f"✅ CONNECTED!")
        print(f"ℹ️  SERVER VERSION: {version}")
        
        await conn.close()
    except Exception as e:
        print(f"❌ FAILED to connect: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_version())
