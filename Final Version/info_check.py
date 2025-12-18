import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

async def check_connectivity():
    uri = os.getenv('NEO4J_URI')
    auth = ('neo4j', os.getenv('NEO4J_PASSWORD'))
    driver = AsyncGraphDatabase.driver(uri, auth=auth)
    
    async with driver.session() as session:
        # 1. Top shared nodes (excluding Person?)
        # Person nodes usually have degree, but mostly outgoing.
        # Skills/Companies should have incoming from multiple people.
        print("Checking Connectivity (Shared Nodes)...")
        r = await session.run("""
            MATCH (n)-[r]-()
            WHERE NOT n.entity_type = 'PERSON'
            WITH n, count(r) as degree
            ORDER BY degree DESC LIMIT 10
            RETURN n.id as name, n.entity_type as type, degree
        """)
        
        print("\nTOP CONNECTED NODES (Hubs):")
        records = await r.fetch(10)
        if not records:
            print("  (No shared nodes found yet)")
        for rec in records:
            print(f"  - {rec['name']} ({rec['type']}): {rec['degree']} connections")
            
        # 2. Check for DUPLICATES (e.g. 'Python' vs 'python')
        # This is hard to do perfectly in Cypher without fuzzy match, 
        # but we can look for case-insensitive grouping.
        print("\nChecking for Potential Duplicates (Case variants):")
        r = await session.run("""
            MATCH (n:SKILL)
            WITH toLower(n.id) as lower_id, collect(n.id) as variants, count(*) as c
            WHERE c > 1
            RETURN lower_id, variants
        """)
        dupes = await r.fetch(10)
        if not dupes:
            print("  (No obvious case-duplicates found)")
        for d in dupes:
            print(f"  ! Duplicate Concept: {d['lower_id']} -> {d['variants']}")

    await driver.close()

if __name__ == "__main__":
    asyncio.run(check_connectivity())
