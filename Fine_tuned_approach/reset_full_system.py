
import asyncio
from neo4j import GraphDatabase
import os
import shutil
import asyncpg
from dotenv import load_dotenv
from src.config import Config

load_dotenv()

async def reset_all():
    print("⚠️  WARNING: This will DELETE ALL DATA in Neo4j, Postgres (LightRAG tables), and local storage. ⚠️")
    confirm = input("Type 'yes' to confirm: ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    # 1. Reset Neo4j
    print("\n[1/3] Clearing Neo4j...")
    try:
        driver = GraphDatabase.driver(Config.NEO4J_URI, auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD))
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        driver.close()
        print("✅ Neo4j cleared.")
    except Exception as e:
        print(f"❌ Neo4j reset failed: {e}")

    # 2. Reset Postgres
    print("\n[2/3] Clearing Postgres Tables...")
    try:
        # Handle asyncpg uri
        dsn = Config.POSTGRES_URI.replace("postgresql+asyncpg://", "postgresql://")
        if "@localhost" in dsn: # IPv4 Fix
             dsn = dsn.replace("@localhost", "@127.0.0.1")

        conn = await asyncpg.connect(dsn)
        tables = [
            "LIGHTRAG_DOC_STATUS", "LIGHTRAG_DOC_CHUNKS", "LIGHTRAG_DOC_FULL",
            "LIGHTRAG_VDB_CHUNKS", "LIGHTRAG_VDB_ENTITY", "LIGHTRAG_VDB_RELATION",
            "LIGHTRAG_TENSOR_STORE", "LIGHTRAG_LLM_CACHE"
        ]
        for table in tables:
            await conn.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
        
        await conn.close()
        print("✅ Postgres tables dropped.")
    except Exception as e:
        print(f"❌ Postgres reset failed: {e}")

    # 3. Clear Local Storage
    print("\n[3/3] Removing Local Storage...")
    storage_dir = Config.RAG_DIR
    if os.path.exists(storage_dir):
        shutil.rmtree(storage_dir)
        print("✅ Local storage removed.")
    else:
        print("ℹ️  Local storage not found.")

    print("\n✨ System Full Reset Complete. You are ready to ingest real data.")

if __name__ == "__main__":
    asyncio.run(reset_all())
