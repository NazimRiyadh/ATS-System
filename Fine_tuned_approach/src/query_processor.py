from openai import AsyncOpenAI
from .config import Config

client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

QUERY_PROCESSING_PROMPT = """
You are an expert Resume Writer and Recruiter.
Your task is to write a HYPOTHETICAL PERFECT RESUME snippet based on the Job Description provided.

Input Job Description:
{text}

Instructions:
1. Analyze the job requirements (Role, Skills, Experience).
2. Write a short, first-person resume summary (about 5-8 sentences) that an ideal candidate would have.
3. Include specific technical keywords, tools, and achievements that match the JD perfectly.
4. Do NOT add filler text. Focus on "I have experience in..." and "I built..." statements.

Example Output:
"I am a Senior Python Developer with 5 years of experience building scalable APIs using Django and FastAPI. I have deep knowledge of AWS services like Lambda and S3. I successfully migrated a monolith to microservices using Docker and Kubernetes. I am proficient in PostgreSQL and Redis for data caching."

Output only the hypothetical resume text.
"""

async def extract_keywords(text: str) -> str:
    """
    Extracts a concise search query from a long text using an LLM.
    """
    # If text is short, just return it
    # if len(text.split()) < 10:
    #     return text

    try:
        response = await client.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": QUERY_PROCESSING_PROMPT.format(text=text)}
            ],
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error processing query: {e}")
        return text # Fallback to original text
