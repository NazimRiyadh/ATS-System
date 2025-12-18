"""
Test to verify LightRAG entity parsing is working with our prompt format.
"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

async def test_single_resume():
    """Test ingestion of a single resume and check if entities are created."""
    from src.rag_config import get_rag_manager
    from lightrag.prompt import PROMPTS
    
    # Initialize RAG
    print("Initializing RAG...")
    manager = get_rag_manager()
    rag = await manager.initialize()
    
    # Print current prompt settings
    print("\n=== PROMPT SETTINGS ===")
    print(f"Tuple delimiter: {PROMPTS.get('DEFAULT_TUPLE_DELIMITER', 'NOT SET')}")
    print(f"Completion delimiter: {PROMPTS.get('DEFAULT_COMPLETION_DELIMITER', 'NOT SET')}")
    entity_prompt = PROMPTS.get('entity_extraction', '')
    print(f"Entity extraction prompt (first 200 chars): {entity_prompt[:200]}...")
    
    # Test with a simple resume
    test_resume = """
RESUME
Name: Test User John Doe
Email: john.doe@test.com
Location: San Francisco, CA

PROFESSIONAL SUMMARY
Software Engineer with 5 years of experience in Python and JavaScript.

EXPERIENCE
Software Engineer at Google (2020-2024)
- Built backend services using Python and Django
- Implemented REST APIs

SKILLS
Python, JavaScript, SQL, AWS, Docker

CERTIFICATIONS
AWS Solutions Architect
"""
    
    print("\n=== INGESTING TEST RESUME ===")
    
    # Insert the resume
    await rag.ainsert(test_resume)
    print("Ingestion complete!")
    
    # Check Neo4j for entities
    import os
    from dotenv import load_dotenv
    from neo4j import AsyncGraphDatabase
    
    load_dotenv()
    driver = AsyncGraphDatabase.driver(
        os.getenv('NEO4J_URI'),
        auth=('neo4j', os.getenv('NEO4J_PASSWORD'))
    )
    
    async with driver.session() as session:
        result = await session.run("MATCH (n) RETURN count(n) as count")
        record = await result.single()
        node_count = record['count']
        
        result2 = await session.run("MATCH ()-[r]->() RETURN count(r) as count")
        record2 = await result2.single()
        rel_count = record2['count']
        
        print(f"\n=== NEO4J RESULTS ===")
        print(f"Nodes: {node_count}")
        print(f"Relationships: {rel_count}")
        
        if node_count > 0:
            result3 = await session.run("""
                MATCH (n:base)
                RETURN n.entity_id as name, n.entity_type as type
                LIMIT 10
            """)
            print("\nSample entities:")
            async for rec in result3:
                print(f"  [{rec['type']}] {rec['name']}")
    
    await driver.close()

if __name__ == "__main__":
    asyncio.run(test_single_resume())
