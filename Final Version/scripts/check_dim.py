
import asyncio
import asyncpg
import sys

async def check_dim():
    try:
        conn = await asyncpg.connect("postgresql://postgres:admin@localhost:5432/ats_db")
        # vector_dims returns the dimension of a vector column if we cast a result, but inspection is better via catalog
        # actually, simply checking vector_dims of an existing row or the type definition
        
        # Checking catalog for column definition
        row = await conn.fetchrow("""
            SELECT atttypmod 
            FROM pg_attribute 
            WHERE attrelid = 'lightrag_doc_chunks'::regclass 
            AND attname = 'content_vector';
        """)
        
        if row:
            print(f"Current Dimension: {row['atttypmod']}") 
        else:
            print("❌ Table or column not found.")
            
        await conn.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_dim())
