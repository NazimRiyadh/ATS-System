import requests
import json
import os

# Define 3 Distinct Job Descriptions
jds = [
    {
        "id": "job_python_001",
        "title": "Senior Python Backend Developer",
        "description": """
        We are looking for a Senior Python Developer with 5+ years of experience.
        Must have strong skills in Django or Flask, and experience with REST APIs.
        Knowledge of PostgreSQL and Docker is required.
        AWS experience is a plus.
        """
    },
    {
        "id": "job_data_002",
        "title": "Data Scientist",
        "description": """
        Seeking a Data Scientist to build predictive models.
        Required skills: Python, Pandas, Scikit-learn, TensorFlow or PyTorch.
        Experience with NLP and Large Language Models (LLMs) is highly desirable.
        Must have a Master's degree in Computer Science or Statistics.
        """
    },
    {
        "id": "job_devops_003",
        "title": "DevOps Engineer",
        "description": """
        We need a DevOps Engineer to manage our cloud infrastructure.
        Must be proficient in AWS, Terraform, and Kubernetes.
        Experience with CI/CD pipelines (Jenkins, GitHub Actions) is mandatory.
        Linux system administration skills are required.
        """
    }
]

OUTPUT_FILE = "batch_search_results.json"
API_URL = "http://127.0.0.1:8000/analyze_job"

results = []

print(f"🚀 Starting Batch Search for {len(jds)} JDs...\n")

for job in jds:
    print(f"🔎 Searching for: {job['title']}...")
    payload = {
        "job_id": job['id'],
        "query": job['description'],
        "top_k": 5
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data.get('candidates_found')} candidates.")
            results.append({
                "job_title": job['title'],
                "job_description": job['description'].strip(),
                "candidates": data.get("candidates_preview", [])
            })
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            results.append({
                "job_title": job['title'],
                "error": response.text
            })
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        results.append({
             "job_title": job['title'],
             "error": str(e)
        })

# Save to file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print(f"\n✨ All Done! Results saved to '{os.path.abspath(OUTPUT_FILE)}'")
