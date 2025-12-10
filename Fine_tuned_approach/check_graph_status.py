
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
AUTH = (os.getenv("NEO4J_USERNAME", "neo4j"), os.getenv("NEO4J_PASSWORD", "password"))

def verify_graph():
    print(f"Connecting to {URI}...")
    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        with driver.session() as session:
            # 1. Total Counts
            print("\n--- 📊 General Stats ---")
            nodes = session.run("MATCH (n) RETURN count(n) as c").single()["c"]
            rels = session.run("MATCH ()-[r]->() RETURN count(r) as c").single()["c"]
            print(f"Total Nodes: {nodes}")
            print(f"Total Relationships: {rels}")
            
            if nodes == 0:
                print("❌ CRITICAL: Database is empty!")
                return

            # 2. Node Labels
            print("\n--- 🏷️ Node Labels ---")
            result = session.run("MATCH (n) RETURN labels(n) as l, count(*) as c ORDER BY c DESC")
            for record in result:
                # labels(n) returns a list, usually just one relevant label for us
                print(f"{record['l']}: {record['c']}")

            # 3. Relationship Types
            print("\n--- 🔗 Relationship Types ---")
            result = session.run("MATCH ()-[r]->() RETURN type(r) as t, count(*) as c ORDER BY c DESC")
            for record in result:
                print(f"{record['t']}: {record['c']}")

            # 4. Orphans (Nodes with no relationships)
            print("\n--- 🏝️ Orphan Nodes (Quality Check) ---")
            orphan_count = session.run("MATCH (n) WHERE NOT (n)--() RETURN count(n) as c").single()["c"]
            print(f"Orphan Nodes: {orphan_count} (Lower is better, but some are normal)")

            print("\n--- 🔍 Inspecting Specific Candidates ---")
            # Check for the names found in the scenario
            names = ["Liton Al Hasan", "Mushfiqur Ali", "Tamim Rahman", "Tasnim Iqbal"]
            for name in names:
                print(f"\nChecking '{name}'...")
                # Search by substring because names might vary slightly
                q = f"MATCH (n:person) WHERE properties(n).entity_name CONTAINS '{name.split()[0]}' RETURN properties(n) as Props, n"
                result = session.run(q)
                found = False
                for r in result:
                    found = True
                    props = r['Props'] or {}
                    print(f"  Found Node ID: {r['n'].id}") 
                    print(f"  Props: {props}")

                    
                    # Check for related skills
                    q_skills = f"MATCH (n)-[]-(s:skill) WHERE id(n) = {r['n'].id} RETURN properties(s).entity_name as Skill"
                    res_skills = session.run(q_skills)
                    skills = [row['Skill'] for row in res_skills]
                    print(f"  Linked Skills: {skills}")
                
                if not found:
                    print("  ❌ Not found in Graph.")







                
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    verify_graph()
