
import asyncio
from neo4j import GraphDatabase
import sys

async def check_neo4j_stats():
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"
    
    print(f"🔌 Connecting to Neo4j...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session() as session:
            # Count Nodes
            nodes = session.run("MATCH (n) RETURN count(n) AS count").single()["count"]
            # Count Relationships
            rels = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
            
            print(f"📊 Neo4j Statistics:")
            print(f"   - Nodes: {nodes}")
            print(f"   - Relationships: {rels}")
            
            if nodes > 0:
                print("✅ YES! Neo4j is being populated.")
            else:
                print("⚠️ Neo4j is empty (might still be processing chunks).")
                
        driver.close()
    except Exception as e:
        print(f"❌ FAILED to query Neo4j: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(check_neo4j_stats())
