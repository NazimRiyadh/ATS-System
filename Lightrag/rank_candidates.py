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
    Retrieve & Re-Rank Architecture with Domain Guard.
    """
    print("Initializing LightRAG...")
    
    # Get or create a loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # 1. Initialize RAG (Async)
    rag = loop.run_until_complete(initialize_rag())

    # 2. Stage 1: HyDE (Hypothetical Document Embedding)
    print(f"User Query: {query}")
    print("Stage 1: Generating HyDE (Hypothetical Perfect Resume)...")
    hyde_resume = loop.run_until_complete(extract_keywords(query))
    print(f"HyDE Generated (Truncated): '{hyde_resume[:150]}...'")
    
    # 3. Hybrid Search (Retrieval)
    structured_query = f"""
    Find candidates who match this production-ready resume:
    {hyde_resume}
    
    Return a list of candidates.
    """
    
    print("Stage 2: Hybrid Retrieval (Vector + Graph) for Top 30 Candidates...")
    retrieved_chunks = loop.run_until_complete(
        rag.chunks_vdb.query(hyde_resume, top_k=30)
    )
    
    candidates_pool = []
    seen_files = set()
    
    if retrieved_chunks and isinstance(retrieved_chunks[0], list):
        retrieved_chunks = retrieved_chunks[0]

    for chunk in retrieved_chunks:
        chunk_data = loop.run_until_complete(rag.text_chunks.get_by_id(chunk['id']))
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
            
    print(f"Retrieved {len(candidates_pool)} unique candidates from Vector Search.")
    
    if not candidates_pool:
        return []

    # --- DOMAIN GUARD APPLICATION ---
    print("Stage 2.5: Applying Domain Guard (Negative Filtering)...")
    candidates_pool = apply_domain_guard(query, candidates_pool)
    
    if not candidates_pool:
        print("All candidates filtered by Domain Guard.")
        return []
    # --------------------------------

    # 4. Stage 2: Re-Ranking (The "Smart Filter")
    print("Stage 3: Cross-Encoder Re-Ranking (The Smart Filter)...")
    
    resume_texts = [c['resume_text'] for c in candidates_pool]
    
    reranked_results = loop.run_until_complete(
        local_rerank_func(query, resume_texts, top_n=top_k)
    )
    
    final_top_candidates = []
    for rank_idx, result_doc in enumerate(reranked_results):
        for cand in candidates_pool:
            if cand['resume_text'] == result_doc['content']:
                cand['rank'] = rank_idx + 1
                final_top_candidates.append(cand)
                break
    
    # 5. Stage 3: Insight (LLM Explanation)
    print("Stage 4: Generating Insight & Evidence via LLM...")
    
    llm_prompt = "You are an expert AI Recruiter. I did the heavy lifting and found these best candidates.\n"
    llm_prompt += f"JOB DESCRIPTION: {query}\n\n"
    llm_prompt += "Explain specificially WHY each candidate matches. Quote evidence.\n"
    llm_prompt += "Return ONLY a JSON list of objects: [{'rank': 1, 'name': '...', 'email': '...', 'evidence': '...'}]\n"
    
    for c in final_top_candidates:
        llm_prompt += f"Rank {c['rank']}: (File: {c['source_file']})\n{c['resume_text'][:2000]}\n\n"
        
    llm_prompt += "Example Output: [{'rank': 1, 'name': 'John', 'email': 'john@doe.com', 'evidence': 'Has 5 years Python...'}]"
    
    llm_response = loop.run_until_complete(rag.llm_model_func(llm_prompt))
    
    json_str = llm_response
    if "```json" in json_str:
        json_str = re.search(r'```json\n(.*?)\n```', json_str, re.DOTALL).group(1)
    elif "```" in json_str:
        json_str = re.search(r'```\n(.*?)\n```', json_str, re.DOTALL).group(1)
        
    try:
        final_list = json.loads(json_str)
        for i, item in enumerate(final_list):
            if i < len(final_top_candidates):
                item['source_file'] = final_top_candidates[i]['source_file']
                item['match_score'] = max(99 - (i * 2), 60) 
        return final_list
    except Exception as e:
        print(f"JSON Parsing Failed: {e}")
        return []

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
