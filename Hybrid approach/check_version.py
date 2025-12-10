from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "987654321")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

with driver.session() as session:
    result = session.run("CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] as version, edition")
    for record in result:
        print(f"Neo4j Version: {record['version']} ({record['edition']})")
        
    # Check indexes
    print("\nIndexes:")
    result = session.run("SHOW INDEXES")
    for record in result:
        print(f"- {record['name']}: {record['type']} on {record['labelsOrTypes']}({record['properties']})")

driver.close()
