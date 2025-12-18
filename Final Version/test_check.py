import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

async def main():
    uri = os.getenv('NEO4J_URI')
    auth = ('neo4j', os.getenv('NEO4J_PASSWORD'))
    driver = AsyncGraphDatabase.driver(uri, auth=auth)
    
    async with driver.session() as session:
        # Count nodes
        r = await session.run("MATCH (n) RETURN count(n) as c")
        nodes = (await r.single())['c']
        
        # Count relationships
        r = await session.run("MATCH ()-[r]->() RETURN count(r) as c")
        rels = (await r.single())['c']
        
        # Count orphans
        r = await session.run("MATCH (n) WHERE NOT (n)-[]-() RETURN count(n) as c")
        orphans = (await r.single())['c']
        
        print(f"NODES: {nodes}")
        print(f"RELATIONSHIPS: {rels}")
        print(f"ORPHANS: {orphans}")

    await driver.close()

if __name__ == "__main__":
    asyncio.run(main())
