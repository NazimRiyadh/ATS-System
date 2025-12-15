
import asyncio
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import sys

# Load env
load_dotenv()

async def test_neo4j_write():
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password")
    
    print(f"🔌 Connecting to Neo4j at {uri} as {user}...")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # 1. Clean up previous test node
            session.run("MATCH (n:TestNode {id: 'test_123'}) DELETE n")
            
            # 2. Creating a Test Node
            print("📝 Attempting to create a test node...")
            session.run("CREATE (n:TestNode {id: 'test_123', name: 'Connectivity Check', timestamp: timestamp()})")
            
            # 3. Reading it back
            result = session.run("MATCH (n:TestNode {id: 'test_123'}) RETURN n.name as name")
            single_result = result.single()
            
            if single_result and single_result["name"] == 'Connectivity Check':
                print("✅ SUCCESS: Successfully wrote and read back from Neo4j.")
            else:
                print("❌ FAILED: Node was not found after creation attempt.")
                
            # 4. Cleanup
            session.run("MATCH (n:TestNode {id: 'test_123'}) DELETE n")
            print("🧹 Cleanup complete.")
                
        driver.close()
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_neo4j_write())
