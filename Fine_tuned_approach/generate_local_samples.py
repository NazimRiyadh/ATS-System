
import asyncio
import os
import random
from src.llm_local import ollama_model_complete

RESUMES_DIR = "./resumes"
TARGET_COUNT = 50

ROLES = [
    "Senior Python Developer", "Data Scientist", "DevOps Engineer", "Project Manager",
    "Frontend Developer (React)", "Machine Learning Engineer", "Cybersecurity Analyst",
    "Product Owner", "QA Automation Engineer", "Full Stack Developer"
]

PROMPT_TEMPLATE = """
Generate a HYPER-REALISTIC resume for a {role} with 5-10 years of experience.
It MUST look like a real parsed text resume.
Include:
1. Name (Use a random international name)
2. Contact Info (Real looking phone/email/linkedin)
3. Summary (Professional and detailed)
4. Experience (3-4 distinct roles with companies, dates, and detailed bullet points of responsibilities)
5. Skills (Technical and Soft skills)
6. Education (Degree, University, Year)
7. Projects (2 real-world complex projects)

DO NOT include placeholders like [Your Name]. Use REAL sounding fake data.
Output ONLY the resume text.
"""

async def generate_resumes():
    if os.path.exists(RESUMES_DIR):
        print(f"Cleaning {RESUMES_DIR}...")
        for f in os.listdir(RESUMES_DIR):
            os.remove(os.path.join(RESUMES_DIR, f))
    else:
        os.makedirs(RESUMES_DIR)

    print(f"Generating {TARGET_COUNT} Realistic Resumes using Qwen 7B...")
    
    tasks = []
    
    for i in range(TARGET_COUNT):
        role = random.choice(ROLES)
        task = generate_one(i, role)
        tasks.append(task)
        
    # Run in chunks to avoid overloading Ollama
    CHUNK_SIZE = 5
    for i in range(0, len(tasks), CHUNK_SIZE):
        chunk = tasks[i:i+CHUNK_SIZE]
        await asyncio.gather(*chunk)

async def generate_one(index, role):
    print(f"Generating #{index+1} ({role})...")
    prompt = PROMPT_TEMPLATE.format(role=role)
    try:
        text = await ollama_model_complete(prompt, max_tokens=1000, temperature=0.7)
        if len(text) < 200:
            print(f"Failed #{index+1} (Too short). Retrying...")
            return await generate_one(index, role)
            
        # Extract Name for filename
        lines = text.split('\n')
        name_line = next((l for l in lines if len(l.strip()) > 0), "Candidate_Unknown")
        safe_name = name_line.strip().replace(" ", "_").replace(":", "")[:20]
        
        filename = f"{role.replace(' ', '_')}_{safe_name}_{index+1}.txt"
        filepath = os.path.join(RESUMES_DIR, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
            
        print(f"Saved: {filename}")
    except Exception as e:
        print(f"Error generating #{index+1}: {e}")

if __name__ == "__main__":
    asyncio.run(generate_resumes())
