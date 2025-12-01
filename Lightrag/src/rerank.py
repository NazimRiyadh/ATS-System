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

async def local_rerank_func(query: str, documents: List[str], **kwargs) -> List[str]:
    """
    Reranks a list of text chunks based on the query using a local CrossEncoder.
    Matches the signature expected by LightRAG's rerank_model_func.
    
    Args:
        query (str): The search query.
        documents (List[str]): A list of text chunks to be reranked.
        top_n (int): Number of top chunks to return.
        
    Returns:
        List[str]: The reranked list of text chunks.
    """
    if not documents:
        return []
        
    try:
        model = get_rerank_model(Config.RERANK_MODEL)
        
        # Prepare pairs for the CrossEncoder
        pairs = [[query, doc] for doc in documents]
        
        # Predict scores
        scores = model.predict(pairs)
        
        # Combine documents with scores
        scored_docs = list(zip(documents, scores))
        
        # Sort by score in descending order
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        
        # Return only the text chunks, sorted
        sorted_docs = [doc for doc, score in scored_docs]
        
        # Handle top_n if passed in kwargs, otherwise return all
        top_n = kwargs.get('top_n', len(sorted_docs))
        
        # Wrap in dicts to satisfy LightRAG expectation
        return [{"content": doc} for doc in sorted_docs[:top_n]]
        
    except Exception as e:
        logger.error(f"Error during reranking: {e}")
        # Fallback: return original documents if reranking fails
        return documents
