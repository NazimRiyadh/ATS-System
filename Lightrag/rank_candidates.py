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

async def rank_candidates(query: str, top_k: int = 5):
    """
    Rank candidates based on a job description or query using LightRAG.
    """
    # console = Console(force_terminal=True, width=120)
    # console.print(Panel(f"[bold blue]Initializing LightRAG...[/bold blue]", border_style="blue"))
    print("Initializing LightRAG...")
    rag = await initialize_rag()

    # Pre-process query
    print(f"Original Query Length: {len(query)} chars")
    refined_query = await extract_keywords(query)
    print(f"Refined Search Query: '{refined_query}'")

    # console.print(f"[bold green]Searching for candidates matching:[/bold green] {query[:50]}...")
    print(f"Searching for candidates matching: {refined_query}...")
    
    # Augmented query to enforce JSON format
    structured_query = f"""
    {refined_query}
    
    IMPORTANT: Return the result ONLY as a JSON list of objects. 
    Each object must have the following keys:
    - "rank": (integer) 1, 2, 3...
    - "name": (string) Candidate Name
    - "match_score": (integer) 0-100 estimate based on skills and experience match
    - "skills_matched": (list of strings) Key skills found in resume that match query
    - "summary": (string) Brief justification (max 20 words)
    
    Do not include any markdown formatting (like ```json). Just the raw JSON string.
    """

    try:
        result = await rag.aquery(
            structured_query,
            param=QueryParam(mode="hybrid", top_k=top_k)
        )
        
        # Clean result to ensure valid JSON
        json_str = result
        if "```json" in json_str:
            json_str = re.search(r'```json\n(.*?)\n```', json_str, re.DOTALL).group(1)
        elif "```" in json_str:
            json_str = re.search(r'```\n(.*?)\n```', json_str, re.DOTALL).group(1)
            
        try:
            candidates = json.loads(json_str)
            
            print("\n" + "="*80)
            print(f"RANKING RESULTS FOR: {query}")
            print("="*80 + "\n")
            
            if not candidates:
                print("No candidates found.")
            else:
                print(f"{'RANK':<5} | {'SCORE':<6} | {'NAME':<25} | {'SUMMARY'}")
                print("-" * 80)
                for cand in candidates:
                    print(f"{cand['rank']:<5} | {cand['match_score']:<5}% | {cand['name']:<25} | {cand['summary']}")
                print("-" * 80 + "\n")

        except json.JSONDecodeError:
            print("Failed to parse structured output. Showing raw result:")
            print(result)
        except Exception as e:
            print(f"An error occurred: {e}")

    finally:
        await rag.finalize_storages()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rank candidates using LightRAG.")
    parser.add_argument("--query", type=str, required=True, help="Job description or query string")
    parser.add_argument("--top_k", type=int, default=5, help="Number of top results to consider")
    args = parser.parse_args()

    asyncio.run(rank_candidates(args.query, args.top_k))
