
import asyncio
import asyncpg
import sys

async def test_connect(password, db_name):
    print(f"Testing connection to '{db_name}' with password '{password}'...")
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password=password,
            database='postgres', # Connect to default DB first to check auth
            host='127.0.0.1',
            port=5432
        )
        print(f"✅ SUCCESS: Auth works with password '{password}'!")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

async def main():
    # Test 1: Old password (likely due to volume persistence)
    print("--- Test 1: Old Password ---")
    res1 = await test_connect('ats_secure_password', 'postgres')
    
    # Test 2: Empty Password
    if not res1:
        print("\n--- Test 2: Empty Password ---")
        res2 = await test_connect('', 'postgres')

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
