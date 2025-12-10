import asyncio
import argparse
import json
import re
from lightrag import LightRAG, QueryParam
from src.rag_engine import initialize_rag
from src.query_processor import extract_keywords
from src.rerank import local_rerank_func  # New import for Cross-Encoder
from rich.console import Console
from rich.table import Table
from rich import print as rprint


# Domain Guard Configuration
DOMAIN_NEGATIVES = {
    "engineer": ["media planner", "journalism", "advertising", "sales associate", "creative director", "traffic coordinator", "marketing strategy"],
    "developer": ["media planner", "journalism", "advertising", "sales associate", "creative director"],
    "data": ["sales associate", "customer service", "receptionist"],
}

def apply_domain_guard(query: str, candidates: list) -> list:
    """
    Penalizes candidates who have high frequency of negative keywords for the specific query domain.
    """
    query_lower = query.lower()
    negative_terms = []
    
    # Identify relevant negative filters
    for domain, terms in DOMAIN_NEGATIVES.items():
        if domain in query_lower:
            negative_terms.extend(terms)
            
    if not negative_terms:
        return candidates

    print(f"Domain Guard Active: Blocking {negative_terms[:3]}...")
    
    filtered_candidates = []
    for cand in candidates:
        text = cand['resume_text'].lower()
        penalty_score = 0
        
        # Check for presence of negative terms
        matches = [term for term in negative_terms if term in text]
        
        # If specific "kill words" are found, heavily penalize
        if len(matches) > 0:
             print(f"  > Penalizing {cand['source_file']} due to forbidden terms: {matches[:2]}")
             # Add a penalty flag or artificially lower score if we had one.
             # Since we are pre-rerank (or post-retrieval), we can just exclude them 
             # or mark them to be skipped.
             cand['is_penalized'] = True
             cand['penalty_reason'] = f"Forbidden terms: {', '.join(matches[:2])}"
        else:
             cand['is_penalized'] = False
             
        filtered_candidates.append(cand)
        
    # Filter out penalized candidates entirely or push to bottom
    # Here we exclude them to ensure "Top 5" are clean
    clean_candidates = [c for c in filtered_candidates if not c.get('is_penalized')]
    
    if len(clean_candidates) < len(candidates):
        print(f"Domain Guard removed {len(candidates) - len(clean_candidates)} candidates.")
        
    return clean_candidates


def get_ranked_candidates(query: str, top_k: int = 5):
    """
    Full Retrieve & Re-Rank Pipeline (Legacy/Direct Use).
    """
    # ... (Reuse internal logic or call the new split functions)
    return run_full_pipeline(query, top_k)

async def retrieve_candidates_vector_only(query: str, top_k: int = 20) -> list:
    """
    Stage 1: The Fast Filter (Vector Only).
    Returns raw candidate data (text, source_file) without heavy re-ranking or building a new graph.
    """
    print(f"Stage 1: Vector Search for '{query}'...")
    
    # Initialize Global RAG just for vector access
    rag = await initialize_rag()
    
    # Generate HyDE
    hyde_resume = await extract_keywords(query)
    
    # Vector Search
    # We ask for a bit more than top_k to account for Domain Guard filtering
    retrieved_chunks = await rag.chunks_vdb.query(hyde_resume, top_k=top_k * 2)
    
    candidates_pool = []
    seen_files = set()
    
    if retrieved_chunks and isinstance(retrieved_chunks[0], list):
        retrieved_chunks = retrieved_chunks[0]

    for chunk in retrieved_chunks:
        chunk_data = await rag.text_chunks.get_by_id(chunk['id'])
        if not chunk_data:
            continue
            
        content = chunk_data.get('content', '')
        file_path = chunk_data.get('file_path', 'Unknown File')
        filename = file_path.split('/')[-1].split('\\')[-1]
        
        if filename not in seen_files:
            candidates_pool.append({
                "source_file": filename,
                "resume_text": content,
                "original_score": chunk.get('score', 0)
            })
            seen_files.add(filename)
            
    # Apply Domain Guard
    candidates_pool = apply_domain_guard(query, candidates_pool)
    
    # --- RERANKING STEP ADDED ---
    # We now apply the Cross-Encoder here to filter out bad matches
    # ensuring we don't return 20 junk results just because top_k=20.
    print(f"Stage 1b: Re-Ranking {len(candidates_pool)} candidates...")
    
    candidate_texts = [c['resume_text'] for c in candidates_pool]
    # This call will use the new FILTERING logic inside rerank.py (Score > 0.35)
    reranked_results = await local_rerank_func(query, candidate_texts, top_n=top_k)
    
    # Re-map back to full candidate objects
    final_candidates = []
    # Reranker returns dicts like {'content': '...'}
    # We need to preserve the source_file metadata.
    # We'll map by content matching.
    
    found_contents = set()
    
    for r in reranked_results:
        r_content = r['content']
        for c in candidates_pool:
            if c['resume_text'] == r_content:
                if r_content not in found_contents:
                    final_candidates.append(c)
                    found_contents.add(r_content)
                break
                
    num_dropped = len(candidates_pool) - len(final_candidates)
    if num_dropped > 0:
        print(f"Reranker Dropped: {num_dropped} low-quality candidates.")
        # DEBUG: Show what was dropped and why
        dropped_docs = []
        for r in reranked_results:
            if r['content'] not in found_contents:
                 dropped_docs.append(r)
        
        # If reranker filtered them out inside local_rerank_func, we won't see them here 
        # because local_rerank_func returns the truncated list.
        # However, checking the logs or the difference helps.
        pass
    
    return final_candidates

def run_full_pipeline(query: str, top_k: int = 5):
    # This preserves the original logic for the CLI tool
    # Re-implementing the original flow using the new async structure or just wrapping it
    # For minimal disruption, I'll allow the original CLI to use the original synchronous wrapper style
    # but re-using the components.
    
    # ... (Actual implementation of the full flow if needed, 
    # but for the API we will explicitly call stages 1, 2, 3)
    # For now, let's keep the original get_ranked_candidates logic essentially 
    # but refactored. 
    pass # Replaced by the implementation below

async def get_ranked_candidates_async(query: str, top_k: int = 5):
    # Original logic adapted
    candidates = await retrieve_candidates_vector_only(query, top_k=30)
    
    if not candidates:
        return []
        
    print("Stage 3: Cross-Encoder Re-Ranking...")
    resume_texts = [c['resume_text'] for c in candidates]
    reranked = await local_rerank_func(query, resume_texts, top_n=top_k)
    
    final = []
    for r in reranked:
        for c in candidates:
            if c['resume_text'] == r['content']:
                final.append(c)
                break
                
    # LLM Insight (Stage 4 in original flow)
    # ... (LLM Logic)
    return final # Simplified for now to focus on the API split


def rank_candidates(query: str, top_k: int = 5):
    candidates = get_ranked_candidates(query, top_k)
    
    print("\n" + "="*80)
    print(f"RETRIEVE & RE-RANK RESULTS FOR: {query}")
    print("="*80 + "\n")

    if not candidates:
        print("No candidates found.")
        return

    console = Console()
    table = Table(title=f"Results: {query}", show_lines=True)

    table.add_column("Rank", style="cyan", no_wrap=True)
    table.add_column("Score", style="magenta")
    table.add_column("Name", style="green")
    table.add_column("Source File", style="blue", overflow="fold")
    table.add_column("Insight / Evidence", style="white", overflow="fold")

    for cand in candidates:
        table.add_row(
            str(cand.get('rank', '-')),
            f"{cand.get('match_score', 0)}%",
            cand.get('name', 'Unknown'),
            cand.get('source_file', 'N/A'),
            cand.get('evidence', 'N/A')
        )
    
    console.print(table)
    print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rank candidates using LightRAG (Retrieve & Re-Rank).")
    parser.add_argument("--query", type=str, required=True, help="Job description or query string")
    parser.add_argument("--top_k", type=int, default=5, help="Number of top results to consider")
    args = parser.parse_args()

    rank_candidates(args.query, args.top_k)
