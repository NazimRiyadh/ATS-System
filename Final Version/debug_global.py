
import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def check_neo4j_communities():
    from src.config import settings
    from neo4j import AsyncGraphDatabase
    
    print("\nChecking Neo4j for Community nodes...")
    try:
        driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
        async with driver.session() as session:
            # Check for generic nodes
            result = await session.run("MATCH (n) RETURN count(n) as count")
            record = await result.single()
            print(f"Total nodes in Graph: {record['count']}")
            
            # Check for LightRAG communities (often labeled differently depending on version)
            # Try generic label or check if any nodes have 'community' in labels
            # LightRAG usually uses __Community__ or similar
            result = await session.run("MATCH (n:__Community__) RETURN count(n) as count")
            record = await result.single()
            print(f"__Community__ nodes: {record['count']}")
            
    except Exception as e:
        print(f"Neo4j Check Failed: {e}")
    finally:
        await driver.close()

async def run_test():
    await check_neo4j_communities()

    try:
        from src.rag_config import get_rag_manager
        from lightrag import QueryParam
        
        print("\nInitializing RAG...")
        manager = get_rag_manager()
        rag = await manager.initialize()
        
        query = "Find Python developers"
        print(f"\nQuerying in 'global' mode: {query}")
        
        # Test Global Mode (pure community summary search)
        response = await rag.aquery(query, param=QueryParam(mode="global"))
        print("\nGlobal Mode Response:")
        print(response)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
