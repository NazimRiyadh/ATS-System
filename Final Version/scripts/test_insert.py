"""
Test script for LightRAG ingestion.
"""
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variables before importing
os.environ['NEO4J_URI'] = 'bolt://localhost:7687'
os.environ['NEO4J_USERNAME'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'password'
os.environ['POSTGRES_HOST'] = 'localhost'
os.environ['POSTGRES_PORT'] = '5432'
os.environ['POSTGRES_USER'] = 'postgres'
os.environ['POSTGRES_PASSWORD'] = 'ats_secure_password'
os.environ['POSTGRES_DATABASE'] = 'ats_db'


async def test_simple_insert():
    """Test a simple insert operation."""
    from lightrag import LightRAG
    from lightrag.utils import EmbeddingFunc
    import numpy as np
    
    print("🔧 Setting up LightRAG...")
    
    async def simple_embed(texts):
        """Simple random embedding for testing."""
        if isinstance(texts, str):
            texts = [texts]
        print(f"  📊 Embedding {len(texts)} texts...")
        return np.random.rand(len(texts), 1024).astype(np.float32)
    
    async def simple_llm(prompt, **kwargs):
        """Simple LLM response for testing."""
        print(f"  🤖 LLM called with {len(prompt)} chars")
        # Return a simple entity extraction response
        return """
ENTITY: John Smith~PERSON~Software developer with 7 years experience
ENTITY: Python~SKILL~Programming language
ENTITY: FastAPI~SKILL~Web framework
RELATION: John Smith~HAS_SKILL~Python~Expert level
RELATION: John Smith~HAS_SKILL~FastAPI~Advanced level
"""
    
    try:
        rag = LightRAG(
            working_dir='./test_rag_storage',
            llm_model_func=simple_llm,
            graph_storage='Neo4JStorage',
            vector_storage='PGVectorStorage',
            embedding_func=EmbeddingFunc(
                embedding_dim=1024,
                max_token_size=8192,
                func=simple_embed
            ),
            chunk_token_size=500,
            chunk_overlap_token_size=100,
        )
        
        print("✅ LightRAG created")
        
        await rag.initialize_storages()
        print("✅ Storages initialized")
        
        # Test document
        test_doc = """
# Resume: John Smith

SOFTWARE ENGINEER

Contact: john.smith@email.com

PROFESSIONAL SUMMARY
Experienced software engineer with 7 years of expertise in Python, FastAPI, and machine learning.

TECHNICAL SKILLS
- Languages: Python, JavaScript, SQL
- Frameworks: FastAPI, Django, Flask
- Databases: PostgreSQL, MongoDB

WORK EXPERIENCE

Senior Software Engineer | TechCorp Inc.
January 2021 - Present
- Built FastAPI microservices
- Led team of 5 engineers
"""
        
        print("📄 Inserting test document...")
        await rag.ainsert(test_doc)
        print("✅ Insert successful!")
        
        # Test query
        print("\n🔍 Testing query...")
        result = await rag.aquery("Who has Python skills?")
        print(f"📝 Query result: {result[:200]}..." if result else "No result")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_simple_insert())
    print("\n" + "="*50)
    print("✅ TEST PASSED" if success else "❌ TEST FAILED")
    sys.exit(0 if success else 1)
