import numpy as np
import asyncio
from sentence_transformers import SentenceTransformer
from typing import List, Union

# Global variable to hold the model instance
_embedding_model = None

def get_embedding_model(model_name: str):
    """
    Singleton pattern to load the model only once.
    """
    global _embedding_model
    if _embedding_model is None:
        print(f"Loading embedding model: {model_name}...")
        _embedding_model = SentenceTransformer(model_name, trust_remote_code=True)
        print("Model loaded successfully.")
    return _embedding_model

async def local_embedding_func(texts: List[str]) -> np.ndarray:
    """
    Generates embeddings using a local SentenceTransformer model.
    Matches the signature expected by LightRAG's embedding_func.
    """
    from .config import Config
    
    model = get_embedding_model(Config.EMBEDDING_MODEL)
    
    # Generate embeddings (blocking, but wrapped in async)
    embeddings = model.encode(texts, normalize_embeddings=True)
    
    return embeddings

# Attach embedding dimension for LightRAG
local_embedding_func.embedding_dim = 1024
