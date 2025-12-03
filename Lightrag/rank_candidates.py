import asyncio
import argparse
import json
import re
from lightrag import LightRAG, QueryParam
from src.rag_engine import initialize_rag
from src.query_processor import extract_keywords
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

async def get_ranked_candidates(query: str, top_k: int = 5, rag_instance=None):
    """
    Rank candidates based on a job description or query using LightRAG.
    Returns a list of candidate dictionaries.
    """
    should_finalize = False
    if rag_instance:
        rag = rag_instance
    else:
        print("Initializing LightRAG...")
        rag = await initialize_rag()
        should_finalize = True

    try:
        # Pre-process query
        print(f"Original Query Length: {len(query)} chars")
        refined_query = await extract_keywords(query)
        print(f"Refined Search Query: '{refined_query}'")
        print(f"Searching for candidates matching: {refined_query}...")
        
        # Augmented query to enforce JSON format
        structured_query = f"""
        {refined_query}
        
        IMPORTANT: Return the result ONLY as a JSON list of objects. 
        
        RULES:
        1. You must ONLY use the information explicitly provided in the retrieved context.
        2. DO NOT hallucinate or make up candidate names. Use the EXACT name found in the resume text.
        3. DO NOT mix up details between different candidates.
        4. You MUST extract the 'email' for each candidate to verify their identity. If you cannot find an email, be very careful about the name.
        5. If a candidate is a partial match or lacks a specific skill, YOU MAY INCLUDE THEM but must lower their 'match_score' significantly (e.g., < 60) and clearly state the missing skills in the summary.
        6. Aim to return exactly {top_k} candidates if sufficient relevant context is available.
        7. EXTRACT THE SOURCE FILENAME provided in the context (e.g., "Source: BUSINESS-DEVELOPMENT_123.txt") and include it in the output.
    
        Each object must have the following keys:
        - "rank": (integer) 1, 2, 3...
        - "name": (string) Candidate Name (EXACTLY as in the document)
        - "email": (string) Candidate Email (to verify identity)
        - "source_file": (string) The filename where this candidate was found (e.g., "BUSINESS-DEVELOPMENT_123.txt")
        - "match_score": (integer) 0-100 estimate based on skills and experience match
        - "skills_matched": (list of strings) Key skills found in resume that match query
        - "evidence": (string) Exact quote from the text that proves the candidate has the skills. If the skill is not explicitly mentioned in the text, return "N/A". DO NOT FABRICATE EVIDENCE.
        - "summary": (string) Brief justification (max 20 words). Mention if a key skill is missing.
        
        Do not include any markdown formatting (like ```json). Just the raw JSON string.
        """
        
        # Custom Retrieval Pipeline to inject filenames
        # 1. Search Vector DB for chunks (query handles embedding internally)
        retrieval_k = max(60, top_k * 5)
        results = await rag.chunks_vdb.query(refined_query, top_k=retrieval_k)
        
        # 3. Retrieve chunk content and filenames
        context_parts = []
        seen_files = set()
        
        # Handle potential batch results (though query usually returns list of dicts)
        if results and isinstance(results[0], list):
            results = results[0]
            
        for res in results:
            chunk_id = res.get('id') or res.get('node_id')
            if not chunk_id:
                continue
                
            chunk_data = await rag.text_chunks.get_by_id(chunk_id)
            if not chunk_data:
                continue
                
            content = chunk_data.get('content', '')
            file_path = chunk_data.get('file_path', 'Unknown File')
            filename = file_path.split('/')[-1].split('\\')[-1] # Extract basename
            
            context_parts.append(f"Source: {filename}\nContent:\n{content}\n")
            seen_files.add(filename)
            
        context_str = "\n---\n".join(context_parts)
        
        print(f"DEBUG: Retrieved {len(context_parts)} chunks from {len(seen_files)} files.")

        # 4. Generate Answer using LLM
        prompt = f"""
        Query: {structured_query}
        
        Retrieved Context:
        {context_str}
        """
        
        result = await rag.llm_model_func(prompt)
        
        if result is None:
            print("ERROR: LLM returned None.")
            return []

        # Clean result to ensure valid JSON
        json_str = result
        if "```json" in json_str:
            json_str = re.search(r'```json\n(.*?)\n```', json_str, re.DOTALL).group(1)
        elif "```" in json_str:
            json_str = re.search(r'```\n(.*?)\n```', json_str, re.DOTALL).group(1)
            
        try:
            candidates = json.loads(json_str)
            
            if not candidates:
                print("No candidates found.")
                return []
            else:
                # Limit to top_k
                candidates = candidates[:top_k]
                return candidates

        except json.JSONDecodeError:
            print("Failed to parse structured output. Showing raw result:")
            print(result)
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    finally:
        if should_finalize:
            await rag.finalize_storages()

async def rank_candidates(query: str, top_k: int = 5):
    candidates = await get_ranked_candidates(query, top_k)
    
    print("\n" + "="*80)
    print(f"RANKING RESULTS FOR: {query}")
    print("="*80 + "\n")

    if not candidates:
        print("No candidates found.")
        return

    console = Console()
    table = Table(title=f"Ranking Results for: {query}", show_lines=True)

    table.add_column("Rank", style="cyan", no_wrap=True)
    table.add_column("Score", style="magenta")
    table.add_column("Name", style="green")
    table.add_column("Source File", style="blue", overflow="fold", min_width=30)
    table.add_column("Keywords Hit", style="yellow")
    table.add_column("Evidence", style="white", overflow="fold")

    for cand in candidates:
        skills_hit = ", ".join(cand.get('skills_matched', []))
        table.add_row(
            str(cand['rank']),
            f"{cand['match_score']}%",
            cand['name'],
            cand.get('source_file', 'N/A'),
            skills_hit,
            cand.get('evidence', 'N/A')
        )
    
    console.print(table)
    print("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rank candidates using LightRAG.")
    parser.add_argument("--query", type=str, required=True, help="Job description or query string")
    parser.add_argument("--top_k", type=int, default=5, help="Number of top results to consider")
    args = parser.parse_args()

    asyncio.run(rank_candidates(args.query, args.top_k))
