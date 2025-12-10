import sys
sys.path.append('..')
from ats_pipeline import get_pipeline

def main():
    pipeline = get_pipeline()
    print("Running Scenario 1...")
    
    job_description = """
    We are looking for a Senior Python Developer to join our backend team.
    Requirements:
    - 5+ years of experience with Python
    - Experience with microservices and Kubernetes
    - Strong knowledge of database design (PostgreSQL)
    - Bachelor's degree in Computer Science
    """
    
    matches = pipeline.search_candidates(job_description)
    
    with open("result.txt", "w") as f:
        f.write(f"Found {len(matches)} matches\n")
        for match in matches:
            f.write(f"- {match.name} (Score: {match.final_score})\n")
    
    print(f"Found {len(matches)} matches")
    for match in matches:
        print(f"- {match.name} (Score: {match.final_score})")

if __name__ == "__main__":
    main()
