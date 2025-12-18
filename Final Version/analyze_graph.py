"""
Analyze the Neo4j knowledge graph to identify issues.
"""
import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

async def analyze_graph():
    driver = AsyncGraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=('neo4j', os.getenv('NEO4J_PASSWORD', 'password'))
    )
    
    try:
        async with driver.session() as session:
            print("=" * 60)
            print("KNOWLEDGE GRAPH ANALYSIS")
            print("=" * 60)
            
            # Node count by label
            print("\n📊 NODE TYPES:")
            result = await session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC LIMIT 15
            """)
            async for record in result:
                print(f"  {record['label']}: {record['count']}")
            
            # Relationship count by type
            print("\n🔗 RELATIONSHIP TYPES:")
            result = await session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(*) as count
                ORDER BY count DESC LIMIT 15
            """)
            async for record in result:
                print(f"  {record['type']}: {record['count']}")
            
            # Orphaned nodes (no relationships)
            print("\n⚠️ ORPHANED NODES (no relationships):")
            result = await session.run("""
                MATCH (n)
                WHERE NOT (n)-[]-()
                RETURN labels(n)[0] as label, count(*) as count
                ORDER BY count DESC LIMIT 10
            """)
            orphan_count = 0
            async for record in result:
                print(f"  {record['label']}: {record['count']}")
                orphan_count += record['count']
            print(f"  TOTAL ORPHANS: {orphan_count}")
            
            # Sample entities that might be causing warnings
            print("\n🔍 SAMPLE ENTITIES (first 10):")
            result = await session.run("""
                MATCH (n:base)
                RETURN n.entity_id as id, n.entity_type as type
                LIMIT 10
            """)
            async for record in result:
                print(f"  [{record['type']}] {record['id']}")
            
            # Check for duplicate entity patterns
            print("\n⚠️ POTENTIAL DUPLICATES (similar names):")
            result = await session.run("""
                MATCH (n:base)
                WHERE n.entity_id CONTAINS 'Java' OR n.entity_id CONTAINS 'Python'
                RETURN n.entity_id as id, n.entity_type as type
                LIMIT 15
            """)
            async for record in result:
                print(f"  [{record['type']}] {record['id']}")
                
    finally:
        await driver.close()

if __name__ == "__main__":
    asyncio.run(analyze_graph())
