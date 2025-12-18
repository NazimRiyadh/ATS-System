import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

async def find_orphans():
    uri = os.getenv('NEO4J_URI')
    auth = ('neo4j', os.getenv('NEO4J_PASSWORD'))
    driver = AsyncGraphDatabase.driver(uri, auth=auth)
    
    async with driver.session() as session:
        print("Searching for Orphan 'Python' nodes...")
        r = await session.run("""
            MATCH (n)
            WHERE toLower(n.entity_id) CONTAINS 'python'
            AND NOT (n)--() 
            RETURN n.entity_id as name, labels(n) as labels
        """)
        
        orphans = await r.fetch(20)
        if not orphans:
            print("No orphan 'Python' nodes found! (Maybe they are connected?)")
            
            # Fallback: Show ANY orphans
            print("\nSearching for ANY orphans (first 10):")
            r2 = await session.run("""
                MATCH (n)
                WHERE NOT (n)--() 
                RETURN n.entity_id as name, labels(n) as labels LIMIT 10
            """)
            any_orphans = await r2.fetch(10)
            for o in any_orphans:
                print(f" - Orphan: {o['name']} (Labels: {o['labels']})")
        else:
            print(f"Found {len(orphans)} orphan Python nodes:")
            for o in orphans:
                print(f" - {o['name']} (Labels: {o['labels']})")

    await driver.close()

if __name__ == "__main__":
    asyncio.run(find_orphans())
