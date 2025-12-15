"""
Diagnostic script to identify ingestion issues.
"""

import asyncio
import sys
import logging
import io
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    # Set UTF-8 encoding for stdout
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def check_rag_initialization():
    """Check if RAG can be initialized."""
    print("\n" + "="*60)
    print("1. Checking RAG Initialization")
    print("="*60)
    
    try:
        from src.rag_config import get_rag_manager
        
        manager = get_rag_manager()
        print("✅ RAG Manager created")
        
        rag = await manager.initialize()
        print("✅ RAG initialized successfully")
        print(f"   Working dir: {manager._rag.working_dir if manager._rag else 'N/A'}")
        print(f"   Initialized: {manager._initialized}")
        
        return True
    except Exception as e:
        print(f"[ERROR] RAG initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_database_connections():
    """Check database connectivity."""
    print("\n" + "="*60)
    print("2. Checking Database Connections")
    print("="*60)
    
    results = {}
    
    # Check PostgreSQL
    try:
        import asyncpg
        from src.config import settings
        
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            user=settings.postgres_user,
            password=settings.postgres_password,
            database=settings.postgres_db
        )
        await conn.close()
        print("[OK] PostgreSQL connection successful")
        results["postgres"] = True
    except Exception as e:
        print(f"[ERROR] PostgreSQL connection failed: {e}")
        results["postgres"] = False
    
    # Check Neo4j
    try:
        from neo4j import AsyncGraphDatabase
        from src.config import settings
        
        driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password)
        )
        await driver.verify_connectivity()
        await driver.close()
        print("✅ Neo4j connection successful")
        results["neo4j"] = True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        results["neo4j"] = False
    
    return results


async def check_ollama():
    """Check Ollama availability."""
    print("\n" + "="*60)
    print("3. Checking Ollama")
    print("="*60)
    
    try:
        from src.llm_adapter import get_ollama_adapter
        
        ollama = get_ollama_adapter()
        is_healthy = await ollama.check_health()
        
        if is_healthy:
            print("[OK] Ollama is available")
            return True
        else:
            print("[ERROR] Ollama is not responding")
            return False
    except Exception as e:
        print(f"[ERROR] Ollama check failed: {e}")
        return False


async def check_embedding_model():
    """Check embedding model."""
    print("\n" + "="*60)
    print("4. Checking Embedding Model")
    print("="*60)
    
    try:
        from src.embedding import get_embedding_model
        
        model = get_embedding_model()
        print(f"[OK] Embedding model loaded: {model.model_name}")
        print(f"   Device: {model.device}")
        print(f"   Dimension: {model.embedding_dim}")
        
        # Test encoding
        test_text = "Test embedding"
        embedding = await model.aencode(test_text)
        print(f"[OK] Test embedding generated: shape {embedding.shape}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Embedding model check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_simple_ingestion():
    """Test a simple ingestion."""
    print("\n" + "="*60)
    print("5. Testing Simple Ingestion")
    print("="*60)
    
    try:
        from src.ingestion import ResumeIngestion
        
        ingestion = ResumeIngestion()
        print("[OK] ResumeIngestion instance created")
        
        # Create a test file
        test_file = Path("./test_resume.txt")
        test_content = """
# John Doe

SOFTWARE ENGINEER

Email: john.doe@example.com
Phone: +1-234-567-8900

PROFESSIONAL SUMMARY
Experienced software engineer with 5 years of Python development experience.

SKILLS
- Python
- FastAPI
- PostgreSQL
- Docker

EXPERIENCE
Senior Software Engineer | TechCorp Inc.
2020 - Present
- Developed REST APIs using FastAPI
- Managed PostgreSQL databases
"""
        
        test_file.write_text(test_content)
        print(f"[OK] Test file created: {test_file}")
        
        # Try ingestion
        print("[INFO] Attempting ingestion...")
        result = await ingestion.ingest_single(str(test_file))
        
        if result.success:
            print(f"[OK] Ingestion successful!")
            print(f"   Candidate: {result.candidate_name}")
            print(f"   Time: {result.processing_time:.2f}s")
        else:
            print(f"[ERROR] Ingestion failed: {result.error}")
        
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        
        return result.success
        
    except Exception as e:
        print(f"❌ Ingestion test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_ingestion_class_rag_sharing():
    """Check if ingestion class properly shares RAG instance."""
    print("\n" + "="*60)
    print("6. Checking RAG Instance Sharing")
    print("="*60)
    
    try:
        from src.ingestion import ResumeIngestion
        from src.rag_config import get_rag_manager
        
        # Initialize RAG manager first
        manager = get_rag_manager()
        await manager.initialize()
        print("[OK] RAG Manager initialized")
        
        # Create ingestion instances
        ingestion1 = ResumeIngestion()
        ingestion2 = ResumeIngestion()
        
        # Check if they get the same RAG instance
        rag1 = await ingestion1._ensure_rag()
        rag2 = await ingestion2._ensure_rag()
        
        # They should get the same instance from get_rag()
        print(f"   ingestion1._rag: {ingestion1._rag is not None}")
        print(f"   ingestion2._rag: {ingestion2._rag is not None}")
        print(f"   Same RAG instance: {rag1 is rag2}")
        
        return True
    except Exception as e:
        print(f"[ERROR] RAG sharing check failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all diagnostics."""
    print("\n" + "="*60)
    print("INGESTION DIAGNOSTIC TOOL")
    print("="*60)
    
    results = {}
    
    # Run checks
    results["rag_init"] = await check_rag_initialization()
    results["databases"] = await check_database_connections()
    results["ollama"] = await check_ollama()
    results["embedding"] = await check_embedding_model()
    results["rag_sharing"] = await check_ingestion_class_rag_sharing()
    results["ingestion"] = await test_simple_ingestion()
    
    # Summary
    print("\n" + "="*60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("="*60)
    
    print(f"RAG Initialization: {'[OK]' if results['rag_init'] else '[ERROR]'}")
    print(f"PostgreSQL: {'[OK]' if results['databases'].get('postgres') else '[ERROR]'}")
    print(f"Neo4j: {'[OK]' if results['databases'].get('neo4j') else '[ERROR]'}")
    print(f"Ollama: {'[OK]' if results['ollama'] else '[ERROR]'}")
    print(f"Embedding Model: {'[OK]' if results['embedding'] else '[ERROR]'}")
    print(f"RAG Sharing: {'[OK]' if results['rag_sharing'] else '[ERROR]'}")
    print(f"Simple Ingestion: {'[OK]' if results['ingestion'] else '[ERROR]'}")
    
    all_passed = (
        results["rag_init"] and
        results["databases"].get("postgres") and
        results["databases"].get("neo4j") and
        results["ollama"] and
        results["embedding"] and
        results["rag_sharing"] and
        results["ingestion"]
    )
    
    print("\n" + ("[SUCCESS] All checks passed!" if all_passed else "[WARNING] Some checks failed"))
    
    return all_passed


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
