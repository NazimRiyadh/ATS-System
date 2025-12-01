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
    
    RULES:
    1. You must ONLY use the information explicitly provided in the retrieved context.
    2. DO NOT hallucinate or make up candidate names. Use the EXACT name found in the resume text.
    3. DO NOT mix up details between different candidates.
    4. You MUST extract the 'email' for each candidate to verify their identity. If you cannot find an email, be very careful about the name.
    5. If a candidate does not have the specific skill requested (e.g., "Java"), DO NOT include them in the top results unless they are a strong match for other reasons, and clearly state they lack that specific skill in the summary.
    6. If the retrieved context does not contain enough information to answer the query for a specific candidate, ignore that candidate.

    Each object must have the following keys:
    - "rank": (integer) 1, 2, 3...
    - "name": (string) Candidate Name (EXACTLY as in the document)
    - "email": (string) Candidate Email (to verify identity)
    - "match_score": (integer) 0-100 estimate based on skills and experience match
    - "skills_matched": (list of strings) Key skills found in resume that match query
    - "evidence": (string) Exact quote from the text that proves the candidate has the skills. If the skill is not explicitly mentioned in the text, return "N/A". DO NOT FABRICATE EVIDENCE.
    - "summary": (string) Brief justification (max 20 words). Mention if a key skill is missing.
    
    Do not include any markdown formatting (like ```json). Just the raw JSON string.
    """
    try:
        # Retrieve more chunks to ensure we find enough candidates
        # One candidate might span multiple chunks, so we need > top_k chunks
        retrieval_k = max(60, top_k * 5)
        
        result = await rag.aquery(
            structured_query,
            param=QueryParam(mode="hybrid", top_k=retrieval_k)
        )
        if result is None:
            print("ERROR: LightRAG returned None. Check LLM or Reranker logs.")
            return

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
                # Limit to top_k
                candidates = candidates[:top_k]
                
                console = Console()
                table = Table(title=f"Ranking Results for: {query}", show_lines=True)

                table.add_column("Rank", style="cyan", no_wrap=True)
                table.add_column("Score", style="magenta")
                table.add_column("Name", style="green")
                table.add_column("Keywords Hit", style="yellow")
                table.add_column("Evidence", style="white", overflow="fold")

                for cand in candidates:
                    # evidence = cand.get('evidence', 'N/A')
                    # No truncation needed, rich handles wrapping
                    skills_hit = ", ".join(cand.get('skills_matched', []))
                    table.add_row(
                        str(cand['rank']),
                        f"{cand['match_score']}%",
                        cand['name'],
                        skills_hit,
                        cand.get('evidence', 'N/A')
                    )
                
                console.print(table)
                print("\n")

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
