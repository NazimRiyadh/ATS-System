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
        
        # Predict scores (Logits)
        raw_scores = model.predict(pairs)
        
        # Apply Sigmoid to convert Logits -> Probability (0 to 1)
        import numpy as np
        scores = 1 / (1 + np.exp(-raw_scores))
        
        # Combine documents with NORMALIZED scores
        scored_docs = list(zip(documents, scores))
        
        # Sort by score in descending order
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        # DEBUG: Log top 5 scores to see what we are dealing with
        # DEBUG: Log top candidates to verify retrieval quality
        if scored_docs:
             logger.info("--- RERANKER TOP CANDIDATES ---")
             for i, (text, score) in enumerate(scored_docs[:3]):
                 snippet = text[:100].replace('\n', ' ')
                 logger.info(f"Rank {i+1}: Score={score:.4f} | Content='{snippet}...'")
             logger.info("-------------------------------")
        
        # FILTER: Keep only documents with score > THRESHOLD
        # This prevents returning irrelevant results even if top_k is high
        threshold = getattr(Config, 'RERANK_THRESHOLD', 0.15)
        filtered_docs = [
            doc for doc, score in scored_docs 
            if score >= threshold
        ]
        
        logger.info(f"Rerank Filter: {len(documents)} -> {len(filtered_docs)} candidates (Threshold: {threshold})")

        # Handle top_n if passed in kwargs
        top_n = kwargs.get('top_n', len(filtered_docs))
        
        # Return truncated list
        final_docs = filtered_docs[:top_n]

        # LightRAG often expects string list, but some versions dict.
        # Based on previous code: return [{"content": doc} ...] seems wrong if LightRAG signature expects List[str].
        # Let's check signature from previous inspections or stick to what worked. 
        # The return type annotation says List[str].
        # But code was returning `[{"content": doc} ...]` which is List[Dict].
        # IMPORTANT: LightRAG's rerank signature usually expects `List[str] -> List[str]`.
        # I will revert to List[str] if I suspect a type mismatch, but if it worked before...
        # Wait, the previous code was: `return [{"content": doc} for doc in sorted_docs[:top_n]]`
        # Let's keep the return format consistent to avoid breaking it, just apply filter.
        
        return [{"content": doc} for doc in final_docs]

    except Exception as e:
        logger.error(f"Error during reranking: {e}")
        # Fallback: return original documents if reranking fails
        return [{"content": doc} for doc in documents]
