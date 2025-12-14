
import asyncio
import asyncpg
import sys

async def test_password(password):
    print(f"Testing password '{password}' on localhost:5432...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password=password,
            database='postgres', # connect to default db
            host='127.0.0.1',
            port=5432
        )
        print(f"✅ SUCCESS: Password '{password}' works!")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

async def main():
    # Test user provided password
    print("--- Test 1 ---")
    res1 = await test_password('123456')
    
    # Test default docker password
    print("\n--- Test 2 ---")
    res2 = await test_password('ats_secure_password')
    
    if res1:
        print("\nCONCLUSION: User password correct.")
    elif res2:
        print("\nCONCLUSION: Docker password correct (Docker likely running on 5432).")
    else:
        print("\nCONCLUSION: Neither password worked.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
