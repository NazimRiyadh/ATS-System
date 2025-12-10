
import asyncio
from src.llm_local import ollama_model_complete
from src.prompts import ATS_ENTITY_EXTRACTION_PROMPT

async def test_quality():
    print("Testing Flan-T5 Quality on Extraction Prompt...")
    
    sample_text = """
    Name: Rahim Uddin
    Experience: 
    - Senior Python Developer at Google (2020-2024). Used Django, AWS.
    Education:
    - B.S. Computer Science, BUET.
    """
    

    # Simulate what LightRAG does
    prompt = ATS_ENTITY_EXTRACTION_PROMPT.format(
        input_text=sample_text,
        entity_types="Organization,Person,Skill,Job",
        tuple_delimiter="|",
        record_delimiter="##"
    )

    
    print("\n--- Sending Prompt to Ollama (Flan-T5) ---")
    response = await ollama_model_complete(prompt)
    
    print("\n--- RAW RESPONSE ---")
    print(response)
    print("\n--------------------")
    
    if not response or len(response) < 10:
        print("❌ FAILED: Response is empty or too short. Model is likely failing to generate.")
    elif "(" not in response:
        print("❌ WARNING: Response doesn't look like tuples. Format might be wrong.")
    else:
        print("✅ SUCCESS: Output looks somewhat structured.")

if __name__ == "__main__":
    asyncio.run(test_quality())
