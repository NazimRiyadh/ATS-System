import asyncio
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.llm_adapter import ollama_llm_func
from src.prompts import ATS_ENTITY_EXTRACTION_PROMPT

async def main():
    print("Testing LLM Entity Extraction...")
    
    # Sample resume text (shorter)
    sample_text = """
    John Doe
    Software Engineer
    San Francisco, CA
    
    Professional Summary:
    Experienced Software Engineer with expertise in Python, Java, and Machine Learning. 
    Worked at Google as a Senior Developer.
    
    Skills: Python, Java, Docker, Kubernetes, PyTorch.
    
    Experience:
    Google, Senior Developer (2020-Present)
    - Developed AI models using PyTorch.
    """
    
    prompt = ATS_ENTITY_EXTRACTION_PROMPT.format(input_text=sample_text)
    
    print("Sending prompt to LLM...")
    try:
        response = await ollama_llm_func(prompt)
        print("\n=== LLM OUTPUT ===")
        print(response)
        print("==================")
        
        # Analyze output
        lines = response.strip().split('\n')
        ents = [l for l in lines if l.startswith('("entity"')]
        rels = [l for l in lines if l.startswith('("relationship"')]
        
        print(f"Entities found: {len(ents)}")
        print(f"Relationships found: {len(rels)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
