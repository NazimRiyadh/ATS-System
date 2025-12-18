import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

async def check():
    uri = os.getenv('NEO4J_URI')
    auth = ('neo4j', os.getenv('NEO4J_PASSWORD'))
    driver = AsyncGraphDatabase.driver(uri, auth=auth)
    
    async with driver.session() as session:
        print("Checking Node Properties:")
        result = await session.run("MATCH (n) RETURN labels(n), properties(n) LIMIT 5")
        async for record in result:
             print(f"Labels: {record['labels(n)']}")
             print(f"Props: {record['properties(n)']}")
             print("-" * 20)

    await driver.close()

if __name__ == "__main__":
    asyncio.run(check())
