
import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure we can import from the library
# (Assuming venv site-packages is in path, otherwise might need adjustments)
try:
    from lightrag.kg.neo4j_impl import Neo4JStorage
except ImportError:
    # Try adding venv path if running outside standard env context (debugging safeguard)
    sys.path.append(os.path.join(os.getcwd(), "venv312", "Lib", "site-packages"))
    from lightrag.kg.neo4j_impl import Neo4JStorage

# Load env
load_dotenv()

async def test_neo4j_storage():
    print("🔌 Testing Neo4JStorage integration...")
    
    # Mock Global Config for LightRAG
    # Neo4JStorage implementation typically looks for os.environ variables
    # but some versions might look at global_config.
    # We will set env vars explicitly to be sure.
    
    os.environ["NEO4J_URI"] = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    os.environ["NEO4J_USERNAME"] = os.getenv("NEO4J_USERNAME", "neo4j")
    os.environ["NEO4J_PASSWORD"] = os.getenv("NEO4J_PASSWORD", "password")
    
    print(f"   URI: {os.environ['NEO4J_URI']}")
    print(f"   User: {os.environ['NEO4J_USERNAME']}")
    
    async def mock_embedding_func(texts):
        return [[0.1] * 1024 for _ in texts]

    try:
        # Initialize Storage
        storage = Neo4JStorage(
            namespace="test_space",
            global_config={},
            embedding_func=mock_embedding_func
        )
        
        # Mock Lock to bypass "NoneType" error in initialize() interaction if needed
        # But wait, Neo4JStorage logic usually sets up its own driver.
        # The crash was in shared_storage.py `await self._lock.acquire()`.
        # This implies Neo4JStorage inherits from something using `self._lock` where `_lock` isn't init.
        # Let's try to set it manually.
        import asyncio
        storage._lock = asyncio.Lock()
        
        await storage.initialize()
        print("✅ Storage initialized.")
        
        print("Methods:", [d for d in dir(storage) if "upsert" in d])
        
        # Test Data
        node_id = "test_node_storage_class"
        node_data = {
            "entity_name": node_id,
            "entity_type": "TEST_ENTITY",
            "description": "Created by isolation test script",
            "source_id": "script"
        }
        
        print(f"📝 Upserting node: {node_id}...")
        if hasattr(storage, "upsert"):
             await storage.upsert({node_id: node_data})
        elif hasattr(storage, "upsert_node"):
             await storage.upsert_node(node_id, node_data)
        else:
             print("❌ No upsert method found!")
        
        # Verify
        
        # Verify
        print("🔍 retrieving node...")
        result = await storage.get([node_id])
        
        if result and result.get(node_id):
             print(f"✅ SUCCESS: Retrieved node: {result[node_id]}")
        else:
             print(f"❌ FAILED: Node not found in storage. Result: {result}")
             
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_neo4j_storage())
