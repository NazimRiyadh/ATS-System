from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "987654321"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("Checking existing indexes and constraints...")

# Check what indexes exist
with driver.session() as session:
    # Show all indexes
    result = session.run("SHOW INDEXES")
    print("\n=== EXISTING INDEXES ===")
    for record in result:
        print(f"  - {record}")
    
    # Show all constraints
    result = session.run("SHOW CONSTRAINTS")
    print("\n=== EXISTING CONSTRAINTS ===")
    for record in result:
        print(f"  - {record}")
    
    # Check if we have any candidates
    result = session.run("MATCH (c:Candidate) RETURN count(c) as count")
    count = result.single()['count']
    print(f"\n=== DATA ===")
    print(f"  - Total candidates: {count}")
    
    if count > 0:
        result = session.run("MATCH (c:Candidate) RETURN c.name as name, c.summary as summary LIMIT 3")
        print("\n  Sample candidates:")
        for record in result:
            print(f"    - {record['name']}: {record['summary'][:50]}...")

driver.close()
