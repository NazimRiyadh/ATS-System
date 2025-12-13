"""
Clean all LightRAG storage to allow fresh schema creation.
This script cleans:
1. PostgreSQL tables (PGVectorStorage)
2. Neo4j graph database (Neo4JStorage)
3. Local JSON files in rag_storage/

WARNING: This will delete all indexed data. Use with caution!
"""

import os
import shutil
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

# Configuration from environment
POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql+asyncpg://postgres:password@127.0.0.1:5432/postgres")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
RAG_DIR = os.getenv("RAG_DIR", "./rag_storage")


async def clean_postgres():
    """Drop all LightRAG-related tables from PostgreSQL."""
    print("\n=== Cleaning PostgreSQL ===")
    engine = create_async_engine(POSTGRES_URI)
    
    try:
        async with engine.begin() as conn:
            # Get all tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
            """))
            tables = [row[0] for row in result]
            
            if not tables:
                print("  ℹ️  No tables found in PostgreSQL")
                return
            
            print(f"  Found {len(tables)} table(s):")
            for table in tables:
                print(f"    - {table}")
            
            # Drop all tables
            for table in tables:
                print(f"  🗑️  Dropping table: {table}")
                await conn.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
            
            print("  ✅ PostgreSQL cleaned successfully")
    
    except Exception as e:
        print(f"  ❌ Error cleaning PostgreSQL: {e}")
    finally:
        await engine.dispose()


async def clean_neo4j():
    """Clear all nodes and relationships from Neo4j."""
    print("\n=== Cleaning Neo4j ===")
    
    try:
        from neo4j import AsyncGraphDatabase
        
        driver = AsyncGraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        async with driver.session(database="neo4j") as session:
            # Count nodes before
            result = await session.run("MATCH (n) RETURN count(n) as count")
            record = await result.single()
            node_count = record["count"] if record else 0
            
            # Count relationships before
            result = await session.run("MATCH ()-[r]->() RETURN count(r) as count")
            record = await result.single()
            rel_count = record["count"] if record else 0
            
            print(f"  Found {node_count} node(s) and {rel_count} relationship(s)")
            
            if node_count > 0 or rel_count > 0:
                # Delete all nodes and relationships
                print("  🗑️  Deleting all nodes and relationships...")
                await session.run("MATCH (n) DETACH DELETE n")
                print("  ✅ Neo4j cleaned successfully")
            else:
                print("  ℹ️  Neo4j is already empty")
        
        await driver.close()
    
    except ImportError:
        print("  ⚠️  neo4j package not installed. Skipping Neo4j cleanup.")
    except Exception as e:
        print(f"  ❌ Error cleaning Neo4j: {e}")


def clean_local_storage():
    """Remove all JSON files from rag_storage directory."""
    print("\n=== Cleaning Local Storage ===")
    
    rag_path = Path(RAG_DIR)
    
    if not rag_path.exists():
        print(f"  ℹ️  Directory {RAG_DIR} does not exist")
        return
    
    # Count files before
    json_files = list(rag_path.glob("*.json"))
    other_files = [f for f in rag_path.iterdir() if f.is_file() and f.suffix != ".json"]
    
    print(f"  Found {len(json_files)} JSON file(s) and {len(other_files)} other file(s)")
    
    if json_files:
        for file in json_files:
            print(f"  🗑️  Deleting: {file.name}")
            file.unlink()
    
    # Also remove any subdirectories
    subdirs = [d for d in rag_path.iterdir() if d.is_dir()]
    if subdirs:
        for subdir in subdirs:
            print(f"  🗑️  Removing directory: {subdir.name}")
            shutil.rmtree(subdir)
    
    print("  ✅ Local storage cleaned successfully")


async def main():
    """Run all cleanup tasks."""
    print("=" * 60)
    print("LightRAG Storage Cleanup Script")
    print("=" * 60)
    print("\n⚠️  WARNING: This will delete ALL indexed data!")
    print("  - PostgreSQL tables")
    print("  - Neo4j graph data")
    print("  - Local JSON files in rag_storage/")
    
    response = input("\nAre you sure you want to continue? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("\n❌ Cleanup cancelled by user")
        return
    
    print("\n🚀 Starting cleanup...\n")
    
    # Clean all storage components
    await clean_postgres()
    await clean_neo4j()
    clean_local_storage()
    
    print("\n" + "=" * 60)
    print("✅ Cleanup Complete!")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("  1. Run: python batch_ingest.py --dir ./resumes --batch 10")
    print("  2. Wait for ingestion to complete")
    print("  3. Test with: python test_modes.py")
    print("  4. Start API: python main.py")


if __name__ == "__main__":
    asyncio.run(main())
