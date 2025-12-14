
import asyncio
from neo4j import GraphDatabase
import sys

async def check_neo4j():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"
    
    print(f"🔌 Connecting to Neo4j at {uri}...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        driver.verify_connectivity()
        print("✅ CONNECTED to Neo4j!")
        driver.close()
    except Exception as e:
        print(f"❌ FAILED to connect: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_neo4j())
