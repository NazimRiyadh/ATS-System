from neo4j import GraphDatabase

# Connection details from Neo4j Desktop
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "987654321"

print("Testing Neo4j connection...")
print(f"URI: {NEO4J_URI}")
print(f"User: {NEO4J_USER}")

try:
    # Try to connect
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    # Test the connection with a simple query
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful!' AS message")
        record = result.single()
        print(f"\n✅ SUCCESS: {record['message']}")
        
        # Get Neo4j version
        version_result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
        for record in version_result:
            print(f"   {record['name']}: {record['version']}")
    
    driver.close()
    print("\n✅ Connection test completed successfully!")
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("\nPossible issues:")
    print("1. Check if the password is correct (default is usually set during first setup)")
    print("2. Make sure the database is started in Neo4j Desktop")
    print("3. Try resetting the password in Neo4j Desktop settings")
