import os
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

import random
import uuid

ROLES = [
    "Senior Python Developer",
    "Junior Frontend Engineer",
    "DevOps Engineer",
    "Data Scientist",
    "Product Manager",
    "Full Stack Developer",
    "Machine Learning Engineer",
    "QA Automation Engineer",
    "UX/UI Designer",
    "Cybersecurity Analyst"
]

PROMPT_TEMPLATE = """
Generate a realistic resume for a {role}.
Include:
- Name (fictional, creative)
- Summary
- Experience (2-4 roles, varied companies)
- Skills (technical and soft skills)
- Education

Format it as plain text.
"""

async def generate_resume(role: str, output_dir: str):
    print(f"Generating resume for: {role}...")
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(role=role)}]
        )
        content = response.choices[0].message.content
        
        # Extract name for filename (simple heuristic)
        lines = content.strip().split('\n')
        name = "Candidate"
        for line in lines:
            if line.strip() and "Name" not in line: # Avoid "Name: John Doe"
                name = line.strip().replace(" ", "_").replace(":", "").replace("*", "")
                break
        
        # Ensure unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{role.replace(' ', '_')}_{name}_{unique_id}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"Saved to {filepath}")
        
    except Exception as e:
        print(f"Error generating resume for {role}: {e}")

async def main():
    output_dir = "./resumes" # Use the main resumes folder
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    tasks = []
    # Generate 3 resumes for each of the 10 roles = 30 resumes
    for role in ROLES:
        for _ in range(3):
            tasks.append(generate_resume(role, output_dir))
        
    await asyncio.gather(*tasks)
    print("Data generation complete.")

if __name__ == "__main__":
    asyncio.run(main())
