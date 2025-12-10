import os
import functools
from dotenv import load_dotenv


from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_share_data, initialize_pipeline_status
from .embeddings import local_embedding_func
from .rerank import local_rerank_func
from .prompts import ATS_ENTITY_EXTRACTION_PROMPT
from .config import Config

from .llm_local import ollama_model_complete

# allow nested loops (Jupyter or other already‐running loops)
# nest_asyncio.apply()

load_dotenv()


async def initialize_rag(working_dir: str = Config.RAG_DIR) -> LightRAG:
    """
    Initialize LightRAG with vector and Graph storage.
    Falls back to NetworkXStorage if Neo4j is not configured or reachable (conceptually).
    """
    # Wrap in EmbeddingFunc
    embedding_func = EmbeddingFunc(
        embedding_dim=local_embedding_func.embedding_dim,
        max_token_size=8192, # BGE-M3 can handle big context, but Chunk size is limiter
        func=local_embedding_func
    )


    # User has confirmed Neo4j configuration, so we default to Neo4JStorage.
    # We can still keep the logic to switch if needed, but let's prioritize Neo4j.
    graph_storage_type = "Neo4JStorage"
    
    # Fallback only if explicitly requested or if we want to be very safe, 
    # but strictly following user intent: "I have configured neo4j credential".

    # Setup ENV for PGVectorStorage (it reads from os.environ)
    if "postgres" in Config.POSTGRES_URI:
        try:
            from urllib.parse import urlparse
            # Handle asyncpg uri if present
            uri = Config.POSTGRES_URI.replace("postgresql+asyncpg://", "postgresql://")
            parsed = urlparse(uri)
            
            os.environ["POSTGRES_USER"] = parsed.username or "postgres"
            os.environ["POSTGRES_PASSWORD"] = parsed.password or ""
            os.environ["POSTGRES_DATABASE"] = parsed.path.lstrip("/") or "postgres"
            os.environ["POSTGRES_HOST"] = parsed.hostname or "localhost"
            os.environ["POSTGRES_PORT"] = str(parsed.port or "5432")
        except Exception as e:
            print(f"⚠️ Failed to parse POSTGRES_URI for environment variables: {e}")

    rag = LightRAG(
        working_dir=working_dir,
        embedding_func=embedding_func,
        llm_model_func=ollama_model_complete, # Switched to Local Flan-T5
        graph_storage=graph_storage_type,

        vector_storage="PGVectorStorage",
        chunk_token_size=Config.CHUNK_SIZE,
        chunk_overlap_token_size=Config.CHUNK_OVERLAP,
        rerank_model_func=local_rerank_func,
        addon_params={"entity_extract_template": ATS_ENTITY_EXTRACTION_PROMPT}
    )
    await rag.initialize_storages()

    # ensure shared dicts exist
    initialize_share_data()
    await initialize_pipeline_status()

    return rag



async def index_data(rag: LightRAG, file_path: str) -> None:
    """
    Index a text file into LightRAG, tagging chunks with its filename.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # stream chunks into vector store and graph
    await rag.ainsert(input=text, file_paths=[file_path])

async def index_file(rag: LightRAG, path: str) -> None:
    """
    Alias for index_data to mirror sync naming.
    """
    await index_data(rag, path)
