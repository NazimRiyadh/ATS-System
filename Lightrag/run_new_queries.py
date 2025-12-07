import asyncio
import json
from rich.console import Console
from rich.table import Table
from rank_candidates import get_ranked_candidates

# Define test JDs
JDS = [
    {
        "company": "Rapidus Corporation US",
        "title": "Process Integration Engineer",
        "description": "Rapidus Corporation US is seeking a Process Integration Engineer... Skills: Semiconductor, Lithography, Yield Improvement, Data Analysis, Process Integration, Advanced Manufacturing, Troubleshooting."
    },
    {
        "company": "Samsung Austin Semiconductor",
        "title": "Senior Process Integration Engineer",
        "description": "Samsung Austin Semiconductor is looking for a Senior Process Integration Engineer... Skills: Semiconductor manufacturing, process flow, defect reduction, yield enhancement, 2nm/3nm technology, cross-functional collaboration."
    }
]

def run_queries():
    console = Console()
    report_content = "# Ranking Results (Retrieve & Re-Rank)\n\n"
    
    for jd in JDS:
        title = jd['title']
        company = jd['company']
        print(f"\nProcessing: {company} - {title}...")
        
        # Call synchronous function
        candidates = get_ranked_candidates(jd['description'], top_k=5)
        
        report_content += f"## {company} - {title}\n\n"
        
        table = Table(title=f"Results: {company} - {title}", show_lines=True)
        table.add_column("Rank", style="cyan", no_wrap=True)
        table.add_column("Score", style="magenta")
        table.add_column("Name", style="green")
        table.add_column("Source", style="blue")
        table.add_column("Insight", style="white")

        if not candidates:
            print("No candidates found.")
            report_content += "No candidates found.\n\n"
        else:
            report_content += "| Rank | Score | Name | Source | Insight |\n"
            report_content += "|---|---|---|---|---|\n"
            for cand in candidates:
                rank = str(cand.get('rank', '-'))
                score = f"{cand.get('match_score', 0)}%"
                name = cand.get('name', 'Unknown')
                source = cand.get('source_file', 'N/A')
                evidence = cand.get('evidence', 'N/A')
                
                table.add_row(rank, score, name, source, evidence[:200] + "...")
                
                # Clean evidence for markdown table
                clean_evidence = (evidence or "").replace('\n', ' ').replace('|', ' ')
                report_content += f"| {rank} | {score} | {name} | {source} | {clean_evidence} |\n"
            
            console.print(table)
            report_content += "\n"
        print("-" * 50)
        report_content += "---\n\n"

    with open("new_jd_results.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    print("\nResults saved to new_jd_results.md")

if __name__ == "__main__":
    run_queries()
