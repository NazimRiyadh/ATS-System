from openai import AsyncOpenAI
from .config import Config

client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

QUERY_PROCESSING_PROMPT = """
You are an expert Recruiter and Search Specialist.
Your task is to extract the most important search keywords from a Job Description.

Input Text:
{text}

Instructions:
1. Identify the Job Role (e.g., "Senior Python Developer").
2. Identify the Top 3-5 Hard Skills.
3. **EXPAND** these skills with common synonyms, acronyms, or related terms to improve search recall.
   - Example: "React" -> "React, React.js, ReactJS"
   - Example: "AWS" -> "AWS, Amazon Web Services, Cloud"
   - Example: "CI/CD" -> "CI/CD, Jenkins, DevOps"
4. Output a single line string in this format:
   "[Role] with [Skill 1, Synonyms], [Skill 2, Synonyms]..."

Example Input:
"We need a frontend dev who knows React and Redux. Must have 3 years exp."
Example Output:
"Frontend Developer with React, React.js, ReactJS, Redux, State Management"

Output only the search string.
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
