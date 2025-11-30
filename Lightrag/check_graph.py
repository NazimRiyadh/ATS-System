from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

def check_graph():
    print(f"Connecting to {uri}...")
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        # 1. Count Nodes
        result = session.run("MATCH (n) RETURN count(n) as count")
        node_count = result.single()["count"]
        print(f"\nTotal Nodes: {node_count}")
        
        # 2. Count Relationships
        result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
        rel_count = result.single()["count"]
        print(f"Total Relationships: {rel_count}")
        
        if node_count == 0:
            print("\n⚠️ The graph is empty! Resume ingestion might have failed silently or no entities were extracted.")
            return

        # 3. Sample Entities (Nodes)
        print("\n--- Sample Entities (Top 10) ---")
        result = session.run("MATCH (n) RETURN labels(n) as labels, n.entity_id as id LIMIT 10")
        for record in result:
            print(f"[{record['labels'][0]}] {record['id']}")

        # 4. Sample Relationships
        print("\n--- Sample Relationships (Top 10) ---")
        result = session.run("MATCH (a)-[r]->(b) RETURN a.entity_id, type(r), b.entity_id LIMIT 10")
        for record in result:
            print(f"'{record['a.entity_id']}' --[{record['type(r)']}]--> '{record['b.entity_id']}'")

    driver.close()

if __name__ == "__main__":
    check_graph()
