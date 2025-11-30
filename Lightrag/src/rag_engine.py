import os
import functools
from dotenv import load_dotenv

from lightrag import LightRAG
from lightrag.utils import EmbeddingFunc
from lightrag.llm.openai import gpt_4o_mini_complete
from lightrag.kg.shared_storage import initialize_share_data, initialize_pipeline_status
from .embeddings import local_embedding_func
from .rerank import local_rerank_func
from .prompts import ATS_ENTITY_EXTRACTION_PROMPT
from .config import Config

# allow nested loops (Jupyter or other already‐running loops)
# nest_asyncio.apply()

load_dotenv()

async def initialize_rag(working_dir: str = Config.RAG_DIR) -> LightRAG:
    """
    Initialize LightRAG with vector and Neo4j graph storage,
    and prepare shared pipeline status to avoid KeyError.
    """
    # Wrap in EmbeddingFunc
    embedding_func = EmbeddingFunc(
        embedding_dim=local_embedding_func.embedding_dim,
        max_token_size=8192,
        func=local_embedding_func
    )

    rag = LightRAG(
        working_dir=working_dir,
        embedding_func=embedding_func,
        llm_model_func=gpt_4o_mini_complete,
        graph_storage="Neo4JStorage",
        vector_storage="FaissVectorDBStorage",
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
