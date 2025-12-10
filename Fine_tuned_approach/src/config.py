import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    # Postgres (pgvector)
    POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql+asyncpg://postgres:password@localhost:5432/postgres")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # LightRAG
    RAG_DIR = os.getenv("RAG_DIR", "./rag_storage")
    RESUMES_DIR = os.getenv("RESUMES_DIR", "./resumes")
    
    # Model Settings
    # Using specific models ensures consistency
    EMBEDDING_MODEL = "BAAI/bge-m3"
    RERANK_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    EMBEDDING_DIM = 1024 
    LLM_MODEL = "qwen2.5:7b"


    
    # RAG Parameters
    # Qwen2.5 has 32k context, so we can use larger chunks
    CHUNK_SIZE = 1200
    CHUNK_OVERLAP = 200


    TOP_K = 5
    RERANK_THRESHOLD = 0.15 # Lowered to allow partial matches
