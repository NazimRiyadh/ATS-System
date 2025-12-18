"""Check entity storage in PostgreSQL."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    conn = await asyncpg.connect(
        f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@localhost:5432/{os.getenv('POSTGRES_DB')}"
    )
    
    print("Entity Storage Check:")
    print(f"  lightrag_vdb_entity: {await conn.fetchval('SELECT COUNT(*) FROM lightrag_vdb_entity')}")
    print(f"  lightrag_full_entities: {await conn.fetchval('SELECT COUNT(*) FROM lightrag_full_entities')}")
    print(f"  lightrag_entity_chunks: {await conn.fetchval('SELECT COUNT(*) FROM lightrag_entity_chunks')}")
    print(f"  lightrag_vdb_relation: {await conn.fetchval('SELECT COUNT(*) FROM lightrag_vdb_relation')}")
    print(f"  lightrag_full_relations: {await conn.fetchval('SELECT COUNT(*) FROM lightrag_full_relations')}")
    print(f"  lightrag_relation_chunks: {await conn.fetchval('SELECT COUNT(*) FROM lightrag_relation_chunks')}")
    
    # Check llm_cache to see what LLM returned
    cache_count = await conn.fetchval('SELECT COUNT(*) FROM lightrag_llm_cache')
    print(f"\nLLM Cache entries: {cache_count}")
    
    if cache_count > 0:
        # Sample a cache entry
        sample = await conn.fetchrow('SELECT mode, original_prompt, return_message FROM lightrag_llm_cache LIMIT 1')
        if sample:
            print(f"\nSample LLM cache entry:")
            print(f"  Mode: {sample['mode']}")
            msg = sample['return_message'] or ''
            if len(msg) > 500:
                msg = msg[:500] + "..."
            print(f"  Response: {msg}")
    
    await conn.close()

asyncio.run(check())
