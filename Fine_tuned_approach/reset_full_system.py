
import asyncio
import os
import shutil
from src.config import Config
from src.job_manager import get_global_rag
from neo4j import GraphDatabase
import asyncpg

async def wipe_postgres():
    print("🧹 Wiping Postgres Tables...")
    uri = Config.POSTGRES_URI.replace("postgresql+asyncpg://", "postgresql://")
    try:
        conn = await asyncpg.connect(uri)
        tables = [
             "LIGHTRAG_VDB_CHUNKS", 
             "LIGHTRAG_VDB_ENTITY", 
             "LIGHTRAG_VDB_RELATION",
             "LIGHTRAG_DOC_STATUS",
             "LIGHTRAG_LLM_CACHE"
        ]
        for t in tables:
            try:
                await conn.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
                print(f"   - Dropped {t}")
            except Exception as e:
                print(f"   - Error dropping {t}: {e}")
        await conn.close()
    except Exception as e:
        print(f"❌ Postgres Wipe Failed: {e}")

async def wipe_neo4j():
    print("🧹 Wiping Neo4j Database...")
    uri = Config.NEO4J_URI
    user = Config.NEO4J_USERNAME
    password = Config.NEO4J_PASSWORD
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session(database="neo4j") as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("   - All nodes/relationships deleted.")
        driver.close()
    except Exception as e:
         # Fallback to default DB if 'neo4j' fails?
         try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
                print("   - All nodes/relationships deleted (Default DB).")
            driver.close()
         except Exception as e2:
             print(f"❌ Neo4j Wipe Failed: {e2}")

async def main():
    await wipe_postgres()
    await wipe_neo4j()
    
    # Also clear local file storage if any
    rag_dir = "./rag_storage"
    if os.path.exists(rag_dir):
        try:
             shutil.rmtree(rag_dir) 
             print(f"   - Deleted local storage: {rag_dir}")
        except Exception as e:
             print(f"Error clearing dir: {e}")
    
    print("\n✨ System Wiped. Ready for Fresh Ingestion.")

if __name__ == "__main__":
    asyncio.run(main())
