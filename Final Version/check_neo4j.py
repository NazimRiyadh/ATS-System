"""Quick check of Neo4j state."""
import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

async def check_neo4j():
    driver = AsyncGraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=('neo4j', os.getenv('NEO4J_PASSWORD'))
    )
    
    async with driver.session() as session:
        # 1. Total Counts
        print("\n=== 1. GRAPH STATISTICS ===")
        r = await session.run("MATCH (n) RETURN count(n) as c")
        nodes = (await r.single())['c']
        r = await session.run("MATCH ()-[r]->() RETURN count(r) as c")
        rels = (await r.single())['c']
        print(f"Nodes: {nodes}")
        print(f"Relationships: {rels}")

        # 2. Entity Types Distribution
        print("\n=== 2. ENTITY TYPES ===")
        r = await session.run("""
            MATCH (n) 
            RETURN labels(n) as l, count(*) as c 
            ORDER BY c DESC
        """)
        async for rec in r:
            lbl = [x for x in rec['l'] if x != 'Global' and x != 'Chunk'][0] if rec['l'] else "NO_LABEL"
            print(f"  {lbl}: {rec['c']}")

        # 3. Relationship Types (Crucial for "Perfect Graph")
        print("\n=== 3. RELATIONSHIP TYPES ===")
        r = await session.run("""
            MATCH ()-[r]->() 
            RETURN type(r) as t, count(*) as c 
            ORDER BY c DESC
        """)
        async for rec in r:
            print(f"  {rec['t']}: {rec['c']}")

        # 4. Canonicalization Check (Skills)
        print("\n=== 4. SKILL CANONICALIZATION CHECK ===")
        r = await session.run("""
            MATCH (n:skill) 
            RETURN n.id as name 
            LIMIT 5
        """)
        async for rec in r:
            print(f"  Skill: {rec['name']}")

        # 5. Quality Issues Inspection
        print("\n=== 5. QUALITY AUDIT ===")
        # Check for UNKNOWN or generic nodes
        r = await session.run("""
            MATCH (n) 
            WHERE n.id CONTAINS 'UNKNOWN' OR labels(n) = []
            RETURN n.id as name, labels(n) as labels
            LIMIT 5
        """)
        found_issues = False
        async for rec in r:
            print(f"  ⚠️  Suspect Node: {rec['name']} {rec['labels']}")
            found_issues = True
        
        if not found_issues:
            print("  ✅ No obvious 'UNKNOWN' nodes found in sample")

    await driver.close()

if __name__ == "__main__":
    asyncio.run(check_neo4j())
