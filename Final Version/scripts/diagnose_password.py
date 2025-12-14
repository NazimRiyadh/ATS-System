
import asyncio
import asyncpg
import sys

async def test_connect(password, label):
    print(f"Testing '{label}' (Password: '{password}')...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password=password,
            database='postgres',
            host='127.0.0.1',
            port=5432
        )
        print(f"✅ SUCCESS: '{label}' works!")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

async def main():
    # Test 1: User's likely password
    await test_connect('ats_secure_password', 'Docker Default')
    
    # Test 2: Empty Password (per user's yml edit)
    await test_connect('', 'Empty Password')
    
    # Test 3: Local Password
    await test_connect('123456', 'Local Password')

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
