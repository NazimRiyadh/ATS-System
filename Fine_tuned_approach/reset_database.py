from neo4j import GraphDatabase
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

def reset_neo4j():
    print(f"Connecting to {uri}...")
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        print("Clearing Neo4j database...")
        session.run("MATCH (n) DETACH DELETE n")
        print("Neo4j database cleared.")
    
    driver.close()

def clear_local_storage():
    storage_dir = "./rag_storage"
    if os.path.exists(storage_dir):
        print(f"Removing local storage directory: {storage_dir}")
        shutil.rmtree(storage_dir)
        print("Local storage cleared.")
    else:
        print("Local storage directory not found, skipping.")


if __name__ == "__main__":
    # confirm = input("This will DELETE ALL DATA in Neo4j and rag_storage. Type 'yes' to proceed: ")
    # if confirm.lower() == "yes":
    print("Forcing reset...")
    reset_neo4j()
    clear_local_storage()

