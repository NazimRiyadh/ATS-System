
import asyncio
import asyncpg
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings

async def apply_schema():
    print("Applying schema from scripts/setup_postgres.sql...")
    try:
        # Read SQL file
        with open("scripts/setup_postgres.sql", "r") as f:
            sql = f.read()

        # Connect
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )

        # Execute
        await conn.execute(sql)
        print("✅ Schema applied successfully.")
        await conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed to apply schema: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(apply_schema())
