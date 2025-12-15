import asyncio
from llm_adapter import OllamaAdapter
from prompts import ATS_ENTITY_EXTRACTION_PROMPT

async def test_llm():
    print("🧪 Testing LLM Adapter logic...")
    
    # This is a sample resume text
    dummy_text = "Jane Doe is a Senior Java Developer at Microsoft. She knows Python and AWS."
    
    # Prepare the prompt exactly like LightRAG does
    prompt = ATS_ENTITY_EXTRACTION_PROMPT.format(input_text=dummy_text)
    
    # Call your function
    print("\n--- Sending Request to Ollama ---")
    response = await OllamaAdapter().generate(prompt)
    
    print("\n--- RAW RESPONSE (Check for Stutter Here) ---")    
    print(response)
    print("---------------------------------------------")

if __name__ == "__main__":
    asyncio.run(test_llm())