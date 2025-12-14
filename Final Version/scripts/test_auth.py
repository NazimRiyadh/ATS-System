
import asyncio
import asyncpg
import sys

async def test_connect():
    print("Testing connection with password 'ats_secure_password'...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='123456',
            database='postgres',  # Default db to test auth
            host='127.0.0.1',
            port=5432
        )
        print("✅ SUCCESS: Connected with '123456'!")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connect())
    sys.exit(0 if success else 1)
