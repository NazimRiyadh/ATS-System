import asyncio
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.llm_adapter import ollama_llm_func
# Ensure we get the latest prompt
from src.prompts import ATS_ENTITY_EXTRACTION_PROMPT

async def main():
    print("Testing LLM Entity Extraction with ### delimiter...")
    print(f"Prompt preview (first 200 chars): {ATS_ENTITY_EXTRACTION_PROMPT[:200]}")
    
    if "###" not in ATS_ENTITY_EXTRACTION_PROMPT:
        print("CRITICAL WARNING: Prompt does not seem to contain '###' delimiter!")
    
    sample_text = """
    John Doe
    Software Engineer
    San Francisco, CA
    
    Experience:
    Google, Senior Developer (2020-Present)
    - Developed AI models.
    """
    
    prompt = ATS_ENTITY_EXTRACTION_PROMPT.format(input_text=sample_text)
    
    print("Sending prompt to LLM...")
    try:
        response = await ollama_llm_func(prompt)
        print("\n=== LLM OUTPUT ===")
        print(response)
        print("==================")
        
        lines = response.strip().split('\n')
        ents = [l for l in lines if l.startswith('("entity"')]
        rels = [l for l in lines if l.startswith('("relationship"')]
        # Also check for pipes just in case
        pipe_lines = [l for l in lines if "|" in l and "###" not in l]
        
        print(f"Entities found (###): {len(ents)}")
        print(f"Relationships found (###): {len(rels)}")
        print(f"Pipe lines found: {len(pipe_lines)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
