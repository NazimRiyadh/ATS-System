
import asyncio
import logging
from src.llm_adapter import ollama_llm_func

logging.basicConfig(level=logging.INFO)

async def test_llm():
    print("🤖 Testing LLM connection (Ollama)...")
    prompt = "Say 'LLM is working' if you can hear me."
    
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
