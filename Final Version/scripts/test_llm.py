
import asyncio
import logging
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm_adapter import ollama_llm_func, settings

logging.basicConfig(level=logging.INFO)

async def test_llm():
    print(f"🤖 Testing LLM connection (Provider: {settings.llm_provider})...")
    print(f"   Model: {settings.gemini_model if settings.llm_provider == 'gemini' else settings.llm_model}")
    
    prompt = "Say 'Gemini is working' if you can hear me."
    
    try:
        response = await ollama_llm_func(prompt)
        print("\n✅ RESPONSE RECEIVED:")
        print("-" * 20)
        print(response)
        print("-" * 20)
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(test_llm())
