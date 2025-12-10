from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://127.0.0.1:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "987654321")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def create_index_simple():
    # Try simpler syntax
    query = """
    CREATE VECTOR INDEX candidate_embedding_idx
    FOR (c:Candidate) ON (c.embedding)
    OPTIONS {indexConfig: {`vector.dimensions`: 1536, `vector.similarity_function`: 'cosine'}}
    """
    print("Attempting to create index...")
    try:
        with driver.session() as session:
            session.run(query)
        print("Index creation command sent.")
    except Exception as e:
        print(f"Index creation failed: {e}")

def check_indexes():
    print("Checking indexes...")
    with driver.session() as session:
        result = session.run("SHOW INDEXES")
        found = False
        for record in result:
            print(f"- {record['name']}: {record['type']}")
            if record['name'] == 'candidate_embedding_idx':
                found = True
        
        if not found:
            print("Index 'candidate_embedding_idx' NOT found.")
        else:
            print("Index FOUND!")

create_index_simple()
check_indexes()
driver.close()
