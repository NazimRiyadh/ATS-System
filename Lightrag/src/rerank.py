from typing import List
from lightrag.utils import logger
from sentence_transformers import CrossEncoder
from .config import Config

# Global variable to cache the model
_rerank_model = None

def get_rerank_model(model_name: str):
    global _rerank_model
    if _rerank_model is None:
        logger.info(f"Loading reranking model: {model_name}...")
        _rerank_model = CrossEncoder(model_name, trust_remote_code=True)
        logger.info("Reranking model loaded successfully.")
    return _rerank_model

def local_rerank_func(query: str, nodes: List[str]) -> List[str]:
    """
    Reranks a list of text chunks based on the query using a local CrossEncoder.
    Matches the signature expected by LightRAG's rerank_model_func.
    
    Args:
        query (str): The search query.
        nodes (List[str]): A list of text chunks to be reranked.
        
    Returns:
        List[str]: The reranked list of text chunks.
    """
    if not nodes:
        return []
        
    try:
        model = get_rerank_model(Config.RERANK_MODEL)
        
        # Prepare pairs for the CrossEncoder
        pairs = [[query, node] for node in nodes]
        
        # Predict scores
        scores = model.predict(pairs)
        
        # Combine nodes with scores
        scored_nodes = list(zip(nodes, scores))
        
        # Sort by score in descending order
        scored_nodes.sort(key=lambda x: x[1], reverse=True)
        
        # Return only the text chunks, sorted
        sorted_nodes = [node for node, score in scored_nodes]
        
        return sorted_nodes
        
    except Exception as e:
        logger.error(f"Error during reranking: {e}")
        # Fallback: return original nodes if reranking fails
        return nodes
