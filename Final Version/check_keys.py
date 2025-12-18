import asyncio
import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase

load_dotenv()

async def check_keys():
    uri = os.getenv('NEO4J_URI')
    auth = ('neo4j', os.getenv('NEO4J_PASSWORD'))
    driver = AsyncGraphDatabase.driver(uri, auth=auth)
    
    async with driver.session() as session:
        print("Checking Node Keys:")
        # Get one node that has properties
        r = await session.run("MATCH (n) WHERE keys(n) <> [] RETURN keys(n) LIMIT 1")
        record = await r.single()
        if record:
            print(f"Keys: {record[0]}")
        else:
            print("No nodes with keys found!")

        # Check an orphan specifically
        print("\nChecking Orphan Keys:")
        r = await session.run("MATCH (n) WHERE NOT (n)--() RETURN keys(n), labels(n) LIMIT 1")
        record = await r.single()
        if record:
            print(f"Orphan Keys: {record[0]}")
            print(f"Orphan Labels: {record[1]}")

    await driver.close()

if __name__ == "__main__":
    asyncio.run(check_keys())
