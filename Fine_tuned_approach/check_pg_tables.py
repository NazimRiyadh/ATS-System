import asyncio
from src.config import Config
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_tables():
    engine = create_async_engine(Config.POSTGRES_URI)
    async with engine.begin() as conn:
        # Get all tables
        result = await conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE' 
            ORDER BY table_name
        """))
        tables = [row[0] for row in result]
        print("\n=== PostgreSQL Tables ===")
        for table in tables:
            print(f"  - {table}")
        
        # Get table columns and structure for LightRAG tables
        for table in tables:
            if 'lightrag' in table.lower() or 'chunk' in table.lower() or 'entities' in table.lower():
                print(f"\n=== Table: {table} ===")
                result = await conn.execute(text(f"""
                    SELECT column_name, data_type, character_maximum_length
                    FROM information_schema.columns
                    WHERE table_name = '{table}'
                    ORDER BY ordinal_position
                """))
                for row in result:
                    col_name, dtype, max_len = row
                    len_info = f"({max_len})" if max_len else ""
                    print(f"  {col_name}: {dtype}{len_info}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())
