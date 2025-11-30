import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Neo4j
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # LightRAG
    RAG_DIR = os.getenv("RAG_DIR", "./rag_storage")
    RESUMES_DIR = os.getenv("RESUMES_DIR", "./resumes")
    
    # Model Settings
    # Using specific models ensures consistency
    EMBEDDING_MODEL = "BAAI/bge-m3"
    RERANK_MODEL = "BAAI/bge-reranker-v2-m3"
    EMBEDDING_DIM = 1024 
    LLM_MODEL = "gpt-4o-mini"
    
    # RAG Parameters
    CHUNK_SIZE = 1500
    CHUNK_OVERLAP = 300
    TOP_K = 5
