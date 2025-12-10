"""
Example: Search for candidates using hybrid approach
"""
import sys
sys.path.append('..')

from ats_pipeline import get_pipeline, SearchFilters

def main():
    print("=" * 70)
    print("ATS PIPELINE - SEARCH DEMO")
    print("=" * 70)
    
    # Initialize pipeline
    pipeline = get_pipeline()
    
    # Scenario 1: Search for Python Developer
    print("\n" + "-" * 70)
    print("SCENARIO 1: Searching for Senior Python Developer")
    print("-" * 70)
    
    job_description = """
    We are looking for a Senior Python Developer to join our backend team.
    
    Requirements:
    - 5+ years of experience with Python
    - Experience with microservices and Kubernetes
    - Strong knowledge of database design (PostgreSQL)
    - Bachelor's degree in Computer Science
    """
    
    matches = pipeline.search_candidates(job_description)
    
    print(f"\nFound {len(matches)} matches:\n")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.name} (Score: {match.final_score:.2f})")
        print(f"   Experience: {match.total_experience} years")
        print(f"   Skills: {', '.join(match.matched_skills[:5])}...")
        if match.match_reason:
            print(f"   AI Analysis: {match.match_reason}")
        print()

    # Scenario 2: Search with specific filters
    print("\n" + "-" * 70)
    print("SCENARIO 2: Searching for ML Engineer with specific filters")
    print("-" * 70)
    
    ml_job_description = "Looking for an ML expert with PyTorch experience."
    
    filters = SearchFilters(
        required_skills=["PyTorch", "Python"],
        min_years_experience=3,
        location="New York"
    )
    
    print(f"Filters: {filters.model_dump(exclude_none=True)}")
    
    matches = pipeline.search_candidates(
        ml_job_description,
        filters=filters,
        use_llm_explanations=True
    )
    
    print(f"\nFound {len(matches)} matches:\n")
    for i, match in enumerate(matches, 1):
        print(f"{i}. {match.name} (Score: {match.final_score:.2f})")
        print(f"   Location: {match.summary[:50]}...") # Location isn't directly on match object in simple view
        if match.match_reason:
            print(f"   AI Analysis: {match.match_reason}")
        print()
        
    # Close pipeline
    pipeline.close()

if __name__ == "__main__":
    main()
