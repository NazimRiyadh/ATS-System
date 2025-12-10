from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "987654321"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("Testing vector search query...")

# Test 1: Simple vector query
test_query = """
CALL db.index.vector.queryNodes('candidate_bio_index', 10, $embedding)
YIELD node AS candidate, score
RETURN candidate.name as name, score
LIMIT 5
"""

try:
    # Create a dummy embedding vector (1536 dimensions)
    dummy_embedding = [0.1] * 1536
    
    with driver.session() as session:
        result = session.run(test_query, embedding=dummy_embedding)
        records = list(result)
        print(f"✅ Vector search works! Found {len(records)} results")
        for record in records:
            print(f"   - {record['name']}: {record['score']}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}")
    print(f"   {str(e)}")

# Test 2: Vector search with experience calculation
test_query2 = """
CALL db.index.vector.queryNodes('candidate_bio_index', 10, $embedding)
YIELD node AS candidate, score

OPTIONAL MATCH (candidate)-[r:WORKED_AT]->(:Company)
WITH candidate, score, coalesce(sum(r.years), 0) as total_experience

RETURN candidate.name as name, 
       candidate.summary as summary, 
       total_experience, 
       score as vector_score
ORDER BY vector_score DESC
"""

print("\nTesting vector search with experience...")
try:
    with driver.session() as session:
        result = session.run(test_query2, embedding=dummy_embedding)
        records = list(result)
        print(f"✅ Vector search with experience works! Found {len(records)} results")
        for record in records:
            print(f"   - {record['name']}: {record['total_experience']} years, score: {record['vector_score']:.4f}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}")
    print(f"   {str(e)}")

# Test 3: Add WHERE clause
test_query3 = """
CALL db.index.vector.queryNodes('candidate_bio_index', 10, $embedding)
YIELD node AS candidate, score

OPTIONAL MATCH (candidate)-[r:WORKED_AT]->(:Company)
WITH candidate, score, coalesce(sum(r.years), 0) as total_experience
WHERE total_experience >= $min_years

RETURN candidate.name as name, 
       candidate.summary as summary, 
       total_experience, 
       score as vector_score
ORDER BY vector_score DESC
"""

print("\nTesting with WHERE filter...")
try:
    with driver.session() as session:
        result = session.run(test_query3, embedding=dummy_embedding, min_years=4)
        records = list(result)
        print(f"✅ Query with WHERE works! Found {len(records)} results")
        for record in records:
            print(f"   - {record['name']}: {record['total_experience']} years, score: {record['vector_score']:.4f}")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}")
    print(f"   {str(e)}")

driver.close()
print("\n✅ All tests completed!")
